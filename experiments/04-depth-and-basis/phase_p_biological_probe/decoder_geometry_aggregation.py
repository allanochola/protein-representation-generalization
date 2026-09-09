#!/usr/bin/env python3
"""
Experiment 04 — post hoc decoder-geometry population aggregation.

IMPORTANT
---------
This driver summarizes already-generated decoder geometry.

It MUST NOT recompute beta vectors.
It MUST NOT recompute decoder geometry.
It MUST NOT access confirmatory data.

The driver is frozen with ENABLE_AGGREGATION=False.

Only a later, separate authorization commit may enable execution.
"""

from __future__ import annotations

import os

# Numerical thread contract.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# HARD EXECUTION GATE
# ---------------------------------------------------------------------------

ENABLE_AGGREGATION = True


# ---------------------------------------------------------------------------
# Frozen upstream identities
# ---------------------------------------------------------------------------

EXPECTED_AGGREGATION_SPEC_SHA256 = (
    "59f3b9f27c51dbf46092e4ff276acfe5"
    "cca4f5aa3fb7c7d94791a5337b8e55d2"
)

EXPECTED_POPULATION_MANIFEST_SHA256 = (
    "a5246082517ca1270a75f48288df9cb0"
    "3d21d5c6393f3f2daaeb41229a4a0257"
)

EXPECTED_ENGINE_SHA256 = (
    "8289d96a11ee3f5506edf298bf0290f5"
    "8414454737156c98737f4522642915ab"
)

EXPECTED_POPULATION_COMPLETION_NOTE_SHA256 = (
    "3a138c6ecd696352d24d1dc322b91b27"
    "5089831bae2ac047e7d8c016fbad2aa7"
)


# ---------------------------------------------------------------------------
# Frozen population contract
# ---------------------------------------------------------------------------

BIO_IDS = tuple(
    range(1000001, 1000101)
)

NULL_IDS = tuple(
    range(1100001, 1100101)
)

EXPECTED_BIO_TOTAL = 100
EXPECTED_BIO_ELIGIBLE = 100
EXPECTED_BIO_ZERO = 0

EXPECTED_NULL_TOTAL = 100
EXPECTED_NULL_ELIGIBLE = 63
EXPECTED_NULL_ZERO = 37

EXPECTED_TOTAL = 200
EXPECTED_ISOTROPIC_TOTAL = 1000

ISOTROPIC_ROOT_SEED = 2026090802


# ---------------------------------------------------------------------------
# Frozen quantities
# ---------------------------------------------------------------------------

K_GRID = (
    1,
    2,
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
)

HEADLINE_K = 32

BOOTSTRAP_ROOT_SEED = 2026090801
N_BOOTSTRAP = 10_000

MONOTONICITY_TOL = 1e-12


# ---------------------------------------------------------------------------
# Frozen deterministic bootstrap stream map
#
# This mapping is frozen BEFORE biological geometry is opened.
#
#  0–8  : single-population median CIs
#  9–17 : median-difference CIs
# ---------------------------------------------------------------------------

BOOTSTRAP_STREAMS = {
    "bio_r32_median": 0,
    "null_r32_median": 1,
    "iso_r32_median": 2,

    "bio_top32_median": 3,
    "null_top32_median": 4,
    "iso_top32_median": 5,

    "bio_neff_median": 6,
    "null_neff_median": 7,
    "iso_neff_median": 8,

    "bio_minus_null_r32": 9,
    "bio_minus_iso_r32": 10,
    "null_minus_iso_r32": 11,

    "bio_minus_null_top32": 12,
    "bio_minus_iso_top32": 13,
    "null_minus_iso_top32": 14,

    "bio_minus_null_neff": 15,
    "bio_minus_iso_neff": 16,
    "null_minus_iso_neff": 17,
}


# ---------------------------------------------------------------------------
# Confirmatory firewall
# ---------------------------------------------------------------------------

CONFIRMATORY_DENY_TOKENS = (
    "confirmatory",
    "confirm_universe",
    "3541",
    "161pos",
)


def sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:

    path = Path(path)

    h = hashlib.sha256()

    with path.open("rb") as f:

        while True:

            block = f.read(
                chunk_size
            )

            if not block:
                break

            h.update(
                block
            )

    return h.hexdigest()


