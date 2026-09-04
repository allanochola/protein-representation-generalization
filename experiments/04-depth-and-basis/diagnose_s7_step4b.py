"""
Experiment 04 — Arm-B S7 step-4b redesign diagnostic.

IMPLEMENTATION STATE: ENABLED / REMOTE-VERIFIED; NOT YET EXECUTED.

This file implements the prospectively frozen S7 step-4b diagnostic contract.

Scientific firewall:
    910001-910100 = CONSUMED / CLOSED
    920001-920100 = ASSIGNED / UNOPENED
    4000-4099     = UNOPENED
    2000-2099     = SEALED

Probe mechanics are inherited unchanged from the frozen amended Arm-B
architecture diagnostic.

The Jaccard helper is inherited unchanged from the frozen Step-1 calibration
implementation.

Execution was enabled only after the disabled runner was audited, committed,
pushed, and remote-verified in a separate enablement commit. The protected
diagnostic namespace remains unopened until the first protected probe fit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
import warnings

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from synthetic_generators import MASTER_TAU, generate_s7


HERE = Path(__file__).resolve().parent

EXECUTION_ENABLED = True

# Dedicated S7 step-4 diagnostic namespace.
DIAGNOSTIC_SEEDS = tuple(range(920001, 920101))

# Explicitly prohibited namespaces.
VALIDATION_SEEDS = frozenset(range(2000, 2100))

CALIBRATION_SEEDS = (
    frozenset(range(1000, 1100))
    | frozenset(range(3000, 3100))
    | frozenset(range(4000, 4100))
    | frozenset(range(5000, 5100))
)

ARCHITECTURE_DIAGNOSTIC_SEEDS = frozenset(
    range(910001, 910101)
)

ACCEPTANCE_TAU_INDICES = frozenset({6, 7, 8})

N_PERTURBATIONS_PER_CELL = 100
N_PAIRWISE_COMPARISONS = 4950

SUPPORT_RESOLUTION_THRESHOLD = 71
RECURRENCE_THRESHOLD = 71
MINORITY_SIGN_THRESHOLD = 8

S7_SCENARIO = "S7"

class CalibrationContractError(RuntimeError):
    """Frozen calibration contract was violated."""

class CalibrationFitFailure(RuntimeError):
    """Frozen solver configuration produced a fit/convergence failure."""

class ScenarioCell:
    scenario: str
    scenario_id: int
    tau: Optional[float]
    tau_index: int
    rho: Optional[float]
    rho_index: int

class R2Result:
    selected_C: float
    best_C: float
    best_mean: float
    best_se: float
    one_se_floor: float
    cv_means: tuple[float, ...]
    cv_ses: tuple[float, ...]
    fold_aurocs: tuple[tuple[float, ...], ...]

TARGET_N_VALUES = (100, 120, 139)

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

TRAIN_PER_CLASS = {
    100: 80,
    120: 96,
    139: 111,
}

N_CV_FOLDS = 5

SCENARIO_ID = {
    "S0": 0,
    "S1": 1,
    "S2": 2,
    "S3": 3,
    "S4": 4,
    "S5": 5,
    "S6": 6,
    "S7": 7,
}

DATASET_NAMESPACE = 100

RUNNER_NAMESPACE = 200

STREAM_SUBSAMPLE = 21

STREAM_STAGE_A_SPLIT = 22

STREAM_CV = 23

STREAM_STAGE_A_FIT = 24

STREAM_STAGE_B_FIT = 25

STREAM_STABILITY_SUBSAMPLE = 26

STREAM_STABILITY_FIT = 27

STABILITY_FRACTION = 0.80

def seedsequence_to_uint32(ss: np.random.SeedSequence) -> int:
    """Frozen SeedSequence -> integer materialization."""
    return int(
        ss.generate_state(
            1,
            dtype=np.uint32,
        )[0]
    )

def dataset_seedsequence(
    scenario_id: int,
    tau_index: int,
) -> np.random.SeedSequence:
    """
    Frozen synthetic-dataset root:

        [s, t, 100]

    Independent of diagnostic seed, N and rho.
    """
    return np.random.SeedSequence(
        [
            int(scenario_id),
            int(tau_index),
            DATASET_NAMESPACE,
        ]
    )

def runner_seedsequence(
    diagnostic_seed: int,
    scenario_id: int,
    tau_index: int,
    rho_index: int,
    target_n: int,
    stream_id: int,
) -> np.random.SeedSequence:
    """
    Frozen runner-level stream:

        [c, s, t, r, N, 200, stream_id]
    """
    return np.random.SeedSequence(
        [
            int(diagnostic_seed),
            int(scenario_id),
            int(tau_index),
            int(rho_index),
            int(target_n),
            RUNNER_NAMESPACE,
            int(stream_id),
        ]
    )

def master_tau_index(tau: float) -> int:
    """
    Return unique zero-based index in the frozen MASTER_TAU ladder.

    Floating values never enter the SeedSequence entropy vector.
    """
    matches = [
        i
        for i, value in enumerate(MASTER_TAU)
        if np.isclose(
            float(tau),
            float(value),
            rtol=0.0,
            atol=1e-12,
        )
    ]

    if len(matches) != 1:
        raise CalibrationContractError(
            f"Tau {tau!r} does not map uniquely to MASTER_TAU."
        )

    return int(matches[0])

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

def atomic_write_csv(
    df: pd.DataFrame,
    final_path: Path,
) -> None:
    """
    Write CSV through a temporary file on the same filesystem,
    then atomically replace the authoritative file.
    """
    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp_path = final_path.with_name(
        final_path.name + ".tmp"
    )

    if tmp_path.exists():
        tmp_path.unlink()

    df.to_csv(
        tmp_path,
        index=False,
    )

    tmp_path.replace(final_path)

def atomic_write_json(
    payload: dict,
    final_path: Path,
) -> None:
    final_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp_path = final_path.with_name(
        final_path.name + ".tmp"
    )

    if tmp_path.exists():
        tmp_path.unlink()

    tmp_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    tmp_path.replace(final_path)

def jaccard_zero_empty(
    a: frozenset,
    b: frozenset,
) -> float:
    union = a | b

    if not union:
        return 0.0

    return float(
        len(a & b) / len(union)
    )

def run_one_perturbation(
    cell: ScenarioCell,
    *,
    diagnostic_seed: int,
    target_n: int,
    dataset,
) -> dict:
    if diagnostic_seed in VALIDATION_SEEDS:
        raise CalibrationContractError(
            "Validation seed access is prohibited in S7 step-4b."
        )

    if diagnostic_seed in CALIBRATION_SEEDS:
        raise CalibrationContractError(
            "Calibration seed access is prohibited in S7 step-4b."
        )

    if diagnostic_seed in ARCHITECTURE_DIAGNOSTIC_SEEDS:
        raise CalibrationContractError(
            "Consumed architecture-diagnostic seed access is prohibited "
            "in S7 step-4b."
        )

    if diagnostic_seed not in DIAGNOSTIC_SEEDS:
        raise CalibrationContractError(
            "S7 step-4b accepts diagnostic seeds 920001-920100 only; "
            f"got {diagnostic_seed}."
        )

    c = int(diagnostic_seed)
    s = int(cell.scenario_id)
    t = int(cell.tau_index)
    r = int(cell.rho_index)
    N = int(target_n)

    # --------------------------------------------------------
    # Stream 21: target-N subsampling
    # --------------------------------------------------------

    subsample_ss = runner_seedsequence(
        c, s, t, r, N,
        STREAM_SUBSAMPLE,
    )

    subsample_rng = np.random.default_rng(
        subsample_ss
    )

    Xn, yn = select_target_n(
        dataset.X,
        dataset.y,
        target_n=N,
        rng=subsample_rng,
    )

    expected_target_pool_y = np.concatenate(
        [
            np.ones(N, dtype=int),
            np.zeros(N, dtype=int),
        ]
    )

    if not np.array_equal(
        np.asarray(yn, dtype=int),
        expected_target_pool_y,
    ):
        raise CalibrationContractError(
            "Frozen target-N pool ordering changed: expected all positive "
            "rows followed by all negative rows. Stream-26 membership and "
            "replay semantics must not proceed under a different ordering."
        )

    # --------------------------------------------------------
    # Stream 22: Stage-A split
    # --------------------------------------------------------

    split_ss = runner_seedsequence(
        c, s, t, r, N,
        STREAM_STAGE_A_SPLIT,
    )

    split_rng = np.random.default_rng(
        split_ss
    )

    X_train, y_train, X_eval, y_eval = stage_a_split(
        Xn,
        yn,
        target_n=N,
        rng=split_rng,
    )

    # --------------------------------------------------------
    # Stream 23: shared five-fold CV construction
    # --------------------------------------------------------

    cv_ss = runner_seedsequence(
        c, s, t, r, N,
        STREAM_CV,
    )

    cv_seed = seedsequence_to_uint32(
        cv_ss
    )

    # --------------------------------------------------------
    # Stream 24: 46 Stage-A fit child seeds
    # --------------------------------------------------------

    fit_ss = runner_seedsequence(
        c, s, t, r, N,
        STREAM_STAGE_A_FIT,
    )

    fit_children = tuple(
        fit_ss.spawn(46)
    )

    if len(fit_children) != 46:
        raise CalibrationContractError(
            "Stage-A fit root did not produce 46 children."
        )

    context = (
        f"scenario={cell.scenario}; "
        f"diagnostic_seed={c}; "
        f"N={N}; "
        f"tau={cell.tau}; "
        f"rho={cell.rho}"
    )

    r2 = select_C_R2(
        X_train,
        y_train,
        cv_seed=cv_seed,
        stage_a_fit_children=fit_children,
        context=context,
    )

    # --------------------------------------------------------
    # Stage-A final selected-C refit: child 45
    # --------------------------------------------------------

    stage_a_final_seed = seedsequence_to_uint32(
        fit_children[45]
    )

    stage_a_model = fit_probe_or_fail(
        X_train,
        y_train,
        C=r2.selected_C,
        random_state=stage_a_final_seed,
        context=f"{context}; Stage-A final refit",
    )

    eval_scores = stage_a_model.decision_function(
        X_eval
    )

    heldout_auc = float(
        roc_auc_score(
            y_eval,
            eval_scores,
        )
    )

    # --------------------------------------------------------
    # Stream 25: Stage-B full-target-N coefficient refit
    # --------------------------------------------------------

    stage_b_ss = runner_seedsequence(
        c, s, t, r, N,
        STREAM_STAGE_B_FIT,
    )

    stage_b_seed = seedsequence_to_uint32(
        stage_b_ss
    )

    stage_b_model = fit_probe_or_fail(
        Xn,
        yn,
        C=r2.selected_C,
        random_state=stage_b_seed,
        context=f"{context}; Stage-B full-N refit",
    )

    beta = np.asarray(
        stage_b_model.coef_[0],
        dtype=float,
    )

    # Frozen exact zero/non-zero semantics.
    selected_idx = np.flatnonzero(
        beta != 0.0
    )

    K_t_full = int(len(selected_idx))

    full_support = tuple(
        int(j)
        for j in selected_idx.tolist()
    )

    full_signed_support = tuple(
        (
            int(j),
            1 if beta[j] > 0.0 else -1,
        )
        for j in selected_idx.tolist()
    )

    # --------------------------------------------------------
    # Stream 26: observation-level stability subsampling
    # --------------------------------------------------------

    stability_subsample_ss = runner_seedsequence(
        c, s, t, r, N,
        STREAM_STABILITY_SUBSAMPLE,
    )

    stability_rng = np.random.default_rng(
        stability_subsample_ss
    )

    (
        stability_selected,
        stability_selected_pos,
        stability_selected_neg,
        stability_membership_sha256,
    ) = select_stability_subsample(
        yn,
        target_n=N,
        rng=stability_rng,
    )

    X_stab = np.asarray(
        Xn[stability_selected],
        dtype=float,
    )
    y_stab = np.asarray(
        yn[stability_selected],
        dtype=int,
    )

    stability_n_per_class = int(
        math.floor(STABILITY_FRACTION * N)
    )

    if X_stab.shape[0] != 2 * stability_n_per_class:
        raise CalibrationContractError(
            "Stability subsample produced wrong total sample count."
        )

    if int(np.sum(y_stab == 1)) != stability_n_per_class:
        raise CalibrationContractError(
            "Stability subsample produced wrong positive count."
        )

    if int(np.sum(y_stab == 0)) != stability_n_per_class:
        raise CalibrationContractError(
            "Stability subsample produced wrong negative count."
        )

    # --------------------------------------------------------
    # Stream 27: stability refit's sklearn random_state
    # --------------------------------------------------------

    stability_fit_ss = runner_seedsequence(
        c, s, t, r, N,
        STREAM_STABILITY_FIT,
    )

    stability_fit_seed = seedsequence_to_uint32(
        stability_fit_ss
    )

    stability_model = fit_probe_or_fail(
        X_stab,
        y_stab,
        C=r2.selected_C,
        random_state=stability_fit_seed,
        context=f"{context}; 80%-within-pool stability refit",
    )

    beta_stab = np.asarray(
        stability_model.coef_[0],
        dtype=float,
    )

    stability_selected_idx = np.flatnonzero(
        beta_stab != 0.0
    )

    K_t_stab = int(
        len(stability_selected_idx)
    )

    stability_support = tuple(
        int(j)
        for j in stability_selected_idx.tolist()
    )

    stability_signed_support = tuple(
        (
            int(j),
            1 if beta_stab[j] > 0.0 else -1,
        )
        for j in stability_selected_idx.tolist()
    )

    # --------------------------------------------------------
    # Raw perturbation record.
    # No gamma / gate / threshold exists here.
    # --------------------------------------------------------

    return {
        "scenario": cell.scenario,
        "scenario_id": cell.scenario_id,
        "diagnostic_seed": c,
        "target_n": N,
        "tau": cell.tau,
        "tau_index": cell.tau_index,
        "rho": cell.rho,
        "rho_index": cell.rho_index,
        "selected_C_R2": r2.selected_C,
        "K_t_full": K_t_full,
        "K_t_stab": K_t_stab,
        "full_support_indices_json": json.dumps(
            full_support,
            separators=(",", ":"),
        ),
        "full_signed_support_json": json.dumps(
            full_signed_support,
            separators=(",", ":"),
        ),
        "stability_support_indices_json": json.dumps(
            stability_support,
            separators=(",", ":"),
        ),
        "stability_signed_support_json": json.dumps(
            stability_signed_support,
            separators=(",", ":"),
        ),
        "stability_positive_membership_json": json.dumps(
            tuple(
                int(i)
                for i in stability_selected_pos.tolist()
            ),
            separators=(",", ":"),
        ),
        "stability_negative_membership_json": json.dumps(
            tuple(
                int(i)
                for i in stability_selected_neg.tolist()
            ),
            separators=(",", ":"),
        ),
        "stability_membership_sha256": stability_membership_sha256,
        "stability_n_per_class": stability_n_per_class,
        "stage_A_final_fit_seed": stage_a_final_seed,
        "stage_B_fit_seed": stage_b_seed,
        "stability_subsample_seed_identity_json": json.dumps(
            [
                c,
                s,
                t,
                r,
                N,
                RUNNER_NAMESPACE,
                STREAM_STABILITY_SUBSAMPLE,
            ],
            separators=(",", ":"),
        ),
        "stability_fit_seed": stability_fit_seed,
    }


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(
                1024 * 1024
            )

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def s7_cells() -> tuple[ScenarioCell, ...]:
    """
    Complete frozen S7 MASTER_TAU ladder.
    """
    cells = tuple(
        ScenarioCell(
            scenario=S7_SCENARIO,
            scenario_id=SCENARIO_ID[S7_SCENARIO],
            tau=float(tau),
            tau_index=master_tau_index(
                float(tau)
            ),
            rho=None,
            rho_index=0,
        )
        for tau in MASTER_TAU
    )

    expected_indices = tuple(
        range(len(MASTER_TAU))
    )

    observed_indices = tuple(
        int(cell.tau_index)
        for cell in cells
    )

    if observed_indices != expected_indices:
        raise CalibrationContractError(
            "S7 cells do not reproduce the complete MASTER_TAU ladder."
        )

    return cells


def generate_s7_cell_dataset(
    cell: ScenarioCell,
    dataset_seed: int,
):
    """
    Generate only the frozen S7 candidate and obtain sign-instability
    eligibility only from its frozen metadata.
    """
    if cell.scenario != S7_SCENARIO:
        raise CalibrationContractError(
            "Dedicated step-4b runner accepts S7 only."
        )

    if cell.rho is not None:
        raise CalibrationContractError(
            "S7 step-4b does not authorize rho."
        )

    if int(cell.rho_index) != 0:
        raise CalibrationContractError(
            "S7 rho-index sentinel must remain zero."
        )

    dataset = generate_s7(
        seed=int(dataset_seed),
        tau=float(cell.tau),
    )

    metadata = dataset.metadata

    if "planted_sign_instability_idx" not in metadata:
        raise CalibrationContractError(
            "Frozen S7 metadata lacks planted_sign_instability_idx."
        )

    planted_coordinates = tuple(
        int(j)
        for j in metadata[
            "planted_sign_instability_idx"
        ]
    )

    if not planted_coordinates:
        raise CalibrationContractError(
            "Frozen S7 metadata identifies no eligible planted coordinate."
        )

    if len(set(planted_coordinates)) != len(
        planted_coordinates
    ):
        raise CalibrationContractError(
            "Frozen S7 planted-coordinate metadata contains duplicates."
        )

    if any(
        j < 0
        or j >= int(dataset.X.shape[1])
        for j in planted_coordinates
    ):
        raise CalibrationContractError(
            "Frozen S7 planted-coordinate metadata is outside X."
        )

    return (
        dataset,
        planted_coordinates,
    )


def parse_unsigned_support(
    value: str,
) -> frozenset:
    raw = json.loads(value)

    support = tuple(
        int(j)
        for j in raw
    )

    if len(set(support)) != len(support):
        raise CalibrationContractError(
            "Persisted unsigned support contains duplicate coordinates."
        )

    return frozenset(support)


def parse_signed_support(
    value: str,
) -> frozenset:
    raw = json.loads(value)

    support = tuple(
        (
            int(pair[0]),
            int(pair[1]),
        )
        for pair in raw
    )

    if any(
        sign not in (-1, 1)
        for _, sign in support
    ):
        raise CalibrationContractError(
            "Persisted signed support contains a sign outside {-1,+1}."
        )

    coordinates = tuple(
        coordinate
        for coordinate, _ in support
    )

    if len(set(coordinates)) != len(
        coordinates
    ):
        raise CalibrationContractError(
            "Persisted signed support repeats a coordinate."
        )

    return frozenset(support)


def planted_coordinate_signs_from_persisted_support(
    signed_support_json: str,
    planted_coordinates: tuple[int, ...],
) -> dict[str, int]:
    """
    Return -1 / 0 / +1 for each prospectively eligible planted coordinate.
    """
    signed_support = parse_signed_support(
        signed_support_json
    )

    signs = {
        int(coordinate): int(sign)
        for coordinate, sign
        in signed_support
    }

    return {
        str(int(j)): int(
            signs.get(
                int(j),
                0,
            )
        )
        for j in planted_coordinates
    }


def frozen_pairwise_jaccards(
    perturbation_rows: pd.DataFrame,
) -> pd.DataFrame:
    """
    Frozen historical I/G construction:

      for i in range(100):
          for j in range(i+1, 100):
              Jaccard(...)
      median of exactly 4,950 values.

    Supports are reconstructed from persisted JSON.
    """
    if len(perturbation_rows) != 100:
        raise CalibrationContractError(
            f"Expected exactly 100 perturbation rows; "
            f"got {len(perturbation_rows)}."
        )

    rows = (
        perturbation_rows
        .sort_values(
            "diagnostic_seed"
        )
        .reset_index(drop=True)
    )

    expected_seeds = tuple(
        DIAGNOSTIC_SEEDS
    )

    observed_seeds = tuple(
        int(x)
        for x in rows[
            "diagnostic_seed"
        ].tolist()
    )

    if observed_seeds != expected_seeds:
        raise CalibrationContractError(
            "Cell does not contain exactly diagnostic seeds "
            "920001-920100 in canonical order."
        )

    supports = [
        parse_unsigned_support(value)
        for value in rows[
            "stability_support_indices_json"
        ].tolist()
    ]

    signed_supports = [
        parse_signed_support(value)
        for value in rows[
            "stability_signed_support_json"
        ].tolist()
    ]

    pair_rows = []

    for i in range(100):
        for j in range(i + 1, 100):

            I_pair = jaccard_zero_empty(
                supports[i],
                supports[j],
            )

            G_pair = jaccard_zero_empty(
                signed_supports[i],
                signed_supports[j],
            )

            # Frozen historical structural invariant.
            if G_pair > I_pair + 1e-15:
                raise CalibrationContractError(
                    f"G_pair > I_pair for pair ({i}, {j})."
                )

            pair_rows.append(
                {
                    "scenario": S7_SCENARIO,
                    "tau": float(
                        rows.iloc[0]["tau"]
                    ),
                    "tau_index": int(
                        rows.iloc[0]["tau_index"]
                    ),
                    "target_n": int(
                        rows.iloc[0]["target_n"]
                    ),
                    "diagnostic_seed_i": int(
                        rows.iloc[i][
                            "diagnostic_seed"
                        ]
                    ),
                    "diagnostic_seed_j": int(
                        rows.iloc[j][
                            "diagnostic_seed"
                        ]
                    ),
                    "I_pair": float(
                        I_pair
                    ),
                    "G_pair": float(
                        G_pair
                    ),
                }
            )

    pair_df = pd.DataFrame(
        pair_rows
    )

    if len(pair_df) != N_PAIRWISE_COMPARISONS:
        raise CalibrationContractError(
            f"Expected 4950 pairwise rows; got {len(pair_df)}."
        )

    return pair_df


def aggregate_step4b_cell(
    perturbation_rows: pd.DataFrame,
    *,
    planted_coordinates: tuple[int, ...],
) -> tuple[dict, pd.DataFrame]:
    """
    Apply frozen §§9-14 cell statistics and decision limbs.

    Recurrence/sign counts are reconstructed only from persisted signed
    stability supports.
    """
    if len(perturbation_rows) != 100:
        raise CalibrationContractError(
            f"Expected exactly 100 perturbation rows; "
            f"got {len(perturbation_rows)}."
        )

    rows = (
        perturbation_rows
        .sort_values(
            "diagnostic_seed"
        )
        .reset_index(drop=True)
    )

    observed_seeds = tuple(
        int(x)
        for x in rows[
            "diagnostic_seed"
        ].tolist()
    )

    if observed_seeds != DIAGNOSTIC_SEEDS:
        raise CalibrationContractError(
            "Step-4b cell does not contain exactly seeds 920001-920100."
        )

    if rows[
        "diagnostic_seed"
    ].duplicated().any():
        raise CalibrationContractError(
            "Step-4b cell contains duplicate diagnostic seeds."
        )

    identity_columns = (
        "scenario",
        "scenario_id",
        "target_n",
        "tau_index",
        "rho_index",
    )

    for column in identity_columns:
        if rows[
            column
        ].nunique(
            dropna=False
        ) != 1:
            raise CalibrationContractError(
                f"Step-4b cell mixes values in {column}."
            )

    first = rows.iloc[0]

    if str(first["scenario"]) != S7_SCENARIO:
        raise CalibrationContractError(
            "Step-4b aggregation received a non-S7 cell."
        )

    target_n = int(
        first["target_n"]
    )

    tau_index = int(
        first["tau_index"]
    )

    expected_stability_n = {
        100: 80,
        120: 96,
        139: 111,
    }.get(target_n)

    if expected_stability_n is None:
        raise CalibrationContractError(
            f"Unexpected target N: {target_n}."
        )

    observed_stability_sizes = {
        int(x)
        for x in rows[
            "stability_n_per_class"
        ].tolist()
    }

    if observed_stability_sizes != {
        expected_stability_n
    }:
        raise CalibrationContractError(
            "Persisted stability-refit size violates frozen 0.80 rule."
        )

    # ------------------------------------------------------------------
    # Verify exact stream-26 identities and membership hashes/replay.
    # ------------------------------------------------------------------

    observed_stream26_identities = []
    direct_memberships = []

    for _, row in rows.iterrows():

        diagnostic_seed = int(
            row["diagnostic_seed"]
        )

        scenario_id = int(
            row["scenario_id"]
        )

        rho_index = int(
            row["rho_index"]
        )

        observed_identity = tuple(
            int(x)
            for x in json.loads(
                row[
                    "stability_subsample_seed_identity_json"
                ]
            )
        )

        expected_identity = (
            diagnostic_seed,
            scenario_id,
            tau_index,
            rho_index,
            target_n,
            RUNNER_NAMESPACE,
            STREAM_STABILITY_SUBSAMPLE,
        )

        if observed_identity != expected_identity:
            raise CalibrationContractError(
                "Stored stream-26 seed identity differs from frozen "
                "SeedSequence derivation."
            )

        observed_stream26_identities.append(
            observed_identity
        )

        pos_membership = tuple(
            int(x)
            for x in json.loads(
                row[
                    "stability_positive_membership_json"
                ]
            )
        )

        neg_membership = tuple(
            int(x)
            for x in json.loads(
                row[
                    "stability_negative_membership_json"
                ]
            )
        )

        if len(pos_membership) != expected_stability_n:
            raise CalibrationContractError(
                "Stored positive stability membership has wrong size."
            )

        if len(neg_membership) != expected_stability_n:
            raise CalibrationContractError(
                "Stored negative stability membership has wrong size."
            )

        if len(set(pos_membership)) != expected_stability_n:
            raise CalibrationContractError(
                "Stored positive stability membership contains duplicates."
            )

        if len(set(neg_membership)) != expected_stability_n:
            raise CalibrationContractError(
                "Stored negative stability membership contains duplicates."
            )

        if any(
            not (0 <= idx < target_n)
            for idx in pos_membership
        ):
            raise CalibrationContractError(
                "Positive stability membership lies outside target pool."
            )

        if any(
            not (
                target_n
                <= idx
                < 2 * target_n
            )
            for idx in neg_membership
        ):
            raise CalibrationContractError(
                "Negative stability membership lies outside target pool."
            )

        membership_payload = {
            "positive_target_pool_indices":
                list(pos_membership),
            "negative_target_pool_indices":
                list(neg_membership),
        }

        membership_json = json.dumps(
            membership_payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        recomputed_hash = hashlib.sha256(
            membership_json.encode(
                "utf-8"
            )
        ).hexdigest()

        if recomputed_hash != str(
            row[
                "stability_membership_sha256"
            ]
        ):
            raise CalibrationContractError(
                "Stored stability-membership SHA-256 mismatch."
            )

        # Exact deterministic replay of stream 26.
        stream26_ss = runner_seedsequence(
            diagnostic_seed,
            scenario_id,
            tau_index,
            rho_index,
            target_n,
            STREAM_STABILITY_SUBSAMPLE,
        )

        replay_rng = np.random.default_rng(
            stream26_ss
        )

        replay_y = np.concatenate(
            [
                np.ones(
                    target_n,
                    dtype=int,
                ),
                np.zeros(
                    target_n,
                    dtype=int,
                ),
            ]
        )

        (
            _,
            replay_pos,
            replay_neg,
            replay_hash,
        ) = select_stability_subsample(
            replay_y,
            target_n=target_n,
            rng=replay_rng,
        )

        if tuple(
            int(x)
            for x in replay_pos.tolist()
        ) != pos_membership:
            raise CalibrationContractError(
                "Positive stability membership fails deterministic replay."
            )

        if tuple(
            int(x)
            for x in replay_neg.tolist()
        ) != neg_membership:
            raise CalibrationContractError(
                "Negative stability membership fails deterministic replay."
            )

        if replay_hash != recomputed_hash:
            raise CalibrationContractError(
                "Replayed stability membership hash mismatch."
            )

        direct_memberships.append(
            (
                pos_membership,
                neg_membership,
            )
        )

    if len(
        set(
            observed_stream26_identities
        )
    ) != 100:
        raise CalibrationContractError(
            "Step-4b requires exactly 100 distinct stream-26 identities."
        )

    # Do NOT create a scientific gate from distinct realized memberships.
    # Duplicate membership is checked only as an integrity anomaly.
    if len(
        set(
            direct_memberships
        )
    ) != 100:
        raise CalibrationContractError(
            "Duplicate realized stability membership observed; "
            "halt for integrity investigation."
        )

    # ------------------------------------------------------------------
    # Reconstruct K_t_stab from persisted unsigned supports.
    # ------------------------------------------------------------------

    unsigned_supports = []
    signed_supports = []
    reconstructed_K = []

    for _, row in rows.iterrows():

        unsigned = parse_unsigned_support(
            row[
                "stability_support_indices_json"
            ]
        )

        signed = parse_signed_support(
            row[
                "stability_signed_support_json"
            ]
        )

        unsigned_coordinates = frozenset(
            int(x)
            for x in unsigned
        )

        signed_coordinates = frozenset(
            int(pair[0])
            for pair in signed
        )

        if signed_coordinates != unsigned_coordinates:
            raise CalibrationContractError(
                "Persisted signed and unsigned supports disagree."
            )

        K_value = int(
            len(unsigned)
        )

        if K_value != int(
            row["K_t_stab"]
        ):
            raise CalibrationContractError(
                "Persisted K_t_stab disagrees with persisted support."
            )

        unsigned_supports.append(
            unsigned
        )

        signed_supports.append(
            signed
        )

        reconstructed_K.append(
            K_value
        )

    K = np.asarray(
        reconstructed_K,
        dtype=int,
    )

    count_K_eq_0 = int(
        np.sum(K == 0)
    )

    count_K_eq_1 = int(
        np.sum(K == 1)
    )

    count_K_eq_2 = int(
        np.sum(K == 2)
    )

    count_K_ge_3 = int(
        np.sum(K >= 3)
    )

    if (
        count_K_eq_0
        + count_K_eq_1
        + count_K_eq_2
        + count_K_ge_3
        != 100
    ):
        raise CalibrationContractError(
            "K_t_stab structural counts do not sum to 100."
        )

    min_K_t_stab = int(
        np.min(K)
    )

    median_K_t_stab = float(
        np.median(K)
    )

    max_K_t_stab = int(
        np.max(K)
    )

    support_resolution_pass = bool(
        count_K_ge_3
        >= SUPPORT_RESOLUTION_THRESHOLD
    )

    # ------------------------------------------------------------------
    # Reconstruct R_j, n_plus_j, n_minus_j, M_j exclusively from the
    # persisted signed supports.
    # ------------------------------------------------------------------

    planted_counts = {}
    qualifying_coordinates = []

    for coordinate in planted_coordinates:

        j = int(coordinate)

        n_plus = int(
            sum(
                (j, 1) in support
                for support in signed_supports
            )
        )

        n_minus = int(
            sum(
                (j, -1) in support
                for support in signed_supports
            )
        )

        R_j = int(
            n_plus + n_minus
        )

        M_j = int(
            min(
                n_plus,
                n_minus,
            )
        )

        qualifies = bool(
            R_j >= RECURRENCE_THRESHOLD
            and M_j >= MINORITY_SIGN_THRESHOLD
        )

        planted_counts[
            str(j)
        ] = {
            "R_j": R_j,
            "n_plus_j": n_plus,
            "n_minus_j": n_minus,
            "M_j": M_j,
            "qualifies": qualifies,
        }

        if qualifies:
            qualifying_coordinates.append(
                j
            )

    recurring_coordinate_sign_instability_pass = bool(
        qualifying_coordinates
    )

    # ------------------------------------------------------------------
    # Frozen historical pairwise Jaccards and medians.
    # ------------------------------------------------------------------

    pair_df = frozen_pairwise_jaccards(
        rows
    )

    I_values = pair_df[
        "I_pair"
    ].to_numpy(
        dtype=float
    )

    G_values = pair_df[
        "G_pair"
    ].to_numpy(
        dtype=float
    )

    if len(I_values) != 4950:
        raise CalibrationContractError(
            f"Expected 4950 I pairs; got {len(I_values)}."
        )

    if len(G_values) != 4950:
        raise CalibrationContractError(
            f"Expected 4950 G pairs; got {len(G_values)}."
        )

    # Frozen historical aggregation.
    I_stat = float(
        np.median(
            np.asarray(
                I_values,
                dtype=float,
            )
        )
    )

    G_stat = float(
        np.median(
            np.asarray(
                G_values,
                dtype=float,
            )
        )
    )

    # Frozen historical structural invariant.
    if G_stat > I_stat + 1e-15:
        raise CalibrationContractError(
            "Frozen invariant G_stat <= I_stat violated."
        )

    aggregate_sign_effect_pass = bool(
        G_stat < I_stat
    )

    acceptance_cell = bool(
        tau_index in ACCEPTANCE_TAU_INDICES
        and target_n in TARGET_N_VALUES
    )

    if acceptance_cell:

        cell_pass = bool(
            support_resolution_pass
            and recurring_coordinate_sign_instability_pass
            and aggregate_sign_effect_pass
        )

        cell_verdict = (
            "PASS"
            if cell_pass
            else "FAIL"
        )

    else:

        # Lower tau values remain descriptive only.
        cell_pass = False
        cell_verdict = "DESCRIPTIVE_ONLY"

    result = {
        "scenario": S7_SCENARIO,
        "scenario_id": int(
            first["scenario_id"]
        ),
        "target_n": target_n,
        "tau": float(
            first["tau"]
        ),
        "tau_index": tau_index,
        "rho": None,
        "rho_index": 0,
        "n_perturbations": 100,
        "stability_n_per_class":
            expected_stability_n,

        "count_K_t_stab_eq_0":
            count_K_eq_0,
        "count_K_t_stab_eq_1":
            count_K_eq_1,
        "count_K_t_stab_eq_2":
            count_K_eq_2,
        "count_K_t_stab_ge_3":
            count_K_ge_3,

        "min_K_t_stab":
            min_K_t_stab,
        "median_K_t_stab":
            median_K_t_stab,
        "max_K_t_stab":
            max_K_t_stab,

        "planted_sign_instability_idx_json":
            canonical_json(
                [
                    int(j)
                    for j
                    in planted_coordinates
                ]
            ),

        "planted_coordinate_counts_json":
            canonical_json(
                planted_counts
            ),

        "qualifying_planted_coordinates_json":
            canonical_json(
                [
                    int(j)
                    for j
                    in qualifying_coordinates
                ]
            ),

        "I_stat":
            I_stat,
        "G_stat":
            G_stat,

        "support_resolution_pass":
            support_resolution_pass,

        "recurring_coordinate_sign_instability_pass":
            recurring_coordinate_sign_instability_pass,

        "aggregate_sign_effect_pass":
            aggregate_sign_effect_pass,

        "acceptance_cell":
            acceptance_cell,

        "cell_pass":
            cell_pass,

        "cell_verdict":
            cell_verdict,
    }

    return (
        result,
        pair_df,
    )


def cell_key(
    tau_index: int,
    target_n: int,
) -> str:
    return (
        f"tau{int(tau_index):02d}"
        f"_N{int(target_n):03d}"
    )


def checkpoint_paths(
    checkpoint_dir: Path,
    *,
    tau_index: int,
    target_n: int,
) -> dict[str, Path]:
    key = cell_key(
        tau_index,
        target_n,
    )

    return {
        "raw":
            checkpoint_dir
            / f"{key}_per_perturbation.csv",

        "pairs":
            checkpoint_dir
            / f"{key}_pairwise_jaccard.csv",

        "summary":
            checkpoint_dir
            / f"{key}_summary.json",

        # Written LAST. Its existence marks an authoritative completed cell.
        "manifest":
            checkpoint_dir
            / f"{key}_manifest.json",
    }


def write_cell_checkpoint(
    *,
    checkpoint_dir: Path,
    perturbation_rows: pd.DataFrame,
    pair_rows: pd.DataFrame,
    aggregate_row: dict,
    planted_coordinates: tuple[int, ...],
    dataset_seed: int,
) -> None:
    """
    Atomic cell transaction.

    The manifest is written last and is therefore the completion marker.
    """
    tau_index = int(
        aggregate_row[
            "tau_index"
        ]
    )

    target_n = int(
        aggregate_row[
            "target_n"
        ]
    )

    paths = checkpoint_paths(
        checkpoint_dir,
        tau_index=tau_index,
        target_n=target_n,
    )

    checkpoint_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_df = (
        perturbation_rows
        .sort_values(
            "diagnostic_seed"
        )
        .reset_index(drop=True)
    )

    pair_df = (
        pair_rows
        .sort_values(
            [
                "diagnostic_seed_i",
                "diagnostic_seed_j",
            ]
        )
        .reset_index(drop=True)
    )

    atomic_write_csv(
        raw_df,
        paths["raw"],
    )

    atomic_write_csv(
        pair_df,
        paths["pairs"],
    )

    atomic_write_json(
        aggregate_row,
        paths["summary"],
    )

    manifest = {
        "status": "COMPLETE",
        "scenario": S7_SCENARIO,
        "tau_index": tau_index,
        "target_n": target_n,
        "dataset_seed":
            int(dataset_seed),

        "planted_sign_instability_idx":
            [
                int(j)
                for j
                in planted_coordinates
            ],

        "n_raw_rows":
            int(len(raw_df)),

        "n_pair_rows":
            int(len(pair_df)),

        "raw_sha256":
            sha256_file(
                paths["raw"]
            ),

        "pairs_sha256":
            sha256_file(
                paths["pairs"]
            ),

        "summary_sha256":
            sha256_file(
                paths["summary"]
            ),
    }

    # Completion marker written last.
    atomic_write_json(
        manifest,
        paths["manifest"],
    )


def load_cell_checkpoint(
    *,
    checkpoint_dir: Path,
    tau_index: int,
    target_n: int,
    planted_coordinates: tuple[int, ...],
    dataset_seed: int,
):
    """
    Validate a completed checkpoint by reconstructing statistics from its
    persisted signed/unsigned supports.

    If no completion manifest exists, return None and deterministically rerun
    that complete cell.
    """
    paths = checkpoint_paths(
        checkpoint_dir,
        tau_index=tau_index,
        target_n=target_n,
    )

    if not paths[
        "manifest"
    ].exists():
        return None

    manifest = json.loads(
        paths[
            "manifest"
        ].read_text(
            encoding="utf-8"
        )
    )

    if manifest.get(
        "status"
    ) != "COMPLETE":
        raise CalibrationContractError(
            "Checkpoint manifest exists but is not COMPLETE."
        )

    for key in (
        "raw",
        "pairs",
        "summary",
    ):
        if not paths[
            key
        ].is_file():
            raise CalibrationContractError(
                f"Completed checkpoint lacks {key}."
            )

    if int(
        manifest[
            "tau_index"
        ]
    ) != int(tau_index):
        raise CalibrationContractError(
            "Checkpoint tau-index mismatch."
        )

    if int(
        manifest[
            "target_n"
        ]
    ) != int(target_n):
        raise CalibrationContractError(
            "Checkpoint target-N mismatch."
        )

    if int(
        manifest[
            "dataset_seed"
        ]
    ) != int(dataset_seed):
        raise CalibrationContractError(
            "Checkpoint dataset-seed mismatch."
        )

    checkpoint_planted = tuple(
        int(j)
        for j
        in manifest[
            "planted_sign_instability_idx"
        ]
    )

    if checkpoint_planted != planted_coordinates:
        raise CalibrationContractError(
            "Checkpoint planted-coordinate metadata mismatch."
        )

    if sha256_file(
        paths["raw"]
    ) != manifest[
        "raw_sha256"
    ]:
        raise CalibrationContractError(
            "Checkpoint raw SHA-256 mismatch."
        )

    if sha256_file(
        paths["pairs"]
    ) != manifest[
        "pairs_sha256"
    ]:
        raise CalibrationContractError(
            "Checkpoint pair SHA-256 mismatch."
        )

    if sha256_file(
        paths["summary"]
    ) != manifest[
        "summary_sha256"
    ]:
        raise CalibrationContractError(
            "Checkpoint summary SHA-256 mismatch."
        )

    raw_df = pd.read_csv(
        paths["raw"]
    )

    pair_df = pd.read_csv(
        paths["pairs"]
    )

    stored_summary = json.loads(
        paths[
            "summary"
        ].read_text(
            encoding="utf-8"
        )
    )

    if len(raw_df) != 100:
        raise CalibrationContractError(
            "Checkpoint raw table does not contain 100 rows."
        )

    if len(pair_df) != 4950:
        raise CalibrationContractError(
            "Checkpoint pair table does not contain 4,950 rows."
        )

    reconstructed_summary, reconstructed_pairs = (
        aggregate_step4b_cell(
            raw_df,
            planted_coordinates=planted_coordinates,
        )
    )

    if canonical_json(
        reconstructed_summary
    ) != canonical_json(
        stored_summary
    ):
        raise CalibrationContractError(
            "Checkpoint summary is not reproducible from persisted supports."
        )

    pair_identity_columns = [
        "diagnostic_seed_i",
        "diagnostic_seed_j",
    ]

    stored_pair_identity = (
        pair_df[
            pair_identity_columns
        ]
        .to_numpy(
            dtype=int
        )
    )

    reconstructed_pair_identity = (
        reconstructed_pairs[
            pair_identity_columns
        ]
        .to_numpy(
            dtype=int
        )
    )

    if not np.array_equal(
        stored_pair_identity,
        reconstructed_pair_identity,
    ):
        raise CalibrationContractError(
            "Checkpoint pair identities are not reproducible."
        )

    if not np.allclose(
        pair_df[
            "I_pair"
        ].to_numpy(
            dtype=float
        ),
        reconstructed_pairs[
            "I_pair"
        ].to_numpy(
            dtype=float
        ),
        rtol=0.0,
        atol=1e-15,
    ):
        raise CalibrationContractError(
            "Checkpoint I_pair values are not reproducible."
        )

    if not np.allclose(
        pair_df[
            "G_pair"
        ].to_numpy(
            dtype=float
        ),
        reconstructed_pairs[
            "G_pair"
        ].to_numpy(
            dtype=float
        ),
        rtol=0.0,
        atol=1e-15,
    ):
        raise CalibrationContractError(
            "Checkpoint G_pair values are not reproducible."
        )

    return (
        raw_df,
        reconstructed_pairs,
        reconstructed_summary,
    )


def build_candidate_verdict(
    cell_summary: pd.DataFrame,
) -> dict:
    """
    Frozen candidate-level rule: all 9/9 high-signal cells must pass.
    """
    expected_total_cells = (
        len(MASTER_TAU)
        * len(TARGET_N_VALUES)
    )

    if len(
        cell_summary
    ) != expected_total_cells:
        raise CalibrationContractError(
            f"Expected {expected_total_cells} completed S7 cells; "
            f"got {len(cell_summary)}."
        )

    acceptance = cell_summary[
        cell_summary[
            "acceptance_cell"
        ].astype(bool)
    ].copy()

    if len(acceptance) != 9:
        raise CalibrationContractError(
            f"Frozen acceptance region requires 9 cells; "
            f"got {len(acceptance)}."
        )

    expected_keys = {
        (
            int(tau_index),
            int(target_n),
        )
        for tau_index
        in ACCEPTANCE_TAU_INDICES
        for target_n
        in TARGET_N_VALUES
    }

    observed_keys = {
        (
            int(row.tau_index),
            int(row.target_n),
        )
        for row
        in acceptance.itertuples(
            index=False
        )
    }

    if observed_keys != expected_keys:
        raise CalibrationContractError(
            "Observed acceptance region differs from frozen nine cells."
        )

    passed = int(
        np.sum(
            acceptance[
                "cell_pass"
            ].astype(bool)
        )
    )

    candidate_pass = bool(
        passed == 9
    )

    return {
        "candidate": "S7-v2",
        "acceptance_cells_total": 9,
        "acceptance_cells_passed": passed,
        "decision_rule": "all_9_of_9",
        "candidate_pass":
            candidate_pass,
        "candidate_verdict":
            (
                "PASS"
                if candidate_pass
                else "REJECTED"
            ),
        "namespace_after_first_probe_fit":
            "920001-920100 = CONSUMED",
        "lower_tau_cells":
            "DESCRIPTIVE_ONLY",
        "gamma_selected":
            False,
    }


def run_s7_step4b_diagnostic(
    output_dir: Path,
) -> None:
    """
    Execute/resume the frozen S7 step-4b diagnostic.

    IMPORTANT:
    The very first protected probe fit consumes namespace 920001-920100.
    """
    # Must be the first substantive execution check.
    if EXECUTION_ENABLED is not True:
        raise CalibrationContractError(
            "S7 step-4b is HARD-DISABLED in this commit. "
            "Separate enablement commit required."
        )

    if DIAGNOSTIC_SEEDS != tuple(
        range(
            920001,
            920101,
        )
    ):
        raise CalibrationContractError(
            "Dedicated diagnostic seed block changed."
        )

    if len(
        DIAGNOSTIC_SEEDS
    ) != 100:
        raise CalibrationContractError(
            "Dedicated diagnostic block must contain exactly 100 seeds."
        )

    if set(
        DIAGNOSTIC_SEEDS
    ) & set(
        VALIDATION_SEEDS
    ):
        raise CalibrationContractError(
            "Diagnostic/validation namespace overlap."
        )

    if set(
        DIAGNOSTIC_SEEDS
    ) & set(
        CALIBRATION_SEEDS
    ):
        raise CalibrationContractError(
            "Diagnostic/calibration namespace overlap."
        )

    if set(
        DIAGNOSTIC_SEEDS
    ) & set(
        ARCHITECTURE_DIAGNOSTIC_SEEDS
    ):
        raise CalibrationContractError(
            "Step-4b/architecture namespace overlap."
        )

    if STABILITY_FRACTION != 0.80:
        raise CalibrationContractError(
            "Frozen stability fraction changed."
        )

    observed_streams = (
        STREAM_SUBSAMPLE,
        STREAM_STAGE_A_SPLIT,
        STREAM_CV,
        STREAM_STAGE_A_FIT,
        STREAM_STAGE_B_FIT,
        STREAM_STABILITY_SUBSAMPLE,
        STREAM_STABILITY_FIT,
    )

    if observed_streams != (
        21,
        22,
        23,
        24,
        25,
        26,
        27,
    ):
        raise CalibrationContractError(
            "Frozen streams 21-27 changed."
        )

    output_dir = output_dir.resolve()

    checkpoint_dir = (
        output_dir
        / "checkpoint_cells"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_final = (
        output_dir
        / "s7_step4b_per_perturbation.csv"
    )

    pairs_final = (
        output_dir
        / "s7_step4b_pairwise_jaccard.csv"
    )

    summary_final = (
        output_dir
        / "s7_step4b_cell_summary.csv"
    )

    archive_manifest = (
        output_dir
        / "s7_step4b_archive_manifest.json"
    )

    verdict_path = (
        output_dir
        / "s7_step4b_candidate_verdict.json"
    )

    cells = s7_cells()

    total_cells = int(
        len(cells)
        * len(TARGET_N_VALUES)
    )

    raw_blocks = []
    pair_blocks = []
    summary_rows = []

    start_time = time.monotonic()

    print(
        "OPENING/RESUMING S7 STEP-4b DIAGNOSTIC 920001-920100.\n"
        "910001-910100 remains consumed/closed.\n"
        "4000-4099 remains unopened.\n"
        "2000-2099 remains sealed.\n"
        "No gamma is selected by this diagnostic."
    )

    for cell in cells:

        # Frozen dataset seed construction.
        dataset_ss = dataset_seedsequence(
            cell.scenario_id,
            cell.tau_index,
        )

        dataset_seed = seedsequence_to_uint32(
            dataset_ss
        )

        dataset, planted_coordinates = (
            generate_s7_cell_dataset(
                cell,
                dataset_seed,
            )
        )

        for target_n in TARGET_N_VALUES:

            checkpoint = load_cell_checkpoint(
                checkpoint_dir=checkpoint_dir,
                tau_index=cell.tau_index,
                target_n=target_n,
                planted_coordinates=planted_coordinates,
                dataset_seed=dataset_seed,
            )

            if checkpoint is not None:

                (
                    raw_df,
                    pair_df,
                    aggregate_row,
                ) = checkpoint

                print(
                    "[checkpoint validated] "
                    f"tau_index={cell.tau_index} "
                    f"N={target_n}"
                )

            else:

                print(
                    "[cell start] "
                    f"tau_index={cell.tau_index} "
                    f"tau={cell.tau} "
                    f"N={target_n}"
                )

                rows = []

                for diagnostic_seed in DIAGNOSTIC_SEEDS:

                    row = run_one_perturbation(
                        cell,
                        diagnostic_seed=diagnostic_seed,
                        target_n=target_n,
                        dataset=dataset,
                    )

                    # §17 persistence firewall.
                    #
                    # K_t_full is permitted, but exact full-target-N
                    # unsigned/signed supports are not authoritative
                    # step-4b outputs. Remove them before raw persistence.
                    removed_full_support = row.pop(
                        "full_support_indices_json",
                        None,
                    )

                    removed_full_signed_support = row.pop(
                        "full_signed_support_json",
                        None,
                    )

                    if removed_full_support is None:
                        raise CalibrationContractError(
                            "Inherited perturbation output unexpectedly lacks "
                            "full_support_indices_json."
                        )

                    if removed_full_signed_support is None:
                        raise CalibrationContractError(
                            "Inherited perturbation output unexpectedly lacks "
                            "full_signed_support_json."
                        )

                    # Permitted required provenance.
                    row[
                        "dataset_seed"
                    ] = int(
                        dataset_seed
                    )

                    row[
                        "planted_sign_instability_idx_json"
                    ] = canonical_json(
                        [
                            int(j)
                            for j
                            in planted_coordinates
                        ]
                    )

                    # Planted-coordinate sign derived from persisted support.
                    row[
                        "planted_coordinate_signs_json"
                    ] = canonical_json(
                        planted_coordinate_signs_from_persisted_support(
                            row[
                                "stability_signed_support_json"
                            ],
                            planted_coordinates,
                        )
                    )

                    rows.append(
                        row
                    )

                raw_df = (
                    pd.DataFrame(
                        rows
                    )
                    .sort_values(
                        "diagnostic_seed"
                    )
                    .reset_index(
                        drop=True
                    )
                )

                # §20 provenance boundary.
                #
                # Persist the per-perturbation table before computing any
                # recurrence/sign counts, pairwise Jaccards, I/G, or cell
                # verdict. The persisted file is then reloaded and becomes
                # the sole authoritative aggregation input.
                preaggregate_paths = checkpoint_paths(
                    checkpoint_dir,
                    tau_index=cell.tau_index,
                    target_n=target_n,
                )

                checkpoint_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                atomic_write_csv(
                    raw_df,
                    preaggregate_paths["raw"],
                )

                persisted_raw_df = pd.read_csv(
                    preaggregate_paths["raw"]
                )

                if len(persisted_raw_df) != 100:
                    raise CalibrationContractError(
                        "Persisted pre-aggregation raw cell does not "
                        "contain exactly 100 perturbations."
                    )

                (
                    aggregate_row,
                    pair_df,
                ) = aggregate_step4b_cell(
                    persisted_raw_df,
                    planted_coordinates=planted_coordinates,
                )

                write_cell_checkpoint(
                    checkpoint_dir=checkpoint_dir,
                    perturbation_rows=persisted_raw_df,
                    pair_rows=pair_df,
                    aggregate_row=aggregate_row,
                    planted_coordinates=planted_coordinates,
                    dataset_seed=dataset_seed,
                )

                # All downstream authoritative concatenation also uses
                # the persisted/reloaded table.
                raw_df = persisted_raw_df

                print(
                    "[cell checkpointed] "
                    f"tau_index={cell.tau_index} "
                    f"N={target_n}"
                )

            raw_blocks.append(
                raw_df
            )

            pair_blocks.append(
                pair_df
            )

            summary_rows.append(
                aggregate_row
            )

    # ------------------------------------------------------------------
    # Complete authoritative output archive FIRST.
    # ------------------------------------------------------------------

    all_raw = (
        pd.concat(
            raw_blocks,
            ignore_index=True,
        )
        .sort_values(
            [
                "tau_index",
                "target_n",
                "diagnostic_seed",
            ]
        )
        .reset_index(drop=True)
    )

    all_pairs = (
        pd.concat(
            pair_blocks,
            ignore_index=True,
        )
        .sort_values(
            [
                "tau_index",
                "target_n",
                "diagnostic_seed_i",
                "diagnostic_seed_j",
            ]
        )
        .reset_index(drop=True)
    )

    all_summary = (
        pd.DataFrame(
            summary_rows
        )
        .sort_values(
            [
                "tau_index",
                "target_n",
            ]
        )
        .reset_index(drop=True)
    )

    expected_raw_rows = (
        total_cells
        * 100
    )

    expected_pair_rows = (
        total_cells
        * 4950
    )

    if len(
        all_raw
    ) != expected_raw_rows:
        raise CalibrationContractError(
            f"Expected {expected_raw_rows} raw rows; "
            f"got {len(all_raw)}."
        )

    if len(
        all_pairs
    ) != expected_pair_rows:
        raise CalibrationContractError(
            f"Expected {expected_pair_rows} pair rows; "
            f"got {len(all_pairs)}."
        )

    if len(
        all_summary
    ) != total_cells:
        raise CalibrationContractError(
            f"Expected {total_cells} cell rows; "
            f"got {len(all_summary)}."
        )

    atomic_write_csv(
        all_raw,
        raw_final,
    )

    atomic_write_csv(
        all_pairs,
        pairs_final,
    )

    atomic_write_csv(
        all_summary,
        summary_final,
    )

    archive_payload = {
        "status":
            "ARCHIVED_BEFORE_CANDIDATE_VERDICT",

        "scenario":
            S7_SCENARIO,

        "diagnostic_namespace":
            "920001-920100 CONSUMED",

        "validation_namespace":
            "2000-2099 SEALED",

        "reserved_calibration_namespace":
            "4000-4099 UNOPENED",

        "total_cells":
            total_cells,

        "n_perturbations_per_cell":
            100,

        "n_pairwise_comparisons_per_cell":
            4950,

        "raw_rows":
            int(
                len(
                    all_raw
                )
            ),

        "pairwise_rows":
            int(
                len(
                    all_pairs
                )
            ),

        "summary_rows":
            int(
                len(
                    all_summary
                )
            ),

        "raw_sha256":
            sha256_file(
                raw_final
            ),

        "pairwise_sha256":
            sha256_file(
                pairs_final
            ),

        "summary_sha256":
            sha256_file(
                summary_final
            ),

        "gamma_selected":
            False,
    }

    atomic_write_json(
        archive_payload,
        archive_manifest,
    )

    # ------------------------------------------------------------------
    # Only after archive: apply frozen 9-of-9 candidate rule.
    # ------------------------------------------------------------------

    archived_summary = pd.read_csv(
        summary_final
    )

    verdict = build_candidate_verdict(
        archived_summary
    )

    verdict[
        "authoritative_summary_sha256"
    ] = sha256_file(
        summary_final
    )

    verdict[
        "archive_manifest_sha256"
    ] = sha256_file(
        archive_manifest
    )

    atomic_write_json(
        verdict,
        verdict_path,
    )

    elapsed = (
        time.monotonic()
        - start_time
    )

    print()
    print("S7 STEP-4b DIAGNOSTIC COMPLETE.")
    print("Raw perturbations :", raw_final)
    print("Pairwise Jaccards :", pairs_final)
    print("Cell summaries    :", summary_final)
    print("Archive manifest  :", archive_manifest)
    print("Candidate verdict :", verdict_path)
    print(
        "Elapsed seconds   :",
        f"{elapsed:.1f}",
    )
    print("No gamma threshold was selected.")
    print("No validation seed was used.")
    print("No biological activation was accessed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Experiment 04 Arm-B S7 step-4b redesign diagnostic."
        )
    )

    parser.add_argument(
        "--execute-s7-step4b-diagnostic",
        action="store_true",
        help=(
            "Explicit execution switch. This cannot execute while "
            "EXECUTION_ENABLED is False."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=(
            HERE
            / "s7_step4b_diagnostic"
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # First executable boundary.
    if EXECUTION_ENABLED is not True:
        raise SystemExit(
            "S7 step-4b diagnostic is HARD-DISABLED in this commit. "
            "A separate enablement commit must be pushed and "
            "remote-verified before execution."
        )

    if not args.execute_s7_step4b_diagnostic:
        raise SystemExit(
            "S7 step-4b diagnostic was NOT executed. "
            "Pass --execute-s7-step4b-diagnostic only after the "
            "enabled checkpoint has been pushed and remote-verified."
        )

    run_s7_step4b_diagnostic(
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
