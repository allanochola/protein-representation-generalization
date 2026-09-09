#!/usr/bin/env python3

"""
Experiment 04 decoder geometry:
secondary C-matched permutation-null population driver.

Scientific role
---------------
This is a post hoc decoder-side population procedure for the prospectively
reconciled secondary marginal C-distribution-matched permutation control.

It consumes only the previously recovered private C-matched Stage-B
coefficient artifact and the exact frozen InterPLM layer-18 SAE checkpoint.

It does NOT:
  - rerun coefficient recovery;
  - rerun Stage-A model selection;
  - create a new seed namespace;
  - alter the canonical Experiment 04 permutation null;
  - compute population summaries;
  - compare biological/null/isotropic populations;
  - bootstrap;
  - compute p-values;
  - access confirmatory data.

Output
------
One private JSON record per C-matched null perturbation plus one completion
manifest.

Exact-zero coefficient vectors are recorded as structurally ineligible for
directional decoder geometry. Every nonzero vector is analyzed exactly once
with the frozen decoder_geometry_analysis.analyze_direction() engine.
"""

# ---------------------------------------------------------------------------
# THREAD CONTRACT — MUST PRECEDE NUMERICAL IMPORTS
# ---------------------------------------------------------------------------

import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"


# ---------------------------------------------------------------------------
# STANDARD LIBRARY
# ---------------------------------------------------------------------------

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


# ---------------------------------------------------------------------------
# HARD EXECUTION GATE
# ---------------------------------------------------------------------------

ENABLE_CMATCHED_GEOMETRY_POPULATION = True


# ---------------------------------------------------------------------------
# FROZEN IDENTITIES
# ---------------------------------------------------------------------------

EXPECTED_ENGINE_SHA256 = (
    "8289d96a11ee3f5506edf298bf0290f58414454737156c98737f4522642915ab"
)

EXPECTED_CMATCHED_REPORT_SHA256 = (
    "bcc20a34612c9f9c81e546cb6fc74ae6fc2fd81c21b9094ba924a6f36143a45c"
)

EXPECTED_CMATCHED_BETA_SHA256 = (
    "a1ac55f9810a0f100e3b9cb4805acbdf5c63a9667980f8229d6478b44be7268c"
)

EXPECTED_SAE_SHA256 = (
    "bf0dfb992321cf4d1ce80fced0db0256f5c7a1f9fdd8a7fe4834e786c1f6472a"
)

EXPECTED_RECOVERY_COMPLETION_NOTE_SHA256 = (
    "0403aa9c379c3e7a69de60adb9f28f426c6f94c0ed898991d912b3144abe3ae1"
)

N_EXPECTED = 100
D_MODEL = 1280

NULL_START = 1100001
NULL_END = 1100100

BIO_START = 1000001
BIO_END = 1000100

POPULATION_NAME = "cmatched_null"


class CMatchedGeometryPopulationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:

    h = hashlib.sha256()

    with path.open("rb") as f:

        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):

            h.update(block)

    return h.hexdigest()


def canonical_beta_sha256(beta) -> str:

    import numpy as np

    arr = np.asarray(
        beta,
        dtype=np.float64,
    )

    if arr.shape != (
        D_MODEL,
    ):

        raise CMatchedGeometryPopulationError(
            f"Coefficient shape changed: {arr.shape}"
        )

    if not np.all(
        np.isfinite(arr)
    ):

        raise CMatchedGeometryPopulationError(
            "Coefficient vector contains non-finite values."
        )

    little = np.ascontiguousarray(
        arr.astype(
            "<f8",
            copy=False,
        )
    )

    return hashlib.sha256(
        little.tobytes(
            order="C",
        )
    ).hexdigest()


def atomic_json_write(
    path: Path,
    payload,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=path.name + ".tmp.",
        delete=False,
    ) as f:

        tmp = Path(
            f.name
        )

        json.dump(
            payload,
            f,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )

        f.write(
            "\n"
        )

    os.replace(
        tmp,
        path,
    )


