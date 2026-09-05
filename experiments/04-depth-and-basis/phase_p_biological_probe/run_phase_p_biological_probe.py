#!/usr/bin/env python3
"""
Experiment 04 — Arm-B Phase-P biological probe runner.

STATUS:
    HARD-DISABLED BEFORE BIOLOGICAL PROBE EXECUTION.

Governed by:

    experiments/04-depth-and-basis/
    ARM_B_PHASE_P_BIOLOGICAL_PROBING_INHERITANCE_CONTRACT.md

Certified contract SHA-256:

    bac4bcf0933a12e149abfa52fd84d3c310c338bdb59b32ca21dfbdaf63952dbe

Authoritative corrected Arm-B mechanics source:

    experiments/04-depth-and-basis/
    diagnose_arm_b_post_failure_architecture.py

Certified mechanics-source SHA-256:

    a15420b8a7528eeae9d2d7faf811ccbd19708793fe2e3562306c64c1b377166d

Scientific firewall while disabled:

- Phase-E matrices must not be loaded.
- Biological labels must not be loaded for probing.
- No biological perturbation seed may be generated or materialized.
- sklearn must not be imported.
- No probe may be fit.
- No CV may run.
- No AUROC may be computed.
- No support statistic may be computed.
- Confirmatory data must not be accessed.
- 4000-4099 remains UNOPENED.
- 2000-2099 remains SEALED.
- 910001-910100 is CONSUMED / CLOSED.
- 920001-920100 is CONSUMED / CLOSED.
- 930001-930100 is CONSUMED / CLOSED.
- No 940001-940100 namespace exists.

The biological perturbation namespace is deliberately unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final
import hashlib
import sys


# ============================================================================
# HARD EXECUTION GATE
# ============================================================================

ENABLE_PHASE_P_BIOLOGICAL_PROBING: Final[bool] = False


# ============================================================================
# Frozen repository provenance
# ============================================================================

HERE: Final[Path] = Path(__file__).resolve().parent
REPO_ROOT: Final[Path] = HERE.parents[2]

CONTRACT_REL: Final[str] = (
    "experiments/04-depth-and-basis/"
    "ARM_B_PHASE_P_BIOLOGICAL_PROBING_INHERITANCE_CONTRACT.md"
)

CONTRACT_SHA256: Final[str] = (
    "bac4bcf0933a12e149abfa52fd84d3c310c338bdb59b32ca21dfbdaf63952dbe"
)

AUTHORITATIVE_MECHANICS_REL: Final[str] = (
    "experiments/04-depth-and-basis/"
    "diagnose_arm_b_post_failure_architecture.py"
)

AUTHORITATIVE_MECHANICS_SHA256: Final[str] = (
    "a15420b8a7528eeae9d2d7faf811ccbd19708793fe2e3562306c64c1b377166d"
)

PHASE_E_OUTPUT_REL: Final[str] = (
    "experiments/04-depth-and-basis/"
    "phase_e_extraction/output"
)


# ============================================================================
# Frozen Phase-E representation identities
# ============================================================================

LAYERS: Final[tuple[int, ...]] = (
    1,
    9,
    18,
    24,
    30,
    33,
)

N_DISCOVERY_PER_CLASS: Final[int] = 139
N_DISCOVERY_TOTAL: Final[int] = 278
ESM_WIDTH: Final[int] = 1280

PHASE_E_MATRIX_SHA256: Final[dict[int, str]] = {
    1: "204b2d0901b805ce9221b8318883e29dfe2c9a2c1aa18f37b6fc831ef3b08c15",
    9: "7eb08b17232cbf34c23ac8e246dbeb07bec2197904d4bb24e6717a93c1d03683",
    18: "c4e408db0963a0cbb90996ebb59b5e83cd86a9120de1a968cd4b7d80f5fa440e",
    24: "78c34e2c4419fb1ba850e383ab56b06b864412e65ba5046379983ff9e1190336",
    30: "ebc98537034ea7946b4c634d4a0a3fff18f503428b3f182c79360a604159c98b",
    33: "64e626858aa8e2a0a323af5121520f969f942679f8cbec4d27c7116bc8501f0d",
}

PHASE_E_ROWS_SHA256: Final[str] = (
    "ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e"
)

PHASE_E_PROVENANCE_SHA256: Final[str] = (
    "655ea47a8300f1056656378238402cf12dc5a024b96c18117397bb804b02e6dd"
)


# Frozen Phase-P attachment identities.
PHASE_E_ROWS_FILENAME: Final[str] = "phase_e_matrix_rows.tsv"
PHASE_E_PROVENANCE_FILENAME: Final[str] = "PHASE_E_PROVENANCE.json"

BASELINE_21D_REL: Final[str] = (
    "experiments/04-depth-and-basis/phase_p_biological_probe/input/baseline_21d.npy"
)
BASELINE_21D_SHA256: Final[str] = (
    "95fa09075b24dbd11133bdf157f9e4a9b27a01f54d644860a074d5bae4c32d98"
)

BASELINE_21D_PROVENANCE_REL: Final[str] = (
    "experiments/04-depth-and-basis/phase_p_biological_probe/input/BASELINE_21D_PROVENANCE.json"
)
BASELINE_21D_PROVENANCE_SHA256: Final[str] = (
    "98f72c402c07d2e5a48e41a6d8fd0d88dd57af6ccf0acd252fd4b7ca86cbb25f"
)


# ============================================================================
# Frozen biological geometry
# ============================================================================

TARGET_N_VALUES: Final[tuple[int, ...]] = (
    100,
    120,
    139,
)

STABILITY_FRACTION: Final[float] = 0.80

STABILITY_PER_CLASS: Final[dict[int, int]] = {
    100: 80,
    120: 96,
    139: 111,
}


# ============================================================================
# Frozen L1 probe family
# ============================================================================

C_GRID: Final[tuple[float, ...]] = (
    1e-4,
    3e-4,
    1e-3,
    3e-3,
    1e-2,
    3e-2,
    1e-1,
    3e-1,
    1.0,
)

N_CV_FOLDS: Final[int] = 5

PROBE_PENALTY: Final[str] = "l1"
PROBE_SOLVER: Final[str] = "liblinear"
PROBE_FIT_INTERCEPT: Final[bool] = True
PROBE_MAX_ITER: Final[int] = 10000
PROBE_TOL: Final[float] = 1e-6

FEATURE_STANDARDIZATION_ENABLED: Final[bool] = False


# ============================================================================
# Frozen stream identities inherited from corrected architecture
#
# These are stream IDs only.
# They do NOT authorize a biological perturbation seed namespace.
# ============================================================================

STREAM_SUBSAMPLE: Final[int] = 21
STREAM_STAGE_A_SPLIT: Final[int] = 22
STREAM_CV: Final[int] = 23
STREAM_STAGE_A_FIT: Final[int] = 24
STREAM_STAGE_B_FIT: Final[int] = 25
STREAM_STABILITY_SUBSAMPLE: Final[int] = 26
STREAM_STABILITY_FIT: Final[int] = 27
STREAM_LABEL_PERMUTATION: Final[int] = 28


# ============================================================================
# Seed firewall
# ============================================================================

CONSUMED_CLOSED_SEED_RANGES: Final[tuple[str, ...]] = (
    "910001-910100",
    "920001-920100",
    "930001-930100",
)

UNOPENED_SEED_RANGE: Final[str] = "4000-4099"
SEALED_VALIDATION_SEED_RANGE: Final[str] = "2000-2099"

# Intentionally no biological perturbation seed range is defined here.
# Intentionally no 940001-940100 range is defined here.


# ============================================================================
# Frozen simple-sequence baseline
# ============================================================================

CANONICAL_AA_ORDER: Final[tuple[str, ...]] = tuple(
    "ACDEFGHIKLMNPQRSTVWY"
)

BASELINE_DIM: Final[int] = 21


# ============================================================================
# Frozen schema
# ============================================================================

@dataclass(frozen=True)
class FrozenProbeSpec:
    penalty: str
    solver: str
    fit_intercept: bool
    max_iter: int
    tol: float
    c_grid: tuple[float, ...]
    n_cv_folds: int
    stability_fraction: float


FROZEN_PROBE_SPEC: Final[FrozenProbeSpec] = FrozenProbeSpec(
    penalty=PROBE_PENALTY,
    solver=PROBE_SOLVER,
    fit_intercept=PROBE_FIT_INTERCEPT,
    max_iter=PROBE_MAX_ITER,
    tol=PROBE_TOL,
    c_grid=C_GRID,
    n_cv_folds=N_CV_FOLDS,
    stability_fraction=STABILITY_FRACTION,
)


class PhasePContractError(RuntimeError):
    """Frozen Phase-P source/provenance violation."""


def sha256_file(path: Path) -> str:
    """Hash a non-biological repository source/provenance file."""
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def validate_static_contract_only() -> None:
    """
    Validate non-biological static source/provenance only.

    Does not load:
    - Phase-E matrices;
    - biological labels;
    - biological perturbation seeds.
    """
    contract_path = REPO_ROOT / CONTRACT_REL
    mechanics_path = REPO_ROOT / AUTHORITATIVE_MECHANICS_REL

    if not contract_path.is_file():
        raise PhasePContractError(
            f"Missing Phase-P inheritance contract: {CONTRACT_REL}"
        )

    if not mechanics_path.is_file():
        raise PhasePContractError(
            "Missing authoritative mechanics source: "
            f"{AUTHORITATIVE_MECHANICS_REL}"
        )

    if sha256_file(contract_path) != CONTRACT_SHA256:
        raise PhasePContractError(
            "Phase-P inheritance contract SHA drift."
        )

    if sha256_file(mechanics_path) != AUTHORITATIVE_MECHANICS_SHA256:
        raise PhasePContractError(
            "Authoritative mechanics source SHA drift."
        )

    if LAYERS != (1, 9, 18, 24, 30, 33):
        raise PhasePContractError("Frozen layer tuple changed.")

    if TARGET_N_VALUES != (100, 120, 139):
        raise PhasePContractError("Frozen target-N tuple changed.")

    if C_GRID != (
        1e-4,
        3e-4,
        1e-3,
        3e-3,
        1e-2,
        3e-2,
        1e-1,
        3e-1,
        1.0,
    ):
        raise PhasePContractError("Frozen C grid changed.")

    if STABILITY_PER_CLASS != {
        100: 80,
        120: 96,
        139: 111,
    }:
        raise PhasePContractError(
            "Frozen stability sample sizes changed."
        )

    if FEATURE_STANDARDIZATION_ENABLED is not False:
        raise PhasePContractError(
            "Feature standardization unexpectedly enabled."
        )

    if BASELINE_DIM != 21:
        raise PhasePContractError(
            "Frozen baseline dimension changed."
        )

    if len(CANONICAL_AA_ORDER) != 20:
        raise PhasePContractError(
            "Canonical amino-acid order must contain 20 residues."
        )


# ============================================================================
# ENABLED-ONLY boundary
#
# No biological implementation exists at this repository boundary.
# ============================================================================

def run_enabled_phase_p() -> None:
    """
    Enabled-only Phase-P mechanics.

    IMPORTANT
    ---------
    This function is unreachable while
    ENABLE_PHASE_P_BIOLOGICAL_PROBING is literal False.

    numpy/sklearn imports, SeedSequence construction, RNG construction,
    biological matrix loading, probe fitting, CV, AUROC, and support
    computation must remain downstream of the top-level hard-disable return.

    At this implementation boundary the corrected mechanics are encoded but
    biological execution is still intentionally unavailable.
    """

    # Enabled-only dependencies. These imports MUST NOT execute on the
    # hard-disabled path.
    from dataclasses import dataclass
    import hashlib
    import json
    import math
    import warnings

    import numpy as np

    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import StratifiedKFold

    # Frozen provenance for this implementation boundary.
    PHASE_P_INHERITANCE_CONTRACT_SHA256 = (
        "bac4bcf0933a12e149abfa52fd84d3c310c338bdb59b32ca21dfbdaf63952dbe"
    )
    MAIN_BIOLOGICAL_SEED_AUTHORIZATION_SHA256 = (
        "1fa0ab69382f5b09095f69926fcd28627f15b3ec610e2f4126a4355372cc864f"
    )
    BIOLOGICAL_SEED_DERIVATION_SPEC_SHA256 = (
        "10193a2b8d596207c3e466011512d6eb98a4529f9367bfc8471693eb11671922"
    )
    AUTHORITATIVE_CORRECTED_MECHANICS_SHA256 = (
        "a15420b8a7528eeae9d2d7faf811ccbd19708793fe2e3562306c64c1b377166d"
    )

    # Frozen biological main-sweep addressing.
    MAIN_BIOLOGICAL_SEED_START = 1000001
    MAIN_BIOLOGICAL_SEED_END = 1000100

    # Frozen descriptive permutation-null addressing.
    PERMUTATION_NULL_SEED_START = 1100001
    PERMUTATION_NULL_SEED_END = 1100100
    PERMUTATION_NULL_TARGET_N = 139

    RUNNER_NAMESPACE = 200

    STAGE_A_FIT_CHILD_COUNT = 46
    STAGE_A_CV_FIT_CHILDREN = tuple(range(45))
    STAGE_A_FINAL_REFIT_CHILD = 45

    C_GRID = (
        1e-4,
        3e-4,
        1e-3,
        3e-3,
        1e-2,
        3e-2,
        1e-1,
        3e-1,
        1.0,
    )

    N_CV_FOLDS = 5

    STABILITY_FRACTION = 0.80

    TARGET_N_VALUES = (100, 120, 139)

    TRAIN_PER_CLASS = {
        100: 80,
        120: 96,
        139: 111,
    }

    class CalibrationContractError(RuntimeError):
        """Frozen calibration contract was violated."""

    class CalibrationFitFailure(RuntimeError):
        """Frozen solver configuration produced a fit/convergence failure."""

    @dataclass(frozen=True)
    class R2Result:
        selected_C: float
        best_C: float
        best_mean: float
        best_se: float
        one_se_floor: float
        cv_means: tuple[float, ...]
        cv_ses: tuple[float, ...]
        fold_aurocs: tuple[tuple[float, ...], ...]

    def runner_seedsequence(
        c: int,
        target_n: int,
        stream_id: int,
    ) -> np.random.SeedSequence:
        """
        Biological translation of the corrected Arm-B runner-level address.

        Frozen entropy vector:
            [c, 0, 0, 0, N, 200, stream_id]

        c is the prospectively authorized biological perturbation identifier.
        The three zero coordinates are fixed sentinels replacing synthetic
        scenario/tau/rho coordinates.

        Representation identity is intentionally absent so memberships, splits,
        folds, and randomization identities remain paired across all six raw-ESM
        layers and the frozen 21-D baseline.
        """
        if not (1000001 <= int(c) <= 1000100):
            raise CalibrationContractError(
                f"biological perturbation identifier outside authorized "
                f"main namespace: {c}"
            )

        if int(target_n) not in TARGET_N_VALUES:
            raise CalibrationContractError(
                f"unauthorized target N: {target_n}"
            )

        if int(stream_id) not in (21, 22, 23, 24, 25, 26, 27):
            raise CalibrationContractError(
                f"unauthorized main biological stream ID: {stream_id}"
            )

        return np.random.SeedSequence(
            [
                int(c),
                0,
                0,
                0,
                int(target_n),
                RUNNER_NAMESPACE,
                int(stream_id),
            ]
        )

    def permutation_null_seedsequence(
        c: int,
        stream_id: int,
    ) -> np.random.SeedSequence:
        """
        Frozen permutation-null runner-level address:

            [c, 0, 0, 0, 139, 200, stream_id]

        The null namespace is strictly disjoint from the main biological
        namespace. Streams 21-27 retain their inherited stochastic roles;
        stream 28 is reserved exclusively for label-position permutation.
        """
        if not (
            PERMUTATION_NULL_SEED_START
            <= int(c)
            <= PERMUTATION_NULL_SEED_END
        ):
            raise CalibrationContractError(
                f"permutation-null perturbation identifier outside "
                f"authorized namespace: {c}"
            )

        if int(stream_id) not in (
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            STREAM_LABEL_PERMUTATION,
        ):
            raise CalibrationContractError(
                f"unauthorized permutation-null stream ID: {stream_id}"
            )

        return np.random.SeedSequence(
            [
                int(c),
                0,
                0,
                0,
                PERMUTATION_NULL_TARGET_N,
                RUNNER_NAMESPACE,
                int(stream_id),
            ]
        )

    def fit_probe_or_fail(
        X: np.ndarray,
        y: np.ndarray,
        *,
        C: float,
        random_state: int,
        context: str,
    ) -> LogisticRegression:
        """
        Any convergence warning/failure is an instrument-level diagnostic fit failure.
        """
        model = make_probe(
            C=C,
            random_state=random_state,
        )

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")

            try:
                model.fit(X, y)
            except Exception as exc:
                raise CalibrationFitFailure(
                    f"Fit failure in {context}: {exc}"
                ) from exc

        convergence = [
            item
            for item in caught
            if issubclass(item.category, ConvergenceWarning)
        ]

        if convergence:
            messages = [str(item.message) for item in convergence]
            raise CalibrationFitFailure(
                f"Convergence warning in {context}: {messages}"
            )

        return model

    def make_probe(
        C: float,
        random_state: int,
    ) -> LogisticRegression:
        return LogisticRegression(
            penalty="l1",
            solver="liblinear",
            C=float(C),
            fit_intercept=True,
            max_iter=10000,
            tol=1e-6,
            random_state=int(random_state),
        )

    def seedsequence_to_uint32(ss: np.random.SeedSequence) -> int:
        """Frozen SeedSequence -> integer materialization."""
        return int(
            ss.generate_state(
                1,
                dtype=np.uint32,
            )[0]
        )

    def select_C_R2(
        X_train: np.ndarray,
        y_train: np.ndarray,
        *,
        cv_seed: int,
        stage_a_fit_children: tuple[np.random.SeedSequence, ...],
        context: str,
    ) -> R2Result:
        """
        Frozen R2:

        - 5-fold shuffled stratified CV;
        - same folds for every C;
        - mean = arithmetic mean of 5 fold held-out AUROCs;
        - sd uses denominator 4;
        - SE = sd / sqrt(5);
        - best C = largest mean, exact tie -> smallest C;
        - one-SE floor = best_mean - SE(best C);
        - selected C = smallest C whose mean >= floor.
        """
        if len(stage_a_fit_children) != 46:
            raise CalibrationContractError(
                "Stage-A requires exactly 46 fit child SeedSequences."
            )

        cv = StratifiedKFold(
            n_splits=N_CV_FOLDS,
            shuffle=True,
            random_state=int(cv_seed),
        )

        # Freeze one fold construction shared by all C values.
        folds = list(cv.split(X_train, y_train))

        if len(folds) != 5:
            raise CalibrationContractError(
                "Expected exactly five CV folds."
            )

        means: list[float] = []
        ses: list[float] = []
        all_fold_scores: list[tuple[float, ...]] = []

        child_index = 0

        for c_index, C in enumerate(C_GRID):
            fold_scores: list[float] = []

            for fold_index, (fit_idx, val_idx) in enumerate(folds):
                child_ss = stage_a_fit_children[child_index]
                child_index += 1

                fit_seed = seedsequence_to_uint32(child_ss)

                model = fit_probe_or_fail(
                    X_train[fit_idx],
                    y_train[fit_idx],
                    C=C,
                    random_state=fit_seed,
                    context=(
                        f"{context}; C={C}; "
                        f"cv_fold={fold_index + 1}"
                    ),
                )

                scores = model.decision_function(
                    X_train[val_idx]
                )

                auc = float(
                    roc_auc_score(
                        y_train[val_idx],
                        scores,
                    )
                )

                fold_scores.append(auc)

            fold_array = np.asarray(
                fold_scores,
                dtype=float,
            )

            mean_C = float(
                np.mean(fold_array)
            )

            sd_C = float(
                np.std(
                    fold_array,
                    ddof=1,
                )
            )

            se_C = float(
                sd_C / math.sqrt(5.0)
            )

            means.append(mean_C)
            ses.append(se_C)
            all_fold_scores.append(
                tuple(float(x) for x in fold_scores)
            )

        if child_index != 45:
            raise CalibrationContractError(
                f"Expected 45 CV child seeds used; got {child_index}."
            )

        # R1 best definition: largest mean, tie -> smallest C.
        best_mean = max(means)

        best_indices = [
            i
            for i, value in enumerate(means)
            if value == best_mean
        ]

        best_index = min(best_indices)
        best_C = float(C_GRID[best_index])
        best_se = float(ses[best_index])

        one_se_floor = float(
            best_mean - best_se
        )

        admissible = [
            i
            for i, value in enumerate(means)
            if value >= one_se_floor
        ]

        if not admissible:
            raise CalibrationContractError(
                "R2 produced no admissible C."
            )

        # C_GRID is ascending; first admissible is strongest L1.
        selected_index = min(admissible)
        selected_C = float(C_GRID[selected_index])

        return R2Result(
            selected_C=selected_C,
            best_C=best_C,
            best_mean=float(best_mean),
            best_se=float(best_se),
            one_se_floor=float(one_se_floor),
            cv_means=tuple(float(x) for x in means),
            cv_ses=tuple(float(x) for x in ses),
            fold_aurocs=tuple(all_fold_scores),
        )

    def select_stability_subsample(
        y: np.ndarray,
        *,
        target_n: int,
        rng: np.random.Generator,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
        """
        Select floor(0.80 * N) observations independently within each class
        from the already-selected target-N pool.

        Returned memberships are indices in target-N-pool index space.
        """
        y = np.asarray(y, dtype=int)

        if y.ndim != 1:
            raise CalibrationContractError(
                "Stability-subsample labels must be one-dimensional."
            )

        if y.shape[0] != 2 * target_n:
            raise CalibrationContractError(
                "Stability subsampling received wrong target-N pool size."
            )

        pos_pool = np.flatnonzero(y == 1)
        neg_pool = np.flatnonzero(y == 0)

        if len(pos_pool) != target_n or len(neg_pool) != target_n:
            raise CalibrationContractError(
                "Stability subsampling requires exactly N observations per class."
            )

        stability_n = int(math.floor(STABILITY_FRACTION * target_n))

        expected_n = {
            100: 80,
            120: 96,
            139: 111,
        }.get(int(target_n))

        if expected_n is None or stability_n != expected_n:
            raise CalibrationContractError(
                f"Unexpected stability-subsample size for N={target_n}: "
                f"{stability_n}."
            )

        selected_pos = np.asarray(
            rng.choice(
                pos_pool,
                size=stability_n,
                replace=False,
            ),
            dtype=int,
        )

        selected_neg = np.asarray(
            rng.choice(
                neg_pool,
                size=stability_n,
                replace=False,
            ),
            dtype=int,
        )

        if len(np.unique(selected_pos)) != stability_n:
            raise CalibrationContractError(
                "Duplicate positive stability-subsample membership."
            )

        if len(np.unique(selected_neg)) != stability_n:
            raise CalibrationContractError(
                "Duplicate negative stability-subsample membership."
            )

        if not np.all(y[selected_pos] == 1):
            raise CalibrationContractError(
                "Positive stability membership contains a non-positive row."
            )

        if not np.all(y[selected_neg] == 0):
            raise CalibrationContractError(
                "Negative stability membership contains a non-negative row."
            )

        selected = np.concatenate(
            [
                selected_pos,
                selected_neg,
            ]
        )

        membership_payload = {
            "positive_target_pool_indices": [
                int(i) for i in selected_pos.tolist()
            ],
            "negative_target_pool_indices": [
                int(i) for i in selected_neg.tolist()
            ],
        }

        membership_json = json.dumps(
            membership_payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        membership_sha256 = hashlib.sha256(
            membership_json.encode("utf-8")
        ).hexdigest()

        return (
            selected,
            selected_pos,
            selected_neg,
            membership_sha256,
        )

    def select_target_n(
        X: np.ndarray,
        y: np.ndarray,
        *,
        target_n: int,
        rng: np.random.Generator,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Select N positives and N negatives without replacement.

        At N=139 the complete dataset is retained.
        """
        if target_n not in TARGET_N_VALUES:
            raise CalibrationContractError(
                f"Invalid target N: {target_n}"
            )

        y = np.asarray(y)

        pos = np.flatnonzero(y == 1)
        neg = np.flatnonzero(y == 0)

        if len(pos) != 139 or len(neg) != 139:
            raise CalibrationContractError(
                f"Expected 139/139 labels, got "
                f"{len(pos)}/{len(neg)}."
            )

        if target_n == 139:
            selected_pos = pos.copy()
            selected_neg = neg.copy()
        else:
            selected_pos = rng.choice(
                pos,
                size=target_n,
                replace=False,
            )
            selected_neg = rng.choice(
                neg,
                size=target_n,
                replace=False,
            )

        selected = np.concatenate(
            [
                np.asarray(selected_pos, dtype=int),
                np.asarray(selected_neg, dtype=int),
            ]
        )

        Xn = np.asarray(X[selected], dtype=float)
        yn = np.asarray(y[selected], dtype=int)

        if Xn.shape[0] != 2 * target_n:
            raise CalibrationContractError(
                "Target-N selection produced wrong sample count."
            )

        if int(np.sum(yn == 1)) != target_n:
            raise CalibrationContractError(
                "Target-N positive count incorrect."
            )

        if int(np.sum(yn == 0)) != target_n:
            raise CalibrationContractError(
                "Target-N negative count incorrect."
            )

        return Xn, yn

    def stage_a_split(
        X: np.ndarray,
        y: np.ndarray,
        *,
        target_n: int,
        rng: np.random.Generator,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Deterministic class-stratified exact-count 80/20 split.
        """
        train_n = TRAIN_PER_CLASS[target_n]
        eval_n = target_n - train_n

        pos = np.flatnonzero(y == 1)
        neg = np.flatnonzero(y == 0)

        if len(pos) != target_n or len(neg) != target_n:
            raise CalibrationContractError(
                "Stage-A input does not contain target-N per class."
            )

        pos_order = rng.permutation(pos)
        neg_order = rng.permutation(neg)

        train_idx = np.concatenate(
            [
                pos_order[:train_n],
                neg_order[:train_n],
            ]
        )

        eval_idx = np.concatenate(
            [
                pos_order[train_n:],
                neg_order[train_n:],
            ]
        )

        if len(eval_idx) != 2 * eval_n:
            raise CalibrationContractError(
                "Stage-A evaluation count incorrect."
            )

        return (
            np.asarray(X[train_idx], dtype=float),
            np.asarray(y[train_idx], dtype=int),
            np.asarray(X[eval_idx], dtype=float),
            np.asarray(y[eval_idx], dtype=int),
        )

    def prepare_permutation_null_stage_a(
        X: np.ndarray,
        y: np.ndarray,
        *,
        c: int,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        """
        Frozen permutation-null ordering at N=139:

            stream 21 target-N selection
                -> stream 28 positional label permutation
                -> stream 22 Stage-A split

        Xn is never permuted. Only the association between the fixed target-pool
        rows and their labels is randomized. Positional permutation preserves
        the selected pool's exact class counts.
        """
        target_ss = permutation_null_seedsequence(
            c,
            STREAM_SUBSAMPLE,
        )
        target_rng = np.random.default_rng(target_ss)

        Xn, yn = select_target_n(
            X,
            y,
            target_n=PERMUTATION_NULL_TARGET_N,
            rng=target_rng,
        )

        if Xn.shape[0] != 2 * PERMUTATION_NULL_TARGET_N:
            raise CalibrationContractError(
                "permutation-null target pool has wrong row count"
            )

        if yn.shape != (2 * PERMUTATION_NULL_TARGET_N,):
            raise CalibrationContractError(
                "permutation-null target labels have wrong shape"
            )

        pre_pos = int(np.sum(yn == 1))
        pre_neg = int(np.sum(yn == 0))

        if (
            pre_pos != PERMUTATION_NULL_TARGET_N
            or pre_neg != PERMUTATION_NULL_TARGET_N
        ):
            raise CalibrationContractError(
                "permutation-null target pool must contain exactly "
                "139 labels per class before permutation"
            )

        permutation_ss = permutation_null_seedsequence(
            c,
            STREAM_LABEL_PERMUTATION,
        )
        permutation_rng = np.random.default_rng(permutation_ss)

        perm = permutation_rng.permutation(len(yn))
        yn_perm = np.asarray(yn[perm], dtype=int)

        if yn_perm.shape != yn.shape:
            raise CalibrationContractError(
                "label permutation changed target-label shape"
            )

        if int(np.sum(yn_perm == 1)) != pre_pos:
            raise CalibrationContractError(
                "label permutation changed positive class count"
            )

        if int(np.sum(yn_perm == 0)) != pre_neg:
            raise CalibrationContractError(
                "label permutation changed negative class count"
            )

        stage_a_ss = permutation_null_seedsequence(
            c,
            STREAM_STAGE_A_SPLIT,
        )
        stage_a_rng = np.random.default_rng(stage_a_ss)

        X_train, y_train, X_eval, y_eval = stage_a_split(
            Xn,
            yn_perm,
            target_n=PERMUTATION_NULL_TARGET_N,
            rng=stage_a_rng,
        )

        return (
            Xn,
            yn_perm,
            X_train,
            y_train,
            X_eval,
            y_eval,
        )

    def validate_stability_membership_labels(
        y_target: np.ndarray,
        pos_membership: np.ndarray,
        neg_membership: np.ndarray,
        *,
        context: str,
    ) -> None:
        """
        Validate stability membership by label-at-index.

        Valid for both the ordinary biological layout and the interleaved
        stream-28 permutation-null layout. No fixed positive/negative index
        ranges are assumed.
        """
        y_target = np.asarray(y_target, dtype=int)
        pos_membership = np.asarray(pos_membership, dtype=int)
        neg_membership = np.asarray(neg_membership, dtype=int)

        if y_target.ndim != 1:
            raise CalibrationContractError(
                f"{context}: target labels must be one-dimensional"
            )

        if pos_membership.ndim != 1 or neg_membership.ndim != 1:
            raise CalibrationContractError(
                f"{context}: stability membership arrays must be one-dimensional"
            )

        if np.any(pos_membership < 0) or np.any(
            pos_membership >= len(y_target)
        ):
            raise CalibrationContractError(
                f"{context}: positive stability membership index out of bounds"
            )

        if np.any(neg_membership < 0) or np.any(
            neg_membership >= len(y_target)
        ):
            raise CalibrationContractError(
                f"{context}: negative stability membership index out of bounds"
            )

        if len(np.unique(pos_membership)) != len(pos_membership):
            raise CalibrationContractError(
                f"{context}: duplicate positive stability membership"
            )

        if len(np.unique(neg_membership)) != len(neg_membership):
            raise CalibrationContractError(
                f"{context}: duplicate negative stability membership"
            )

        if np.intersect1d(
            pos_membership,
            neg_membership,
        ).size != 0:
            raise CalibrationContractError(
                f"{context}: positive/negative stability memberships overlap"
            )

        if not np.all(y_target[pos_membership] == 1):
            raise CalibrationContractError(
                f"{context}: positive stability membership contains "
                "a row whose current label is not positive"
            )

        if not np.all(y_target[neg_membership] == 0):
            raise CalibrationContractError(
                f"{context}: negative stability membership contains "
                "a row whose current label is not negative"
            )


    def seedsequence_for_frozen_path(
        *,
        path_kind: str,
        c: int,
        target_n: int,
        stream_id: int,
    ) -> np.random.SeedSequence:
        """
        Route a stochastic address solely by frozen path identity.
        """
        if path_kind == "biological":
            return runner_seedsequence(
                c,
                target_n,
                stream_id,
            )

        if path_kind == "permutation_null":
            if int(target_n) != PERMUTATION_NULL_TARGET_N:
                raise CalibrationContractError(
                    "permutation-null downstream mechanics require N=139"
                )

            return permutation_null_seedsequence(
                c,
                stream_id,
            )

        raise CalibrationContractError(
            f"unknown frozen Phase-P path identity: {path_kind}"
        )


    def run_downstream_perturbation_mechanics(
        Xn: np.ndarray,
        yn_work: np.ndarray,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_eval: np.ndarray,
        y_eval: np.ndarray,
        *,
        c: int,
        target_n: int,
        path_kind: str,
        context: str,
    ) -> dict[str, object]:
        """
        Frozen streams 23-27 per-perturbation mechanics.

          23 — shared five-fold CV
          24 — Stage-A CV fits + child-45 final Stage-A refit
          25 — full-target-N Stage-B fit
          26 — independent stability subsample
          27 — stability fit

        Definition only while Phase-P remains hard-disabled.
        """
        Xn = np.asarray(Xn, dtype=float)
        yn_work = np.asarray(yn_work, dtype=int)
        X_train = np.asarray(X_train, dtype=float)
        y_train = np.asarray(y_train, dtype=int)
        X_eval = np.asarray(X_eval, dtype=float)
        y_eval = np.asarray(y_eval, dtype=int)

        if Xn.ndim != 2:
            raise CalibrationContractError(
                f"{context}: target-pool X must be two-dimensional"
            )

        if yn_work.shape != (2 * int(target_n),):
            raise CalibrationContractError(
                f"{context}: target-pool label shape inconsistent with N"
            )

        if Xn.shape[0] != len(yn_work):
            raise CalibrationContractError(
                f"{context}: target-pool row/label count mismatch"
            )

        if int(np.sum(yn_work == 1)) != int(target_n):
            raise CalibrationContractError(
                f"{context}: target pool does not contain exactly N positives"
            )

        if int(np.sum(yn_work == 0)) != int(target_n):
            raise CalibrationContractError(
                f"{context}: target pool does not contain exactly N negatives"
            )

        if X_train.shape[0] != len(y_train):
            raise CalibrationContractError(
                f"{context}: Stage-A training row/label count mismatch"
            )

        if X_eval.shape[0] != len(y_eval):
            raise CalibrationContractError(
                f"{context}: Stage-A evaluation row/label count mismatch"
            )

        # stream 23
        cv_ss = seedsequence_for_frozen_path(
            path_kind=path_kind,
            c=c,
            target_n=target_n,
            stream_id=STREAM_CV,
        )
        cv_seed = seedsequence_to_uint32(cv_ss)

        # stream 24
        stage_a_fit_ss = seedsequence_for_frozen_path(
            path_kind=path_kind,
            c=c,
            target_n=target_n,
            stream_id=STREAM_STAGE_A_FIT,
        )

        stage_a_fit_children = tuple(
            stage_a_fit_ss.spawn(STAGE_A_FIT_CHILD_COUNT)
        )

        if len(stage_a_fit_children) != STAGE_A_FIT_CHILD_COUNT:
            raise CalibrationContractError(
                f"{context}: Stage-A seed spawn count changed"
            )

        selection = select_C_R2(
            X_train,
            y_train,
            cv_seed=cv_seed,
            stage_a_fit_children=stage_a_fit_children,
            context=f"{context}:stage_a_cv",
        )

        selected_C = float(selection.selected_C)

        stage_a_final_seed = seedsequence_to_uint32(
            stage_a_fit_children[STAGE_A_FINAL_REFIT_CHILD]
        )

        stage_a_model = fit_probe_or_fail(
            X_train,
            y_train,
            C=selected_C,
            random_state=stage_a_final_seed,
            context=f"{context}:stage_a_final_refit",
        )

        stage_a_eval_score = np.asarray(
            stage_a_model.predict_proba(X_eval)[:, 1],
            dtype=float,
        )

        stage_a_eval_auroc = float(
            roc_auc_score(
                y_eval,
                stage_a_eval_score,
            )
        )

        # stream 25
        stage_b_ss = seedsequence_for_frozen_path(
            path_kind=path_kind,
            c=c,
            target_n=target_n,
            stream_id=STREAM_STAGE_B_FIT,
        )
        stage_b_seed = seedsequence_to_uint32(stage_b_ss)

        stage_b_model = fit_probe_or_fail(
            Xn,
            yn_work,
            C=selected_C,
            random_state=stage_b_seed,
            context=f"{context}:stage_b_full_target_n",
        )

        stage_b_coef = np.asarray(
            stage_b_model.coef_[0],
            dtype=float,
        )

        if stage_b_coef.ndim != 1:
            raise CalibrationContractError(
                f"{context}: Stage-B coefficient vector has wrong shape"
            )

        # stream 26
        stability_ss = seedsequence_for_frozen_path(
            path_kind=path_kind,
            c=c,
            target_n=target_n,
            stream_id=STREAM_STABILITY_SUBSAMPLE,
        )
        stability_rng = np.random.default_rng(stability_ss)

        (
            stability_indices,
            pos_membership,
            neg_membership,
            membership_sha256,
        ) = select_stability_subsample(
            yn_work,
            target_n=target_n,
            rng=stability_rng,
        )

        stability_indices = np.asarray(stability_indices, dtype=int)
        pos_membership = np.asarray(pos_membership, dtype=int)
        neg_membership = np.asarray(neg_membership, dtype=int)

        validate_stability_membership_labels(
            yn_work,
            pos_membership,
            neg_membership,
            context=f"{context}:stability_membership",
        )

        expected_stability_indices = np.concatenate(
            [
                pos_membership,
                neg_membership,
            ]
        )

        if not np.array_equal(
            stability_indices,
            expected_stability_indices,
        ):
            raise CalibrationContractError(
                f"{context}: inherited stability membership order changed"
            )

        # stream 27
        stability_fit_ss = seedsequence_for_frozen_path(
            path_kind=path_kind,
            c=c,
            target_n=target_n,
            stream_id=STREAM_STABILITY_FIT,
        )
        stability_fit_seed = seedsequence_to_uint32(
            stability_fit_ss
        )

        stability_model = fit_probe_or_fail(
            Xn[stability_indices],
            yn_work[stability_indices],
            C=selected_C,
            random_state=stability_fit_seed,
            context=f"{context}:stability_fit",
        )

        stability_coef = np.asarray(
            stability_model.coef_[0],
            dtype=float,
        )

        if stability_coef.shape != stage_b_coef.shape:
            raise CalibrationContractError(
                f"{context}: Stage-B/stability coefficient dimensions differ"
            )

        return {
            "selected_C": selected_C,
            "selection": selection,
            "stage_a_eval_auroc": stage_a_eval_auroc,
            "stage_a_model": stage_a_model,
            "stage_b_model": stage_b_model,
            "stage_b_coef": stage_b_coef,
            "stability_indices": stability_indices,
            "pos_membership": pos_membership,
            "neg_membership": neg_membership,
            "membership_sha256": membership_sha256,
            "stability_model": stability_model,
            "stability_coef": stability_coef,
        }


    def replay_permutation_null_stability_membership(
        X: np.ndarray,
        y: np.ndarray,
        *,
        c: int,
        original_yn_perm: np.ndarray,
        original_pos_membership: np.ndarray,
        original_neg_membership: np.ndarray,
        original_membership_sha256: str,
    ) -> dict[str, object]:
        """
        Exact null replay:

          stream 21
            -> stream 28
            -> exact row-level yn_perm equality
            -> stream 26 membership replay
        """
        original_yn_perm = np.asarray(
            original_yn_perm,
            dtype=int,
        )
        original_pos_membership = np.asarray(
            original_pos_membership,
            dtype=int,
        )
        original_neg_membership = np.asarray(
            original_neg_membership,
            dtype=int,
        )

        target_ss = permutation_null_seedsequence(
            c,
            STREAM_SUBSAMPLE,
        )
        target_rng = np.random.default_rng(target_ss)

        replay_Xn, replay_yn = select_target_n(
            X,
            y,
            target_n=PERMUTATION_NULL_TARGET_N,
            rng=target_rng,
        )

        permutation_ss = permutation_null_seedsequence(
            c,
            STREAM_LABEL_PERMUTATION,
        )
        permutation_rng = np.random.default_rng(
            permutation_ss
        )

        replay_perm = permutation_rng.permutation(
            len(replay_yn)
        )

        replay_yn_perm = np.asarray(
            replay_yn[replay_perm],
            dtype=int,
        )

        if replay_yn_perm.shape != original_yn_perm.shape:
            raise CalibrationContractError(
                "permutation-null replay label shape mismatch"
            )

        if not np.array_equal(
            replay_yn_perm,
            original_yn_perm,
        ):
            raise CalibrationContractError(
                "permutation-null replay did not reconstruct the exact "
                "row-level yn_perm state"
            )

        stability_ss = permutation_null_seedsequence(
            c,
            STREAM_STABILITY_SUBSAMPLE,
        )
        stability_rng = np.random.default_rng(
            stability_ss
        )

        (
            replay_stability_indices,
            replay_pos_membership,
            replay_neg_membership,
            replay_membership_sha256,
        ) = select_stability_subsample(
            replay_yn_perm,
            target_n=PERMUTATION_NULL_TARGET_N,
            rng=stability_rng,
        )

        replay_stability_indices = np.asarray(
            replay_stability_indices,
            dtype=int,
        )
        replay_pos_membership = np.asarray(
            replay_pos_membership,
            dtype=int,
        )
        replay_neg_membership = np.asarray(
            replay_neg_membership,
            dtype=int,
        )

        validate_stability_membership_labels(
            replay_yn_perm,
            replay_pos_membership,
            replay_neg_membership,
            context="permutation_null_replay",
        )

        if not np.array_equal(
            replay_pos_membership,
            original_pos_membership,
        ):
            raise CalibrationContractError(
                "permutation-null replay positive stability membership mismatch"
            )

        if not np.array_equal(
            replay_neg_membership,
            original_neg_membership,
        ):
            raise CalibrationContractError(
                "permutation-null replay negative stability membership mismatch"
            )

        if (
            str(replay_membership_sha256)
            != str(original_membership_sha256)
        ):
            raise CalibrationContractError(
                "permutation-null replay stability membership SHA mismatch"
            )

        return {
            "replay_Xn": replay_Xn,
            "replay_yn_perm": replay_yn_perm,
            "replay_stability_indices": replay_stability_indices,
            "replay_pos_membership": replay_pos_membership,
            "replay_neg_membership": replay_neg_membership,
            "replay_membership_sha256": replay_membership_sha256,
        }


    def run_biological_per_perturbation(
        X: np.ndarray,
        y: np.ndarray,
        *,
        c: int,
        target_n: int,
        context: str,
    ) -> dict[str, object]:
        """
        Frozen biological per-perturbation path:

          21 -> 22 -> 23 -> 24 -> 25 -> 26 -> 27
        """
        target_ss = runner_seedsequence(
            c,
            target_n,
            STREAM_SUBSAMPLE,
        )
        target_rng = np.random.default_rng(target_ss)

        Xn, yn = select_target_n(
            X,
            y,
            target_n=target_n,
            rng=target_rng,
        )

        stage_a_ss = runner_seedsequence(
            c,
            target_n,
            STREAM_STAGE_A_SPLIT,
        )
        stage_a_rng = np.random.default_rng(stage_a_ss)

        X_train, y_train, X_eval, y_eval = stage_a_split(
            Xn,
            yn,
            target_n=target_n,
            rng=stage_a_rng,
        )

        downstream = run_downstream_perturbation_mechanics(
            Xn,
            yn,
            X_train,
            y_train,
            X_eval,
            y_eval,
            c=c,
            target_n=target_n,
            path_kind="biological",
            context=context,
        )

        return {
            "Xn": Xn,
            "yn": yn,
            "X_train": X_train,
            "y_train": y_train,
            "X_eval": X_eval,
            "y_eval": y_eval,
            **downstream,
        }


    def run_permutation_null_per_perturbation(
        X: np.ndarray,
        y: np.ndarray,
        *,
        c: int,
        context: str,
    ) -> dict[str, object]:
        """
        Frozen permutation-null per-perturbation path:

          21 -> 28 -> 22 -> 23 -> 24 -> 25 -> 26 -> 27

        Exact stream-21 + stream-28 replay is then required before
        stream-26 membership replay comparison.
        """
        (
            Xn,
            yn_perm,
            X_train,
            y_train,
            X_eval,
            y_eval,
        ) = prepare_permutation_null_stage_a(
            X,
            y,
            c=c,
        )

        downstream = run_downstream_perturbation_mechanics(
            Xn,
            yn_perm,
            X_train,
            y_train,
            X_eval,
            y_eval,
            c=c,
            target_n=PERMUTATION_NULL_TARGET_N,
            path_kind="permutation_null",
            context=context,
        )

        replay = replay_permutation_null_stability_membership(
            X,
            y,
            c=c,
            original_yn_perm=yn_perm,
            original_pos_membership=downstream["pos_membership"],
            original_neg_membership=downstream["neg_membership"],
            original_membership_sha256=downstream["membership_sha256"],
        )

        return {
            "Xn": Xn,
            "yn_perm": yn_perm,
            "X_train": X_train,
            "y_train": y_train,
            "X_eval": X_eval,
            "y_eval": y_eval,
            **downstream,
            **replay,
        }


    # ──────────────────────────────────────────────────────────────────────
    # Hard-disabled Phase-P experiment-level orchestration core.
    #
    # These are definitions only. No function in this block is called at
    # this source freeze. The existing terminal PhasePContractError below
    # remains effective even if the outer gate is changed prematurely.
    #
    # Frozen Phase-E + baseline attachment is implemented below, but remains
    # unreachable while the top-level biological execution gate is False.
    # The attachment derives labels only from the authoritative Phase-E row
    # manifest and verifies all frozen artifact identities before returning
    # already-loaded immutable inputs to the orchestration boundary.
    # ──────────────────────────────────────────────────────────────────────

    ORCHESTRATION_OUTPUT_CONTRACT_SHA256 = (
        "5c62729c16c906faf0c158c17499524ee3a6eb79d938d26b1f88846e8fc7f348"
    )

    REPRESENTATION_ORDER = (
        "esm_layer_1",
        "esm_layer_9",
        "esm_layer_18",
        "esm_layer_24",
        "esm_layer_30",
        "esm_layer_33",
        "baseline_21d",
    )

    REPRESENTATION_TO_LAYER = {
        "esm_layer_1": 1,
        "esm_layer_9": 9,
        "esm_layer_18": 18,
        "esm_layer_24": 24,
        "esm_layer_30": 30,
        "esm_layer_33": 33,
        "baseline_21d": None,
    }

    MAIN_OUTPUT_FILENAME = "main_per_perturbation.csv"
    NULL_OUTPUT_FILENAME = "permutation_null_per_perturbation.csv"
    EXECUTION_MANIFEST_FILENAME = "execution_manifest.json"
    RESULT_FILENAME = "RESULT.md"

    MAIN_ATOMIC_KEY_FIELDS = (
        "biological_perturbation_id",
        "target_n",
        "representation",
    )

    NULL_ATOMIC_KEY_FIELDS = (
        "null_perturbation_id",
    )

    MAIN_OUTPUT_FIELDS = (
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

    NULL_OUTPUT_FIELDS = (
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

    def exact_support_from_coef(
        beta: np.ndarray,
    ) -> tuple[
        tuple[int, ...],
        tuple[tuple[int, int], ...],
    ]:
        """
        Frozen exact-zero support convention.

        A coefficient is selected iff beta_j != 0.0 exactly.
        Signed support stores (coordinate, sign), where sign is -1 or +1.
        """
        beta_arr = np.asarray(beta)

        if beta_arr.ndim == 2:
            if beta_arr.shape[0] != 1:
                raise PhasePContractError(
                    "Expected a binary-probe coefficient row with shape "
                    "(1, p)."
                )
            beta_arr = beta_arr[0]

        if beta_arr.ndim != 1:
            raise PhasePContractError(
                "Coefficient array must be one-dimensional after binary-row "
                "normalization."
            )

        selected = np.flatnonzero(beta_arr != 0.0)

        unsigned = tuple(
            int(j)
            for j in selected.tolist()
        )

        signed = tuple(
            (
                int(j),
                1 if float(beta_arr[j]) > 0.0 else -1,
            )
            for j in selected.tolist()
        )

        return unsigned, signed


    def jaccard_zero_empty(
        a: frozenset[object],
        b: frozenset[object],
    ) -> float:
        """
        Frozen Jaccard convention: Jaccard(empty, empty) = 0.
        """
        union = a | b

        if not union:
            return 0.0

        return float(
            len(a & b) / len(union)
        )


    def aggregate_cell_support_statistics(
        rows: list[dict[str, object]],
    ) -> dict[str, float]:
        """
        Frozen 100-perturbation cell-level support aggregation.

        I_stat:
            median pairwise unsigned-support Jaccard.

        G_stat:
            median pairwise signed-support Jaccard.

        Exactly choose(100, 2) = 4,950 unordered pairs are required.
        """
        if len(rows) != 100:
            raise PhasePContractError(
                "Support-cell aggregation requires exactly 100 perturbations."
            )

        unsigned_sets = []
        signed_sets = []

        for row in rows:
            unsigned_raw = row.get("stability_unsigned_support")
            signed_raw = row.get("stability_signed_support")

            if unsigned_raw is None or signed_raw is None:
                raise PhasePContractError(
                    "Support-cell row is missing exact stability support."
                )

            unsigned_sets.append(
                frozenset(
                    int(j)
                    for j in unsigned_raw
                )
            )

            signed_sets.append(
                frozenset(
                    (int(j), int(sign))
                    for j, sign in signed_raw
                )
            )

        I_pairs = []
        G_pairs = []

        for t in range(100):
            for u in range(t + 1, 100):
                I_pairs.append(
                    jaccard_zero_empty(
                        unsigned_sets[t],
                        unsigned_sets[u],
                    )
                )
                G_pairs.append(
                    jaccard_zero_empty(
                        signed_sets[t],
                        signed_sets[u],
                    )
                )

        if len(I_pairs) != 4950 or len(G_pairs) != 4950:
            raise PhasePContractError(
                "Expected exactly 4,950 unordered perturbation pairs."
            )

        I_stat = float(np.median(np.asarray(I_pairs, dtype=float)))
        G_stat = float(np.median(np.asarray(G_pairs, dtype=float)))

        if G_stat > I_stat + 1e-15:
            raise PhasePContractError(
                "Frozen invariant violated: G_stat > I_stat."
            )

        return {
            "I_stat": I_stat,
            "G_stat": G_stat,
        }


    def canonical_json_dumps(
        value: object,
    ) -> str:
        """
        Stable compact JSON serialization used only for persisted provenance
        and exact support identities.
        """
        import json as _json

        return _json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )


    def parse_persisted_support_json(
        row: dict[str, object],
    ) -> dict[str, object]:
        """
        Reconstruct exact stability support from persisted canonical JSON.
        """
        unsigned_text = row.get(
            "stability_unsigned_support_json"
        )
        signed_text = row.get(
            "stability_signed_support_json"
        )

        if (
            not isinstance(unsigned_text, str)
            or not isinstance(signed_text, str)
        ):
            raise PhasePContractError(
                "Persisted support JSON fields must be strings."
            )

        try:
            unsigned_raw = json.loads(
                unsigned_text
            )
            signed_raw = json.loads(
                signed_text
            )
        except Exception as exc:
            raise PhasePContractError(
                "Persisted support JSON is malformed."
            ) from exc

        if not isinstance(unsigned_raw, list):
            raise PhasePContractError(
                "Unsigned support JSON must decode to a list."
            )

        unsigned = []

        for value in unsigned_raw:
            if type(value) is not int:
                raise PhasePContractError(
                    "Unsigned support coordinates must be integers."
                )

            if value < 0:
                raise PhasePContractError(
                    "Unsigned support coordinate cannot be negative."
                )

            unsigned.append(
                int(value)
            )

        if unsigned != sorted(set(unsigned)):
            raise PhasePContractError(
                "Unsigned support coordinates must be unique and strictly "
                "increasing."
            )

        if not isinstance(signed_raw, list):
            raise PhasePContractError(
                "Signed support JSON must decode to a list."
            )

        signed = []

        for item in signed_raw:
            if (
                not isinstance(item, list)
                or len(item) != 2
            ):
                raise PhasePContractError(
                    "Each signed-support entry must be [coordinate, sign]."
                )

            coordinate, sign = item

            if type(coordinate) is not int:
                raise PhasePContractError(
                    "Signed-support coordinate must be an integer."
                )

            if type(sign) is not int or sign not in (-1, 1):
                raise PhasePContractError(
                    "Signed-support sign must be exactly -1 or +1."
                )

            signed.append(
                (
                    int(coordinate),
                    int(sign),
                )
            )

        signed_coordinates = [
            coordinate
            for coordinate, _sign in signed
        ]

        if signed_coordinates != unsigned:
            raise PhasePContractError(
                "Signed-support coordinates must exactly equal unsigned "
                "coordinates in the same order."
            )

        if unsigned_text != canonical_json_dumps(
            unsigned
        ):
            raise PhasePContractError(
                "Unsigned support JSON is not canonical."
            )

        if signed_text != canonical_json_dumps(
            [
                [coordinate, sign]
                for coordinate, sign in signed
            ]
        ):
            raise PhasePContractError(
                "Signed support JSON is not canonical."
            )

        return {
            "stability_unsigned_support": tuple(
                unsigned
            ),
            "stability_signed_support": tuple(
                signed
            ),
        }


    def aggregate_persisted_cell_support_statistics(
        rows: list[dict[str, object]],
    ) -> dict[str, float]:
        """
        Frozen persisted-row -> I_stat/G_stat aggregation path.
        """
        reconstructed = [
            parse_persisted_support_json(
                row
            )
            for row in rows
        ]

        return aggregate_cell_support_statistics(
            reconstructed
        )


    def validate_sha256_hex(
        value: object,
        *,
        field: str,
    ) -> str:
        if not isinstance(value, str):
            raise PhasePContractError(
                f"{field} must be a SHA-256 string."
            )

        if (
            len(value) != 64
            or value != value.lower()
            or any(
                ch not in "0123456789abcdef"
                for ch in value
            )
        ):
            raise PhasePContractError(
                f"{field} is not canonical lowercase SHA-256 hex."
            )

        return value


    def parse_checkpoint_int(
        value: object,
        *,
        field: str,
    ) -> int:
        if not isinstance(value, str):
            raise PhasePContractError(
                f"Checkpoint field {field} must be text."
            )

        try:
            parsed = int(value)
        except Exception as exc:
            raise PhasePContractError(
                f"Checkpoint field {field} is not an integer."
            ) from exc

        if str(parsed) != value:
            raise PhasePContractError(
                f"Checkpoint integer field {field} is not canonical."
            )

        return parsed


    def parse_checkpoint_float(
        value: object,
        *,
        field: str,
    ) -> float:
        if not isinstance(value, str):
            raise PhasePContractError(
                f"Checkpoint field {field} must be text."
            )

        try:
            parsed = float(value)
        except Exception as exc:
            raise PhasePContractError(
                f"Checkpoint field {field} is not numeric."
            ) from exc

        if not math.isfinite(parsed):
            raise PhasePContractError(
                f"Checkpoint field {field} is non-finite."
            )

        return parsed


    def validate_persisted_scientific_row(
        row: dict[str, object],
        *,
        null_path: bool,
    ) -> None:
        """
        Validate a persisted row before its atomic key counts as completed.
        """
        if null_path:
            perturbation_id = parse_checkpoint_int(
                row["null_perturbation_id"],
                field="null_perturbation_id",
            )

            if not (
                PERMUTATION_NULL_SEED_START
                <= perturbation_id
                <= PERMUTATION_NULL_SEED_END
            ):
                raise PhasePContractError(
                    "Null perturbation id outside frozen namespace."
                )

            target_n = parse_checkpoint_int(
                row["target_n"],
                field="target_n",
            )

            if target_n != PERMUTATION_NULL_TARGET_N:
                raise PhasePContractError(
                    "Persisted null target_n must equal 139."
                )

            representation = row[
                "representation"
            ]

            if representation != "esm_layer_18":
                raise PhasePContractError(
                    "Persisted null representation must be esm_layer_18."
                )

        else:
            perturbation_id = parse_checkpoint_int(
                row["biological_perturbation_id"],
                field="biological_perturbation_id",
            )

            if not (
                MAIN_BIOLOGICAL_SEED_START
                <= perturbation_id
                <= MAIN_BIOLOGICAL_SEED_END
            ):
                raise PhasePContractError(
                    "Biological perturbation id outside frozen namespace."
                )

            target_n = parse_checkpoint_int(
                row["target_n"],
                field="target_n",
            )

            if target_n not in TARGET_N_VALUES:
                raise PhasePContractError(
                    "Persisted main target_n outside frozen census."
                )

            representation = row[
                "representation"
            ]

            if representation not in REPRESENTATION_ORDER:
                raise PhasePContractError(
                    "Persisted representation outside frozen census."
                )

        auroc = parse_checkpoint_float(
            row["stage_a_eval_auroc"],
            field="stage_a_eval_auroc",
        )

        if not 0.0 <= auroc <= 1.0:
            raise PhasePContractError(
                "Persisted AUROC outside [0, 1]."
            )

        selected_C = parse_checkpoint_float(
            row["selected_C"],
            field="selected_C",
        )

        if selected_C not in C_GRID:
            raise PhasePContractError(
                "Persisted selected_C outside exact frozen C grid."
            )

        K_t_full = parse_checkpoint_int(
            row["K_t_full"],
            field="K_t_full",
        )

        K_t_stab = parse_checkpoint_int(
            row["K_t_stab"],
            field="K_t_stab",
        )

        width = (
            BASELINE_DIM
            if representation == "baseline_21d"
            else ESM_WIDTH
        )

        if not 0 <= K_t_full <= width:
            raise PhasePContractError(
                "Persisted K_t_full outside representation width."
            )

        if not 0 <= K_t_stab <= width:
            raise PhasePContractError(
                "Persisted K_t_stab outside representation width."
            )

        support = parse_persisted_support_json(
            row
        )

        unsigned = support[
            "stability_unsigned_support"
        ]

        if len(unsigned) != K_t_stab:
            raise PhasePContractError(
                "K_t_stab does not equal persisted support size."
            )

        if any(
            coordinate >= width
            for coordinate in unsigned
        ):
            raise PhasePContractError(
                "Persisted support coordinate exceeds representation width."
            )

        membership_sha = validate_sha256_hex(
            row["membership_sha256"],
            field="membership_sha256",
        )

        if null_path:
            replay_sha = validate_sha256_hex(
                row["replay_membership_sha256"],
                field="replay_membership_sha256",
            )

            if replay_sha != membership_sha:
                raise PhasePContractError(
                    "Null replay membership SHA does not match original."
                )

            if row["replay_success"] != "True":
                raise PhasePContractError(
                    "Null replay_success must be exactly True."
                )


    def validate_persisted_main_row(
        row: dict[str, object],
    ) -> None:
        validate_persisted_scientific_row(
            row,
            null_path=False,
        )


    def validate_persisted_null_row(
        row: dict[str, object],
    ) -> None:
        validate_persisted_scientific_row(
            row,
            null_path=True,
        )

    def csv_safe_row(
        row: dict[str, object],
        fieldnames: tuple[str, ...],
    ) -> dict[str, object]:
        """
        Require exact output schema and convert values to CSV-safe scalars.
        """
        if set(row) != set(fieldnames):
            missing = sorted(set(fieldnames) - set(row))
            extra = sorted(set(row) - set(fieldnames))

            raise PhasePContractError(
                "Output row schema mismatch. "
                f"missing={missing!r}; extra={extra!r}"
            )

        out = {}

        for field in fieldnames:
            value = row[field]

            if isinstance(value, np.generic):
                value = value.item()

            if isinstance(value, float) and not math.isfinite(value):
                raise PhasePContractError(
                    f"Non-finite persisted float in field {field!r}."
                )

            out[field] = value

        return out


    def atomic_key_from_row(
        row: dict[str, object],
        key_fields: tuple[str, ...],
    ) -> tuple[object, ...]:
        return tuple(
            row[field]
            for field in key_fields
        )


    def read_existing_csv_rows_exact(
        path: Path,
        *,
        fieldnames: tuple[str, ...],
        key_fields: tuple[str, ...],
        semantic_validator=None,
    ) -> tuple[
        list[dict[str, str]],
        set[tuple[object, ...]],
    ]:
        """
        Strict checkpoint reader.

        A row's atomic key counts as completed only AFTER structural and
        scientific semantic validation succeed.
        """
        import csv as _csv

        if not path.exists():
            return [], set()

        if not path.is_file():
            raise PhasePContractError(
                f"Checkpoint path is not a regular file: {path}"
            )

        rows = []
        keys = set()

        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            reader = _csv.DictReader(
                handle
            )

            if tuple(reader.fieldnames or ()) != fieldnames:
                raise PhasePContractError(
                    f"Checkpoint header mismatch for {path.name}."
                )

            for physical_row_number, row in enumerate(
                reader,
                start=2,
            ):
                if None in row:
                    raise PhasePContractError(
                        f"Malformed checkpoint row {physical_row_number} "
                        f"in {path.name}."
                    )

                if set(row) != set(fieldnames):
                    raise PhasePContractError(
                        f"Checkpoint row schema mismatch at physical row "
                        f"{physical_row_number} in {path.name}."
                    )

                if semantic_validator is not None:
                    semantic_validator(
                        row
                    )

                key = atomic_key_from_row(
                    row,
                    key_fields,
                )

                if key in keys:
                    raise PhasePContractError(
                        f"Duplicate checkpoint key {key!r} in {path.name}."
                    )

                keys.add(
                    key
                )
                rows.append(
                    row
                )

        return rows, keys


    def append_csv_row_fsync(
        path: Path,
        *,
        fieldnames: tuple[str, ...],
        row: dict[str, object],
    ) -> None:
        """
        Append exactly one completed row, then flush and fsync.

        This function is never called at the current hard-disabled freeze.
        """
        import csv as _csv
        import os as _os

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        new_file = not path.exists()

        clean = csv_safe_row(
            row,
            fieldnames,
        )

        with path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = _csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                extrasaction="raise",
            )

            if new_file:
                writer.writeheader()

            writer.writerow(clean)
            handle.flush()
            _os.fsync(handle.fileno())


    def write_manifest_once_or_validate(
        path: Path,
        manifest: dict[str, object],
    ) -> None:
        """
        Create execution_manifest.json once, or require exact byte-equivalent
        canonical JSON on resume.

        No provenance adaptation is permitted.
        """
        import os as _os

        canonical = (
            canonical_json_dumps(manifest)
            + "\n"
        )

        if path.exists():
            existing = path.read_text(
                encoding="utf-8",
            )

            if existing != canonical:
                raise PhasePContractError(
                    "Execution-manifest provenance mismatch on resume."
                )

            return

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "x",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(canonical)
            handle.flush()
            _os.fsync(handle.fileno())


    def expected_main_keys() -> tuple[
        tuple[int, int, str],
        ...,
    ]:
        keys = []

        for c in range(
            MAIN_BIOLOGICAL_SEED_START,
            MAIN_BIOLOGICAL_SEED_END + 1,
        ):
            for target_n in TARGET_N_VALUES:
                for representation in REPRESENTATION_ORDER:
                    keys.append(
                        (
                            c,
                            target_n,
                            representation,
                        )
                    )

        if len(keys) != 2100:
            raise PhasePContractError(
                "Frozen main census did not produce exactly 2,100 keys."
            )

        return tuple(keys)


    def expected_null_keys() -> tuple[
        tuple[int],
        ...,
    ]:
        keys = tuple(
            (c,)
            for c in range(
                PERMUTATION_NULL_SEED_START,
                PERMUTATION_NULL_SEED_END + 1,
            )
        )

        if len(keys) != 100:
            raise PhasePContractError(
                "Frozen null census did not produce exactly 100 keys."
            )

        return keys


    def load_json_object_exact(
        path: Path,
        *,
        expected_sha256: str,
        label: str,
    ) -> dict[str, object]:
        """
        Hash-verify and parse one frozen JSON provenance object.
        """
        if not path.is_file():
            raise PhasePContractError(
                f"Missing frozen {label}: {path}"
            )

        got_sha = sha256_file(path)

        if got_sha != expected_sha256:
            raise PhasePContractError(
                f"Frozen {label} SHA-256 mismatch."
            )

        try:
            obj = json.loads(
                path.read_text(encoding="utf-8")
            )
        except Exception as exc:
            raise PhasePContractError(
                f"Frozen {label} is not valid JSON."
            ) from exc

        if not isinstance(obj, dict):
            raise PhasePContractError(
                f"Frozen {label} must be a JSON object."
            )

        return obj


    def load_phase_e_rows_and_labels(
        path: Path,
    ) -> tuple[list[dict[str, str]], np.ndarray]:
        """
        Load the frozen authoritative 278-row Phase-E manifest and derive y.

        Label authority:
          positive -> 1
          negative -> 0

        No label source other than class_name in this manifest is permitted.
        """
        if not path.is_file():
            raise PhasePContractError(
                f"Missing frozen Phase-E row manifest: {path}"
            )

        if sha256_file(path) != PHASE_E_ROWS_SHA256:
            raise PhasePContractError(
                "Frozen Phase-E row-manifest SHA-256 mismatch."
            )

        import csv
        import io

        raw = path.read_text(encoding="utf-8")

        reader = csv.DictReader(
            io.StringIO(raw),
            delimiter="\t",
        )

        expected_fields = [
            "matrix_row",
            "class_name",
            "identifier",
            "retrieved_length",
            "sequence_sha256",
        ]

        if reader.fieldnames != expected_fields:
            raise PhasePContractError(
                "Frozen Phase-E row-manifest schema mismatch."
            )

        rows = list(reader)

        if len(rows) != N_DISCOVERY_TOTAL:
            raise PhasePContractError(
                "Frozen Phase-E row manifest must contain exactly 278 rows."
            )

        labels = []

        for expected_row, row in enumerate(rows):
            try:
                matrix_row = int(row["matrix_row"])
            except Exception as exc:
                raise PhasePContractError(
                    "Invalid matrix_row in frozen Phase-E manifest."
                ) from exc

            if matrix_row != expected_row:
                raise PhasePContractError(
                    "Frozen Phase-E matrix_row order must be exactly 0..277."
                )

            class_name = row["class_name"]

            if class_name == "positive":
                label_value = 1
            elif class_name == "negative":
                label_value = 0
            else:
                raise PhasePContractError(
                    "Frozen Phase-E manifest contains unknown class_name."
                )

            identifier = row["identifier"]

            if not identifier:
                raise PhasePContractError(
                    "Frozen Phase-E manifest contains empty identifier."
                )

            try:
                retrieved_length = int(
                    row["retrieved_length"]
                )
            except Exception as exc:
                raise PhasePContractError(
                    "Invalid retrieved_length in frozen Phase-E manifest."
                ) from exc

            if retrieved_length <= 0:
                raise PhasePContractError(
                    "Frozen Phase-E manifest contains non-positive length."
                )

            sequence_sha = row["sequence_sha256"]

            if (
                len(sequence_sha) != 64
                or any(
                    ch not in "0123456789abcdef"
                    for ch in sequence_sha
                )
            ):
                raise PhasePContractError(
                    "Frozen Phase-E manifest contains invalid sequence SHA-256."
                )

            labels.append(label_value)

        y = np.asarray(
            labels,
            dtype=np.int64,
        )

        unique, counts = np.unique(
            y,
            return_counts=True,
        )

        if (
            unique.tolist() != [0, 1]
            or counts.tolist() != [139, 139]
        ):
            raise PhasePContractError(
                "Manifest-derived biological labels are not exactly "
                "139 negatives and 139 positives."
            )

        y.setflags(write=False)

        return rows, y


    def load_frozen_npy_exact(
        path: Path,
        *,
        expected_sha256: str,
        expected_shape: tuple[int, int],
        label: str,
    ) -> np.ndarray:
        """
        Hash-verify then load one frozen NumPy matrix without mutation.
        """
        if not path.is_file():
            raise PhasePContractError(
                f"Missing frozen {label}: {path}"
            )

        if sha256_file(path) != expected_sha256:
            raise PhasePContractError(
                f"Frozen {label} SHA-256 mismatch."
            )

        try:
            arr = np.load(
                path,
                allow_pickle=False,
            )
        except Exception as exc:
            raise PhasePContractError(
                f"Could not load frozen {label}."
            ) from exc

        if arr.shape != expected_shape:
            raise PhasePContractError(
                f"Frozen {label} has unexpected shape {arr.shape!r}."
            )

        if arr.dtype != np.dtype("float32"):
            raise PhasePContractError(
                f"Frozen {label} must have dtype float32."
            )

        if not np.all(np.isfinite(arr)):
            raise PhasePContractError(
                f"Frozen {label} contains non-finite values."
            )

        arr.setflags(write=False)

        return arr


    def attach_frozen_phase_p_inputs(
    ) -> tuple[
        dict[str, np.ndarray],
        np.ndarray,
        dict[str, object],
    ]:
        """
        Attach the frozen Phase-E matrices, frozen 21-D baseline, and
        manifest-derived biological labels.

        This function performs no fitting, CV, AUROC, support computation,
        RNG construction, or seed access.
        """
        phase_e_dir = REPO_ROOT / PHASE_E_OUTPUT_REL

        rows_path = (
            phase_e_dir
            / PHASE_E_ROWS_FILENAME
        )

        phase_e_provenance_path = (
            phase_e_dir
            / PHASE_E_PROVENANCE_FILENAME
        )

        baseline_path = (
            REPO_ROOT
            / BASELINE_21D_REL
        )

        baseline_provenance_path = (
            REPO_ROOT
            / BASELINE_21D_PROVENANCE_REL
        )

        rows, y = load_phase_e_rows_and_labels(
            rows_path
        )

        phase_e_provenance = load_json_object_exact(
            phase_e_provenance_path,
            expected_sha256=PHASE_E_PROVENANCE_SHA256,
            label="Phase-E provenance",
        )

        baseline_provenance = load_json_object_exact(
            baseline_provenance_path,
            expected_sha256=BASELINE_21D_PROVENANCE_SHA256,
            label="baseline provenance",
        )

        # Cross-check frozen provenance statements against the already
        # hash-authorized attachment contract.
        if phase_e_provenance.get("expected_rows") != N_DISCOVERY_TOTAL:
            raise PhasePContractError(
                "Phase-E provenance expected_rows mismatch."
            )

        if phase_e_provenance.get("discovery_positive") != 139:
            raise PhasePContractError(
                "Phase-E provenance positive census mismatch."
            )

        if phase_e_provenance.get("discovery_negative") != 139:
            raise PhasePContractError(
                "Phase-E provenance negative census mismatch."
            )

        if phase_e_provenance.get("hidden_width") != ESM_WIDTH:
            raise PhasePContractError(
                "Phase-E provenance hidden width mismatch."
            )

        if tuple(
            phase_e_provenance.get("layers", [])
        ) != LAYERS:
            raise PhasePContractError(
                "Phase-E provenance layer order mismatch."
            )

        rows_manifest_obj = phase_e_provenance.get(
            "rows_manifest"
        )

        if not isinstance(rows_manifest_obj, dict):
            raise PhasePContractError(
                "Phase-E provenance rows_manifest missing."
            )

        if (
            rows_manifest_obj.get("sha256")
            != PHASE_E_ROWS_SHA256
        ):
            raise PhasePContractError(
                "Phase-E provenance row-manifest identity mismatch."
            )

        artifact_obj = baseline_provenance.get(
            "artifact"
        )

        if not isinstance(artifact_obj, dict):
            raise PhasePContractError(
                "Baseline provenance artifact object missing."
            )

        if artifact_obj.get("sha256") != BASELINE_21D_SHA256:
            raise PhasePContractError(
                "Baseline provenance artifact SHA mismatch."
            )

        if artifact_obj.get("shape") != [
            N_DISCOVERY_TOTAL,
            BASELINE_DIM,
        ]:
            raise PhasePContractError(
                "Baseline provenance shape mismatch."
            )

        label_authority = baseline_provenance.get(
            "label_authority"
        )

        if not isinstance(label_authority, dict):
            raise PhasePContractError(
                "Baseline provenance label authority missing."
            )

        if label_authority.get("source") != (
            "authoritative matrix manifest class_name"
        ):
            raise PhasePContractError(
                "Baseline provenance label authority changed."
            )

        if label_authority.get("mapping") != {
            "negative": 0,
            "positive": 1,
        }:
            raise PhasePContractError(
                "Baseline provenance label mapping changed."
            )

        correspondence = baseline_provenance.get(
            "correspondence_proof"
        )

        if not isinstance(correspondence, dict):
            raise PhasePContractError(
                "Baseline provenance correspondence proof missing."
            )

        if correspondence.get("passed") is not True:
            raise PhasePContractError(
                "Baseline row-correspondence proof is not PASS."
            )

        if correspondence.get("rows_checked") != N_DISCOVERY_TOTAL:
            raise PhasePContractError(
                "Baseline correspondence row count mismatch."
            )

        if correspondence.get(
            "matrix_row_exact_0_to_277"
        ) is not True:
            raise PhasePContractError(
                "Baseline matrix-row correspondence not exact."
            )

        representations: dict[str, np.ndarray] = {}

        for layer in LAYERS:
            representation = f"esm_layer_{layer}"

            matrix_path = (
                phase_e_dir
                / f"raw_esm_layer_{layer}.npy"
            )

            representations[representation] = (
                load_frozen_npy_exact(
                    matrix_path,
                    expected_sha256=PHASE_E_MATRIX_SHA256[layer],
                    expected_shape=(
                        N_DISCOVERY_TOTAL,
                        ESM_WIDTH,
                    ),
                    label=f"Phase-E layer-{layer} matrix",
                )
            )

        representations["baseline_21d"] = (
            load_frozen_npy_exact(
                baseline_path,
                expected_sha256=BASELINE_21D_SHA256,
                expected_shape=(
                    N_DISCOVERY_TOTAL,
                    BASELINE_DIM,
                ),
                label="21-D baseline matrix",
            )
        )

        if tuple(representations.keys()) != REPRESENTATION_ORDER:
            raise PhasePContractError(
                "Attachment representation order mismatch."
            )

        validate_loaded_phase_p_inputs(
            representations,
            y,
        )

        input_provenance = {
            "phase_e_rows": {
                "path": str(
                    Path(PHASE_E_OUTPUT_REL)
                    / PHASE_E_ROWS_FILENAME
                ),
                "sha256": PHASE_E_ROWS_SHA256,
                "rows": len(rows),
                "label_authority": "class_name",
                "label_mapping": {
                    "negative": 0,
                    "positive": 1,
                },
            },
            "phase_e_provenance": {
                "path": str(
                    Path(PHASE_E_OUTPUT_REL)
                    / PHASE_E_PROVENANCE_FILENAME
                ),
                "sha256": PHASE_E_PROVENANCE_SHA256,
            },
            "phase_e_matrices": {
                f"esm_layer_{layer}": {
                    "path": str(
                        Path(PHASE_E_OUTPUT_REL)
                        / f"raw_esm_layer_{layer}.npy"
                    ),
                    "sha256": PHASE_E_MATRIX_SHA256[layer],
                    "shape": [
                        N_DISCOVERY_TOTAL,
                        ESM_WIDTH,
                    ],
                    "dtype": "float32",
                }
                for layer in LAYERS
            },
            "baseline_21d": {
                "path": BASELINE_21D_REL,
                "sha256": BASELINE_21D_SHA256,
                "provenance_path": BASELINE_21D_PROVENANCE_REL,
                "provenance_sha256": (
                    BASELINE_21D_PROVENANCE_SHA256
                ),
                "shape": [
                    N_DISCOVERY_TOTAL,
                    BASELINE_DIM,
                ],
                "dtype": "float32",
            },
        }

        return (
            representations,
            y,
            input_provenance,
        )


    def validate_loaded_phase_p_inputs(
        representations: dict[str, np.ndarray],
        y: np.ndarray,
    ) -> None:
        """
        Validate already-loaded immutable Phase-P inputs.

        Loading/construction itself is intentionally outside this source patch.
        """
        if tuple(representations.keys()) != REPRESENTATION_ORDER:
            raise PhasePContractError(
                "Loaded representation order does not equal the frozen "
                "canonical order."
            )

        y_arr = np.asarray(y)

        if y_arr.shape != (N_DISCOVERY_TOTAL,):
            raise PhasePContractError(
                "Frozen biological label vector must have shape (278,)."
            )

        if not np.all(np.isfinite(y_arr)):
            raise PhasePContractError(
                "Biological label vector contains non-finite values."
            )

        unique, counts = np.unique(
            y_arr,
            return_counts=True,
        )

        if (
            unique.tolist() != [0, 1]
            or counts.tolist() != [139, 139]
        ):
            raise PhasePContractError(
                "Frozen biological labels must contain exactly "
                "139 negatives and 139 positives."
            )

        for representation in REPRESENTATION_ORDER:
            X = np.asarray(
                representations[representation]
            )

            expected_width = (
                BASELINE_DIM
                if representation == "baseline_21d"
                else ESM_WIDTH
            )

            if X.shape != (
                N_DISCOVERY_TOTAL,
                expected_width,
            ):
                raise PhasePContractError(
                    f"{representation} has unexpected shape {X.shape!r}."
                )

            if not np.all(np.isfinite(X)):
                raise PhasePContractError(
                    f"{representation} contains non-finite values."
                )


    def perturbation_result_to_persisted_row(
        result: dict[str, object],
        *,
        perturbation_id: int,
        target_n: int,
        representation: str,
        null_path: bool,
    ) -> dict[str, object]:
        """
        Convert one frozen wrapper result into the exact persisted CSV row.

        Persisted support JSON is the authoritative post-row support record.
        """
        full_unsigned, _full_signed = exact_support_from_coef(
            np.asarray(result["stage_b_coef"])
        )

        stab_unsigned, stab_signed = exact_support_from_coef(
            np.asarray(result["stability_coef"])
        )

        base = {
            "target_n": int(target_n),
            "representation": representation,
            "stage_a_eval_auroc": float(
                result["stage_a_eval_auroc"]
            ),
            "selected_C": float(
                result["selected_C"]
            ),
            "K_t_full": int(
                len(full_unsigned)
            ),
            "K_t_stab": int(
                len(stab_unsigned)
            ),
            "stability_unsigned_support_json": canonical_json_dumps(
                list(stab_unsigned)
            ),
            "stability_signed_support_json": canonical_json_dumps(
                [
                    [j, sign]
                    for j, sign in stab_signed
                ]
            ),
            "membership_sha256": str(
                result["membership_sha256"]
            ),
        }

        if null_path:
            replay_sha = str(
                result["replay_membership_sha256"]
            )
            original_sha = str(
                result["membership_sha256"]
            )

            if replay_sha != original_sha:
                raise PhasePContractError(
                    "Permutation-null stability-membership replay SHA "
                    "does not match original SHA."
                )

            return {
                "null_perturbation_id": int(
                    perturbation_id
                ),
                **base,
                "replay_membership_sha256": replay_sha,
                "replay_success": True,
            }

        return {
            "biological_perturbation_id": int(
                perturbation_id
            ),
            **base,
        }


    def run_main_sweep_from_loaded_inputs(
        representations: dict[str, np.ndarray],
        y: np.ndarray,
        *,
        output_csv: Path,
    ) -> None:
        """
        Frozen 100 × 3 × 7 main sweep from already-loaded inputs.

        Existing rows are never rerun or repaired. A resumed key is accepted
        only after strict full-row semantic validation.
        """
        validate_loaded_phase_p_inputs(
            representations,
            y,
        )

        _existing_rows, existing_raw_keys = read_existing_csv_rows_exact(
            output_csv,
            fieldnames=MAIN_OUTPUT_FIELDS,
            key_fields=MAIN_ATOMIC_KEY_FIELDS,
            semantic_validator=validate_persisted_main_row,
        )

        existing_keys = set()

        for raw_key in existing_raw_keys:
            try:
                normalized = (
                    int(raw_key[0]),
                    int(raw_key[1]),
                    str(raw_key[2]),
                )
            except Exception as exc:
                raise PhasePContractError(
                    "Malformed main checkpoint key."
                ) from exc

            existing_keys.add(
                normalized
            )

        expected = set(
            expected_main_keys()
        )

        unexpected = (
            existing_keys - expected
        )

        if unexpected:
            raise PhasePContractError(
                "Unexpected atomic key(s) in main checkpoint: "
                f"{sorted(unexpected)!r}"
            )

        for c in range(
            MAIN_BIOLOGICAL_SEED_START,
            MAIN_BIOLOGICAL_SEED_END + 1,
        ):
            for target_n in TARGET_N_VALUES:
                for representation in REPRESENTATION_ORDER:
                    key = (
                        c,
                        target_n,
                        representation,
                    )

                    if key in existing_keys:
                        continue

                    X = representations[
                        representation
                    ]

                    context = (
                        "phase_p_main:"
                        f"c={c}:"
                        f"N={target_n}:"
                        f"representation={representation}"
                    )

                    result = run_biological_per_perturbation(
                        X,
                        y,
                        c=c,
                        target_n=target_n,
                        context=context,
                    )

                    persisted = perturbation_result_to_persisted_row(
                        result,
                        perturbation_id=c,
                        target_n=target_n,
                        representation=representation,
                        null_path=False,
                    )

                    append_csv_row_fsync(
                        output_csv,
                        fieldnames=MAIN_OUTPUT_FIELDS,
                        row=persisted,
                    )

                    existing_keys.add(
                        key
                    )

        if existing_keys != expected:
            missing = sorted(
                expected - existing_keys
            )

            raise PhasePContractError(
                "Main sweep did not close at the exact 2,100-row census. "
                f"missing={missing[:10]!r}"
            )


    def run_null_sweep_from_loaded_inputs(
        representations: dict[str, np.ndarray],
        y: np.ndarray,
        *,
        output_csv: Path,
    ) -> None:
        """
        Frozen 100-row layer-18, N=139 descriptive permutation-null sweep.

        Existing rows count as completed only after strict semantic validation.
        """
        validate_loaded_phase_p_inputs(
            representations,
            y,
        )

        _existing_rows, existing_raw_keys = read_existing_csv_rows_exact(
            output_csv,
            fieldnames=NULL_OUTPUT_FIELDS,
            key_fields=NULL_ATOMIC_KEY_FIELDS,
            semantic_validator=validate_persisted_null_row,
        )

        existing_keys = set()

        for raw_key in existing_raw_keys:
            try:
                normalized = (
                    int(raw_key[0]),
                )
            except Exception as exc:
                raise PhasePContractError(
                    "Malformed null checkpoint key."
                ) from exc

            existing_keys.add(
                normalized
            )

        expected = set(
            expected_null_keys()
        )

        unexpected = (
            existing_keys - expected
        )

        if unexpected:
            raise PhasePContractError(
                "Unexpected atomic key(s) in null checkpoint: "
                f"{sorted(unexpected)!r}"
            )

        X = representations[
            "esm_layer_18"
        ]

        for c in range(
            PERMUTATION_NULL_SEED_START,
            PERMUTATION_NULL_SEED_END + 1,
        ):
            key = (
                c,
            )

            if key in existing_keys:
                continue

            context = (
                "phase_p_permutation_null:"
                f"c={c}:"
                "N=139:"
                "representation=esm_layer_18"
            )

            result = run_permutation_null_per_perturbation(
                X,
                y,
                c=c,
                context=context,
            )

            persisted = perturbation_result_to_persisted_row(
                result,
                perturbation_id=c,
                target_n=PERMUTATION_NULL_TARGET_N,
                representation="esm_layer_18",
                null_path=True,
            )

            append_csv_row_fsync(
                output_csv,
                fieldnames=NULL_OUTPUT_FIELDS,
                row=persisted,
            )

            existing_keys.add(
                key
            )

        if existing_keys != expected:
            missing = sorted(
                expected - existing_keys
            )

            raise PhasePContractError(
                "Null sweep did not close at the exact 100-row census. "
                f"missing={missing[:10]!r}"
            )


    def paired_raw_minus_baseline_auroc(
        rows: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        """
        Derive paired raw-ESM-minus-baseline AUROC only from persisted,
        same-perturbation / same-target-N rows.

        No unpaired replacement is permitted.
        """
        lookup = {}

        for row in rows:
            key = (
                int(row["biological_perturbation_id"]),
                int(row["target_n"]),
                str(row["representation"]),
            )

            if key in lookup:
                raise PhasePContractError(
                    f"Duplicate main result key during paired derivation: "
                    f"{key!r}"
                )

            lookup[key] = row

        derived = []

        for c in range(
            MAIN_BIOLOGICAL_SEED_START,
            MAIN_BIOLOGICAL_SEED_END + 1,
        ):
            for target_n in TARGET_N_VALUES:
                baseline_key = (
                    c,
                    target_n,
                    "baseline_21d",
                )

                if baseline_key not in lookup:
                    raise PhasePContractError(
                        "Paired baseline row missing."
                    )

                baseline_auroc = float(
                    lookup[baseline_key][
                        "stage_a_eval_auroc"
                    ]
                )

                for representation in REPRESENTATION_ORDER[:-1]:
                    raw_key = (
                        c,
                        target_n,
                        representation,
                    )

                    if raw_key not in lookup:
                        raise PhasePContractError(
                            "Paired raw-ESM row missing."
                        )

                    raw_auroc = float(
                        lookup[raw_key][
                            "stage_a_eval_auroc"
                        ]
                    )

                    derived.append(
                        {
                            "biological_perturbation_id": c,
                            "target_n": target_n,
                            "representation": representation,
                            "raw_auroc": raw_auroc,
                            "baseline_auroc": baseline_auroc,
                            "delta_raw_minus_baseline_auroc": (
                                raw_auroc
                                - baseline_auroc
                            ),
                        }
                    )

        if len(derived) != 1800:
            raise PhasePContractError(
                "Expected exactly 1,800 paired raw-minus-baseline deltas."
            )

        return derived


    def build_phase_p_execution_manifest(
        *,
        input_provenance: dict[str, object],
    ) -> dict[str, object]:
        """
        Build the exact prospective execution manifest from externally audited
        immutable input provenance.

        No input provenance is inferred here.
        """
        return {
            "orchestration_output_contract_sha256": (
                ORCHESTRATION_OUTPUT_CONTRACT_SHA256
            ),
            "phase_p_inheritance_contract_sha256": (
                PHASE_P_INHERITANCE_CONTRACT_SHA256
            ),
            "main_biological_seed_authorization_sha256": (
                MAIN_BIOLOGICAL_SEED_AUTHORIZATION_SHA256
            ),
            "biological_seed_derivation_spec_sha256": (
                BIOLOGICAL_SEED_DERIVATION_SPEC_SHA256
            ),
            "authoritative_corrected_mechanics_sha256": (
                AUTHORITATIVE_CORRECTED_MECHANICS_SHA256
            ),
            "representation_order": list(
                REPRESENTATION_ORDER
            ),
            "target_n_values": list(
                TARGET_N_VALUES
            ),
            "main_perturbation_range": [
                MAIN_BIOLOGICAL_SEED_START,
                MAIN_BIOLOGICAL_SEED_END,
            ],
            "null_perturbation_range": [
                PERMUTATION_NULL_SEED_START,
                PERMUTATION_NULL_SEED_END,
            ],
            "null_target_n": (
                PERMUTATION_NULL_TARGET_N
            ),
            "c_grid": list(
                C_GRID
            ),
            "main_expected_rows": 2100,
            "null_expected_rows": 100,
            "support_nonzero_convention": (
                "beta != 0.0"
            ),
            "support_empty_jaccard_convention": (
                "Jaccard(empty, empty) = 0"
            ),
            "input_provenance": input_provenance,
        }


    def run_phase_p_orchestration_from_loaded_inputs(
        representations: dict[str, np.ndarray],
        y: np.ndarray,
        *,
        output_dir: Path,
        input_provenance: dict[str, object],
    ) -> None:
        """
        Prospective full experiment-level orchestration entrypoint.

        IMPORTANT:
        This function is DEFINED but never CALLED at this hard-disabled source
        freeze.  The terminal PhasePContractError below remains in force.

        Frozen execution order once separately authorized:
          1. validate already-loaded inputs;
          2. create/validate manifest;
          3. main 2,100-row sweep;
          4. verify exact main census;
          5. 100-row layer-18 permutation-null sweep;
          6. verify exact null census.

        RESULT.md and interpretive summaries are intentionally downstream of a
        separate read-only post-execution audit.
        """
        validate_loaded_phase_p_inputs(
            representations,
            y,
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        manifest = build_phase_p_execution_manifest(
            input_provenance=input_provenance,
        )

        write_manifest_once_or_validate(
            output_dir / EXECUTION_MANIFEST_FILENAME,
            manifest,
        )

        run_main_sweep_from_loaded_inputs(
            representations,
            y,
            output_csv=(
                output_dir
                / MAIN_OUTPUT_FILENAME
            ),
        )

        main_rows, main_keys_raw = read_existing_csv_rows_exact(
            output_dir / MAIN_OUTPUT_FILENAME,
            fieldnames=MAIN_OUTPUT_FIELDS,
            key_fields=MAIN_ATOMIC_KEY_FIELDS,
            semantic_validator=validate_persisted_main_row,
        )

        main_keys = {
            (
                int(k[0]),
                int(k[1]),
                str(k[2]),
            )
            for k in main_keys_raw
        }

        if main_keys != set(expected_main_keys()):
            raise PhasePContractError(
                "Main census verification failed after sweep."
            )

        if len(main_rows) != 2100:
            raise PhasePContractError(
                "Main output must contain exactly 2,100 rows."
            )

        run_null_sweep_from_loaded_inputs(
            representations,
            y,
            output_csv=(
                output_dir
                / NULL_OUTPUT_FILENAME
            ),
        )

        null_rows, null_keys_raw = read_existing_csv_rows_exact(
            output_dir / NULL_OUTPUT_FILENAME,
            fieldnames=NULL_OUTPUT_FIELDS,
            key_fields=NULL_ATOMIC_KEY_FIELDS,
            semantic_validator=validate_persisted_null_row,
        )

        null_keys = {
            (int(k[0]),)
            for k in null_keys_raw
        }

        if null_keys != set(expected_null_keys()):
            raise PhasePContractError(
                "Null census verification failed after sweep."
            )

        if len(null_rows) != 100:
            raise PhasePContractError(
                "Null output must contain exactly 100 rows."
            )



    # Implementation freeze checks. These are definitions only while the
    # outer execution gate remains False.
    # Attachment freeze checks. Definitions only; no input is loaded here.
    assert PHASE_E_ROWS_FILENAME == "phase_e_matrix_rows.tsv"
    assert PHASE_E_PROVENANCE_FILENAME == "PHASE_E_PROVENANCE.json"
    assert BASELINE_21D_SHA256 == (
        "95fa09075b24dbd11133bdf157f9e4a9b27a01f54d644860a074d5bae4c32d98"
    )
    assert BASELINE_21D_PROVENANCE_SHA256 == (
        "98f72c402c07d2e5a48e41a6d8fd0d88dd57af6ccf0acd252fd4b7ca86cbb25f"
    )

    assert TARGET_N_VALUES == (100, 120, 139)
    assert N_CV_FOLDS == 5
    assert STABILITY_FRACTION == 0.80
    assert TRAIN_PER_CLASS == {
        100: 80,
        120: 96,
        139: 111,
    }
    assert C_GRID == (
        1e-4,
        3e-4,
        1e-3,
        3e-3,
        1e-2,
        3e-2,
        1e-1,
        3e-1,
        1.0,
    )
    assert RUNNER_NAMESPACE == 200
    assert PERMUTATION_NULL_SEED_START == 1100001
    assert PERMUTATION_NULL_SEED_END == 1100100
    assert PERMUTATION_NULL_TARGET_N == 139
    assert STREAM_LABEL_PERMUTATION == 28
    assert STAGE_A_FIT_CHILD_COUNT == 46
    assert STAGE_A_CV_FIT_CHILDREN == tuple(range(45))
    assert STAGE_A_FINAL_REFIT_CHILD == 45

    # STOP boundary:
    # Full biological orchestration and execution are not authorized at this
    # source freeze. Even if somebody changes the outer gate prematurely,
    # this implementation raises before any biological matrix, label,
    # SeedSequence, RNG, probe, CV, AUROC, or support computation.
    raise PhasePContractError(
        "Phase-P corrected mechanics are encoded, but biological execution "
        "is not yet authorized at this freeze."
    )


def main() -> int:
    """
    Hard-disabled execution entrypoint.

    Gate is checked before static validation and before the enabled placeholder.
    """
    if not ENABLE_PHASE_P_BIOLOGICAL_PROBING:
        print("PHASE-P BIOLOGICAL PROBING: HARD-DISABLED")
        print("No Phase-E matrix was loaded.")
        print("No biological label was loaded for probing.")
        print("No perturbation seed namespace was accessed.")
        print("No sklearn model was imported or fit.")
        print("No CV was performed.")
        print("No AUROC was computed.")
        print("No support statistic was computed.")
        print("No confirmatory data was accessed.")
        print("4000-4099: UNOPENED")
        print("2000-2099: SEALED")
        return 0

    validate_static_contract_only()
    run_enabled_phase_p()

    return 0


if __name__ == "__main__":
    sys.exit(main())