def assert_no_confirmatory_path(
    path: Path,
) -> None:

    lower = str(
        Path(path)
    ).lower()

    bad = [
        token
        for token in CONFIRMATORY_DENY_TOKENS
        if token in lower
    ]

    if bad:

        raise RuntimeError(
            "CONFIRMATORY FIREWALL: "
            f"denied path token(s) {bad}: {path}"
        )


def load_json(
    path: Path,
) -> Dict[str, Any]:

    path = Path(
        path
    )

    assert_no_confirmatory_path(
        path
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:

        obj = json.load(
            f
        )

    if not isinstance(
        obj,
        dict,
    ):

        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return obj


def finite_unit_interval(
    value: Any,
    label: str,
) -> float:

    x = float(
        value
    )

    if not np.isfinite(
        x
    ):

        raise RuntimeError(
            f"Non-finite {label}"
        )

    if (
        x < -1e-12
        or x > 1.0 + 1e-12
    ):

        raise RuntimeError(
            f"Out-of-bounds {label}: {x}"
        )

    return float(
        np.clip(
            x,
            0.0,
            1.0,
        )
    )


# ---------------------------------------------------------------------------
# Population record verification
# ---------------------------------------------------------------------------

def verify_population_manifest(
    manifest_path: Path,
    records_dir: Path,
) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
]:

    manifest_path = Path(
        manifest_path
    )

    records_dir = Path(
        records_dir
    )

    assert_no_confirmatory_path(
        manifest_path
    )

    assert_no_confirmatory_path(
        records_dir
    )

    if (
        sha256_file(
            manifest_path
        )
        != EXPECTED_POPULATION_MANIFEST_SHA256
    ):

        raise RuntimeError(
            "Population completion manifest SHA mismatch."
        )

    manifest = load_json(
        manifest_path
    )

    if (
        manifest.get("state")
        != "DECODER_GEOMETRY_POPULATION_COMPLETE"
    ):

        raise RuntimeError(
            "Population manifest state mismatch."
        )

    if manifest.get(
        "accepted"
    ) is not True:

        raise RuntimeError(
            "Population manifest not accepted."
        )

    accounting = manifest.get(
        "observed_accounting"
    )

    expected_accounting = {
        "total_accounted": 200,
        "completed_eligible": 163,
        "zero_ineligible": 37,
        "biological_complete": 100,
        "biological_zero": 0,
        "null_complete": 63,
        "null_zero": 37,
    }

    if accounting != expected_accounting:

        raise RuntimeError(
            "Population accounting mismatch."
        )

    manifest_records = manifest.get(
        "records"
    )

    if (
        not isinstance(
            manifest_records,
            list,
        )
        or len(
            manifest_records
        ) != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Population manifest record count mismatch."
        )

    biological: List[
        Dict[str, Any]
    ] = []

    canonical_null: List[
        Dict[str, Any]
    ] = []

    seen = set()

    for entry in manifest_records:

        name = entry.get(
            "path"
        )

        expected_sha = entry.get(
            "sha256"
        )

        if (
            not isinstance(name, str)
            or not isinstance(
                expected_sha,
                str,
            )
        ):

            raise RuntimeError(
                "Malformed population manifest record."
            )

        record_path = (
            records_dir
            / name
        )

        if not record_path.is_file():

            raise RuntimeError(
                f"Missing population record: {name}"
            )

        observed_sha = sha256_file(
            record_path
        )

        if observed_sha != expected_sha:

            raise RuntimeError(
                f"Population record SHA mismatch: {name}"
            )

        record = load_json(
            record_path
        )

        population = record.get(
            "population"
        )

        perturbation_id = int(
            record.get(
                "perturbation_id"
            )
        )

        key = (
            population,
            perturbation_id,
        )

        if key in seen:

            raise RuntimeError(
                f"Duplicate population record: {key}"
            )

        seen.add(
            key
        )

        if population == "biological":

            biological.append(
                record
            )

        elif population == "permutation_null":

            canonical_null.append(
                record
            )

        else:

            raise RuntimeError(
                f"Unexpected population label: {population}"
            )

    biological.sort(
        key=lambda row: int(
            row["perturbation_id"]
        )
    )

    canonical_null.sort(
        key=lambda row: int(
            row["perturbation_id"]
        )
    )

    bio_ids = tuple(
        int(
            row["perturbation_id"]
        )
        for row in biological
    )

    null_ids = tuple(
        int(
            row["perturbation_id"]
        )
        for row in canonical_null
    )

    if bio_ids != BIO_IDS:

        raise RuntimeError(
            "Biological ID universe mismatch."
        )

    if null_ids != NULL_IDS:

        raise RuntimeError(
            "Canonical-null ID universe mismatch."
        )

    return (
        biological,
        canonical_null,
    )


