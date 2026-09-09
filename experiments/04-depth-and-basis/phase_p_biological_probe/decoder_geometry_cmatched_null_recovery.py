#!/usr/bin/env python3
"""
Experiment 04 — secondary marginal C-distribution-matched permutation control.

STATUS
------
HARD-DISABLED BEFORE C-MATCHED FITTING.

Purpose
-------
Implement Section 11 of the frozen decoder-geometry / beta-recovery
specification.

For ordinal i:

    biological 1000001+i
        supplies persisted selected C

    null 1100001+i
        supplies the frozen null target-N pool,
        frozen stream-28 permuted labels,
        and frozen null Stage-B stream-25 seed.

This arm:

- does NOT rerun Stage-A model selection;
- changes only imposed C relative to canonical null Stage-B fitting;
- uses marginal C-distribution matching only;
- is NOT a paired biological-versus-null design;
- uses no new seed namespace;
- records convergence warnings/failures/exceptions without retry;
- serializes valid C-matched Stage-B betas privately;
- computes no decoder geometry;
- computes no population comparison;
- accesses no confirmatory data.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Thread contract before numerical imports.
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
# HARD EXECUTION GATE
# ---------------------------------------------------------------------------

ENABLE_CMATCHED_RECOVERY = True


# ---------------------------------------------------------------------------
# Frozen identities
# ---------------------------------------------------------------------------

EXPECTED_ORIGINAL_SPEC_SHA256 = (
    "205d13b20ef5bf9325794274b531f46c9"
    "ffa7fa7cc77a7e8bdd0a8be05edce69"
)

EXPECTED_RECONCILIATION_SHA256 = (
    "2993ce95285b54f6e0c5992298a0ca56"
    "bd183bce25b076c3563818a1c8126d4f"
)

EXPECTED_PASS1_DRIVER_SHA256 = (
    "b73af5a62c99171eb99f37244ecc38df"
    "19fe19def3377b542bcbe2ec6753ef91"
)

EXPECTED_RUNNER_SHA256 = (
    "e0a39b9c7a83943248166c6251ef273c"
    "9505dfece23eff4cbb6531c163cbaeec"
)

TARGET_N = 139
REPRESENTATION = "esm_layer_18"

BIO_START = 1000001
BIO_END = 1000100

NULL_START = 1100001
NULL_END = 1100100

EXPECTED_COUNT = 100
ESM_WIDTH = 1280

STREAM_SUBSAMPLE = 21
STREAM_STAGE_B_FIT = 25
STREAM_LABEL_PERMUTATION = 28

HERE = Path(__file__).resolve().parent

ORIGINAL_SPEC_PATH = (
    HERE / "DECODER_GEOMETRY_BETA_RECOVERY_SPEC.md"
)

RECONCILIATION_PATH = (
    HERE / "DECODER_GEOMETRY_CMATCHED_RECONCILIATION.md"
)

PASS1_PATH = (
    HERE / "decoder_geometry_beta_recovery.py"
)

RUNNER_PATH = (
    HERE / "run_phase_p_biological_probe.py"
)


class CMatchedRecoveryError(RuntimeError):
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
        ORIGINAL_SPEC_PATH:
            EXPECTED_ORIGINAL_SPEC_SHA256,
        RECONCILIATION_PATH:
            EXPECTED_RECONCILIATION_SHA256,
        PASS1_PATH:
            EXPECTED_PASS1_DRIVER_SHA256,
        RUNNER_PATH:
            EXPECTED_RUNNER_SHA256,
    }

    for path, digest in expected.items():

        if not path.is_file():

            raise CMatchedRecoveryError(
                f"Missing frozen source: {path}"
            )

        observed = sha256_file(
            path
        )

        if observed != digest:

            raise CMatchedRecoveryError(
                "Frozen source identity mismatch.\n"
                f"path={path}\n"
                f"expected={digest}\n"
                f"observed={observed}"
            )


def load_pass1_library():

    verify_static_identities()

    name = (
        "_exp04_cmatched_pass1_library"
    )

    if name in sys.modules:

        raise CMatchedRecoveryError(
            "Synthetic Pass-1 module name already registered."
        )

    spec = importlib.util.spec_from_file_location(
        name,
        PASS1_PATH,
    )

    if spec is None or spec.loader is None:

        raise CMatchedRecoveryError(
            "Unable to load frozen Pass-1 library."
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[name] = module

    spec.loader.exec_module(
        module
    )

    if module.ENABLE_PASS1 is not False:

        raise CMatchedRecoveryError(
            "Pass-1 recovery library must remain hard-disabled."
        )

    return module


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

    tmp_path = Path(
        tmp_name
    )

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
    ids,
    biological_ids,
    imposed_c,
    beta,
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

    os.close(
        fd
    )

    tmp_path = Path(
        tmp_name
    )

    try:

        np.savez_compressed(
            tmp_path,
            null_ids=np.asarray(
                ids,
                dtype=np.int64,
            ),
            biological_source_ids=np.asarray(
                biological_ids,
                dtype=np.int64,
            ),
            imposed_C=np.asarray(
                imposed_c,
                dtype=np.float64,
            ),
            beta=np.asarray(
                beta,
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


def label_vector_sha256(
    y,
) -> str:

    """
    Provenance-only identity hash for a reconstructed frozen label vector.

    Canonical serialization:
      - shape must be (2 * TARGET_N,)
      - values must be exactly {0, 1}
      - contiguous little-endian signed int64
      - C-order bytes
    """

    import numpy as np

    arr = np.asarray(
        y,
    )

    if arr.shape != (
        2 * TARGET_N,
    ):

        raise CMatchedRecoveryError(
            "Permuted-label vector shape mismatch: "
            f"{arr.shape}"
        )

    if not np.all(
        np.isin(
            arr,
            (0, 1),
        )
    ):

        raise CMatchedRecoveryError(
            "Permuted-label vector contains values outside {0,1}."
        )

    little = np.ascontiguousarray(
        arr.astype(
            "<i8",
            copy=False,
        )
    )

    digest = hashlib.sha256(
        little.tobytes(
            order="C"
        )
    ).hexdigest()

    return digest


def coefficient_sha256(
    beta,
) -> str:

    import numpy as np

    arr = np.asarray(
        beta,
        dtype=np.float64,
    )

    if arr.shape != (
        ESM_WIDTH,
    ):

        raise CMatchedRecoveryError(
            "C-matched Stage-B beta shape mismatch: "
            f"{arr.shape}"
        )

    if not np.all(
        np.isfinite(arr)
    ):

        raise CMatchedRecoveryError(
            "C-matched Stage-B beta contains non-finite values."
        )

    little = np.ascontiguousarray(
        arr.astype(
            "<f8",
            copy=False,
        )
    )

    return hashlib.sha256(
        little.tobytes(
            order="C"
        )
    ).hexdigest()


def run_cmatched_recovery(
    *,
    private_phase_p_dir: Path,
    output_dir: Path,
) -> int:

    """
    Execute the already-frozen Section-11 secondary arm.

    This routine intentionally performs no decoder geometry and no
    population-level comparison.
    """

    verify_static_identities()

    if output_dir.exists():

        raise CMatchedRecoveryError(
            "Output directory already exists; refusing overwrite."
        )

    pass1 = load_pass1_library()

    frozen = (
        pass1.build_frozen_phase_p_namespace()
    )

    (
        biological_rows,
        canonical_null_rows,
    ) = pass1.select_canonical_rows(
        private_phase_p_dir,
        frozen,
    )

    if len(
        biological_rows
    ) != EXPECTED_COUNT:

        raise CMatchedRecoveryError(
            "Biological selected-C census is not 100."
        )

    if len(
        canonical_null_rows
    ) != EXPECTED_COUNT:

        raise CMatchedRecoveryError(
            "Canonical-null census is not 100."
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

    import numpy as np
    import warnings

    from sklearn.exceptions import (
        ConvergenceWarning,
    )

    prepare_null = frozen[
        "prepare_permutation_null_stage_a"
    ]

    null_seedsequence = frozen[
        "permutation_null_seedsequence"
    ]

    seed_to_uint32 = frozen[
        "seedsequence_to_uint32"
    ]

    make_probe = frozen[
        "make_probe"
    ]

    records: list[
        dict[str, Any]
    ] = []

    valid_null_ids: list[int] = []
    valid_bio_ids: list[int] = []
    valid_imposed_c: list[float] = []
    valid_beta: list[Any] = []

    converged_count = 0
    excluded_count = 0

    for ordinal in range(
        EXPECTED_COUNT
    ):

        biological_id = (
            BIO_START
            + ordinal
        )

        null_id = (
            NULL_START
            + ordinal
        )

        biological_row = (
            biological_rows[
                biological_id
            ]
        )

        canonical_null_row = (
            canonical_null_rows[
                null_id
            ]
        )

        imposed_C = float(
            biological_row[
                "selected_C"
            ]
        )

        canonical_null_C = float(
            canonical_null_row[
                "selected_C"
            ]
        )

        record: dict[
            str,
            Any,
        ] = {
            "ordinal_index":
                int(
                    ordinal + 1
                ),
            "biological_source_id":
                int(
                    biological_id
                ),
            "null_perturbation_id":
                int(
                    null_id
                ),
            "imposed_biological_C":
                float(
                    imposed_C
                ),
            "canonical_null_selected_C":
                float(
                    canonical_null_C
                ),
            "target_n":
                TARGET_N,
            "representation":
                REPRESENTATION,
            "stage_a_selection_rerun":
                False,
            "stage_b_seed_stream":
                STREAM_STAGE_B_FIT,
            "new_seed_namespace_consumed":
                False,
            "status":
                None,
            "convergence_warning":
                False,
            "convergence_messages":
                [],
            "fit_exception_type":
                None,
            "fit_exception_message":
                None,
            "permuted_label_sha256":
                None,
            "coefficient_sha256":
                None,
            "exact_zero_beta":
                None,
        }

        try:

            (
                Xn,
                yn_perm,
                _X_train,
                _y_train,
                _X_eval,
                _y_eval,
            ) = prepare_null(
                X,
                y,
                c=null_id,
            )

            Xn = np.asarray(
                Xn,
                dtype=np.float64,
            )

            yn_perm = np.asarray(
                yn_perm,
                dtype=np.int64,
            )

            if Xn.shape != (
                2 * TARGET_N,
                ESM_WIDTH,
            ):

                raise CMatchedRecoveryError(
                    "C-matched null target-pool shape mismatch: "
                    f"{Xn.shape}"
                )

            if yn_perm.shape != (
                2 * TARGET_N,
            ):

                raise CMatchedRecoveryError(
                    "C-matched null label shape mismatch."
                )

            if int(
                np.sum(
                    yn_perm == 1
                )
            ) != TARGET_N:

                raise CMatchedRecoveryError(
                    "C-matched permuted positive count changed."
                )

            if int(
                np.sum(
                    yn_perm == 0
                )
            ) != TARGET_N:

                raise CMatchedRecoveryError(
                    "C-matched permuted negative count changed."
                )

            record[
                "permuted_label_sha256"
            ] = label_vector_sha256(
                yn_perm
            )

            stage_b_ss = null_seedsequence(
                null_id,
                STREAM_STAGE_B_FIT,
            )

            stage_b_seed = seed_to_uint32(
                stage_b_ss
            )

            model = make_probe(
                C=imposed_C,
                random_state=stage_b_seed,
            )

            with warnings.catch_warnings(
                record=True
            ) as caught:

                warnings.simplefilter(
                    "always"
                )

                try:

                    model.fit(
                        Xn,
                        yn_perm,
                    )

                except Exception as exc:

                    record[
                        "status"
                    ] = "fit_exception"

                    record[
                        "fit_exception_type"
                    ] = type(
                        exc
                    ).__name__

                    record[
                        "fit_exception_message"
                    ] = str(
                        exc
                    )

                    excluded_count += 1
                    records.append(
                        record
                    )

                    continue

            convergence = [
                item
                for item in caught
                if issubclass(
                    item.category,
                    ConvergenceWarning,
                )
            ]

            if convergence:

                record[
                    "status"
                ] = "convergence_warning"

                record[
                    "convergence_warning"
                ] = True

                record[
                    "convergence_messages"
                ] = [
                    str(
                        item.message
                    )
                    for item in convergence
                ]

                excluded_count += 1
                records.append(
                    record
                )

                continue

            beta = np.asarray(
                model.coef_[0],
                dtype=np.float64,
            )

            if beta.shape != (
                ESM_WIDTH,
            ):

                raise CMatchedRecoveryError(
                    "C-matched beta width changed."
                )

            if not np.all(
                np.isfinite(
                    beta
                )
            ):

                raise CMatchedRecoveryError(
                    "C-matched beta contains non-finite values."
                )

            beta_hash = coefficient_sha256(
                beta
            )

            exact_zero = bool(
                np.linalg.norm(
                    beta
                ) == 0.0
            )

            record[
                "status"
            ] = "converged"

            record[
                "coefficient_sha256"
            ] = beta_hash

            record[
                "exact_zero_beta"
            ] = exact_zero

            valid_null_ids.append(
                null_id
            )

            valid_bio_ids.append(
                biological_id
            )

            valid_imposed_c.append(
                imposed_C
            )

            valid_beta.append(
                beta.copy()
            )

            converged_count += 1

            records.append(
                record
            )

        except CMatchedRecoveryError:
            raise

        except Exception as exc:

            # Infrastructure / invariant errors are NOT scientific
            # convergence exclusions. Fail closed.
            raise CMatchedRecoveryError(
                "Unexpected C-matched recovery failure at "
                f"null perturbation {null_id}: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

    if len(
        records
    ) != EXPECTED_COUNT:

        raise CMatchedRecoveryError(
            "C-matched record census is not 100."
        )

    if (
        converged_count
        + excluded_count
        != EXPECTED_COUNT
    ):

        raise CMatchedRecoveryError(
            "C-matched outcome accounting does not sum to 100."
        )

    import numpy as np

    if len(
        valid_beta
    ) == 0:

        beta_matrix = np.empty(
            (
                0,
                ESM_WIDTH,
            ),
            dtype=np.float64,
        )

    else:

        beta_matrix = np.asarray(
            valid_beta,
            dtype=np.float64,
        )

        if beta_matrix.shape != (
            len(
                valid_beta
            ),
            ESM_WIDTH,
        ):

            raise CMatchedRecoveryError(
                "C-matched beta artifact shape mismatch: "
                f"{beta_matrix.shape}"
            )

    output_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    report_path = (
        output_dir
        / "cmatched_recovery_report.json"
    )

    beta_path = (
        output_dir
        / "cmatched_stage_b_beta.npz"
    )

    report = {
        "status":
            "complete_secondary_recovery",
        "scientific_role":
            "secondary_marginal_C_distribution_matched_permutation_control",
        "paired_design":
            False,
        "target_n":
            TARGET_N,
        "representation":
            REPRESENTATION,
        "expected_count":
            EXPECTED_COUNT,
        "accounted_count":
            len(
                records
            ),
        "converged_count":
            int(
                converged_count
            ),
        "excluded_fit_or_convergence_count":
            int(
                excluded_count
            ),
        "valid_beta_count":
            int(
                len(
                    valid_beta
                )
            ),
        "stage_a_selection_rerun":
            False,
        "new_seed_namespace_consumed":
            False,
        "frozen_null_stage_b_stream":
            STREAM_STAGE_B_FIT,
        "records":
            records,
        "provenance": {
            "original_spec_sha256":
                EXPECTED_ORIGINAL_SPEC_SHA256,
            "reconciliation_sha256":
                EXPECTED_RECONCILIATION_SHA256,
            "pass1_driver_sha256":
                EXPECTED_PASS1_DRIVER_SHA256,
            "runner_sha256":
                EXPECTED_RUNNER_SHA256,
        },
        "boundary": {
            "decoder_geometry_computed":
                False,
            "population_comparison_computed":
                False,
            "bootstrap_computed":
                False,
            "confirmatory_accessed":
                False,
        },
    }

    atomic_json_write(
        report_path,
        report,
    )

    atomic_npz_write(
        beta_path,
        ids=valid_null_ids,
        biological_ids=valid_bio_ids,
        imposed_c=valid_imposed_c,
        beta=beta_matrix,
    )

    print(
        "C-matched secondary recovery complete."
    )

    print(
        "accounted:",
        len(
            records
        ),
    )

    print(
        "converged:",
        converged_count,
    )

    print(
        "excluded fit/convergence:",
        excluded_count,
    )

    print(
        "report:",
        report_path,
    )

    print(
        "beta artifact:",
        beta_path,
    )

    print(
        "No decoder geometry computed."
    )

    print(
        "No population comparison computed."
    )

    print(
        "No bootstrap computed."
    )

    print(
        "No confirmatory data accessed."
    )

    return 0


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--private-phase-p-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )

    return parser.parse_args()


def main() -> int:

    if not ENABLE_CMATCHED_RECOVERY:

        print(
            "EXP 04 C-MATCHED NULL RECOVERY: HARD-DISABLED"
        )

        print(
            "No Phase-E matrix opened."
        )

        print(
            "No biological label opened."
        )

        print(
            "No canonical Phase-P CSV opened."
        )

        print(
            "No C-matched probe fit."
        )

        print(
            "No C-matched beta generated."
        )

        print(
            "No decoder geometry computed."
        )

        print(
            "No population comparison computed."
        )

        print(
            "No confirmatory data accessed."
        )

        return 0

    args = parse_args()

    return run_cmatched_recovery(
        private_phase_p_dir=(
            args.private_phase_p_dir.resolve()
        ),
        output_dir=(
            args.output_dir.resolve()
        ),
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
