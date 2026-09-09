#!/usr/bin/env python3
"""
Experiment 04 — decoder-geometry Stage-B beta recovery, Pass 2.

PASS-2 STATUS: HARD-DISABLED.

Purpose
-------
Only after accepted Pass 1 verification, replay the same 200 canonical
layer-18 / N=139 perturbations under the identical frozen Phase-P procedure.

For every Pass-2 row require BOTH:

    1. complete persisted-invariant reproduction; and
    2. exact Stage-B coefficient SHA-256 equality with accepted Pass 1.

Only if all 200 rows satisfy both requirements may Stage-B coefficient
vectors be serialized to a private/local recovery artifact.

No decoder geometry is computed by this driver.

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
import hashlib
import importlib.util
import json
import sys
import tempfile


# ---------------------------------------------------------------------------
# Hard execution gate
# ---------------------------------------------------------------------------

ENABLE_PASS2 = False


# ---------------------------------------------------------------------------
# Frozen identities
# ---------------------------------------------------------------------------

EXPECTED_PASS1_DRIVER_SHA256 = (
    "b73af5a62c99171eb99f37244ecc38df"
    "19fe19def3377b542bcbe2ec6753ef91"
)

EXPECTED_PASS1_REPORT_SHA256 = (
    "f701d2d76f3363b28c420cdc0c4b8ae"
    "4c728039f024fab93d76531dbc97060b7"
)

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

PASS1_DRIVER_PATH = (
    HERE / "decoder_geometry_beta_recovery.py"
)

RUNNER_PATH = (
    HERE / "run_phase_p_biological_probe.py"
)

SPEC_PATH = (
    HERE / "DECODER_GEOMETRY_BETA_RECOVERY_SPEC.md"
)

ENGINE_PATH = (
    HERE / "decoder_geometry_analysis.py"
)


class Pass2RecoveryError(RuntimeError):
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


def verify_static_identities() -> None:
    expected = {
        PASS1_DRIVER_PATH:
            EXPECTED_PASS1_DRIVER_SHA256,
        RUNNER_PATH:
            EXPECTED_RUNNER_SHA256,
        SPEC_PATH:
            EXPECTED_SPEC_SHA256,
        ENGINE_PATH:
            EXPECTED_ENGINE_SHA256,
    }

    for path, digest in expected.items():
        if not path.is_file():
            raise Pass2RecoveryError(
                f"Missing frozen source: {path}"
            )

        observed = sha256_file(path)

        if observed != digest:
            raise Pass2RecoveryError(
                "Frozen source identity mismatch.\n"
                f"path={path}\n"
                f"expected={digest}\n"
                f"observed={observed}"
            )


def load_pass1_module():
    verify_static_identities()

    name = "_exp04_decoder_geometry_pass1_library"

    if name in sys.modules:
        raise Pass2RecoveryError(
            "Pass-1 library module name "
            "already registered."
        )

    spec = importlib.util.spec_from_file_location(
        name,
        PASS1_DRIVER_PATH,
    )

    if spec is None or spec.loader is None:
        raise Pass2RecoveryError(
            "Unable to create Pass-1 module spec."
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module

    spec.loader.exec_module(
        module
    )

    if module.ENABLE_PASS1 is not False:
        raise Pass2RecoveryError(
            "Pass-1 driver must remain "
            "hard-disabled during Pass 2."
        )

    return module


def load_accepted_pass1_report(
    path: Path,
) -> tuple[
    dict[str, Any],
    dict[tuple[str, int], str],
]:
    if not path.is_file():
        raise Pass2RecoveryError(
            f"Missing accepted Pass-1 report: {path}"
        )

    digest = sha256_file(path)

    if digest != EXPECTED_PASS1_REPORT_SHA256:
        raise Pass2RecoveryError(
            "Accepted Pass-1 report SHA mismatch.\n"
            f"expected={EXPECTED_PASS1_REPORT_SHA256}\n"
            f"observed={digest}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        report = json.load(handle)

    if not isinstance(report, dict):
        raise Pass2RecoveryError(
            "Pass-1 report must be a JSON object."
        )

    required_top = {
        "pass": 1,
        "status": "verified",
        "verified_count": EXPECTED_TOTAL,
        "expected_count": EXPECTED_TOTAL,
        "mismatch_count": 0,
    }

    for field, expected in required_top.items():
        observed = report.get(field)

        if observed != expected:
            raise Pass2RecoveryError(
                "Accepted Pass-1 report failed "
                "top-level verification.\n"
                f"field={field!r}\n"
                f"expected={expected!r}\n"
                f"observed={observed!r}"
            )

    records = report.get(
        "records"
    )

    if not isinstance(records, list):
        raise Pass2RecoveryError(
            "Pass-1 records missing."
        )

    if len(records) != EXPECTED_TOTAL:
        raise Pass2RecoveryError(
            "Pass-1 record census mismatch: "
            f"{len(records)}"
        )

    hashes: dict[
        tuple[str, int],
        str,
    ] = {}

    bio_count = 0
    null_count = 0

    for record in records:
        if not isinstance(record, dict):
            raise Pass2RecoveryError(
                "Malformed Pass-1 record."
            )

        population = record.get(
            "population"
        )

        perturbation_id = record.get(
            "perturbation_id"
        )

        verified = record.get(
            "verified"
        )

        mismatches = record.get(
            "mismatches"
        )

        exception = record.get(
            "exception"
        )

        beta_hash = record.get(
            "stage_b_coefficient_sha256"
        )

        if verified is not True:
            raise Pass2RecoveryError(
                "Pass-1 record not verified."
            )

        if mismatches != []:
            raise Pass2RecoveryError(
                "Pass-1 record contains mismatches."
            )

        if exception is not None:
            raise Pass2RecoveryError(
                "Pass-1 record contains exception."
            )

        if not isinstance(
            perturbation_id,
            int,
        ):
            raise Pass2RecoveryError(
                "Pass-1 perturbation ID "
                "must be int."
            )

        if not isinstance(
            beta_hash,
            str,
        ):
            raise Pass2RecoveryError(
                "Missing Pass-1 beta hash."
            )

        if len(beta_hash) != 64:
            raise Pass2RecoveryError(
                "Malformed Pass-1 beta hash."
            )

        try:
            int(beta_hash, 16)
        except ValueError as exc:
            raise Pass2RecoveryError(
                "Non-hex Pass-1 beta hash."
            ) from exc

        if population == "biological":
            if not (
                BIO_START
                <= perturbation_id
                <= BIO_END
            ):
                raise Pass2RecoveryError(
                    "Biological Pass-1 ID "
                    "out of range."
                )

            bio_count += 1

        elif population == "permutation_null":
            if not (
                NULL_START
                <= perturbation_id
                <= NULL_END
            ):
                raise Pass2RecoveryError(
                    "Null Pass-1 ID out of range."
                )

            null_count += 1

        else:
            raise Pass2RecoveryError(
                "Unknown Pass-1 population: "
                f"{population!r}"
            )

        key = (
            population,
            perturbation_id,
        )

        if key in hashes:
            raise Pass2RecoveryError(
                f"Duplicate Pass-1 key: {key}"
            )

        hashes[key] = beta_hash

    if bio_count != EXPECTED_BIO_COUNT:
        raise Pass2RecoveryError(
            f"Pass-1 biological count={bio_count}"
        )

    if null_count != EXPECTED_NULL_COUNT:
        raise Pass2RecoveryError(
            f"Pass-1 null count={null_count}"
        )

    if len(hashes) != EXPECTED_TOTAL:
        raise Pass2RecoveryError(
            "Pass-1 coefficient hash census "
            f"mismatch: {len(hashes)}"
        )

    return (
        report,
        hashes,
    )


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
            os.fsync(
                handle.fileno()
            )

        os.replace(
            tmp_path,
            path,
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def atomic_npz_write(
    path: Path,
    *,
    biological_ids,
    biological_beta,
    null_ids,
    null_beta,
) -> None:
    import numpy as np

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".npz",
        dir=str(path.parent),
    )

    os.close(fd)

    tmp_path = Path(
        tmp_name
    )

    try:
        np.savez_compressed(
            tmp_path,
            biological_ids=np.asarray(
                biological_ids,
                dtype=np.int64,
            ),
            biological_beta=np.asarray(
                biological_beta,
                dtype=np.float64,
            ),
            null_ids=np.asarray(
                null_ids,
                dtype=np.int64,
            ),
            null_beta=np.asarray(
                null_beta,
                dtype=np.float64,
            ),
        )

        os.replace(
            tmp_path,
            path,
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def run_pass2(
    *,
    private_dir: Path,
    pass1_report_path: Path,
    output_json: Path,
    output_npz: Path,
) -> int:
    """
    Pass-2 recovery.

    Replays all 200 canonical paths.

    Betas remain in process memory while verification proceeds.

    The coefficient artifact is serialized ONLY if all 200 rows reproduce:
      - every frozen persisted invariant; and
      - exact Pass-1 Stage-B coefficient SHA-256.

    If any row fails, no beta artifact is written.
    """

    import numpy as np

    verify_static_identities()

    pass1 = load_pass1_module()

    (
        pass1_report,
        pass1_hashes,
    ) = load_accepted_pass1_report(
        pass1_report_path
    )

    frozen = (
        pass1.build_frozen_phase_p_namespace()
    )

    original_manifest = (
        pass1.load_original_manifest(
            private_dir
        )
    )

    original_env = (
        pass1.original_environment_provenance(
            original_manifest
        )
    )

    env_now = (
        pass1.current_environment()
    )

    (
        biological_rows,
        null_rows,
    ) = pass1.select_canonical_rows(
        private_dir,
        frozen,
    )

    print(
        "PASS — accepted Pass-1 report "
        "identity exact."
    )

    print(
        "PASS — Pass-1 acceptance state "
        "200/200 verified."
    )

    print(
        "PASS — canonical persisted census "
        "100 biological + 100 null."
    )

    print(
        "PASS — original execution manifest "
        "read before replay."
    )

    print(
        "Original execution-environment "
        "provenance: UNAVAILABLE in "
        "historical manifest."
    )

    print(
        "PASS — unavailable original "
        "environment fields recorded; "
        "none inferred."
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

    records: list[
        dict[str, Any]
    ] = []

    retained_bio_ids: list[int] = []
    retained_bio_beta: list[Any] = []

    retained_null_ids: list[int] = []
    retained_null_beta: list[Any] = []

    verified_count = 0
    hash_match_count = 0

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
            "persisted_invariants_verified": False,
            "pass1_hash_match": False,
            "verified": False,
            "mismatches": [],
            "exception": None,
            "pass1_stage_b_coefficient_sha256":
                pass1_hashes[
                    ("biological", c)
                ],
            "pass2_stage_b_coefficient_sha256":
                None,
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
                    f"pass2:biological:{c}"
                ),
            )

            replay_row = to_row(
                result,
                perturbation_id=c,
                target_n=TARGET_N,
                representation=REPRESENTATION,
                null_path=False,
            )

            mismatches = (
                pass1.compare_exact_row(
                    replay_row,
                    biological_rows[c],
                    fields=pass1.MAIN_FIELDS,
                    csv_safe_row=csv_safe,
                )
            )

            beta = np.asarray(
                result[
                    "stage_b_coef"
                ],
                dtype=np.float64,
            ).copy()

            if beta.shape != (
                ESM_WIDTH,
            ):
                raise Pass2RecoveryError(
                    "Stage-B beta shape mismatch: "
                    f"{beta.shape}"
                )

            if not np.all(
                np.isfinite(beta)
            ):
                raise Pass2RecoveryError(
                    "Non-finite Stage-B beta."
                )

            digest = (
                pass1.coefficient_sha256(
                    beta
                )
            )

            expected_digest = (
                pass1_hashes[
                    ("biological", c)
                ]
            )

            hash_match = (
                digest
                == expected_digest
            )

            record[
                "pass2_stage_b_coefficient_sha256"
            ] = digest

            record[
                "mismatches"
            ] = mismatches

            record[
                "persisted_invariants_verified"
            ] = (
                len(mismatches) == 0
            )

            record[
                "pass1_hash_match"
            ] = hash_match

            record[
                "verified"
            ] = (
                len(mismatches) == 0
                and hash_match
            )

            if (
                record[
                    "persisted_invariants_verified"
                ]
            ):
                verified_count += 1

            if hash_match:
                hash_match_count += 1

            # Retain in memory only.
            # Nothing is serialized until global 200/200 acceptance.
            retained_bio_ids.append(
                c
            )

            retained_bio_beta.append(
                beta
            )

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
            "persisted_invariants_verified": False,
            "pass1_hash_match": False,
            "verified": False,
            "mismatches": [],
            "exception": None,
            "pass1_stage_b_coefficient_sha256":
                pass1_hashes[
                    ("permutation_null", c)
                ],
            "pass2_stage_b_coefficient_sha256":
                None,
        }

        result = None

        try:
            result = run_null(
                X,
                y,
                c=c,
                context=(
                    "decoder_geometry_beta_recovery:"
                    f"pass2:null:{c}"
                ),
            )

            replay_row = to_row(
                result,
                perturbation_id=c,
                target_n=TARGET_N,
                representation=REPRESENTATION,
                null_path=True,
            )

            mismatches = (
                pass1.compare_exact_row(
                    replay_row,
                    null_rows[c],
                    fields=pass1.NULL_FIELDS,
                    csv_safe_row=csv_safe,
                )
            )

            beta = np.asarray(
                result[
                    "stage_b_coef"
                ],
                dtype=np.float64,
            ).copy()

            if beta.shape != (
                ESM_WIDTH,
            ):
                raise Pass2RecoveryError(
                    "Stage-B beta shape mismatch: "
                    f"{beta.shape}"
                )

            if not np.all(
                np.isfinite(beta)
            ):
                raise Pass2RecoveryError(
                    "Non-finite Stage-B beta."
                )

            digest = (
                pass1.coefficient_sha256(
                    beta
                )
            )

            expected_digest = (
                pass1_hashes[
                    ("permutation_null", c)
                ]
            )

            hash_match = (
                digest
                == expected_digest
            )

            record[
                "pass2_stage_b_coefficient_sha256"
            ] = digest

            record[
                "mismatches"
            ] = mismatches

            record[
                "persisted_invariants_verified"
            ] = (
                len(mismatches) == 0
            )

            record[
                "pass1_hash_match"
            ] = hash_match

            record[
                "verified"
            ] = (
                len(mismatches) == 0
                and hash_match
            )

            if (
                record[
                    "persisted_invariants_verified"
                ]
            ):
                verified_count += 1

            if hash_match:
                hash_match_count += 1

            retained_null_ids.append(
                c
            )

            retained_null_beta.append(
                beta
            )

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

    failed_records = [
        record
        for record in records
        if not record[
            "verified"
        ]
    ]

    accepted = (
        len(records) == EXPECTED_TOTAL
        and verified_count == EXPECTED_TOTAL
        and hash_match_count == EXPECTED_TOTAL
        and len(failed_records) == 0
        and len(retained_bio_beta)
            == EXPECTED_BIO_COUNT
        and len(retained_null_beta)
            == EXPECTED_NULL_COUNT
    )

    report = {
        "pass": 2,
        "status": (
            "verified"
            if accepted
            else "failed_closed"
        ),
        "pass1_acceptance": {
            "report_sha256":
                EXPECTED_PASS1_REPORT_SHA256,
            "persisted_invariant_result":
                "200/200 verified",
        },
        "frozen_source_sha256": {
            "pass1_driver":
                EXPECTED_PASS1_DRIVER_SHA256,
            "runner":
                EXPECTED_RUNNER_SHA256,
            "spec":
                EXPECTED_SPEC_SHA256,
            "engine":
                EXPECTED_ENGINE_SHA256,
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
        "canonical_population": {
            "representation":
                REPRESENTATION,
            "target_n":
                TARGET_N,
            "biological_range": [
                BIO_START,
                BIO_END,
            ],
            "null_range": [
                NULL_START,
                NULL_END,
            ],
        },
        "original_execution_manifest":
            original_manifest,
        "original_execution_environment":
            original_env,
        "environment_comparison": {
            "status":
                "original_environment_unavailable",
            "exact_comparison_possible":
                False,
            "inference_performed":
                False,
            "replay_contract_changed":
                False,
        },
        "current_environment":
            env_now,
        "input_provenance":
            input_provenance,
        "persisted_invariants_verified_count":
            verified_count,
        "coefficient_hash_match_count":
            hash_match_count,
        "expected_count":
            EXPECTED_TOTAL,
        "failed_record_count":
            len(failed_records),
        "records":
            records,
        "limitation": (
            "Canonical Experiment 04 output "
            "persisted K_t_full only as a "
            "Stage-B support-cardinality check; "
            "it did not persist Stage-B support "
            "coordinates, signs, or coefficient "
            "magnitudes."
        ),
    }

    # Verification report may be written regardless of success.
    atomic_json_write(
        output_json,
        report,
    )

    if not accepted:
        retained_bio_beta.clear()
        retained_null_beta.clear()
        retained_bio_ids.clear()
        retained_null_ids.clear()

        if output_npz.exists():
            raise Pass2RecoveryError(
                "Refusing failed-closed state "
                "with existing beta artifact."
            )

        print()
        print(
            "persisted invariants:",
            f"{verified_count}/{EXPECTED_TOTAL}",
        )
        print(
            "Pass-1/Pass-2 coefficient hashes:",
            f"{hash_match_count}/{EXPECTED_TOTAL}",
        )
        print(
            "failed records:",
            len(failed_records),
        )
        print(
            "STATE = "
            "BETA_RECOVERY_PASS2_FAILED_CLOSED"
        )

        return 1

    biological_beta = np.stack(
        retained_bio_beta,
        axis=0,
    )

    null_beta = np.stack(
        retained_null_beta,
        axis=0,
    )

    if biological_beta.shape != (
        EXPECTED_BIO_COUNT,
        ESM_WIDTH,
    ):
        raise Pass2RecoveryError(
            "Biological beta matrix "
            f"shape mismatch: {biological_beta.shape}"
        )

    if null_beta.shape != (
        EXPECTED_NULL_COUNT,
        ESM_WIDTH,
    ):
        raise Pass2RecoveryError(
            "Null beta matrix "
            f"shape mismatch: {null_beta.shape}"
        )

    if output_npz.exists():
        raise Pass2RecoveryError(
            "Refusing to overwrite existing "
            "Pass-2 coefficient artifact."
        )

    atomic_npz_write(
        output_npz,
        biological_ids=
            retained_bio_ids,
        biological_beta=
            biological_beta,
        null_ids=
            retained_null_ids,
        null_beta=
            null_beta,
    )

    print()
    print(
        "persisted invariants:",
        f"{verified_count}/{EXPECTED_TOTAL}",
    )

    print(
        "Pass-1/Pass-2 coefficient hashes:",
        f"{hash_match_count}/{EXPECTED_TOTAL}",
    )

    print(
        "PASS — 200 / 200 Pass-2 "
        "persisted bundles verified."
    )

    print(
        "PASS — 200 / 200 Pass-1 versus "
        "Pass-2 Stage-B coefficient hashes identical."
    )

    print(
        "Private beta artifact:",
        output_npz,
    )

    print(
        "STATE = "
        "BETA_RECOVERY_PASS2_VERIFIED"
    )

    return 0


def main() -> int:
    verify_static_identities()

    if not ENABLE_PASS2:
        print(
            "EXP 04 BETA RECOVERY PASS 2: "
            "HARD-DISABLED"
        )

        print(
            "Frozen Pass-1/runner/spec/engine "
            "identities verified."
        )

        print(
            "Accepted Pass-1 report not opened."
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
            "No beta artifact written."
        )

        print(
            "No decoder geometry computed."
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
    )

    parser.add_argument(
        "--pass1-report",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output-json",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output-npz",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    private_dir = (
        args.phase_p_private_dir
        .expanduser()
        .resolve()
    )

    pass1_report_path = (
        args.pass1_report
        .expanduser()
        .resolve()
    )

    output_json = (
        args.output_json
        .expanduser()
        .resolve()
    )

    output_npz = (
        args.output_npz
        .expanduser()
        .resolve()
    )

    for path in (
        private_dir,
        pass1_report_path,
        output_json,
        output_npz,
    ):
        lower = str(
            path
        ).lower()

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
            raise Pass2RecoveryError(
                "CONFIRMATORY FIREWALL: "
                f"denied path token(s) {hits}"
            )

    if output_json == output_npz:
        raise Pass2RecoveryError(
            "Pass-2 report and coefficient "
            "artifact paths must differ."
        )

    return run_pass2(
        private_dir=private_dir,
        pass1_report_path=
            pass1_report_path,
        output_json=output_json,
        output_npz=output_npz,
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