# ---------------------------------------------------------------------------
# Eligible geometry extraction
# ---------------------------------------------------------------------------

def validate_eligible_geometry(
    record: Dict[str, Any],
) -> Dict[str, Any]:

    if (
        record.get(
            "eligibility"
        )
        != "eligible_nonzero_beta"
    ):

        raise RuntimeError(
            "Expected eligible_nonzero_beta."
        )

    if (
        record.get(
            "analysis_status"
        )
        != "complete"
    ):

        raise RuntimeError(
            "Eligible analysis not complete."
        )

    geometry = record.get(
        "geometry"
    )

    if not isinstance(
        geometry,
        dict,
    ):

        raise RuntimeError(
            "Eligible record missing geometry."
        )

    if geometry.get(
        "status"
    ) != "complete":

        raise RuntimeError(
            "Geometry status not complete."
        )

    omp = geometry.get(
        "omp"
    )

    raw = geometry.get(
        "raw_weight"
    )

    if (
        not isinstance(omp, dict)
        or not isinstance(
            raw,
            dict,
        )
    ):

        raise RuntimeError(
            "Geometry payload schema mismatch."
        )

    if raw.get(
        "status"
    ) != "complete":

        raise RuntimeError(
            "Raw-weight geometry not complete."
        )

    r_by_k = omp.get(
        "r_by_k"
    )

    topk = raw.get(
        "topk_mass"
    )

    if (
        not isinstance(
            r_by_k,
            dict,
        )
        or not isinstance(
            topk,
            dict,
        )
    ):

        raise RuntimeError(
            "Frozen-grid geometry missing."
        )

    previous_r = None
    previous_mass = None

    rank_deficient = bool(
        omp.get(
            "rank_deficient"
        )
    )

    deficiency_step = omp.get(
        "rank_deficiency_step"
    )

    for k in K_GRID:

        key = str(k)

        r = r_by_k.get(
            key
        )

        if r is not None:

            r = finite_unit_interval(
                r,
                f"R({k})",
            )

            if (
                previous_r is not None
                and r
                < previous_r
                - MONOTONICITY_TOL
            ):

                raise RuntimeError(
                    "R(k) monotonicity violation."
                )

            previous_r = r

        else:

            if not rank_deficient:

                raise RuntimeError(
                    "Missing R(k) without rank deficiency."
                )

            if deficiency_step is None:

                raise RuntimeError(
                    "Rank deficiency lacks step."
                )

            if k < int(
                deficiency_step
            ):

                raise RuntimeError(
                    "R(k) missing before rank deficiency."
                )

        mass = finite_unit_interval(
            topk.get(
                key
            ),
            f"top-{k} mass",
        )

        if (
            previous_mass is not None
            and mass
            < previous_mass
            - MONOTONICITY_TOL
        ):

            raise RuntimeError(
                "Top-k mass monotonicity violation."
            )

        previous_mass = mass

    n_eff = float(
        raw.get(
            "n_eff"
        )
    )

    if (
        not np.isfinite(
            n_eff
        )
        or n_eff <= 0.0
    ):

        raise RuntimeError(
            "Invalid N_eff."
        )

    return geometry


def split_population(
    records: Sequence[
        Dict[str, Any]
    ],
    expected_eligible: int,
    expected_zero: int,
) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
]:

    eligible = []
    zero = []

    for record in records:

        eligibility = record.get(
            "eligibility"
        )

        if (
            eligibility
            == "eligible_nonzero_beta"
        ):

            validate_eligible_geometry(
                record
            )

            eligible.append(
                record
            )

        elif (
            eligibility
            == "ineligible_zero_beta"
        ):

            if (
                record.get(
                    "analysis_status"
                )
                != "not_run_zero_beta"
            ):

                raise RuntimeError(
                    "Zero-beta analysis-status mismatch."
                )

            if record.get(
                "geometry"
            ) is not None:

                raise RuntimeError(
                    "Zero-beta record unexpectedly has geometry."
                )

            zero.append(
                record
            )

        else:

            raise RuntimeError(
                f"Unknown eligibility: {eligibility}"
            )

    if len(
        eligible
    ) != expected_eligible:

        raise RuntimeError(
            "Eligible population count mismatch."
        )

    if len(
        zero
    ) != expected_zero:

        raise RuntimeError(
            "Zero-beta population count mismatch."
        )

    return (
        eligible,
        zero,
    )


