"""
Arm-B Phase-P numerical-conditioning dry run.

ENGINEERING DIAGNOSTIC ONLY.
HARD-DISABLED UNTIL SEPARATELY AND PROSPECTIVELY ENABLED.

Fit-local numerical failures are recorded and deferred.
Integrity failures remain immediate STOP conditions.
"""

from pathlib import Path
import csv
import hashlib
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression


EXECUTION_ENABLED = False

EXPECTED_SPEC_SHA256 = '6374290afac554741161fba15c78ff4d7f3f7b2f05f3405cb31584ae06142349'
EXPECTED_AMENDMENT1_SHA256 = 'd73f491077c74e9eed6d1f866106584d49e5f5f7951570079c1865ce0d708a91'
EXPECTED_AMENDMENT2_SHA256 = 'd44de4945ac3d670e43c0c14383da949fdb6addde3ad727ddd1815e245048dc2'
EXPECTED_MANIFEST_SHA256 = 'ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e'

LAYERS = (1, 9, 18, 24, 30, 33)

FIT_SIZES = (
    128, 153, 154, 160, 177, 178,
    192, 200, 222, 240, 278,
)

C_GRID = (
    1e-4, 3e-4, 1e-3, 3e-3, 1e-2,
    3e-2, 1e-1, 3e-1, 1.0,
)

ENGINEERING_SOLVER_STATES = (0, 1, 2, 3, 4)
EXPECTED_FIT_COUNT = 2970

MATRIX_SHA256 = {
    1: '204b2d0901b805ce9221b8318883e29dfe2c9a2c1aa18f37b6fc831ef3b08c15',
    9: '7eb08b17232cbf34c23ac8e246dbeb07bec2197904d4bb24e6717a93c1d03683',
    18: 'c4e408db0963a0cbb90996ebb59b5e83cd86a9120de1a968cd4b7d80f5fa440e',
    24: '78c34e2c4419fb1ba850e383ab56b06b864412e65ba5046379983ff9e1190336',
    30: 'ebc98537034ea7946b4c634d4a0a3fff18f503428b3f182c79360a604159c98b',
    33: '64e626858aa8e2a0a323af5121520f969f942679f8cbec4d27c7116bc8501f0d',
}


class ConditioningIntegrityStop(RuntimeError):
    pass