def load_engine(
    engine_path: Path,
):

    if not engine_path.is_file():

        raise CMatchedGeometryPopulationError(
            f"Frozen geometry engine missing: {engine_path}"
        )

    observed_sha = sha256_file(
        engine_path
    )

    if observed_sha != EXPECTED_ENGINE_SHA256:

        raise CMatchedGeometryPopulationError(
            "Frozen geometry-engine SHA mismatch."
        )

    module_name = (
        "_exp04_frozen_decoder_geometry_analysis"
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        engine_path,
    )

    if (
        spec is None
        or spec.loader is None
    ):

        raise CMatchedGeometryPopulationError(
            "Could not create frozen geometry-engine import spec."
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

    return module


def verify_recovery_report(
    report_path: Path,
):

    if not report_path.is_file():

        raise CMatchedGeometryPopulationError(
            f"C-matched recovery report missing: {report_path}"
        )

    if sha256_file(
        report_path
    ) != EXPECTED_CMATCHED_REPORT_SHA256:

        raise CMatchedGeometryPopulationError(
            "C-matched recovery-report SHA mismatch."
        )

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as f:

        report = json.load(
            f
        )

    if report.get(
        "status"
    ) != "complete_secondary_recovery":

        raise CMatchedGeometryPopulationError(
            "C-matched recovery did not report complete status."
        )

    required = {
        "expected_count": 100,
        "accounted_count": 100,
        "converged_count": 100,
        "excluded_fit_or_convergence_count": 0,
        "valid_beta_count": 100,
        "stage_a_selection_rerun": False,
        "new_seed_namespace_consumed": False,
    }

    for key, expected in required.items():

        if report.get(
            key
        ) != expected:

            raise CMatchedGeometryPopulationError(
                f"Recovery report invariant changed: {key}"
            )

    boundary = report.get(
        "boundary"
    )

    if not isinstance(
        boundary,
        dict,
    ):

        raise CMatchedGeometryPopulationError(
            "Recovery report boundary missing."
        )

    for key in (
        "decoder_geometry_computed",
        "population_comparison_computed",
        "bootstrap_computed",
        "confirmatory_accessed",
    ):

        if boundary.get(
            key
        ) is not False:

            raise CMatchedGeometryPopulationError(
                f"Recovery scientific boundary changed: {key}"
            )

    return report


def load_verified_beta_population(
    beta_path: Path,
):

    import numpy as np

    if not beta_path.is_file():

        raise CMatchedGeometryPopulationError(
            f"C-matched beta artifact missing: {beta_path}"
        )

    if sha256_file(
        beta_path
    ) != EXPECTED_CMATCHED_BETA_SHA256:

        raise CMatchedGeometryPopulationError(
            "C-matched beta-artifact SHA mismatch."
        )

    with np.load(
        beta_path,
        allow_pickle=False,
    ) as z:

        expected_keys = {
            "null_ids",
            "biological_source_ids",
            "imposed_C",
            "beta",
        }

        if set(
            z.files
        ) != expected_keys:

            raise CMatchedGeometryPopulationError(
                "C-matched beta-artifact key set changed."
            )

        null_ids = np.array(
            z["null_ids"],
            copy=True,
        )

        biological_ids = np.array(
            z["biological_source_ids"],
            copy=True,
        )

        imposed_c = np.array(
            z["imposed_C"],
            copy=True,
        )

        beta = np.array(
            z["beta"],
            dtype=np.float64,
            copy=True,
        )

    if null_ids.shape != (
        N_EXPECTED,
    ):

        raise CMatchedGeometryPopulationError(
            f"null_ids shape changed: {null_ids.shape}"
        )

    if biological_ids.shape != (
        N_EXPECTED,
    ):

        raise CMatchedGeometryPopulationError(
            f"biological_source_ids shape changed: {biological_ids.shape}"
        )

    if imposed_c.shape != (
        N_EXPECTED,
    ):

        raise CMatchedGeometryPopulationError(
            f"imposed_C shape changed: {imposed_c.shape}"
        )

    if beta.shape != (
        N_EXPECTED,
        D_MODEL,
    ):

        raise CMatchedGeometryPopulationError(
            f"beta matrix shape changed: {beta.shape}"
        )

    if beta.dtype != np.float64:

        raise CMatchedGeometryPopulationError(
            f"beta dtype changed: {beta.dtype}"
        )

    if not np.all(
        np.isfinite(beta)
    ):

        raise CMatchedGeometryPopulationError(
            "beta matrix contains non-finite values."
        )

    if not np.all(
        np.isfinite(imposed_c)
    ):

        raise CMatchedGeometryPopulationError(
            "imposed_C contains non-finite values."
        )

    expected_null = np.arange(
        NULL_START,
        NULL_END + 1,
        dtype=null_ids.dtype,
    )

    expected_bio = np.arange(
        BIO_START,
        BIO_END + 1,
        dtype=biological_ids.dtype,
    )

    if not np.array_equal(
        null_ids,
        expected_null,
    ):

        raise CMatchedGeometryPopulationError(
            "C-matched null-ID sequence changed."
        )

    if not np.array_equal(
        biological_ids,
        expected_bio,
    ):

        raise CMatchedGeometryPopulationError(
            "C-matched biological-source-ID sequence changed."
        )

    return (
        null_ids,
        biological_ids,
        imposed_c,
        beta,
    )


def verify_sae_checkpoint_bytes(
    checkpoint_path: Path,
):

    if not checkpoint_path.is_file():

        raise CMatchedGeometryPopulationError(
            f"SAE checkpoint missing: {checkpoint_path}"
        )

    observed_sha = sha256_file(
        checkpoint_path
    )

    if observed_sha != EXPECTED_SAE_SHA256:

        raise CMatchedGeometryPopulationError(
            "SAE checkpoint SHA mismatch."
        )


def verify_completion_note(
    note_path: Path,
):

    if not note_path.is_file():

        raise CMatchedGeometryPopulationError(
            f"Recovery completion note missing: {note_path}"
        )

    if sha256_file(
        note_path
    ) != EXPECTED_RECOVERY_COMPLETION_NOTE_SHA256:

        raise CMatchedGeometryPopulationError(
            "Recovery completion-note SHA mismatch."
        )


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--engine-path",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--recovery-report",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--beta-artifact",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--sae-checkpoint",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--recovery-completion-note",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
    )

    return parser.parse_args()