# ---------------------------------------------------------------------------
# Frozen isotropic record loading
# ---------------------------------------------------------------------------

def expected_isotropic_child_identifier(
    index: int,
) -> str:

    if not isinstance(
        index,
        (int, np.integer),
    ):

        raise TypeError(
            "isotropic index must be integer"
        )

    index = int(
        index
    )

    if index < 0:

        raise ValueError(
            "isotropic index must be nonnegative"
        )

    ss = np.random.SeedSequence(
        ISOTROPIC_ROOT_SEED,
        spawn_key=(
            index,
        ),
    )

    words = ss.generate_state(
        4,
        dtype=np.uint32,
    )

    raw = np.ascontiguousarray(
        words.astype(
            "<u4"
        )
    ).tobytes()

    return hashlib.sha256(
        raw
    ).hexdigest()


def discover_isotropic_records(
    roots: Sequence[Path],
) -> List[Dict[str, Any]]:

    if not roots:

        raise RuntimeError(
            "At least one isotropic root is required."
        )

    candidates = []

    for root in roots:

        root = Path(
            root
        )

        assert_no_confirmatory_path(
            root
        )

        if not root.exists():

            raise RuntimeError(
                f"Missing isotropic root: {root}"
            )

        candidates.extend(
            sorted(
                root.rglob(
                    "*.json"
                )
            )
        )

    by_index: Dict[
        int,
        Dict[str, Any],
    ] = {}

    for path in candidates:

        obj = load_json(
            path
        )

        # Non-vector manifests may coexist in private datasets.
        # They are not used as scientific observations.
        if (
            "vector_index"
            not in obj
        ):

            continue

        index = int(
            obj["vector_index"]
        )

        if (
            index < 0
            or index
            >= EXPECTED_ISOTROPIC_TOTAL
        ):

            raise RuntimeError(
                f"Invalid isotropic vector index: {index}"
            )

        if index in by_index:

            raise RuntimeError(
                f"Duplicate isotropic vector index: {index}"
            )

        observed_child_identifier = obj.get(
            "child_stream_identifier"
        )

        if not isinstance(
            observed_child_identifier,
            str,
        ):

            raise RuntimeError(
                "Missing isotropic child-stream identifier."
            )

        expected_child_identifier = (
            expected_isotropic_child_identifier(
                index
            )
        )

        if (
            observed_child_identifier
            != expected_child_identifier
        ):

            raise RuntimeError(
                "Isotropic child-stream identity mismatch "
                f"at vector index {index}."
            )

        if obj.get(
            "status"
        ) != "complete":

            raise RuntimeError(
                f"Incomplete isotropic record: {index}"
            )

        # Isotropic object has the same direction-level geometry schema,
        # without the outer population-record wrapper.
        synthetic_wrapper = {
            "eligibility": "eligible_nonzero_beta",
            "analysis_status": "complete",
            "geometry": {
                "status": obj["status"],
                "omp": obj.get(
                    "omp"
                ),
                "raw_weight": obj.get(
                    "raw_weight"
                ),
            },
        }

        validate_eligible_geometry(
            synthetic_wrapper
        )

        by_index[
            index
        ] = obj

    expected = set(
        range(
            EXPECTED_ISOTROPIC_TOTAL
        )
    )

    observed = set(
        by_index
    )

    if observed != expected:

        missing = sorted(
            expected
            - observed
        )

        raise RuntimeError(
            "Isotropic population incomplete. "
            f"missing count={len(missing)}"
        )

    return [
        by_index[i]
        for i in range(
            EXPECTED_ISOTROPIC_TOTAL
        )
    ]


# ---------------------------------------------------------------------------
# Metric extraction
# ---------------------------------------------------------------------------

def geometry_from_population_record(
    record: Dict[str, Any],
) -> Dict[str, Any]:

    return record[
        "geometry"
    ]


def geometry_from_isotropic_record(
    record: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "status": record["status"],
        "omp": record["omp"],
        "raw_weight": record["raw_weight"],
    }


