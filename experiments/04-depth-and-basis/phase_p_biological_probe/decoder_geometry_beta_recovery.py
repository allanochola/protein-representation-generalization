#!/usr/bin/env python3
"""
Experiment 04 — decoder-geometry Stage-B beta recovery.

PASS-1 STATUS: HARD-DISABLED.

Purpose
-------
Recover the 200 canonical layer-18 / N=139 Stage-B coefficient
directions by deterministic replay under the frozen Phase-P mechanics.

Pass 1 is verification-only:
    - replay all 100 biological perturbations;
    - replay all 100 canonical permutation-null perturbations;
    - compare every persisted invariant against the committed Phase-P rows;
    - hash each transient Stage-B coefficient as contiguous little-endian
      float64;
    - retain only hashes and verification metadata;
    - do not retain coefficient vectors;
    - continue through all 200 rows even after mismatches.

No decoder geometry is computed in Pass 1.

No confirmatory data may be accessed.

Frozen governing specification:
    DECODER_GEOMETRY_BETA_RECOVERY_SPEC.md
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Thread contract MUST be established before numerical-library imports.
# ---------------------------------------------------------------------------

import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from pathlib import Path
from typing import Any
import argparse
import ast
import csv
import hashlib
import json
import platform
import sys
import tempfile


# ---------------------------------------------------------------------------
# Hard execution gate
# ---------------------------------------------------------------------------

ENABLE_PASS1 = False


# ---------------------------------------------------------------------------
# Frozen identities
# ---------------------------------------------------------------------------

EXPECTED_RUNNER_SHA256 = (
    "e0a39b9c7a83943248166c6251ef273c"
    "9505dfece23eff4cbb6531c163cbaeec"
)

EXPECTED_SPEC_SHA256 = (
    "205d13b20ef5bf9325794274b531f46c9"
    "ffa7fa7cc77a7e8bdd0a8be05edce69"
)

EXPECTED_ENGINE_SHA256 = (
    "8289d96a11ee3f5506edf298bf0290f"
    "58414454737156c98737f4522642915ab"
)

TARGET_N = 139
REPRESENTATION = "esm_layer_18"

BIO_START = 1000001
BIO_END = 1000100

NULL_START = 1100001
NULL_END = 1100100

EXPECTED_BIO_COUNT = 100
EXPECTED_NULL_COUNT = 100
EXPECTED_TOTAL = 200
ESM_WIDTH = 1280

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]

RUNNER_PATH = HERE / "run_phase_p_biological_probe.py"
SPEC_PATH = HERE / "DECODER_GEOMETRY_BETA_RECOVERY_SPEC.md"
ENGINE_PATH = HERE / "decoder_geometry_analysis.py"

MAIN_FILENAME = "main_per_perturbation.csv"
NULL_FILENAME = "permutation_null_per_perturbation.csv"
MANIFEST_FILENAME = "execution_manifest.json"

MAIN_FIELDS = (
    "biological_perturbation_id",
    "target_n",
    "representation",
    "stage_a_eval_auroc",
    "selected_C",
    "K_t_full",
    "K_t_stab",
    "stability_unsigned_support_json",
    "stability_signed_support_json",
    "membership_sha256",
)

NULL_FIELDS = (
    "null_perturbation_id",
    "target_n",
    "representation",
    "stage_a_eval_auroc",
    "selected_C",
    "K_t_full",
    "K_t_stab",
    "stability_unsigned_support_json",
    "stability_signed_support_json",
    "membership_sha256",
    "replay_membership_sha256",
    "replay_success",
)


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

class RecoveryError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def atomic_json_write(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )

    tmp_path = Path(tmp_name)

    try:
        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                payload,
                handle,
                sort_keys=True,
                indent=2,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(
            tmp_path,
            path,
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def verify_static_identities() -> None:
    for path in (
        RUNNER_PATH,
        SPEC_PATH,
        ENGINE_PATH,
    ):
        if not path.is_file():
            raise RecoveryError(
                f"Missing frozen source: {path}"
            )

    observed = {
        "runner": sha256_file(RUNNER_PATH),
        "spec": sha256_file(SPEC_PATH),
        "engine": sha256_file(ENGINE_PATH),
    }

    expected = {
        "runner": EXPECTED_RUNNER_SHA256,
        "spec": EXPECTED_SPEC_SHA256,
        "engine": EXPECTED_ENGINE_SHA256,
    }

    if observed != expected:
        raise RecoveryError(
            "Frozen source identity mismatch.\n"
            f"expected={expected}\n"
            f"observed={observed}"
        )


# ---------------------------------------------------------------------------
# Frozen-namespace extraction
# ---------------------------------------------------------------------------

def build_frozen_phase_p_namespace() -> dict[str, Any]:
    """
    Materialize the nested frozen Phase-P functions without invoking the
    original production wiring.

    Mechanism:
      1. parse exact frozen runner source;
      2. locate run_enabled_phase_p();
      3. replace only its terminal direct call
             run_wired_phase_p_from_frozen_attachments()
         with
             globals()["_RECOVERY_PHASE_P_NS"] = locals().copy()
      4. compile the modified source in an isolated namespace;
      5. call the modified run_enabled_phase_p() once.

    This exposes the already-frozen nested mechanics without executing the
    production Phase-P orchestration.

    The transformation does not alter any stochastic/fitting function body.
    """

    verify_static_identities()

    source = RUNNER_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(RUNNER_PATH),
    )

    target = None

    for node in tree.body:
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "run_enabled_phase_p"
        ):
            target = node
            break

    if target is None:
        raise RecoveryError(
            "run_enabled_phase_p not found."
        )

    replaced = 0

    for index, stmt in enumerate(target.body):
        if not isinstance(stmt, ast.Expr):
            continue

        call = stmt.value

        if not isinstance(call, ast.Call):
            continue

        if not isinstance(call.func, ast.Name):
            continue

        if (
            call.func.id
            != "run_wired_phase_p_from_frozen_attachments"
        ):
            continue

        replacement = ast.parse(
            'globals()["_RECOVERY_PHASE_P_NS"] = '
            'locals().copy()'
        ).body[0]

        replacement = ast.copy_location(
            replacement,
            stmt,
        )

        target.body[index] = replacement
        replaced += 1

    if replaced != 1:
        raise RecoveryError(
            "Expected exactly one production wiring call "
            f"to replace; observed {replaced}."
        )

    ast.fix_missing_locations(tree)

    namespace: dict[str, Any] = {
        "__name__": "_exp04_beta_recovery_frozen_runner",
        "__file__": str(RUNNER_PATH),
    }

    compiled = compile(
        tree,
        filename=str(RUNNER_PATH),
        mode="exec",
    )

    exec(
        compiled,
        namespace,
        namespace,
    )

    fn = namespace.get(
        "run_enabled_phase_p"
    )

    if not callable(fn):
        raise RecoveryError(
            "Modified run_enabled_phase_p unavailable."
        )

    fn()

    recovered = namespace.get(
        "_RECOVERY_PHASE_P_NS"
    )

    if not isinstance(recovered, dict):
        raise RecoveryError(
            "Frozen Phase-P namespace was not captured."
        )

    required = (
        "attach_frozen_phase_p_inputs",
        "validate_loaded_phase_p_inputs",
        "run_biological_per_perturbation",
        "run_permutation_null_per_perturbation",
        "perturbation_result_to_persisted_row",
        "csv_safe_row",
        "validate_persisted_main_row",
        "validate_persisted_null_row",
        "MAIN_OUTPUT_FIELDS",
        "NULL_OUTPUT_FIELDS",
        "MAIN_ATOMIC_KEY_FIELDS",
        "NULL_ATOMIC_KEY_FIELDS",
    )

    missing = [
        name
        for name in required
        if name not in recovered
    ]

    if missing:
        raise RecoveryError(
            "Frozen namespace missing required names: "
            + repr(missing)
        )

    return recovered


# ---------------------------------------------------------------------------
# Canonical committed-row loading
# ---------------------------------------------------------------------------

def load_csv_exact(
    path: Path,
    *,
    expected_fields: tuple[str, ...],
) -> list[dict[str, str]]:
    if not path.is_file():
        raise RecoveryError(
            f"Missing canonical CSV: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        observed_fields = tuple(
            reader.fieldnames or ()
        )

        if observed_fields != expected_fields:
            raise RecoveryError(
                f"CSV schema mismatch for {path.name}.\n"
                f"expected={expected_fields}\n"
                f"observed={observed_fields}"
            )

        rows = []

        for physical_row, row in enumerate(
            reader,
            start=2,
        ):
            if None in row:
                raise RecoveryError(
                    f"Malformed row {physical_row} "
                    f"in {path.name}."
                )

            rows.append(
                dict(row)
            )

    return rows


def select_canonical_rows(
    private_dir: Path,
    frozen: dict[str, Any],
) -> tuple[
    dict[int, dict[str, str]],
    dict[int, dict[str, str]],
]:
    main_path = (
        private_dir
        / MAIN_FILENAME
    )

    null_path = (
        private_dir
        / NULL_FILENAME
    )

    main_rows = load_csv_exact(
        main_path,
        expected_fields=MAIN_FIELDS,
    )

    null_rows = load_csv_exact(
        null_path,
        expected_fields=NULL_FIELDS,
    )

    validate_main = frozen[
        "validate_persisted_main_row"
    ]

    validate_null = frozen[
        "validate_persisted_null_row"
    ]

    biological: dict[int, dict[str, str]] = {}

    for row in main_rows:
        validate_main(row)

        if int(row["target_n"]) != TARGET_N:
            continue

        if row["representation"] != REPRESENTATION:
            continue

        c = int(
            row["biological_perturbation_id"]
        )

        if not BIO_START <= c <= BIO_END:
            continue

        if c in biological:
            raise RecoveryError(
                f"Duplicate biological canonical row: {c}"
            )

        biological[c] = row

    canonical_null: dict[int, dict[str, str]] = {}

    for row in null_rows:
        validate_null(row)

        if int(row["target_n"]) != TARGET_N:
            raise RecoveryError(
                "Canonical null target N changed."
            )

        if row["representation"] != REPRESENTATION:
            raise RecoveryError(
                "Canonical null representation changed."
            )

        c = int(
            row["null_perturbation_id"]
        )

        if not NULL_START <= c <= NULL_END:
            continue

        if c in canonical_null:
            raise RecoveryError(
                f"Duplicate null canonical row: {c}"
            )

        canonical_null[c] = row

    expected_bio_ids = set(
        range(
            BIO_START,
            BIO_END + 1,
        )
    )

    expected_null_ids = set(
        range(
            NULL_START,
            NULL_END + 1,
        )
    )

    if set(biological) != expected_bio_ids:
        missing = sorted(
            expected_bio_ids
            - set(biological)
        )

        extra = sorted(
            set(biological)
            - expected_bio_ids
        )

        raise RecoveryError(
            "Biological canonical census mismatch. "
            f"missing={missing[:10]!r} "
            f"extra={extra[:10]!r}"
        )

    if set(canonical_null) != expected_null_ids:
        missing = sorted(
            expected_null_ids
            - set(canonical_null)
        )

        extra = sorted(
            set(canonical_null)
            - expected_null_ids
        )

        raise RecoveryError(
            "Null canonical census mismatch. "
            f"missing={missing[:10]!r} "
            f"extra={extra[:10]!r}"
        )

    return (
        biological,
        canonical_null,
    )


# ---------------------------------------------------------------------------
# Environment provenance
# ---------------------------------------------------------------------------

def current_environment() -> dict[str, Any]:
    import numpy as np
    import scipy
    import sklearn

    env: dict[str, Any] = {
        "python": sys.version,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "OMP_NUM_THREADS": os.environ.get(
            "OMP_NUM_THREADS"
        ),
        "OPENBLAS_NUM_THREADS": os.environ.get(
            "OPENBLAS_NUM_THREADS"
        ),
        "MKL_NUM_THREADS": os.environ.get(
            "MKL_NUM_THREADS"
        ),
    }

    try:
        from io import StringIO
        import contextlib

        buf = StringIO()

        with contextlib.redirect_stdout(buf):
            np.show_config()

        env["numpy_show_config"] = (
            buf.getvalue()
        )

    except Exception as exc:
        env["numpy_show_config"] = (
            "UNAVAILABLE: "
            + type(exc).__name__
            + ": "
            + str(exc)
        )

    return env


def load_original_manifest(
    private_dir: Path,
) -> dict[str, Any]:
    path = (
        private_dir
        / MANIFEST_FILENAME
    )

    if not path.is_file():
        raise RecoveryError(
            f"Missing execution manifest: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        obj = json.load(handle)

    if not isinstance(obj, dict):
        raise RecoveryError(
            "Execution manifest must be an object."
        )

    return obj


def original_environment_provenance(
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """
    Record only environment provenance actually present in the historical
    Phase-P execution manifest.

    The frozen historical manifest contains no execution-environment fields.
    No missing value is inferred or reconstructed.
    """

    concepts = (
        "python",
        "numpy",
        "scipy",
        "sklearn",
        "blas_or_lapack",
        "platform",
        "architecture_or_machine",
        "thread_environment",
    )

    return {
        "source": "historical Phase-P execution_manifest.json",
        "availability": "unavailable",
        "reason": (
            "The frozen historical Phase-P execution manifest contains "
            "input/scientific provenance but no execution-environment "
            "provenance fields."
        ),
        "fields": {
            concept: {
                "available": False,
                "value": None,
            }
            for concept in concepts
        },
    }


# ---------------------------------------------------------------------------
# Coefficient hash
# ---------------------------------------------------------------------------

def coefficient_sha256(
    beta: Any,
) -> str:
    import numpy as np

    arr = np.asarray(
        beta,
        dtype=np.float64,
    )

    if arr.shape != (ESM_WIDTH,):
        raise RecoveryError(
            "Stage-B coefficient shape mismatch: "
            f"{arr.shape}"
        )

    if not np.all(
        np.isfinite(arr)
    ):
        raise RecoveryError(
            "Stage-B coefficient contains non-finite values."
        )

    little = np.ascontiguousarray(
        arr.astype(
            "<f8",
            copy=False,
        )
    )

    digest = hashlib.sha256(
        little.tobytes(
            order="C"
        )
    ).hexdigest()

    del little
    del arr

    return digest


# ---------------------------------------------------------------------------
# Persisted-row comparison
# ---------------------------------------------------------------------------

def compare_exact_row(
    replay_row: dict[str, Any],
    canonical_row: dict[str, str],
    *,
    fields: tuple[str, ...],
    csv_safe_row,
) -> list[dict[str, str]]:
    normalized = csv_safe_row(
        replay_row,
        fields,
    )

    mismatches = []

    for field in fields:
        expected = canonical_row[field]
        observed = normalized[field]

        if observed != expected:
            mismatches.append({
                "field": field,
                "expected": expected,
                "observed": observed,
            })

    return mismatches


# ---------------------------------------------------------------------------
# Pass 1
# ---------------------------------------------------------------------------

def run_pass1(
    *,
    private_dir: Path,
    output_json: Path,
) -> int:
    """
    Verification-only replay.

    Continues through all 200 canonical rows even if one or more rows fail.
    No Stage-B beta vector is retained after hashing.
    """

    verify_static_identities()

    frozen = (
        build_frozen_phase_p_namespace()
    )

    original_manifest = (
        load_original_manifest(
            private_dir
        )
    )

    original_env = (
        original_environment_provenance(
            original_manifest
        )
    )

    env_now = current_environment()

    (
        biological_rows,
        null_rows,
    ) = select_canonical_rows(
        private_dir,
        frozen,
    )

    print(
        "PASS — canonical persisted census "
        "100 biological + 100 null."
    )

    print(
        "PASS — original execution manifest read "
        "before replay."
    )

    print(
        "Original execution-environment provenance: "
        "UNAVAILABLE in historical manifest."
    )

    print(
        "PASS — missing original environment fields "
        "recorded explicitly; none inferred."
    )

    print(
        "current environment:"
    )

    for key in (
        "python",
        "numpy",
        "scipy",
        "sklearn",
        "platform",
        "machine",
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
    ):
        print(
            f"  {key}: {env_now.get(key)}"
        )

    (
        representations,
        y,
        input_provenance,
    ) = frozen[
        "attach_frozen_phase_p_inputs"
    ]()

    frozen[
        "validate_loaded_phase_p_inputs"
    ](
        representations,
        y,
    )

    X = representations[
        REPRESENTATION
    ]

    run_bio = frozen[
        "run_biological_per_perturbation"
    ]

    run_null = frozen[
        "run_permutation_null_per_perturbation"
    ]

    to_row = frozen[
        "perturbation_result_to_persisted_row"
    ]

    csv_safe = frozen[
        "csv_safe_row"
    ]

    records: list[dict[str, Any]] = []

    verified_count = 0


    # ---------------------------------------------------------------
    # Biological 100
    # ---------------------------------------------------------------

    for ordinal, c in enumerate(
        range(
            BIO_START,
            BIO_END + 1,
        ),
        start=1,
    ):
        print(
            f"[bio {ordinal:03d}/100] {c}",
            flush=True,
        )

        record: dict[str, Any] = {
            "population": "biological",
            "perturbation_id": c,
            "verified": False,
            "mismatches": [],
            "exception": None,
            "stage_b_coefficient_sha256": None,
        }

        result = None

        try:
            result = run_bio(
                X,
                y,
                c=c,
                target_n=TARGET_N,
                context=(
                    "decoder_geometry_beta_recovery:"
                    f"pass1:biological:{c}"
                ),
            )

            replay_row = to_row(
                result,
                perturbation_id=c,
                target_n=TARGET_N,
                representation=REPRESENTATION,
                null_path=False,
            )

            mismatches = compare_exact_row(
                replay_row,
                biological_rows[c],
                fields=MAIN_FIELDS,
                csv_safe_row=csv_safe,
            )

            digest = (
                coefficient_sha256(
                    result[
                        "stage_b_coef"
                    ]
                )
            )

            record[
                "stage_b_coefficient_sha256"
            ] = digest

            record[
                "mismatches"
            ] = mismatches

            record[
                "verified"
            ] = (
                len(mismatches) == 0
            )

            if record["verified"]:
                verified_count += 1

        except Exception as exc:
            record["exception"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }

        finally:
            if isinstance(
                result,
                dict,
            ):
                result.pop(
                    "stage_b_coef",
                    None,
                )

                result.pop(
                    "stage_b_model",
                    None,
                )

                result.pop(
                    "stability_coef",
                    None,
                )

                result.pop(
                    "stability_model",
                    None,
                )

            result = None

        records.append(
            record
        )


    # ---------------------------------------------------------------
    # Canonical permutation-null 100
    # ---------------------------------------------------------------

    for ordinal, c in enumerate(
        range(
            NULL_START,
            NULL_END + 1,
        ),
        start=1,
    ):
        print(
            f"[null {ordinal:03d}/100] {c}",
            flush=True,
        )

        record = {
            "population": "permutation_null",
            "perturbation_id": c,
            "verified": False,
            "mismatches": [],
            "exception": None,
            "stage_b_coefficient_sha256": None,
        }

        result = None

        try:
            result = run_null(
                X,
                y,
                c=c,
                context=(
                    "decoder_geometry_beta_recovery:"
                    f"pass1:null:{c}"
                ),
            )

            replay_row = to_row(
                result,
                perturbation_id=c,
                target_n=TARGET_N,
                representation=REPRESENTATION,
                null_path=True,
            )

            mismatches = compare_exact_row(
                replay_row,
                null_rows[c],
                fields=NULL_FIELDS,
                csv_safe_row=csv_safe,
            )

            digest = (
                coefficient_sha256(
                    result[
                        "stage_b_coef"
                    ]
                )
            )

            record[
                "stage_b_coefficient_sha256"
            ] = digest

            record[
                "mismatches"
            ] = mismatches

            record[
                "verified"
            ] = (
                len(mismatches) == 0
            )

            if record["verified"]:
                verified_count += 1

        except Exception as exc:
            record["exception"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }

        finally:
            if isinstance(
                result,
                dict,
            ):
                result.pop(
                    "stage_b_coef",
                    None,
                )

                result.pop(
                    "stage_b_model",
                    None,
                )

                result.pop(
                    "stability_coef",
                    None,
                )

                result.pop(
                    "stability_model",
                    None,
                )

            result = None

        records.append(
            record
        )


    # ---------------------------------------------------------------
    # Full Pass-1 report
    # ---------------------------------------------------------------

    mismatch_records = [
        record
        for record in records
        if not record[
            "verified"
        ]
    ]

    report = {
        "pass": 1,
        "status": (
            "verified"
            if verified_count
            == EXPECTED_TOTAL
            else "failed_closed"
        ),
        "frozen_source_sha256": {
            "runner": EXPECTED_RUNNER_SHA256,
            "spec": EXPECTED_SPEC_SHA256,
            "engine": EXPECTED_ENGINE_SHA256,
        },
        "thread_contract": {
            "OMP_NUM_THREADS": os.environ.get(
                "OMP_NUM_THREADS"
            ),
            "OPENBLAS_NUM_THREADS": os.environ.get(
                "OPENBLAS_NUM_THREADS"
            ),
            "MKL_NUM_THREADS": os.environ.get(
                "MKL_NUM_THREADS"
            ),
        },
        "canonical_population": {
            "representation": REPRESENTATION,
            "target_n": TARGET_N,
            "biological_range": [
                BIO_START,
                BIO_END,
            ],
            "null_range": [
                NULL_START,
                NULL_END,
            ],
        },
        "original_execution_manifest": (
            original_manifest
        ),
        "original_execution_environment": (
            original_env
        ),
        "environment_comparison": {
            "status": (
                "original_environment_unavailable"
            ),
            "exact_comparison_possible": False,
            "inference_performed": False,
            "replay_contract_changed": False,
        },
        "current_environment": env_now,
        "input_provenance": input_provenance,
        "verified_count": verified_count,
        "expected_count": EXPECTED_TOTAL,
        "mismatch_count": len(
            mismatch_records
        ),
        "records": records,
    }

    atomic_json_write(
        output_json,
        report,
    )

    print()
    print(
        "verified:",
        f"{verified_count}/{EXPECTED_TOTAL}",
    )

    print(
        "mismatches/exceptions:",
        len(mismatch_records),
    )

    print(
        "Pass-1 report:",
        output_json,
    )

    if (
        verified_count
        == EXPECTED_TOTAL
    ):
        print()
        print(
            "PASS — 200 / 200 canonical "
            "perturbations verified."
        )
        print(
            "STATE = "
            "BETA_RECOVERY_PASS1_VERIFIED"
        )
        return 0

    print()
    print(
        "STATE = "
        "BETA_RECOVERY_PASS1_FAILED_CLOSED"
    )

    return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    verify_static_identities()

    if not ENABLE_PASS1:
        print(
            "EXP 04 BETA RECOVERY PASS 1: "
            "HARD-DISABLED"
        )
        print(
            "Frozen runner/spec/engine "
            "identities verified."
        )
        print(
            "No Phase-E matrix loaded."
        )
        print(
            "No biological label loaded."
        )
        print(
            "No perturbation seed consumed."
        )
        print(
            "No sklearn fit executed."
        )
        print(
            "No Stage-B beta recovered."
        )
        print(
            "No confirmatory data accessed."
        )
        return 0

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--phase-p-private-dir",
        required=True,
        type=Path,
        help=(
            "Directory containing the exact private "
            "Phase-P execution_manifest.json, "
            "main_per_perturbation.csv, and "
            "permutation_null_per_perturbation.csv."
        ),
    )

    parser.add_argument(
        "--output-json",
        required=True,
        type=Path,
        help=(
            "Private/local Pass-1 verification output."
        ),
    )

    args = parser.parse_args()

    private_dir = (
        args.phase_p_private_dir
        .expanduser()
        .resolve()
    )

    output_json = (
        args.output_json
        .expanduser()
        .resolve()
    )

    # Confirmatory firewall on user-supplied paths.
    for path in (
        private_dir,
        output_json,
    ):
        lower = str(path).lower()

        denied = (
            "confirmatory",
            "confirm_universe",
            "3541",
            "161pos",
        )

        hits = [
            token
            for token in denied
            if token in lower
        ]

        if hits:
            raise RecoveryError(
                "CONFIRMATORY FIREWALL: "
                f"denied path token(s) {hits}"
            )

    return run_pass1(
        private_dir=private_dir,
        output_json=output_json,
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