def run_population(args):

    import numpy as np

    output_dir = args.output_dir.resolve()

    if output_dir.exists():

        raise CMatchedGeometryPopulationError(
            f"Output directory already exists: {output_dir}"
        )

    verify_completion_note(
        args.recovery_completion_note.resolve()
    )

    verify_recovery_report(
        args.recovery_report.resolve()
    )

    (
        null_ids,
        biological_ids,
        imposed_c,
        beta_matrix,
    ) = load_verified_beta_population(
        args.beta_artifact.resolve()
    )

    verify_sae_checkpoint_bytes(
        args.sae_checkpoint.resolve()
    )

    engine = load_engine(
        args.engine_path.resolve()
    )

    # Decoder deserialization occurs only here, after every input gate passes.
    decoder = engine.load_verified_decoder(
        args.sae_checkpoint.resolve()
    )

    records_dir = (
        output_dir
        / "records"
    )

    records_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    record_manifest = []

    eligible_count = 0
    zero_beta_count = 0

    for i in range(
        N_EXPECTED
    ):

        null_id = int(
            null_ids[i]
        )

        biological_source_id = int(
            biological_ids[i]
        )

        beta = np.asarray(
            beta_matrix[i],
            dtype=np.float64,
        )

        coefficient_sha = canonical_beta_sha256(
            beta
        )

        # Exact zero semantics match the frozen geometry engine:
        # normalize_direction() returns None iff exact L2 norm == 0.
        direction = engine.normalize_direction(
            beta
        )

        if direction is None:

            zero_beta_count += 1

            record = {
                "population": POPULATION_NAME,
                "perturbation_id": null_id,
                "biological_source_id": biological_source_id,
                "eligibility": "ineligible_zero_beta",
                "coefficient_sha256": coefficient_sha,
                "analysis_status": "not_run_zero_beta",
                "geometry": None,
            }

        else:

            eligible_count += 1

            # Exactly one geometry call for every eligible direction.
            geometry = engine.analyze_direction(
                beta,
                decoder,
            )

            if not isinstance(
                geometry,
                dict,
            ):

                raise CMatchedGeometryPopulationError(
                    f"Geometry result is not a dict for null ID {null_id}."
                )

            if geometry.get(
                "status"
            ) != "complete":

                raise CMatchedGeometryPopulationError(
                    f"Eligible geometry incomplete for null ID {null_id}."
                )

            record = {
                "population": POPULATION_NAME,
                "perturbation_id": null_id,
                "biological_source_id": biological_source_id,
                "eligibility": "eligible_nonzero_beta",
                "coefficient_sha256": coefficient_sha,
                "analysis_status": "complete",
                "geometry": geometry,
            }

        record_path = (
            records_dir
            / f"cmatched_null_{null_id}.json"
        )

        atomic_json_write(
            record_path,
            record,
        )

        record_manifest.append(
            {
                "perturbation_id": null_id,
                "biological_source_id": biological_source_id,
                "path": str(
                    record_path.relative_to(
                        output_dir
                    )
                ),
                "sha256": sha256_file(
                    record_path
                ),
                "eligibility": record[
                    "eligibility"
                ],
                "analysis_status": record[
                    "analysis_status"
                ],
            }
        )

    if (
        eligible_count
        + zero_beta_count
        != N_EXPECTED
    ):

        raise CMatchedGeometryPopulationError(
            "Population accounting does not close."
        )

    manifest = {
        "status": "complete_unsummarized",
        "scientific_role":
            "secondary_marginal_C_distribution_matched_permutation_control",
        "population": POPULATION_NAME,
        "expected_count": N_EXPECTED,
        "accounted_count": len(
            record_manifest
        ),
        "eligible_nonzero_beta_count": eligible_count,
        "ineligible_zero_beta_count": zero_beta_count,
        "geometry_complete_count": eligible_count,
        "engine_sha256": EXPECTED_ENGINE_SHA256,
        "cmatched_recovery_report_sha256":
            EXPECTED_CMATCHED_REPORT_SHA256,
        "cmatched_beta_artifact_sha256":
            EXPECTED_CMATCHED_BETA_SHA256,
        "sae_checkpoint_sha256":
            EXPECTED_SAE_SHA256,
        "recovery_completion_note_sha256":
            EXPECTED_RECOVERY_COMPLETION_NOTE_SHA256,
        "thread_environment": {
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
        "records": record_manifest,
        "boundary": {
            "population_summary_computed": False,
            "biological_geometry_opened_for_comparison": False,
            "canonical_null_geometry_opened_for_comparison": False,
            "isotropic_geometry_opened_for_comparison": False,
            "bootstrap_computed": False,
            "p_value_computed": False,
            "scientific_verdict_computed": False,
            "confirmatory_accessed": False,
        },
    }

    if manifest[
        "accounted_count"
    ] != N_EXPECTED:

        raise CMatchedGeometryPopulationError(
            "Manifest row count changed."
        )

    completion_manifest = (
        output_dir
        / "completion_manifest.json"
    )

    atomic_json_write(
        completion_manifest,
        manifest,
    )

    print(
        "C-matched geometry population complete."
    )

    print(
        "accounted:",
        N_EXPECTED,
    )

    print(
        "eligible nonzero beta:",
        eligible_count,
    )

    print(
        "ineligible exact-zero beta:",
        zero_beta_count,
    )

    print(
        "geometry complete:",
        eligible_count,
    )

    print(
        "completion manifest:",
        completion_manifest,
    )

    print(
        "No population summary computed."
    )

    print(
        "No biological/canonical-null/isotropic comparison computed."
    )

    print(
        "No bootstrap computed."
    )

    print(
        "No confirmatory data accessed."
    )


def main():

    if not ENABLE_CMATCHED_GEOMETRY_POPULATION:

        print(
            "EXP 04 C-MATCHED GEOMETRY POPULATION: HARD-DISABLED"
        )

        print(
            "No C-matched beta artifact opened."
        )

        print(
            "No SAE checkpoint deserialized."
        )

        print(
            "No beta direction normalized."
        )

        print(
            "No decoder geometry computed."
        )

        print(
            "No population summary computed."
        )

        print(
            "No biological/canonical-null/isotropic comparison computed."
        )

        print(
            "No bootstrap computed."
        )

        print(
            "No confirmatory data accessed."
        )

        return

    args = parse_args()

    try:

        run_population(
            args
        )

    except CMatchedGeometryPopulationError:

        raise

    except Exception as exc:

        raise CMatchedGeometryPopulationError(
            "Unexpected C-matched geometry population failure."
        ) from exc


if __name__ == "__main__":
    main()