def metric_array(
    geometries: Sequence[
        Dict[str, Any]
    ],
    metric: str,
) -> np.ndarray:

    values: List[
        float
    ] = []

    for geometry in geometries:

        if metric == "r32":

            value = (
                geometry[
                    "omp"
                ][
                    "r_by_k"
                ][
                    str(
                        HEADLINE_K
                    )
                ]
            )

            if value is None:

                raise RuntimeError(
                    "Headline R(32) unavailable for an eligible direction; "
                    "refusing silent denominator change."
                )

            values.append(
                finite_unit_interval(
                    value,
                    "R(32)",
                )
            )

        elif metric == "top32":

            values.append(
                finite_unit_interval(
                    geometry[
                        "raw_weight"
                    ][
                        "topk_mass"
                    ][
                        str(
                            HEADLINE_K
                        )
                    ],
                    "top-32 mass",
                )
            )

        elif metric == "neff":

            value = float(
                geometry[
                    "raw_weight"
                ][
                    "n_eff"
                ]
            )

            if (
                not np.isfinite(
                    value
                )
                or value <= 0.0
            ):

                raise RuntimeError(
                    "Invalid N_eff."
                )

            values.append(
                value
            )

        else:

            raise ValueError(
                f"Unknown metric: {metric}"
            )

    if not values:

        raise RuntimeError(
            f"No available observations for {metric}."
        )

    return np.asarray(
        values,
        dtype=np.float64,
    )


# ---------------------------------------------------------------------------
# Descriptive summaries
# ---------------------------------------------------------------------------

def descriptive(
    x: np.ndarray,
) -> Dict[str, Any]:

    arr = np.asarray(
        x,
        dtype=np.float64,
    )

    if (
        arr.ndim != 1
        or arr.size == 0
        or not np.all(
            np.isfinite(
                arr
            )
        )
    ):

        raise RuntimeError(
            "Invalid descriptive input."
        )

    return {
        "n": int(
            arr.size
        ),
        "mean": float(
            np.mean(
                arr
            )
        ),
        "median": float(
            np.median(
                arr
            )
        ),
        "p2_5": float(
            np.percentile(
                arr,
                2.5,
            )
        ),
        "p97_5": float(
            np.percentile(
                arr,
                97.5,
            )
        ),
    }


def bootstrap_rng(
    stream_name: str,
) -> np.random.Generator:

    if stream_name not in BOOTSTRAP_STREAMS:

        raise KeyError(
            stream_name
        )

    stream_id = int(
        BOOTSTRAP_STREAMS[
            stream_name
        ]
    )

    ss = np.random.SeedSequence(
        BOOTSTRAP_ROOT_SEED,
        spawn_key=(
            stream_id,
        ),
    )

    return np.random.Generator(
        np.random.PCG64(
            ss
        )
    )


def bootstrap_median_ci(
    x: np.ndarray,
    stream_name: str,
) -> Dict[str, float]:

    arr = np.asarray(
        x,
        dtype=np.float64,
    )

    rng = bootstrap_rng(
        stream_name
    )

    n = int(
        arr.size
    )

    estimates = np.empty(
        N_BOOTSTRAP,
        dtype=np.float64,
    )

    for b in range(
        N_BOOTSTRAP
    ):

        sample = arr[
            rng.integers(
                0,
                n,
                size=n,
            )
        ]

        estimates[b] = np.median(
            sample
        )

    return {
        "estimate": float(
            np.median(
                arr
            )
        ),
        "ci_low": float(
            np.percentile(
                estimates,
                2.5,
            )
        ),
        "ci_high": float(
            np.percentile(
                estimates,
                97.5,
            )
        ),
    }


def bootstrap_median_difference_ci(
    left: np.ndarray,
    right: np.ndarray,
    stream_name: str,
) -> Dict[str, float]:

    a = np.asarray(
        left,
        dtype=np.float64,
    )

    b = np.asarray(
        right,
        dtype=np.float64,
    )

    rng = bootstrap_rng(
        stream_name
    )

    na = int(
        a.size
    )

    nb = int(
        b.size
    )

    estimates = np.empty(
        N_BOOTSTRAP,
        dtype=np.float64,
    )

    for i in range(
        N_BOOTSTRAP
    ):

        sa = a[
            rng.integers(
                0,
                na,
                size=na,
            )
        ]

        sb = b[
            rng.integers(
                0,
                nb,
                size=nb,
            )
        ]

        estimates[i] = (
            np.median(
                sa
            )
            - np.median(
                sb
            )
        )

    estimate = (
        float(
            np.median(
                a
            )
        )
        - float(
            np.median(
                b
            )
        )
    )

    return {
        "estimate": estimate,
        "ci_low": float(
            np.percentile(
                estimates,
                2.5,
            )
        ),
        "ci_high": float(
            np.percentile(
                estimates,
                97.5,
            )
        ),
    }


