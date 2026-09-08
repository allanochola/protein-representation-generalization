#!/usr/bin/env python3
"""
Experiment 04 post hoc decoder-geometry analysis engine.

IMPORTANT
---------
This module implements decoder-side geometry only.

It does not recover biological or permutation-null Stage-B coefficients.
It does not access confirmatory data.
It does not itself run the isotropic population unless explicitly invoked
by a separate audited driver.

Frozen specification:
DECODER_GEOMETRY_BETA_RECOVERY_SPEC.md
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Any
import hashlib
import json
import math
import os
import time
import tempfile

import numpy as np


# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------

D_MODEL = 1280
N_DECODER_COLUMNS = 10240
N_ZERO_COLUMNS = 9
N_USABLE_COLUMNS = 10231

OMP_MAX_K = 512
K_GRID = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)

LSTSQ_RCOND = 1e-12
RESIDUAL_ZERO_TOL = 1e-12
CORRELATION_ZERO_TOL = 1e-12
R_BOUND_TOL = 1e-12
MONOTONICITY_TOL = 1e-12
RAW_WEIGHT_DENOM_TOL = 1e-15

ISOTROPIC_ROOT_SEED = 2026090802
BOOTSTRAP_ROOT_SEED = 2026090801

EXPECTED_SAE_SHA256 = (
    "bf0dfb992321cf4d1ce80fced0db0256f5c7a1f9fdd8a7fe4834e786c1f6472a"
)
EXPECTED_DECODER_KEY = "decoder.weight"

TIMING_VECTOR_INDICES = (0, 1, 2, 3, 4)
TIMING_PROJECTED_1000_HOURS_CUTOFF = 8.0
ALLOWED_N_ISO = (500, 1000)

# This module never names or opens confirmatory paths.
CONFIRMATORY_DENY_TOKENS = (
    "confirmatory",
    "confirm_universe",
    "3541",
    "161pos",
)


# ---------------------------------------------------------------------------
# Result structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DecoderBundle:
    """
    In-memory decoder representations.

    D_raw:
        Exact checkpoint decoder.weight in float64, shape (1280, 10240).

    D_unit:
        Unit-L2 normalized copy of nonzero decoder columns only,
        shape (1280, 10231).

    usable_original_indices:
        Original checkpoint column index for every D_unit atom.

    zero_original_indices:
        Exact zero-norm checkpoint decoder columns.
    """
    D_raw: np.ndarray
    D_unit: np.ndarray
    usable_original_indices: np.ndarray
    zero_original_indices: np.ndarray


@dataclass
class OMPResult:
    status: str
    rank_deficient: bool
    rank_deficiency_step: Optional[int]
    exact_reconstruction_step: Optional[int]
    selected_original_indices: List[int]
    r_by_k: Dict[str, Optional[float]]
    rank_by_k: Dict[str, Optional[int]]
    condition_by_k: Dict[str, Optional[float]]
    threshold_k_50: Optional[str]
    threshold_k_80: Optional[str]
    threshold_k_90: Optional[str]


@dataclass
class RawWeightResult:
    status: str
    denominator: float
    topk_mass: Dict[str, Optional[float]]
    n_eff: Optional[float]


# ---------------------------------------------------------------------------
# General helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def assert_no_confirmatory_path(path: Path) -> None:
    lower = str(path).lower()
    bad = [token for token in CONFIRMATORY_DENY_TOKENS if token in lower]
    if bad:
        raise RuntimeError(
            f"CONFIRMATORY FIREWALL: denied path token(s) {bad}: {path}"
        )


def _as_float64_vector(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    if arr.shape != (D_MODEL,):
        raise ValueError(
            f"Expected vector shape {(D_MODEL,)}, observed {arr.shape}"
        )
    if not np.all(np.isfinite(arr)):
        raise ValueError("Vector contains non-finite values.")
    return np.ascontiguousarray(arr, dtype=np.float64)


def normalize_direction(x: np.ndarray) -> Optional[np.ndarray]:
    """
    Exact zero-beta semantics.

    Returns None iff ||x||_2 == 0 exactly.
    """
    arr = _as_float64_vector(x)
    norm = float(np.linalg.norm(arr))
    if norm == 0.0:
        return None
    return np.ascontiguousarray(arr / norm, dtype=np.float64)


# ---------------------------------------------------------------------------
# Exact decoder verification / loading
# ---------------------------------------------------------------------------

def load_verified_decoder(checkpoint_path: Path) -> DecoderBundle:
    """
    Verify exact SAE artifact SHA-256 before deserialization.

    Uses torch.load(..., weights_only=True) and reads decoder.weight only.
    """
    checkpoint_path = Path(checkpoint_path)
    assert_no_confirmatory_path(checkpoint_path)

    observed_sha = sha256_file(checkpoint_path)
    if observed_sha != EXPECTED_SAE_SHA256:
        raise RuntimeError(
            "SAE checkpoint SHA mismatch.\n"
            f"expected: {EXPECTED_SAE_SHA256}\n"
            f"observed: {observed_sha}"
        )

    import torch

    state = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=True,
    )

    if EXPECTED_DECODER_KEY not in state:
        raise RuntimeError(
            f"Missing checkpoint tensor {EXPECTED_DECODER_KEY!r}"
        )

    tensor = state[EXPECTED_DECODER_KEY]

    if tuple(tensor.shape) != (D_MODEL, N_DECODER_COLUMNS):
        raise RuntimeError(
            "Decoder shape mismatch.\n"
            f"expected: {(D_MODEL, N_DECODER_COLUMNS)}\n"
            f"observed: {tuple(tensor.shape)}"
        )

    D_raw = np.asarray(
        tensor.detach().cpu().numpy(),
        dtype=np.float64,
    )
    D_raw = np.ascontiguousarray(D_raw)

    if not np.all(np.isfinite(D_raw)):
        raise RuntimeError("Decoder contains non-finite entries.")

    norms = np.linalg.norm(D_raw, axis=0)

    zero_mask = norms == 0.0
    zero_indices = np.flatnonzero(zero_mask).astype(np.int64)
    usable_indices = np.flatnonzero(~zero_mask).astype(np.int64)

    if zero_indices.size != N_ZERO_COLUMNS:
        raise RuntimeError(
            f"Expected {N_ZERO_COLUMNS} exact zero atoms, "
            f"observed {zero_indices.size}."
        )

    if usable_indices.size != N_USABLE_COLUMNS:
        raise RuntimeError(
            f"Expected {N_USABLE_COLUMNS} usable atoms, "
            f"observed {usable_indices.size}."
        )

    D_unit = D_raw[:, usable_indices] / norms[usable_indices][None, :]
    D_unit = np.ascontiguousarray(D_unit, dtype=np.float64)

    unit_norms = np.linalg.norm(D_unit, axis=0)

    if not np.allclose(
        unit_norms,
        1.0,
        rtol=0.0,
        atol=1e-10,
    ):
        raise RuntimeError("D_unit normalization invariant failed.")

    return DecoderBundle(
        D_raw=D_raw,
        D_unit=D_unit,
        usable_original_indices=usable_indices,
        zero_original_indices=zero_indices,
    )


# ---------------------------------------------------------------------------
# Indexed isotropic RNG
# ---------------------------------------------------------------------------

def isotropic_child_seedsequence(index: int) -> np.random.SeedSequence:
    """
    Independently derive vector index i from the frozen root.

    This does not advance any shared RNG state.
    """
    if not isinstance(index, (int, np.integer)):
        raise TypeError("index must be integer")
    index = int(index)
    if index < 0:
        raise ValueError("index must be nonnegative")

    return np.random.SeedSequence(
        ISOTROPIC_ROOT_SEED,
        spawn_key=(index,),
    )


def isotropic_child_identifier(index: int) -> str:
    ss = isotropic_child_seedsequence(index)
    words = ss.generate_state(4, dtype=np.uint32)
    raw = np.ascontiguousarray(words.astype("<u4")).tobytes()
    return hashlib.sha256(raw).hexdigest()


def generate_isotropic_direction(index: int) -> np.ndarray:
    ss = isotropic_child_seedsequence(index)
    rng = np.random.Generator(np.random.PCG64(ss))

    x = rng.standard_normal(D_MODEL, dtype=np.float64)
    norm = float(np.linalg.norm(x))

    if not np.isfinite(norm) or norm == 0.0:
        raise RuntimeError(
            f"Invalid isotropic vector norm at index {index}: {norm}"
        )

    x = x / norm
    x = np.ascontiguousarray(x, dtype=np.float64)

    if x.shape != (D_MODEL,):
        raise RuntimeError("Isotropic vector shape invariant failed.")

    if abs(float(np.linalg.norm(x)) - 1.0) > 1e-12:
        raise RuntimeError("Isotropic unit-norm invariant failed.")

    return x


# ---------------------------------------------------------------------------
# Frozen OMP
# ---------------------------------------------------------------------------

def _condition_from_lstsq_singular_values(
    singular_values: np.ndarray,
    rank: int,
    support_size: int,
) -> float:
    """
    2-norm condition number from the singular values already returned by
    numpy.linalg.lstsq, avoiding a second SVD.

    Only meaningful when full column rank is present.
    """
    s = np.asarray(singular_values, dtype=np.float64)

    if rank != support_size:
        return math.inf

    if s.size == 0 or s[-1] <= 0.0:
        return math.inf

    return float(s[0] / s[-1])


def _threshold_grid_value(
    r_by_k: Dict[str, Optional[float]],
    threshold: float,
    rank_deficient: bool,
    rank_deficiency_step: Optional[int],
) -> Optional[str]:
    for k in K_GRID:
        value = r_by_k.get(str(k))
        if value is not None and value >= threshold:
            return str(k)

    if rank_deficient:
        # unavailable beyond the halt; do not mislabel >512
        return None

    return ">512"


def omp_reconstruct_direction(
    beta_unit: np.ndarray,
    D_unit: np.ndarray,
    usable_original_indices: np.ndarray,
) -> OMPResult:
    """
    Frozen deterministic OMP.

    Rank is checked at EVERY step.

    At first rank deficiency:
      - record rank_deficiency_step
      - halt immediately
      - later grid values remain unavailable.
    """
    beta = _as_float64_vector(beta_unit)

    beta_norm = float(np.linalg.norm(beta))
    if abs(beta_norm - 1.0) > 1e-10:
        raise ValueError("OMP input beta must already be unit norm.")

    D = np.asarray(D_unit, dtype=np.float64)
    original_indices = np.asarray(
        usable_original_indices,
        dtype=np.int64,
    )

    if D.shape != (D_MODEL, N_USABLE_COLUMNS):
        raise ValueError(
            f"Unexpected D_unit shape: {D.shape}"
        )

    if original_indices.shape != (N_USABLE_COLUMNS,):
        raise ValueError(
            f"Unexpected original-index shape: {original_indices.shape}"
        )

    residual = beta.copy()
    selected_local: List[int] = []
    selected_original: List[int] = []
    selected_mask = np.zeros(N_USABLE_COLUMNS, dtype=bool)

    r_by_k: Dict[str, Optional[float]] = {
        str(k): None for k in K_GRID
    }
    rank_by_k: Dict[str, Optional[int]] = {
        str(k): None for k in K_GRID
    }
    condition_by_k: Dict[str, Optional[float]] = {
        str(k): None for k in K_GRID
    }

    previous_recorded_r: Optional[float] = None
    rank_deficiency_step: Optional[int] = None
    exact_reconstruction_step: Optional[int] = None

    for step in range(1, OMP_MAX_K + 1):

        correlations = D.T @ residual
        abs_corr = np.abs(correlations)

        abs_corr[selected_mask] = -np.inf

        max_abs_corr = float(np.max(abs_corr))

        if (
            max_abs_corr <= CORRELATION_ZERO_TOL
            and float(np.linalg.norm(residual)) > RESIDUAL_ZERO_TOL
        ):
            raise RuntimeError(
                "OMP global failure: no usable residual correlation "
                "while residual remains nonzero."
            )

        candidate_local = np.flatnonzero(abs_corr == max_abs_corr)

        if candidate_local.size == 0:
            raise RuntimeError("OMP failed to identify a candidate atom.")

        if candidate_local.size == 1:
            chosen_local = int(candidate_local[0])
        else:
            candidate_original = original_indices[candidate_local]
            chosen_local = int(
                candidate_local[np.argmin(candidate_original)]
            )

        if selected_mask[chosen_local]:
            raise RuntimeError("OMP attempted to reselect an atom.")

        selected_mask[chosen_local] = True
        selected_local.append(chosen_local)
        selected_original.append(int(original_indices[chosen_local]))

        A = D[:, selected_local]

        coef, _, rank, singular_values = np.linalg.lstsq(
            A,
            beta,
            rcond=LSTSQ_RCOND,
        )

        rank = int(rank)

        # Frozen §12.2 requirement:
        # check rank at every single OMP step.
        if rank != step:
            rank_deficiency_step = step
            return OMPResult(
                status="rank_deficient",
                rank_deficient=True,
                rank_deficiency_step=rank_deficiency_step,
                exact_reconstruction_step=None,
                selected_original_indices=selected_original,
                r_by_k=r_by_k,
                rank_by_k=rank_by_k,
                condition_by_k=condition_by_k,
                threshold_k_50=_threshold_grid_value(
                    r_by_k, 0.50, True, rank_deficiency_step
                ),
                threshold_k_80=_threshold_grid_value(
                    r_by_k, 0.80, True, rank_deficiency_step
                ),
                threshold_k_90=_threshold_grid_value(
                    r_by_k, 0.90, True, rank_deficiency_step
                ),
            )

        fitted = A @ coef
        residual = beta - fitted

        residual_norm = float(np.linalg.norm(residual))
        r_value = 1.0 - residual_norm * residual_norm

        if r_value < -R_BOUND_TOL or r_value > 1.0 + R_BOUND_TOL:
            raise RuntimeError(
                f"OMP R bound failure at step {step}: {r_value}"
            )

        r_value = float(np.clip(r_value, 0.0, 1.0))

        condition = _condition_from_lstsq_singular_values(
            singular_values,
            rank,
            step,
        )

        if step in K_GRID:
            key = str(step)
            r_by_k[key] = r_value
            rank_by_k[key] = rank
            condition_by_k[key] = condition

            if (
                previous_recorded_r is not None
                and r_value < previous_recorded_r - MONOTONICITY_TOL
            ):
                raise RuntimeError(
                    "OMP monotonicity invariant failed: "
                    f"R({step})={r_value} < previous grid R "
                    f"{previous_recorded_r}."
                )

            previous_recorded_r = r_value

        if residual_norm <= RESIDUAL_ZERO_TOL:
            exact_reconstruction_step = step

            for k in K_GRID:
                if k > step:
                    r_by_k[str(k)] = 1.0

            return OMPResult(
                status="exact_reconstruction",
                rank_deficient=False,
                rank_deficiency_step=None,
                exact_reconstruction_step=step,
                selected_original_indices=selected_original,
                r_by_k=r_by_k,
                rank_by_k=rank_by_k,
                condition_by_k=condition_by_k,
                threshold_k_50=_threshold_grid_value(
                    r_by_k, 0.50, False, None
                ),
                threshold_k_80=_threshold_grid_value(
                    r_by_k, 0.80, False, None
                ),
                threshold_k_90=_threshold_grid_value(
                    r_by_k, 0.90, False, None
                ),
            )

    return OMPResult(
        status="complete",
        rank_deficient=False,
        rank_deficiency_step=None,
        exact_reconstruction_step=exact_reconstruction_step,
        selected_original_indices=selected_original,
        r_by_k=r_by_k,
        rank_by_k=rank_by_k,
        condition_by_k=condition_by_k,
        threshold_k_50=_threshold_grid_value(
            r_by_k, 0.50, False, None
        ),
        threshold_k_80=_threshold_grid_value(
            r_by_k, 0.80, False, None
        ),
        threshold_k_90=_threshold_grid_value(
            r_by_k, 0.90, False, None
        ),
    )


# ---------------------------------------------------------------------------
# Raw decoder-weight concentration
# ---------------------------------------------------------------------------

def raw_decoder_weight_concentration(
    beta_unit: np.ndarray,
    D_raw: np.ndarray,
) -> RawWeightResult:

    beta = _as_float64_vector(beta_unit)

    beta_norm = float(np.linalg.norm(beta))
    if abs(beta_norm - 1.0) > 1e-10:
        raise ValueError(
            "Raw-weight input beta must already be unit norm."
        )

    D = np.asarray(D_raw, dtype=np.float64)

    if D.shape != (D_MODEL, N_DECODER_COLUMNS):
        raise ValueError(f"Unexpected D_raw shape: {D.shape}")

    w = D.T @ beta
    abs_w = np.abs(w)

    denom = float(np.sum(abs_w))

    if denom <= RAW_WEIGHT_DENOM_TOL:
        return RawWeightResult(
            status="undefined_zero_denominator",
            denominator=denom,
            topk_mass={str(k): None for k in K_GRID},
            n_eff=None,
        )

    p = abs_w / denom

    # Deterministic order:
    # primary key descending |w_j|,
    # secondary key ascending original checkpoint index.
    indices = np.arange(N_DECODER_COLUMNS, dtype=np.int64)
    order = np.lexsort((indices, -abs_w))

    cumulative = np.cumsum(abs_w[order]) / denom

    topk_mass = {
        str(k): float(cumulative[k - 1])
        for k in K_GRID
    }

    positive = p > 0.0
    H = -float(np.sum(p[positive] * np.log(p[positive])))
    n_eff = float(np.exp(H))

    return RawWeightResult(
        status="complete",
        denominator=denom,
        topk_mass=topk_mass,
        n_eff=n_eff,
    )


# ---------------------------------------------------------------------------
# Per-direction analysis
# ---------------------------------------------------------------------------

def analyze_direction(
    vector: np.ndarray,
    decoder: DecoderBundle,
) -> Dict[str, Any]:

    beta_unit = normalize_direction(vector)

    if beta_unit is None:
        return {
            "status": "zero_vector",
            "omp": None,
            "raw_weight": None,
        }

    omp_result = omp_reconstruct_direction(
        beta_unit=beta_unit,
        D_unit=decoder.D_unit,
        usable_original_indices=decoder.usable_original_indices,
    )

    raw_result = raw_decoder_weight_concentration(
        beta_unit=beta_unit,
        D_raw=decoder.D_raw,
    )

    return {
        "status": "complete",
        "omp": asdict(omp_result),
        "raw_weight": asdict(raw_result),
    }


# ---------------------------------------------------------------------------
# Timing-only calibration
# ---------------------------------------------------------------------------

def timing_only_calibration(
    decoder: DecoderBundle,
) -> Dict[str, Any]:
    """
    Frozen five-vector timing-only calibration.

    IMPORTANT:
    This function intentionally does NOT return:
      - R(k)
      - selected atoms
      - condition numbers
      - raw-weight mass
      - N_eff
      - any geometry result

    It returns wall-clock timing only and the mechanical N_iso choice.
    """
    per_vector_seconds: List[float] = []

    for index in TIMING_VECTOR_INDICES:
        direction = generate_isotropic_direction(index)

        start = time.perf_counter()

        # Timing rule is specifically for frozen OMP cost.
        _ = omp_reconstruct_direction(
            beta_unit=direction,
            D_unit=decoder.D_unit,
            usable_original_indices=decoder.usable_original_indices,
        )

        elapsed = float(time.perf_counter() - start)
        per_vector_seconds.append(elapsed)

        # Drop all geometry immediately.
        del _

    median_seconds = float(np.median(per_vector_seconds))
    projected_1000_hours = median_seconds * 1000.0 / 3600.0

    n_iso = (
        1000
        if projected_1000_hours <= TIMING_PROJECTED_1000_HOURS_CUTOFF
        else 500
    )

    if n_iso not in ALLOWED_N_ISO:
        raise RuntimeError("Mechanical N_iso rule produced invalid value.")

    return {
        "mode": "timing_only",
        "vector_indices": list(TIMING_VECTOR_INDICES),
        "per_vector_seconds": per_vector_seconds,
        "median_seconds_per_vector": median_seconds,
        "projected_1000_hours": projected_1000_hours,
        "cutoff_hours": TIMING_PROJECTED_1000_HOURS_CUTOFF,
        "N_iso": n_iso,
        "geometry_returned": False,
    }


# ---------------------------------------------------------------------------
# Isotropic analysis record
# ---------------------------------------------------------------------------

def analyze_isotropic_index(
    index: int,
    decoder: DecoderBundle,
) -> Dict[str, Any]:
    """
    Analyze one independently derivable isotropic vector.

    This function is intentionally index-addressable and order-independent.
    """
    direction = generate_isotropic_direction(index)

    result = analyze_direction(
        vector=direction,
        decoder=decoder,
    )

    return {
        "vector_index": int(index),
        "child_stream_identifier": isotropic_child_identifier(index),
        **result,
    }


# ---------------------------------------------------------------------------
# Atomic private checkpoint writer
# ---------------------------------------------------------------------------

def atomic_write_json(
    record: Dict[str, Any],
    destination: Path,
) -> None:
    """
    Atomic JSON write.

    Caller is responsible for supplying the already-resolved PRIVATE Phase-P
    checkpoint destination.

    This engine deliberately does not invent, discover, or create a public
    checkpoint destination.
    """
    destination = Path(destination)
    assert_no_confirmatory_path(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = (
        json.dumps(
            record,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )

    fd, tmp_name = tempfile.mkstemp(
        prefix=destination.name + ".tmp.",
        dir=str(destination.parent),
    )

    tmp_path = Path(tmp_name)

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, destination)

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ---------------------------------------------------------------------------
# Checkpoint-minimal record
# ---------------------------------------------------------------------------

def minimal_isotropic_checkpoint_record(
    full_record: Dict[str, Any],
    *,
    engine_sha256: str,
    spec_sha256: str,
) -> Dict[str, Any]:
    """
    Strip a full per-vector result to the minimal frozen resume state.

    Selected atom identities are intentionally NOT retained because §15.2
    requires only minimal derived resume state.
    """
    idx = int(full_record["vector_index"])
    stream_id = str(full_record["child_stream_identifier"])

    status = full_record.get("status")

    if status == "zero_vector":
        return {
            "vector_index": idx,
            "child_stream_identifier": stream_id,
            "status": status,
            "engine_sha256": engine_sha256,
            "spec_sha256": spec_sha256,
        }

    omp = full_record["omp"]
    raw = full_record["raw_weight"]

    return {
        "vector_index": idx,
        "child_stream_identifier": stream_id,
        "status": status,
        "omp_status": omp["status"],
        "rank_deficient": omp["rank_deficient"],
        "rank_deficiency_step": omp["rank_deficiency_step"],
        "exact_reconstruction_step": omp["exact_reconstruction_step"],
        "r_by_k": omp["r_by_k"],
        "rank_by_k": omp["rank_by_k"],
        "condition_by_k": omp["condition_by_k"],
        "raw_weight_status": raw["status"],
        "topk_mass": raw["topk_mass"],
        "n_eff": raw["n_eff"],
        "engine_sha256": engine_sha256,
        "spec_sha256": spec_sha256,
    }


# ---------------------------------------------------------------------------
# Static implementation audit helper
# ---------------------------------------------------------------------------

def frozen_contract_manifest() -> Dict[str, Any]:
    return {
        "D_MODEL": D_MODEL,
        "N_DECODER_COLUMNS": N_DECODER_COLUMNS,
        "N_ZERO_COLUMNS": N_ZERO_COLUMNS,
        "N_USABLE_COLUMNS": N_USABLE_COLUMNS,
        "OMP_MAX_K": OMP_MAX_K,
        "K_GRID": list(K_GRID),
        "LSTSQ_RCOND": LSTSQ_RCOND,
        "RESIDUAL_ZERO_TOL": RESIDUAL_ZERO_TOL,
        "CORRELATION_ZERO_TOL": CORRELATION_ZERO_TOL,
        "R_BOUND_TOL": R_BOUND_TOL,
        "MONOTONICITY_TOL": MONOTONICITY_TOL,
        "RAW_WEIGHT_DENOM_TOL": RAW_WEIGHT_DENOM_TOL,
        "ISOTROPIC_ROOT_SEED": ISOTROPIC_ROOT_SEED,
        "BOOTSTRAP_ROOT_SEED": BOOTSTRAP_ROOT_SEED,
        "EXPECTED_SAE_SHA256": EXPECTED_SAE_SHA256,
        "TIMING_VECTOR_INDICES": list(TIMING_VECTOR_INDICES),
        "TIMING_PROJECTED_1000_HOURS_CUTOFF":
            TIMING_PROJECTED_1000_HOURS_CUTOFF,
        "ALLOWED_N_ISO": list(ALLOWED_N_ISO),
    }


if __name__ == "__main__":
    # Deliberately no analysis execution from the module entrypoint.
    print(
        json.dumps(
            frozen_contract_manifest(),
            sort_keys=True,
            indent=2,
        )
    )


# ---------------------------------------------------------------------------
# Deterministic bootstrap / population summaries
# ---------------------------------------------------------------------------

BOOTSTRAP_REPLICATES = 10000

BOOTSTRAP_POPULATION_CODES = {
    "biological": 1,
    "canonical_null": 2,
    "c_matched_null": 3,
    "isotropic_reference": 4,
}


def bootstrap_child_seedsequence(
    population: str,
    statistic_code: int,
) -> np.random.SeedSequence:
    """
    Deterministic child stream derived from frozen bootstrap root.

    population identifies the frozen population.
    statistic_code is an explicit deterministic integer assigned by caller
    to the reported statistic/grid point.
    """
    if population not in BOOTSTRAP_POPULATION_CODES:
        raise ValueError(
            f"Unknown bootstrap population: {population!r}"
        )

    if not isinstance(statistic_code, (int, np.integer)):
        raise TypeError("statistic_code must be integer")

    statistic_code = int(statistic_code)

    if statistic_code < 0:
        raise ValueError("statistic_code must be nonnegative")

    return np.random.SeedSequence(
        BOOTSTRAP_ROOT_SEED,
        spawn_key=(
            BOOTSTRAP_POPULATION_CODES[population],
            statistic_code,
        ),
    )


def bootstrap_median_interval(
    values: Sequence[float],
    *,
    population: str,
    statistic_code: int,
    replicates: int = BOOTSTRAP_REPLICATES,
    chunk_size: int = 500,
) -> Dict[str, Any]:
    """
    Frozen percentile bootstrap for the population median.

    Resampling unit is one eligible perturbation/reference row.
    Exactly `replicates` resamples are produced.

    Chunking changes memory use only; RNG draw order is deterministic.
    """
    arr = np.asarray(values, dtype=np.float64)

    if arr.ndim != 1:
        raise ValueError("bootstrap values must be one-dimensional")

    if arr.size == 0:
        return {
            "n": 0,
            "median": None,
            "bootstrap_replicates": int(replicates),
            "ci_2p5": None,
            "ci_97p5": None,
        }

    if not np.all(np.isfinite(arr)):
        raise ValueError("bootstrap values contain non-finite entries")

    if int(replicates) != BOOTSTRAP_REPLICATES:
        raise ValueError(
            f"Frozen bootstrap requires exactly {BOOTSTRAP_REPLICATES} "
            f"replicates, observed {replicates}"
        )

    ss = bootstrap_child_seedsequence(
        population=population,
        statistic_code=statistic_code,
    )
    rng = np.random.Generator(np.random.PCG64(ss))

    n = int(arr.size)
    medians = np.empty(BOOTSTRAP_REPLICATES, dtype=np.float64)

    cursor = 0

    while cursor < BOOTSTRAP_REPLICATES:
        m = min(chunk_size, BOOTSTRAP_REPLICATES - cursor)

        indices = rng.integers(
            0,
            n,
            size=(m, n),
            endpoint=False,
            dtype=np.int64,
        )

        medians[cursor:cursor + m] = np.median(
            arr[indices],
            axis=1,
        )

        cursor += m

    q = np.percentile(
        medians,
        [2.5, 97.5],
        method="linear",
    )

    return {
        "n": n,
        "median": float(np.median(arr)),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "ci_2p5": float(q[0]),
        "ci_97p5": float(q[1]),
    }


def summarize_geometry_population(
    records: Sequence[Dict[str, Any]],
    *,
    population: str,
) -> Dict[str, Any]:
    """
    Frozen population summaries for one completed population.

    Statistics are summarized only over rows valid for the relevant
    quantity. Denominators are explicit.

    No significance test or p-value is produced.
    """
    if population not in BOOTSTRAP_POPULATION_CODES:
        raise ValueError(f"Unknown population {population!r}")

    rows = list(records)
    summary: Dict[str, Any] = {
        "population": population,
        "n_rows_total": len(rows),
        "r_by_k": {},
        "topk_mass": {},
        "n_eff": None,
    }

    # Stable statistic codes:
    #   1000 + k => R(k)
    #   2000 + k => top-k raw mass
    #   3000     => N_eff
    for k in K_GRID:
        key = str(k)

        r_values: List[float] = []
        conditions: List[float] = []
        unavailable = 0

        mass_values: List[float] = []
        mass_unavailable = 0

        for row in rows:
            if row.get("status") != "complete":
                unavailable += 1
                mass_unavailable += 1
                continue

            omp = row.get("omp")
            raw = row.get("raw_weight")

            rv = None if omp is None else omp["r_by_k"].get(key)

            if rv is None:
                unavailable += 1
            else:
                r_values.append(float(rv))

                cv = omp["condition_by_k"].get(key)
                if cv is not None and np.isfinite(float(cv)):
                    conditions.append(float(cv))

            mv = None if raw is None else raw["topk_mass"].get(key)

            if mv is None:
                mass_unavailable += 1
            else:
                mass_values.append(float(mv))

        r_boot = bootstrap_median_interval(
            r_values,
            population=population,
            statistic_code=1000 + k,
        )

        mass_boot = bootstrap_median_interval(
            mass_values,
            population=population,
            statistic_code=2000 + k,
        )

        summary["r_by_k"][key] = {
            **r_boot,
            "unavailable_count": int(unavailable),
            "median_condition_number": (
                None
                if len(conditions) == 0
                else float(np.median(np.asarray(conditions)))
            ),
        }

        summary["topk_mass"][key] = {
            **mass_boot,
            "unavailable_count": int(mass_unavailable),
        }

    n_eff_values: List[float] = []
    n_eff_unavailable = 0

    for row in rows:
        if row.get("status") != "complete":
            n_eff_unavailable += 1
            continue

        raw = row.get("raw_weight")

        value = None if raw is None else raw.get("n_eff")

        if value is None:
            n_eff_unavailable += 1
        else:
            n_eff_values.append(float(value))

    summary["n_eff"] = {
        **bootstrap_median_interval(
            n_eff_values,
            population=population,
            statistic_code=3000,
        ),
        "unavailable_count": int(n_eff_unavailable),
    }

    summary["headline"] = {
        "k": 32,
        "median_R32": summary["r_by_k"]["32"]["median"],
        "median_top32_mass": summary["topk_mass"]["32"]["median"],
        "median_N_eff": summary["n_eff"]["median"],
    }

    return summary


# ---------------------------------------------------------------------------
# Private checkpoint integrity / resume helpers
# ---------------------------------------------------------------------------

def assert_private_checkpoint_destination(
    destination: Path,
    *,
    repository_root: Path,
) -> None:
    """
    Fail closed if a checkpoint destination lies inside the public Git repo.

    The caller must still resolve the existing private Phase-P checkpoint
    boundary before using this function.
    """
    destination = Path(destination).resolve()
    repository_root = Path(repository_root).resolve()

    assert_no_confirmatory_path(destination)

    try:
        destination.relative_to(repository_root)
    except ValueError:
        return

    raise RuntimeError(
        "Checkpoint destination is inside the public Git repository: "
        f"{destination}"
    )


def load_isotropic_checkpoint(
    path: Path,
    *,
    expected_index: int,
    expected_engine_sha256: str,
    expected_spec_sha256: str,
) -> Dict[str, Any]:
    """
    Read and verify one minimal isotropic checkpoint record.
    """
    path = Path(path)
    assert_no_confirmatory_path(path)

    with path.open("r", encoding="utf-8") as f:
        record = json.load(f)

    required = {
        "vector_index",
        "child_stream_identifier",
        "status",
        "engine_sha256",
        "spec_sha256",
    }

    missing = sorted(required - set(record))

    if missing:
        raise RuntimeError(
            f"Checkpoint missing required fields {missing}: {path}"
        )

    if int(record["vector_index"]) != int(expected_index):
        raise RuntimeError(
            f"Checkpoint vector-index mismatch at {path}"
        )

    expected_stream = isotropic_child_identifier(int(expected_index))

    if record["child_stream_identifier"] != expected_stream:
        raise RuntimeError(
            f"Checkpoint child-stream mismatch at {path}"
        )

    if record["engine_sha256"] != expected_engine_sha256:
        raise RuntimeError(
            f"Checkpoint engine SHA mismatch at {path}"
        )

    if record["spec_sha256"] != expected_spec_sha256:
        raise RuntimeError(
            f"Checkpoint spec SHA mismatch at {path}"
        )

    return record


def audit_isotropic_checkpoint_set(
    checkpoint_dir: Path,
    *,
    n_iso: int,
    expected_engine_sha256: str,
    expected_spec_sha256: str,
) -> Dict[str, Any]:
    """
    Audit completed checkpoint indices without running or regenerating vectors.

    Expected filename:
        isotropic_000000.json
        ...
    """
    if n_iso not in ALLOWED_N_ISO:
        raise ValueError(
            f"N_iso must be one of {ALLOWED_N_ISO}, observed {n_iso}"
        )

    checkpoint_dir = Path(checkpoint_dir)

    completed: List[int] = []
    missing: List[int] = []

    for index in range(n_iso):
        path = checkpoint_dir / f"isotropic_{index:06d}.json"

        if not path.exists():
            missing.append(index)
            continue

        load_isotropic_checkpoint(
            path,
            expected_index=index,
            expected_engine_sha256=expected_engine_sha256,
            expected_spec_sha256=expected_spec_sha256,
        )

        completed.append(index)

    return {
        "N_iso": int(n_iso),
        "completed_count": len(completed),
        "missing_count": len(missing),
        "complete": len(missing) == 0,
        "completed_indices": completed,
        "missing_indices": missing,
    }
