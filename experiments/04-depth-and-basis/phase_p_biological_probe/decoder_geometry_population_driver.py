#!/usr/bin/env python3
"""
Experiment 04 post hoc biological/null decoder-geometry population driver.

IMPORTANT
---------
This driver is an execution wrapper around the already-frozen
decoder_geometry_analysis.py engine.

It does not define a new geometry method.

The driver is deliberately hard-disabled when first frozen.

When separately authorized, its only scientific task is:

    1. verify exact frozen inputs;
    2. load the recovered Stage-B beta artifact;
    3. load the exact frozen SAE decoder through the frozen engine;
    4. account for all 100 biological and all 100 canonical-null rows;
    5. mark exact-zero beta rows explicitly as ineligible_zero_beta;
    6. call the frozen analyze_direction() function exactly once for
       each nonzero eligible direction;
    7. write private per-row records and a completion manifest.

It MUST NOT compute population summaries, biological-v-null comparisons,
isotropic comparisons, bootstrap statistics, p-values, PASS/FAIL scientific
verdicts, or interpretation.

Confirmatory-universe access is prohibited.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Thread contract — must be pinned before numerical imports
# ---------------------------------------------------------------------------

import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"


# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# HARD EXECUTION GATE
# ---------------------------------------------------------------------------

ENABLE_GEOMETRY = True


# ---------------------------------------------------------------------------
# Frozen identities
# ---------------------------------------------------------------------------

EXPECTED_ENGINE_SHA256 = (
    "8289d96a11ee3f5506edf298bf0290f5"
    "8414454737156c98737f4522642915ab"
)

EXPECTED_SPEC_SHA256 = (
    "205d13b20ef5bf9325794274b531f46c"
    "9ffa7fa7cc77a7e8bdd0a8be05edce69"
)

EXPECTED_BETA_NPZ_SHA256 = (
    "934b69de6765fb96f5dfe43460544cd7"
    "d06ad2bc0557029c6f66daeb18fd3580"
)

EXPECTED_SAE_SHA256 = (
    "bf0dfb992321cf4d1ce80fced0db0256"
    "f5c7a1f9fdd8a7fe4834e786c1f6472a"
)

EXPECTED_PASS2_REPORT_SHA256 = (
    "b1905cb7ad9140f9f85f3c7cd621b1ac"
    "e5dece645e63b0a8c1317ff643de10ed"
)

EXPECTED_PASS2_NOTE_SHA256 = (
    "a77ccd84830c162fea6013365bbd36359"
    "d02ced6d0da4133c1f5f468916057e5"
)


# ---------------------------------------------------------------------------
# Frozen population contract
# ---------------------------------------------------------------------------

BIO_START = 1000001
BIO_END = 1000100

NULL_START = 1100001
NULL_END = 1100100

EXPECTED_BIO_TOTAL = 100
EXPECTED_NULL_TOTAL = 100
EXPECTED_TOTAL = 200

EXPECTED_BIO_ELIGIBLE = 100
EXPECTED_BIO_ZERO = 0

EXPECTED_NULL_ELIGIBLE = 63
EXPECTED_NULL_ZERO = 37

EXPECTED_ELIGIBLE_TOTAL = 163
EXPECTED_ZERO_TOTAL = 37

D_MODEL = 1280


# ---------------------------------------------------------------------------
# Frozen private artifact schemas
# ---------------------------------------------------------------------------

EXPECTED_NPZ_KEYS = {
    "biological_ids",
    "biological_beta",
    "null_ids",
    "null_beta",
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:

    path = Path(path)

    h = hashlib.sha256()

    with path.open("rb") as f:

        while True:

            block = f.read(chunk_size)

            if not block:
                break

            h.update(block)

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


def atomic_json_write(
    path: Path,
    obj: Any,
) -> None:

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )

    try:

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                obj,
                f,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )

            f.write("\n")

            f.flush()

            os.fsync(
                f.fileno()
            )

        os.replace(
            tmp_name,
            path,
        )

    except Exception:

        try:
            os.unlink(
                tmp_name
            )
        except FileNotFoundError:
            pass

        raise


def exact_zero_beta(
    beta: np.ndarray,
) -> bool:

    arr = np.asarray(
        beta,
        dtype=np.float64,
    )

    if arr.shape != (D_MODEL,):

        raise RuntimeError(
            "Unexpected beta shape: "
            f"{arr.shape}"
        )

    if not np.all(
        np.isfinite(arr)
    ):

        raise RuntimeError(
            "Beta contains non-finite values."
        )

    return (
        float(
            np.linalg.norm(arr)
        )
        == 0.0
    )


def beta_sha256(
    beta: np.ndarray,
) -> str:

    arr = np.asarray(
        beta,
        dtype=np.float64,
    )

    if arr.shape != (D_MODEL,):

        raise RuntimeError(
            f"Unexpected beta shape: {arr.shape}"
        )

    if not np.all(
        np.isfinite(arr)
    ):

        raise RuntimeError(
            "Beta contains non-finite values."
        )

    arr = np.ascontiguousarray(
        arr.astype(
            "<f8",
            copy=False,
        )
    )

    return hashlib.sha256(
        arr.tobytes(
            order="C"
        )
    ).hexdigest()


# ---------------------------------------------------------------------------
# Frozen public-source verification
# ---------------------------------------------------------------------------

def verify_public_sources(
    engine_path: Path,
    spec_path: Path,
    pass2_note_path: Path,
) -> None:

    for path in (
        engine_path,
        spec_path,
        pass2_note_path,
    ):

        assert_no_confirmatory_path(
            path
        )

        if not Path(path).is_file():

            raise RuntimeError(
                f"Missing frozen source: {path}"
            )

    identities = (
        (
            engine_path,
            EXPECTED_ENGINE_SHA256,
            "decoder geometry engine",
        ),
        (
            spec_path,
            EXPECTED_SPEC_SHA256,
            "decoder geometry spec",
        ),
        (
            pass2_note_path,
            EXPECTED_PASS2_NOTE_SHA256,
            "Pass-2 verification note",
        ),
    )

    for path, expected, label in identities:

        observed = sha256_file(
            path
        )

        if observed != expected:

            raise RuntimeError(
                f"{label} SHA mismatch.\n"
                f"expected: {expected}\n"
                f"observed: {observed}"
            )


# ---------------------------------------------------------------------------
# Frozen engine import
# ---------------------------------------------------------------------------

def load_frozen_engine(
    engine_path: Path,
):

    engine_path = Path(
        engine_path
    )

    observed = sha256_file(
        engine_path
    )

    if observed != EXPECTED_ENGINE_SHA256:

        raise RuntimeError(
            "Refusing to import non-frozen geometry engine."
        )

    module_name = (
        "_exp04_frozen_decoder_geometry_engine"
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        engine_path,
    )

    if (
        spec is None
        or spec.loader is None
    ):

        raise RuntimeError(
            "Unable to create frozen-engine module spec."
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[
        module_name
    ] = module

    spec.loader.exec_module(
        module
    )

    required = (
        "load_verified_decoder",
        "normalize_direction",
        "analyze_direction",
        "sha256_file",
        "EXPECTED_SAE_SHA256",
        "D_MODEL",
        "K_GRID",
    )

    for name in required:

        if not hasattr(
            module,
            name,
        ):

            raise RuntimeError(
                "Frozen engine missing required symbol: "
                + name
            )

    if (
        module.EXPECTED_SAE_SHA256
        != EXPECTED_SAE_SHA256
    ):

        raise RuntimeError(
            "Driver/engine SAE identity disagreement."
        )

    if module.D_MODEL != D_MODEL:

        raise RuntimeError(
            "Driver/engine model-dimension disagreement."
        )

    return module


# ---------------------------------------------------------------------------
# Pass-2 report verification
# ---------------------------------------------------------------------------

def load_verified_pass2_report(
    path: Path,
) -> Dict[str, Any]:

    path = Path(
        path
    )

    assert_no_confirmatory_path(
        path
    )

    observed = sha256_file(
        path
    )

    if (
        observed
        != EXPECTED_PASS2_REPORT_SHA256
    ):

        raise RuntimeError(
            "Pass-2 verification report SHA mismatch."
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:

        report = json.load(
            f
        )

    if report.get("pass") != 2:

        raise RuntimeError(
            "Pass-2 report does not record pass=2."
        )

    if report.get("status") != "verified":

        raise RuntimeError(
            "Pass-2 report is not verified."
        )

    if (
        report.get(
            "persisted_invariants_verified_count"
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Pass-2 persisted verification count mismatch."
        )

    if (
        report.get(
            "coefficient_hash_match_count"
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Pass-2 coefficient-hash count mismatch."
        )

    if (
        report.get(
            "failed_record_count"
        )
        != 0
    ):

        raise RuntimeError(
            "Pass-2 report contains failed records."
        )

    records = report.get(
        "records"
    )

    if (
        not isinstance(records, list)
        or len(records) != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Unexpected Pass-2 record population."
        )

    return report


def pass2_hash_map(
    report: Dict[str, Any],
) -> Dict[Tuple[str, int], str]:

    result: Dict[
        Tuple[str, int],
        str
    ] = {}

    for row in report["records"]:

        population = row.get(
            "population"
        )

        perturbation_id = int(
            row.get(
                "perturbation_id"
            )
        )

        if population not in (
            "biological",
            "permutation_null",
        ):

            raise RuntimeError(
                "Unexpected Pass-2 population."
            )

        if row.get("verified") is not True:

            raise RuntimeError(
                "Pass-2 row not verified."
            )

        if (
            row.get(
                "persisted_invariants_verified"
            )
            is not True
        ):

            raise RuntimeError(
                "Pass-2 persisted invariant failure."
            )

        if (
            row.get(
                "pass1_hash_match"
            )
            is not True
        ):

            raise RuntimeError(
                "Pass-2 hash agreement failure."
            )

        h1 = row.get(
            "pass1_stage_b_coefficient_sha256"
        )

        h2 = row.get(
            "pass2_stage_b_coefficient_sha256"
        )

        if (
            not isinstance(h1, str)
            or not isinstance(h2, str)
            or h1 != h2
            or len(h1) != 64
        ):

            raise RuntimeError(
                "Invalid Pass-2 coefficient hash identity."
            )

        key = (
            population,
            perturbation_id,
        )

        if key in result:

            raise RuntimeError(
                f"Duplicate Pass-2 key: {key}"
            )

        result[
            key
        ] = h1

    if len(result) != EXPECTED_TOTAL:

        raise RuntimeError(
            "Pass-2 hash map population mismatch."
        )

    return result


# ---------------------------------------------------------------------------
# Recovered-beta loading
# ---------------------------------------------------------------------------

def load_verified_beta_artifact(
    beta_npz_path: Path,
    coefficient_hashes: Dict[Tuple[str, int], str],
):

    beta_npz_path = Path(
        beta_npz_path
    )

    assert_no_confirmatory_path(
        beta_npz_path
    )

    observed = sha256_file(
        beta_npz_path
    )

    if observed != EXPECTED_BETA_NPZ_SHA256:

        raise RuntimeError(
            "Recovered beta artifact SHA mismatch."
        )

    with np.load(
        beta_npz_path,
        allow_pickle=False,
    ) as z:

        if set(z.files) != EXPECTED_NPZ_KEYS:

            raise RuntimeError(
                "Recovered beta NPZ key mismatch."
            )

        biological_ids = np.asarray(
            z["biological_ids"],
            dtype=np.int64,
        ).copy()

        biological_beta = np.asarray(
            z["biological_beta"],
            dtype=np.float64,
        ).copy()

        null_ids = np.asarray(
            z["null_ids"],
            dtype=np.int64,
        ).copy()

        null_beta = np.asarray(
            z["null_beta"],
            dtype=np.float64,
        ).copy()

    if biological_ids.shape != (
        EXPECTED_BIO_TOTAL,
    ):

        raise RuntimeError(
            "Biological ID shape mismatch."
        )

    if biological_beta.shape != (
        EXPECTED_BIO_TOTAL,
        D_MODEL,
    ):

        raise RuntimeError(
            "Biological beta shape mismatch."
        )

    if null_ids.shape != (
        EXPECTED_NULL_TOTAL,
    ):

        raise RuntimeError(
            "Null ID shape mismatch."
        )

    if null_beta.shape != (
        EXPECTED_NULL_TOTAL,
        D_MODEL,
    ):

        raise RuntimeError(
            "Null beta shape mismatch."
        )

    expected_bio_ids = np.arange(
        BIO_START,
        BIO_END + 1,
        dtype=np.int64,
    )

    expected_null_ids = np.arange(
        NULL_START,
        NULL_END + 1,
        dtype=np.int64,
    )

    if not np.array_equal(
        biological_ids,
        expected_bio_ids,
    ):

        raise RuntimeError(
            "Biological ID sequence mismatch."
        )

    if not np.array_equal(
        null_ids,
        expected_null_ids,
    ):

        raise RuntimeError(
            "Null ID sequence mismatch."
        )

    if not np.all(
        np.isfinite(
            biological_beta
        )
    ):

        raise RuntimeError(
            "Biological beta contains non-finite values."
        )

    if not np.all(
        np.isfinite(
            null_beta
        )
    ):

        raise RuntimeError(
            "Null beta contains non-finite values."
        )

    # Re-verify all serialized beta vectors against accepted Pass-2 hashes.

    for idx, perturbation_id in enumerate(
        biological_ids.tolist()
    ):

        observed_hash = beta_sha256(
            biological_beta[idx]
        )

        expected_hash = coefficient_hashes[
            (
                "biological",
                int(perturbation_id),
            )
        ]

        if observed_hash != expected_hash:

            raise RuntimeError(
                "Biological beta hash mismatch at "
                f"{perturbation_id}."
            )

    for idx, perturbation_id in enumerate(
        null_ids.tolist()
    ):

        observed_hash = beta_sha256(
            null_beta[idx]
        )

        expected_hash = coefficient_hashes[
            (
                "permutation_null",
                int(perturbation_id),
            )
        ]

        if observed_hash != expected_hash:

            raise RuntimeError(
                "Null beta hash mismatch at "
                f"{perturbation_id}."
            )

    bio_zero = int(
        sum(
            exact_zero_beta(
                biological_beta[i]
            )
            for i in range(
                EXPECTED_BIO_TOTAL
            )
        )
    )

    null_zero = int(
        sum(
            exact_zero_beta(
                null_beta[i]
            )
            for i in range(
                EXPECTED_NULL_TOTAL
            )
        )
    )

    if bio_zero != EXPECTED_BIO_ZERO:

        raise RuntimeError(
            "Biological zero-beta count mismatch."
        )

    if null_zero != EXPECTED_NULL_ZERO:

        raise RuntimeError(
            "Canonical-null zero-beta count mismatch."
        )

    return (
        biological_ids,
        biological_beta,
        null_ids,
        null_beta,
    )


# ---------------------------------------------------------------------------
# Per-row record construction
# ---------------------------------------------------------------------------

def ineligible_zero_record(
    population: str,
    perturbation_id: int,
    coefficient_sha256: str,
) -> Dict[str, Any]:

    return {
        "population": population,
        "perturbation_id": int(
            perturbation_id
        ),
        "eligibility": "ineligible_zero_beta",
        "coefficient_sha256": coefficient_sha256,
        "analysis_status": "not_run_zero_beta",
        "geometry": None,
    }


def eligible_geometry_record(
    population: str,
    perturbation_id: int,
    coefficient_sha256: str,
    geometry: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "population": population,
        "perturbation_id": int(
            perturbation_id
        ),
        "eligibility": "eligible_nonzero_beta",
        "coefficient_sha256": coefficient_sha256,
        "analysis_status": "complete",
        "geometry": geometry,
    }


# ---------------------------------------------------------------------------
# Population execution
# ---------------------------------------------------------------------------

def run_population_geometry(
    *,
    engine_path: Path,
    spec_path: Path,
    pass2_note_path: Path,
    pass2_report_path: Path,
    beta_npz_path: Path,
    sae_checkpoint_path: Path,
    output_dir: Path,
) -> None:

    if not ENABLE_GEOMETRY:

        raise RuntimeError(
            "Geometry execution is hard-disabled."
        )

    paths = (
        engine_path,
        spec_path,
        pass2_note_path,
        pass2_report_path,
        beta_npz_path,
        sae_checkpoint_path,
        output_dir,
    )

    for path in paths:

        assert_no_confirmatory_path(
            Path(path)
        )

    output_dir = Path(
        output_dir
    )

    if output_dir.exists():

        raise RuntimeError(
            "Output directory already exists; "
            "refusing to overwrite or resume implicitly."
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    records_dir = (
        output_dir
        / "per_direction"
    )

    records_dir.mkdir(
        parents=False,
        exist_ok=False,
    )

    verify_public_sources(
        engine_path,
        spec_path,
        pass2_note_path,
    )

    pass2_report = (
        load_verified_pass2_report(
            pass2_report_path
        )
    )

    coefficient_hashes = (
        pass2_hash_map(
            pass2_report
        )
    )

    (
        biological_ids,
        biological_beta,
        null_ids,
        null_beta,
    ) = load_verified_beta_artifact(
        beta_npz_path,
        coefficient_hashes,
    )

    engine = load_frozen_engine(
        engine_path
    )

    observed_sae_sha = sha256_file(
        sae_checkpoint_path
    )

    if (
        observed_sae_sha
        != EXPECTED_SAE_SHA256
    ):

        raise RuntimeError(
            "SAE checkpoint SHA mismatch before decoder load."
        )

    # Frozen engine performs its own independent SHA check before torch.load.
    decoder = engine.load_verified_decoder(
        sae_checkpoint_path
    )

    completed_eligible = 0
    zero_ineligible = 0
    total_accounted = 0

    biological_complete = 0
    biological_zero = 0

    null_complete = 0
    null_zero = 0

    record_identities: List[
        Dict[str, Any]
    ] = []

    # ---------------------------------------------------------------
    # Biological population
    # ---------------------------------------------------------------

    for index in range(
        EXPECTED_BIO_TOTAL
    ):

        perturbation_id = int(
            biological_ids[index]
        )

        beta = biological_beta[
            index
        ]

        coefficient_sha = (
            coefficient_hashes[
                (
                    "biological",
                    perturbation_id,
                )
            ]
        )

        print(
            f"[biological "
            f"{index + 1:03d}/"
            f"{EXPECTED_BIO_TOTAL:03d}] "
            f"{perturbation_id}",
            flush=True,
        )

        if exact_zero_beta(
            beta
        ):

            record = (
                ineligible_zero_record(
                    "biological",
                    perturbation_id,
                    coefficient_sha,
                )
            )

            biological_zero += 1
            zero_ineligible += 1

        else:

            # The only geometry method permitted here.
            geometry = (
                engine.analyze_direction(
                    beta,
                    decoder,
                )
            )

            record = (
                eligible_geometry_record(
                    "biological",
                    perturbation_id,
                    coefficient_sha,
                    geometry,
                )
            )

            biological_complete += 1
            completed_eligible += 1

        total_accounted += 1

        record_path = (
            records_dir
            / (
                "biological_"
                f"{perturbation_id}.json"
            )
        )

        atomic_json_write(
            record_path,
            record,
        )

        record_identities.append(
            {
                "population": "biological",
                "perturbation_id": perturbation_id,
                "path": record_path.name,
                "sha256": sha256_file(
                    record_path
                ),
            }
        )

    # ---------------------------------------------------------------
    # Canonical permutation-null population
    # ---------------------------------------------------------------

    for index in range(
        EXPECTED_NULL_TOTAL
    ):

        perturbation_id = int(
            null_ids[index]
        )

        beta = null_beta[
            index
        ]

        coefficient_sha = (
            coefficient_hashes[
                (
                    "permutation_null",
                    perturbation_id,
                )
            ]
        )

        print(
            f"[null "
            f"{index + 1:03d}/"
            f"{EXPECTED_NULL_TOTAL:03d}] "
            f"{perturbation_id}",
            flush=True,
        )

        if exact_zero_beta(
            beta
        ):

            record = (
                ineligible_zero_record(
                    "permutation_null",
                    perturbation_id,
                    coefficient_sha,
                )
            )

            null_zero += 1
            zero_ineligible += 1

        else:

            geometry = (
                engine.analyze_direction(
                    beta,
                    decoder,
                )
            )

            record = (
                eligible_geometry_record(
                    "permutation_null",
                    perturbation_id,
                    coefficient_sha,
                    geometry,
                )
            )

            null_complete += 1
            completed_eligible += 1

        total_accounted += 1

        record_path = (
            records_dir
            / (
                "permutation_null_"
                f"{perturbation_id}.json"
            )
        )

        atomic_json_write(
            record_path,
            record,
        )

        record_identities.append(
            {
                "population": "permutation_null",
                "perturbation_id": perturbation_id,
                "path": record_path.name,
                "sha256": sha256_file(
                    record_path
                ),
            }
        )

    # ---------------------------------------------------------------
    # Structural acceptance only.
    #
    # NO geometry summaries.
    # NO population comparisons.
    # NO medians.
    # NO R(k) aggregation.
    # NO raw-weight aggregation.
    # NO isotropic comparison.
    # NO bootstrap.
    # ---------------------------------------------------------------

    accepted = (
        total_accounted
        == EXPECTED_TOTAL

        and completed_eligible
        == EXPECTED_ELIGIBLE_TOTAL

        and zero_ineligible
        == EXPECTED_ZERO_TOTAL

        and biological_complete
        == EXPECTED_BIO_ELIGIBLE

        and biological_zero
        == EXPECTED_BIO_ZERO

        and null_complete
        == EXPECTED_NULL_ELIGIBLE

        and null_zero
        == EXPECTED_NULL_ZERO

        and len(
            record_identities
        )
        == EXPECTED_TOTAL
    )

    manifest = {
        "state": (
            "DECODER_GEOMETRY_POPULATION_COMPLETE"
            if accepted
            else
            "DECODER_GEOMETRY_POPULATION_FAILED_CLOSED"
        ),
        "accepted": bool(
            accepted
        ),
        "frozen_inputs": {
            "engine_sha256":
                EXPECTED_ENGINE_SHA256,
            "spec_sha256":
                EXPECTED_SPEC_SHA256,
            "beta_npz_sha256":
                EXPECTED_BETA_NPZ_SHA256,
            "sae_checkpoint_sha256":
                EXPECTED_SAE_SHA256,
            "pass2_report_sha256":
                EXPECTED_PASS2_REPORT_SHA256,
            "pass2_note_sha256":
                EXPECTED_PASS2_NOTE_SHA256,
        },
        "thread_contract": {
            "OMP_NUM_THREADS":
                os.environ.get(
                    "OMP_NUM_THREADS"
                ),
            "OPENBLAS_NUM_THREADS":
                os.environ.get(
                    "OPENBLAS_NUM_THREADS"
                ),
            "MKL_NUM_THREADS":
                os.environ.get(
                    "MKL_NUM_THREADS"
                ),
        },
        "population_contract": {
            "expected_total":
                EXPECTED_TOTAL,
            "expected_eligible_total":
                EXPECTED_ELIGIBLE_TOTAL,
            "expected_zero_total":
                EXPECTED_ZERO_TOTAL,
            "expected_biological_total":
                EXPECTED_BIO_TOTAL,
            "expected_biological_eligible":
                EXPECTED_BIO_ELIGIBLE,
            "expected_biological_zero":
                EXPECTED_BIO_ZERO,
            "expected_null_total":
                EXPECTED_NULL_TOTAL,
            "expected_null_eligible":
                EXPECTED_NULL_ELIGIBLE,
            "expected_null_zero":
                EXPECTED_NULL_ZERO,
        },
        "observed_accounting": {
            "total_accounted":
                total_accounted,
            "completed_eligible":
                completed_eligible,
            "zero_ineligible":
                zero_ineligible,
            "biological_complete":
                biological_complete,
            "biological_zero":
                biological_zero,
            "null_complete":
                null_complete,
            "null_zero":
                null_zero,
        },
        "records": record_identities,
        "scientific_boundary": {
            "population_summaries_computed":
                False,
            "population_comparison_computed":
                False,
            "isotropic_comparison_computed":
                False,
            "bootstrap_computed":
                False,
            "p_values_computed":
                False,
            "scientific_verdict_computed":
                False,
            "confirmatory_accessed":
                False,
        },
    }

    manifest_path = (
        output_dir
        / "completion_manifest.json"
    )

    atomic_json_write(
        manifest_path,
        manifest,
    )

    if not accepted:

        raise RuntimeError(
            "STATE = "
            "DECODER_GEOMETRY_POPULATION_FAILED_CLOSED"
        )

    print()
    print(
        "accounted rows:",
        total_accounted,
        "/",
        EXPECTED_TOTAL,
    )

    print(
        "eligible analyses complete:",
        completed_eligible,
        "/",
        EXPECTED_ELIGIBLE_TOTAL,
    )

    print(
        "explicit zero-beta ineligible:",
        zero_ineligible,
        "/",
        EXPECTED_ZERO_TOTAL,
    )

    print(
        "PASS — all frozen population accounting complete."
    )

    print(
        "PASS — no population summaries computed."
    )

    print(
        "PASS — no biological/null comparison computed."
    )

    print(
        "PASS — no isotropic comparison computed."
    )

    print(
        "PASS — no bootstrap computed."
    )

    print(
        "PASS — no confirmatory data accessed."
    )

    print(
        "STATE = "
        "DECODER_GEOMETRY_POPULATION_COMPLETE"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--engine",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--spec",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--pass2-note",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--pass2-report",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--beta-npz",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--sae-checkpoint",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )

    return parser.parse_args()


def main():

    if not ENABLE_GEOMETRY:

        print(
            "EXP 04 DECODER GEOMETRY POPULATION: "
            "HARD-DISABLED"
        )

        print(
            "Frozen engine/spec/input identities "
            "encoded but protected inputs not opened."
        )

        print(
            "Recovered beta artifact not opened."
        )

        print(
            "SAE checkpoint not deserialized."
        )

        print(
            "No biological direction normalized."
        )

        print(
            "No canonical-null direction normalized."
        )

        print(
            "No OMP executed."
        )

        print(
            "No raw-weight geometry executed."
        )

        print(
            "No population summary computed."
        )

        print(
            "No population comparison computed."
        )

        print(
            "No isotropic comparison computed."
        )

        print(
            "No bootstrap computed."
        )

        print(
            "No confirmatory data accessed."
        )

        return 0

    args = parse_args()

    run_population_geometry(
        engine_path=args.engine,
        spec_path=args.spec,
        pass2_note_path=args.pass2_note,
        pass2_report_path=args.pass2_report,
        beta_npz_path=args.beta_npz,
        sae_checkpoint_path=args.sae_checkpoint,
        output_dir=args.output_dir,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