class ConditioningFinalStop(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_sha(path: Path, expected: str, label: str) -> None:
    observed = sha256_file(path)
    if observed != expected:
        raise ConditioningIntegrityStop(
            f"{label} SHA mismatch: expected={expected} observed={observed}"
        )


def make_conditioning_probe(
    C: float,
    engineering_solver_state: int,
) -> LogisticRegression:
    return LogisticRegression(
        penalty="l1",
        solver="liblinear",
        C=float(C),
        fit_intercept=True,
        max_iter=10000,
        tol=1e-6,
        random_state=int(engineering_solver_state),
    )


def deterministic_row_permutation() -> np.ndarray:
    p = np.asarray(
        [(137 * j) % 278 for j in range(278)],
        dtype=np.int64,
    )
    if p.shape != (278,):
        raise ConditioningIntegrityStop("row permutation shape failure")
    if np.unique(p).size != 278:
        raise ConditioningIntegrityStop("row rule is not a permutation")
    if not np.array_equal(
        np.sort(p),
        np.arange(278, dtype=np.int64),
    ):
        raise ConditioningIntegrityStop("row rule does not cover 0..277")
    return p


def artificial_labels() -> np.ndarray:
    y = np.arange(278, dtype=np.int64) % 2
    if y.shape != (278,):
        raise ConditioningIntegrityStop("artificial-label shape failure")
    if int(np.sum(y == 0)) != 139:
        raise ConditioningIntegrityStop("artificial class-0 count failure")
    if int(np.sum(y == 1)) != 139:
        raise ConditioningIntegrityStop("artificial class-1 count failure")
    return y


def validate_matrix(X: np.ndarray, layer: int) -> None:
    if X.shape != (278, 1280):
        raise ConditioningIntegrityStop(
            f"layer {layer}: unexpected shape {X.shape}"
        )
    if X.dtype != np.dtype("float32"):
        raise ConditioningIntegrityStop(
            f"layer {layer}: unexpected dtype {X.dtype}"
        )
    if not np.isfinite(X).all():
        raise ConditioningIntegrityStop(
            f"layer {layer}: matrix contains non-finite values"
        )


def fit_one(
    X: np.ndarray,
    y: np.ndarray,
    C: float,
    engineering_solver_state: int,
) -> dict:
    result = {
        "fit_completed": False,
        "convergence_warning": False,
        "coefficient_finite": "",
        "intercept_finite": "",
        "n_iter": "",
        "exception_type": "",
        "exception_message": "",
    }

    model = make_conditioning_probe(
        C=C,
        engineering_solver_state=engineering_solver_state,
    )

    caught = []

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.fit(X, y)

        result["fit_completed"] = True

        coefficient_finite = bool(np.isfinite(model.coef_).all())
        intercept_finite = bool(np.isfinite(model.intercept_).all())

        result["coefficient_finite"] = coefficient_finite
        result["intercept_finite"] = intercept_finite

        if hasattr(model, "n_iter_"):
            arr = np.asarray(model.n_iter_)
            if arr.size:
                result["n_iter"] = int(arr.reshape(-1)[0])

    except Exception as exc:
        result["exception_type"] = type(exc).__name__
        result["exception_message"] = str(exc)

    finally:
        result["convergence_warning"] = any(
            issubclass(w.category, ConvergenceWarning)
            for w in caught
        )

    return result


def is_fit_local_failure(result: dict) -> bool:
    if result["fit_completed"] is not True:
        return True
    if result["convergence_warning"] is True:
        return True
    if result["coefficient_finite"] is not True:
        return True
    if result["intercept_finite"] is not True:
        return True
    return False


def run_enabled_conditioning(repo: Path) -> None:
    if EXECUTION_ENABLED is not True:
        raise ConditioningIntegrityStop(
            "conditioning execution is hard-disabled; prospective enablement required"
        )

    spec = repo / 'experiments/04-depth-and-basis/ARM_B_PHASE_P_NUMERICAL_CONDITIONING_DRY_RUN_SPEC.md'
    amendment1 = repo / 'experiments/04-depth-and-basis/ARM_B_PHASE_P_NUMERICAL_CONDITIONING_DRY_RUN_AMENDMENT.md'
    amendment2 = repo / 'experiments/04-depth-and-basis/ARM_B_PHASE_P_NUMERICAL_CONDITIONING_DEFERRED_STOP_AMENDMENT.md'
    manifest = repo / 'experiments/03-toxin-representation/stage1_model_contact/discovery_extraction/discovery_matrix_rows.tsv'

    require_sha(spec, EXPECTED_SPEC_SHA256, "conditioning spec")
    require_sha(amendment1, EXPECTED_AMENDMENT1_SHA256, "conditioning amendment 1")
    require_sha(amendment2, EXPECTED_AMENDMENT2_SHA256, "conditioning amendment 2")
    require_sha(manifest, EXPECTED_MANIFEST_SHA256, "Phase-E row manifest")

    if (
        len(LAYERS)
        * len(FIT_SIZES)
        * len(C_GRID)
        * len(ENGINEERING_SOLVER_STATES)
        != EXPECTED_FIT_COUNT
    ):
        raise ConditioningIntegrityStop("frozen fit-count arithmetic failure")

    matrices = {}

    for layer in LAYERS:
        matrix_path = (
            repo
            / "experiments/04-depth-and-basis/phase_e_extraction/output"
            / f"raw_esm_layer_{layer}.npy"
        )
        require_sha(
            matrix_path,
            MATRIX_SHA256[layer],
            f"layer {layer} matrix",
        )

        X_full = np.load(matrix_path, allow_pickle=False)
        validate_matrix(X_full, layer)
        matrices[layer] = X_full

    p = deterministic_row_permutation()
    y_global = artificial_labels()

    output_dir = (
        repo
        / "experiments/04-depth-and-basis"
        / "phase_p_biological_probe"
        / "numerical_conditioning_output"
    )

    if output_dir.exists():
        raise ConditioningIntegrityStop(
            f"output path already exists: {output_dir}"
        )

    output_dir.mkdir(parents=True, exist_ok=False)
    output_path = output_dir / "conditioning_fit_diagnostics.csv"

    fieldnames = [
        "layer",
        "fit_size",
        "C",
        "engineering_solver_state",
        "fit_completed",
        "convergence_warning",
        "coefficient_finite",
        "intercept_finite",
        "n_iter",
        "exception_type",
        "exception_message",
    ]

    attempted = 0
    local_failures = 0

    with output_path.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for layer in LAYERS:
            X_full = matrices[layer]

            for fit_size in FIT_SIZES:
                idx = p[:fit_size]
                X = X_full[idx]
                y = y_global[idx]

                if X.shape != (fit_size, 1280):
                    raise ConditioningIntegrityStop(
                        "conditioning subset shape failure"
                    )

                n0 = int(np.sum(y == 0))
                n1 = int(np.sum(y == 1))

                if n0 == 0 or n1 == 0 or abs(n0 - n1) > 1:
                    raise ConditioningIntegrityStop(
                        "artificial-label subset-count failure"
                    )

                for C in C_GRID:
                    for engineering_solver_state in ENGINEERING_SOLVER_STATES:
                        result = fit_one(
                            X=X,
                            y=y,
                            C=C,
                            engineering_solver_state=engineering_solver_state,
                        )

                        attempted += 1

                        if is_fit_local_failure(result):
                            local_failures += 1

                        row = {
                            "layer": layer,
                            "fit_size": fit_size,
                            "C": C,
                            "engineering_solver_state": engineering_solver_state,
                            **result,
                        }

                        writer.writerow(row)
                        f.flush()

    if attempted != EXPECTED_FIT_COUNT:
        raise ConditioningIntegrityStop(
            f"fit-count mismatch: expected={EXPECTED_FIT_COUNT} observed={attempted}"
        )

    if local_failures:
        raise ConditioningFinalStop(
            f"conditioning STOP after complete census: "
            f"{local_failures}/{attempted} fit-local numerical failures"
        )


def main() -> None:
    if EXECUTION_ENABLED is not True:
        raise ConditioningIntegrityStop(
            "conditioning execution is hard-disabled; prospective enablement required"
        )

    repo = Path(__file__).resolve().parents[3]
    run_enabled_conditioning(repo)


if __name__ == "__main__":
    main()