# ---------------------------------------------------------------------------
# Full frozen-grid summaries
# ---------------------------------------------------------------------------

def full_grid_summary(
    geometries: Sequence[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:

    result: Dict[
        str,
        Any,
    ] = {}

    for k in K_GRID:

        r_values = []

        mass_values = []

        for geometry in geometries:

            r = geometry[
                "omp"
            ][
                "r_by_k"
            ][
                str(k)
            ]

            if r is not None:

                r_values.append(
                    finite_unit_interval(
                        r,
                        f"R({k})",
                    )
                )

            mass_values.append(
                finite_unit_interval(
                    geometry[
                        "raw_weight"
                    ][
                        "topk_mass"
                    ][
                        str(k)
                    ],
                    f"top-{k} mass",
                )
            )

        result[
            str(k)
        ] = {
            "R": descriptive(
                np.asarray(
                    r_values,
                    dtype=np.float64,
                )
            ),
            "topk_mass": descriptive(
                np.asarray(
                    mass_values,
                    dtype=np.float64,
                )
            ),
            "R_missing_count": int(
                len(
                    geometries
                )
                - len(
                    r_values
                )
            ),
        }

    neff = np.asarray(
        [
            float(
                g[
                    "raw_weight"
                ][
                    "n_eff"
                ]
            )
            for g in geometries
        ],
        dtype=np.float64,
    )

    result[
        "N_eff"
    ] = descriptive(
        neff
    )

    return result


# ---------------------------------------------------------------------------
# Threshold-grid summaries
# ---------------------------------------------------------------------------

def threshold_summary(
    geometries: Sequence[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:

    """
    Frozen cumulative threshold summaries.

    For each threshold field, report the proportion whose first frozen-grid
    attainment is by <=32, <=64, <=128, <=256, or <=512.

    These are cumulative quantities, not mutually-exclusive bins.

    Literal >512 and unavailable remain separate structural categories.
    """

    result = {}

    cutoffs = (
        32,
        64,
        128,
        256,
        512,
    )

    for field in (
        "threshold_k_50",
        "threshold_k_80",
        "threshold_k_90",
    ):

        cumulative_counts = {
            f"<={cutoff}": 0
            for cutoff in cutoffs
        }

        gt_512 = 0
        unavailable = 0

        for geometry in geometries:

            value = geometry[
                "omp"
            ].get(
                field
            )

            if value is None:

                unavailable += 1
                continue

            if value == ">512":

                gt_512 += 1
                continue

            attained_k = int(
                value
            )

            if attained_k not in K_GRID:

                raise RuntimeError(
                    "Unexpected threshold grid value: "
                    f"{attained_k}"
                )

            for cutoff in cutoffs:

                if attained_k <= cutoff:

                    cumulative_counts[
                        f"<={cutoff}"
                    ] += 1

        n = int(
            len(
                geometries
            )
        )

        counts = {
            **cumulative_counts,
            ">512": int(
                gt_512
            ),
            "unavailable": int(
                unavailable
            ),
        }

        proportions = {
            key: (
                value / n
            )
            for key, value
            in counts.items()
        }

        result[
            field
        ] = {
            "n": n,
            "counts": counts,
            "proportions": proportions,
        }

    return result


# ---------------------------------------------------------------------------
# Integrity diagnostics
# ---------------------------------------------------------------------------

def integrity_summary(
    geometries: Sequence[
        Dict[str, Any]
    ],
) -> Dict[str, int]:

    result = {
        "geometry_complete": 0,
        "omp_complete": 0,
        "omp_rank_deficient": 0,
        "exact_reconstruction": 0,
        "missing_frozen_grid_values": 0,
    }

    for geometry in geometries:

        if geometry.get(
            "status"
        ) == "complete":

            result[
                "geometry_complete"
            ] += 1

        omp = geometry[
            "omp"
        ]

        status = omp.get(
            "status"
        )

        if status == "complete":

            result[
                "omp_complete"
            ] += 1

        elif status == "rank_deficient":

            result[
                "omp_rank_deficient"
            ] += 1

        else:

            raise RuntimeError(
                f"Unexpected OMP status: {status}"
            )

        if (
            omp.get(
                "exact_reconstruction_step"
            )
            is not None
        ):

            result[
                "exact_reconstruction"
            ] += 1

        result[
            "missing_frozen_grid_values"
        ] += sum(
            1
            for k in K_GRID
            if omp[
                "r_by_k"
            ].get(
                str(k)
            ) is None
        )

    return result


# ---------------------------------------------------------------------------
# Headline analysis
# ---------------------------------------------------------------------------

def headline_analysis(
    biological_geometry: Sequence[
        Dict[str, Any]
    ],
    null_geometry: Sequence[
        Dict[str, Any]
    ],
    isotropic_geometry: Sequence[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:

    arrays = {}

    for population, geometries in (
        (
            "bio",
            biological_geometry,
        ),
        (
            "null",
            null_geometry,
        ),
        (
            "iso",
            isotropic_geometry,
        ),
    ):

        arrays[
            population
        ] = {
            "r32": metric_array(
                geometries,
                "r32",
            ),
            "top32": metric_array(
                geometries,
                "top32",
            ),
            "neff": metric_array(
                geometries,
                "neff",
            ),
        }

    single_streams = {
        (
            "bio",
            "r32",
        ): "bio_r32_median",
        (
            "null",
            "r32",
        ): "null_r32_median",
        (
            "iso",
            "r32",
        ): "iso_r32_median",

        (
            "bio",
            "top32",
        ): "bio_top32_median",
        (
            "null",
            "top32",
        ): "null_top32_median",
        (
            "iso",
            "top32",
        ): "iso_top32_median",

        (
            "bio",
            "neff",
        ): "bio_neff_median",
        (
            "null",
            "neff",
        ): "null_neff_median",
        (
            "iso",
            "neff",
        ): "iso_neff_median",
    }

    medians = {}

    for (
        population,
        metric,
    ), stream in single_streams.items():

        medians[
            f"{population}_{metric}"
        ] = bootstrap_median_ci(
            arrays[
                population
            ][
                metric
            ],
            stream,
        )

    comparisons = {}

    comparison_contract = (
        (
            "bio_minus_null",
            "bio",
            "null",
        ),
        (
            "bio_minus_iso",
            "bio",
            "iso",
        ),
        (
            "null_minus_iso",
            "null",
            "iso",
        ),
    )

    for (
        comparison,
        left,
        right,
    ) in comparison_contract:

        comparisons[
            comparison
        ] = {}

        for metric in (
            "r32",
            "top32",
            "neff",
        ):

            stream = (
                f"{comparison}_{metric}"
            )

            comparisons[
                comparison
            ][
                metric
            ] = bootstrap_median_difference_ci(
                arrays[
                    left
                ][
                    metric
                ],
                arrays[
                    right
                ][
                    metric
                ],
                stream,
            )

    return {
        "population_median_bootstrap": medians,
        "median_difference_bootstrap": comparisons,
    }


# ---------------------------------------------------------------------------
# Atomic result write
# ---------------------------------------------------------------------------

def atomic_json_write(
    path: Path,
    obj: Dict[str, Any],
) -> None:

    path = Path(
        path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    if temp.exists():

        raise RuntimeError(
            f"Refusing existing temp file: {temp}"
        )

    with temp.open(
        "x",
        encoding="utf-8",
    ) as f:

        json.dump(
            obj,
            f,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )

        f.write(
            "\n"
        )

        f.flush()

        os.fsync(
            f.fileno()
        )

    os.replace(
        temp,
        path,
    )


# ---------------------------------------------------------------------------
# Authorized execution
# ---------------------------------------------------------------------------

def run_aggregation(
    aggregation_spec_path: Path,
    population_manifest_path: Path,
    population_records_dir: Path,
    isotropic_roots: Sequence[Path],
    output_path: Path,
) -> None:

    for path in (
        aggregation_spec_path,
        population_manifest_path,
        population_records_dir,
        output_path,
    ):

        assert_no_confirmatory_path(
            path
        )

    for root in isotropic_roots:

        assert_no_confirmatory_path(
            root
        )

    if (
        sha256_file(
            aggregation_spec_path
        )
        != EXPECTED_AGGREGATION_SPEC_SHA256
    ):

        raise RuntimeError(
            "Aggregation specification SHA mismatch."
        )

    output_path = Path(
        output_path
    )

    if output_path.exists():

        raise RuntimeError(
            "Refusing to overwrite existing aggregation output."
        )

    biological, canonical_null = (
        verify_population_manifest(
            population_manifest_path,
            population_records_dir,
        )
    )

    biological_eligible, biological_zero = (
        split_population(
            biological,
            EXPECTED_BIO_ELIGIBLE,
            EXPECTED_BIO_ZERO,
        )
    )

    null_eligible, null_zero = (
        split_population(
            canonical_null,
            EXPECTED_NULL_ELIGIBLE,
            EXPECTED_NULL_ZERO,
        )
    )

    isotropic = discover_isotropic_records(
        isotropic_roots
    )

    bio_geometry = [
        geometry_from_population_record(
            row
        )
        for row in biological_eligible
    ]

    null_geometry = [
        geometry_from_population_record(
            row
        )
        for row in null_eligible
    ]

    iso_geometry = [
        geometry_from_isotropic_record(
            row
        )
        for row in isotropic
    ]

    # Result order is fixed by the specification.
    result = {
        "state": (
            "DECODER_GEOMETRY_AGGREGATION_COMPLETE"
        ),
        "scientific_status": (
            "post_hoc_descriptive"
        ),
        "confirmatory_accessed": False,
        "p_values_computed": False,
        "pass_fail_verdict_computed": False,

        "population_accounting": {
            "biological_total": 100,
            "biological_geometry_eligible": 100,
            "biological_zero_beta": 0,
            "canonical_null_total": 100,
            "canonical_null_geometry_eligible": 63,
            "canonical_null_zero_beta": 37,
            "isotropic_total": 1000,
        },

        "headline": headline_analysis(
            bio_geometry,
            null_geometry,
            iso_geometry,
        ),

        "full_grid": {
            "biological": full_grid_summary(
                bio_geometry
            ),
            "canonical_null_eligible": full_grid_summary(
                null_geometry
            ),
            "isotropic": full_grid_summary(
                iso_geometry
            ),
        },

        "threshold_grid": {
            "biological": threshold_summary(
                bio_geometry
            ),
            "canonical_null_eligible": threshold_summary(
                null_geometry
            ),
            "isotropic": threshold_summary(
                iso_geometry
            ),
        },

        "integrity": {
            "biological": integrity_summary(
                bio_geometry
            ),
            "canonical_null_eligible": integrity_summary(
                null_geometry
            ),
            "isotropic": integrity_summary(
                iso_geometry
            ),
        },

        "bootstrap": {
            "root_seed": BOOTSTRAP_ROOT_SEED,
            "replicates": N_BOOTSTRAP,
            "stream_map": BOOTSTRAP_STREAMS,
        },
    }

    atomic_json_write(
        output_path,
        result,
    )

    print(
        "PASS — decoder-geometry aggregation completed."
    )

    print(
        "PASS — 100 biological directions retained."
    )

    print(
        "PASS — 63 canonical-null eligible directions retained."
    )

    print(
        "PASS — 37 canonical-null zero-beta rows retained separately."
    )

    print(
        "PASS — 1000 isotropic directions retained."
    )

    print(
        "PASS — no p-values computed."
    )

    print(
        "PASS — no PASS/FAIL verdict computed."
    )

    print(
        "PASS — no confirmatory data accessed."
    )

    print(
        "STATE = DECODER_GEOMETRY_AGGREGATION_COMPLETE"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--aggregation-spec",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--population-manifest",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--population-records-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--isotropic-root",
        type=Path,
        action="append",
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    return parser


def main() -> int:

    if not ENABLE_AGGREGATION:

        print(
            "EXP 04 DECODER GEOMETRY AGGREGATION: HARD-DISABLED"
        )

        print(
            "Aggregation specification frozen but private geometry "
            "records not opened."
        )

        print(
            "No biological geometry payload opened."
        )

        print(
            "No canonical-null geometry payload opened."
        )

        print(
            "No isotropic checkpoint payload opened."
        )

        print(
            "No population statistic computed."
        )

        print(
            "No bootstrap computed."
        )

        print(
            "No population comparison computed."
        )

        print(
            "No confirmatory data accessed."
        )

        return 0

    args = build_parser().parse_args()

    run_aggregation(
        aggregation_spec_path=args.aggregation_spec,
        population_manifest_path=args.population_manifest,
        population_records_dir=args.population_records_dir,
        isotropic_roots=args.isotropic_root,
        output_path=args.output,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
