#!/usr/bin/env python3
"""
Experiment 04 Arm-B calibration — Step 1 only.

Purpose
-------
Compute and persist raw calibration statistics under the fully frozen
pre-calibration instrument.

This script deliberately does NOT:

- select gamma_P;
- select gamma_S;
- select gamma_I;
- select gamma_G;
- evaluate PROBE STABLE;
- enforce final positive/negative-control thresholds;
- access validation seeds 2000-2099;
- access biological activations;
- modify PROTOCOL.md.

Its terminal products are:

1. one per-perturbation table containing Stage-A prediction and Stage-B
   coefficient properties;
2. one per-cell table containing P_stat, S_stat, I_stat and G_stat.

Threshold choice is a separate later calibration-analysis step.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

import numpy as np
import pandas as pd

from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


# ============================================================
# Local import of frozen generators
# ============================================================

HERE = Path(__file__).resolve().parent

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from synthetic_generators import (  # noqa: E402
    MASTER_TAU,
    S1_TAU,
    S2_TAU,
    generate_s0,
    generate_s1,
    generate_s2,
    generate_s3,
    generate_s4,
    generate_s5,
    generate_s6,
    generate_s7,
)


# ============================================================
# Frozen calibration constants
# ============================================================

CALIBRATION_SEEDS = tuple(range(1000, 1100))
VALIDATION_SEEDS = frozenset(range(2000, 2100))

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

N_CV_FOLDS = 5

S3_RHO = (0.70, 0.90, 0.99)
S6_RHO = (0.30, 0.60, 0.90)

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

EXPECTED_STAGE_A_FIT_CHILDREN = 9 * 5 + 1
assert EXPECTED_STAGE_A_FIT_CHILDREN == 46


# ============================================================
# Exceptions
# ============================================================

class CalibrationContractError(RuntimeError):
    """Frozen calibration contract was violated."""


class CalibrationFitFailure(RuntimeError):
    """Frozen solver configuration produced a fit/convergence failure."""


# ============================================================
# Scenario-cell definition
# ============================================================

@dataclass(frozen=True)
class ScenarioCell:
    scenario: str
    scenario_id: int
    tau: Optional[float]
    tau_index: int
    rho: Optional[float]
    rho_index: int


# ============================================================
# Frozen SeedSequence mechanics
# ============================================================

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

    Independent of calibration seed, N and rho.
    """
    return np.random.SeedSequence(
        [
            int(scenario_id),
            int(tau_index),
            DATASET_NAMESPACE,
        ]
    )


def runner_seedsequence(
    calibration_seed: int,
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
            int(calibration_seed),
            int(scenario_id),
            int(tau_index),
            int(rho_index),
            int(target_n),
            RUNNER_NAMESPACE,
            int(stream_id),
        ]
    )


# ============================================================
# Frozen tau indexing
# ============================================================

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


# ============================================================
# Frozen scenario grid
# ============================================================

def scenario_cells() -> tuple[ScenarioCell, ...]:
    cells: list[ScenarioCell] = []

    # S0: no public tau/rho; frozen namespace sentinels are zero.
    cells.append(
        ScenarioCell(
            scenario="S0",
            scenario_id=SCENARIO_ID["S0"],
            tau=None,
            tau_index=0,
            rho=None,
            rho_index=0,
        )
    )

    # S1: frozen strong-signal subset only.
    for tau in S1_TAU:
        cells.append(
            ScenarioCell(
                scenario="S1",
                scenario_id=SCENARIO_ID["S1"],
                tau=float(tau),
                tau_index=master_tau_index(float(tau)),
                rho=None,
                rho_index=0,
            )
        )

    # S2: frozen weak-signal subset only.
    for tau in S2_TAU:
        cells.append(
            ScenarioCell(
                scenario="S2",
                scenario_id=SCENARIO_ID["S2"],
                tau=float(tau),
                tau_index=master_tau_index(float(tau)),
                rho=None,
                rho_index=0,
            )
        )

    # S3: full master tau ladder x frozen rho ladder.
    for tau in MASTER_TAU:
        for rho_index, rho in enumerate(S3_RHO):
            cells.append(
                ScenarioCell(
                    scenario="S3",
                    scenario_id=SCENARIO_ID["S3"],
                    tau=float(tau),
                    tau_index=master_tau_index(float(tau)),
                    rho=float(rho),
                    rho_index=int(rho_index),
                )
            )

    # S4 and S5: full master tau ladder.
    for scenario in ("S4", "S5"):
        for tau in MASTER_TAU:
            cells.append(
                ScenarioCell(
                    scenario=scenario,
                    scenario_id=SCENARIO_ID[scenario],
                    tau=float(tau),
                    tau_index=master_tau_index(float(tau)),
                    rho=None,
                    rho_index=0,
                )
            )

    # S6: full master tau ladder x frozen covariance ladder.
    for tau in MASTER_TAU:
        for rho_index, rho in enumerate(S6_RHO):
            cells.append(
                ScenarioCell(
                    scenario="S6",
                    scenario_id=SCENARIO_ID["S6"],
                    tau=float(tau),
                    tau_index=master_tau_index(float(tau)),
                    rho=float(rho),
                    rho_index=int(rho_index),
                )
            )

    # S7: full master tau ladder.
    for tau in MASTER_TAU:
        cells.append(
            ScenarioCell(
                scenario="S7",
                scenario_id=SCENARIO_ID["S7"],
                tau=float(tau),
                tau_index=master_tau_index(float(tau)),
                rho=None,
                rho_index=0,
            )
        )

    return tuple(cells)


# ============================================================
# Keyword-only frozen generator dispatch
# ============================================================

def generate_cell_dataset(
    cell: ScenarioCell,
    dataset_seed: int,
):
    """
    All generator calls use explicit keyword arguments.

    In particular this avoids the S3/S6 positional-order mismatch.
    """
    if cell.scenario == "S0":
        return generate_s0(
            seed=dataset_seed,
        )

    if cell.scenario == "S1":
        return generate_s1(
            seed=dataset_seed,
            tau=cell.tau,
        )

    if cell.scenario == "S2":
        return generate_s2(
            seed=dataset_seed,
            tau=cell.tau,
        )

    if cell.scenario == "S3":
        return generate_s3(
            seed=dataset_seed,
            rho=cell.rho,
            tau=cell.tau,
        )

    if cell.scenario == "S4":
        return generate_s4(
            seed=dataset_seed,
            tau=cell.tau,
        )

    if cell.scenario == "S5":
        return generate_s5(
            seed=dataset_seed,
            tau=cell.tau,
        )

    if cell.scenario == "S6":
        return generate_s6(
            seed=dataset_seed,
            tau=cell.tau,
            rho=cell.rho,
        )

    if cell.scenario == "S7":
        return generate_s7(
            seed=dataset_seed,
            tau=cell.tau,
        )

    raise CalibrationContractError(
        f"Unknown scenario: {cell.scenario}"
    )


# ============================================================
# Frozen solver
# ============================================================

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
    Any convergence warning/failure is an instrument-level calibration failure.
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


# ============================================================
# Frozen target-N subsampling
# ============================================================

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


# ============================================================
# Frozen Stage-A split
# ============================================================

TRAIN_PER_CLASS = {
    100: 80,
    120: 96,
    139: 111,
}


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


# ============================================================
# Frozen R2 one-standard-error selection
# ============================================================

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


# ============================================================
# One frozen perturbation
# ============================================================

def run_one_perturbation(
    cell: ScenarioCell,
    *,
    calibration_seed: int,
    target_n: int,
    dataset,
) -> dict:
    if calibration_seed not in CALIBRATION_SEEDS:
        raise CalibrationContractError(
            f"Step 1 accepts calibration seeds 1000-1099 only; "
            f"got {calibration_seed}."
        )

    if calibration_seed in VALIDATION_SEEDS:
        raise CalibrationContractError(
            "Validation seed access is prohibited in Step 1."
        )

    c = int(calibration_seed)
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
        f"calibration_seed={c}; "
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

    K_t = int(len(selected_idx))

    support = tuple(
        int(j)
        for j in selected_idx.tolist()
    )

    signed_support = tuple(
        (
            int(j),
            1 if beta[j] > 0.0 else -1,
        )
        for j in selected_idx.tolist()
    )

    # --------------------------------------------------------
    # Raw perturbation record.
    # No gamma / gate / threshold exists here.
    # --------------------------------------------------------

    return {
        "scenario": cell.scenario,
        "scenario_id": cell.scenario_id,
        "calibration_seed": c,
        "target_n": N,
        "tau": cell.tau,
        "tau_index": cell.tau_index,
        "rho": cell.rho,
        "rho_index": cell.rho_index,
        "selected_C_R2": r2.selected_C,
        "R1_best_C": r2.best_C,
        "R1_best_mean_CV_AUROC": r2.best_mean,
        "R1_best_SE": r2.best_se,
        "R2_one_se_floor": r2.one_se_floor,
        "stage_A_heldout_AUROC": heldout_auc,
        "K_t": K_t,
        "support_indices_json": json.dumps(
            support,
            separators=(",", ":"),
        ),
        "signed_support_json": json.dumps(
            signed_support,
            separators=(",", ":"),
        ),
        "cv_mean_by_C_json": json.dumps(
            dict(zip(C_GRID, r2.cv_means)),
            separators=(",", ":"),
        ),
        "cv_se_by_C_json": json.dumps(
            dict(zip(C_GRID, r2.cv_ses)),
            separators=(",", ":"),
        ),
        "cv_fold_AUROC_json": json.dumps(
            {
                str(C): list(scores)
                for C, scores
                in zip(C_GRID, r2.fold_aurocs)
            },
            separators=(",", ":"),
        ),
        "stage_A_final_fit_seed": stage_a_final_seed,
        "stage_B_fit_seed": stage_b_seed,
        "cv_seed": cv_seed,
    }


# ============================================================
# Frozen I/G statistics
# ============================================================

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


def aggregate_cell(
    perturbation_rows: pd.DataFrame,
) -> dict:
    """
    Aggregate exactly 100 perturbations into raw P/S/I/G statistics.
    """
    if len(perturbation_rows) != 100:
        raise CalibrationContractError(
            f"Expected exactly 100 perturbation rows, "
            f"got {len(perturbation_rows)}."
        )

    seeds = tuple(
        sorted(
            int(x)
            for x in perturbation_rows[
                "calibration_seed"
            ].tolist()
        )
    )

    if seeds != CALIBRATION_SEEDS:
        raise CalibrationContractError(
            "Cell does not contain exactly calibration seeds 1000-1099."
        )

    auc = perturbation_rows[
        "stage_A_heldout_AUROC"
    ].to_numpy(dtype=float)

    K = perturbation_rows[
        "K_t"
    ].to_numpy(dtype=float)

    P_stat = float(np.median(auc))
    S_stat = float(np.median(K))

    supports = [
        frozenset(
            int(x)
            for x in json.loads(value)
        )
        for value in perturbation_rows[
            "support_indices_json"
        ].tolist()
    ]

    signed_supports = [
        frozenset(
            (int(pair[0]), int(pair[1]))
            for pair in json.loads(value)
        )
        for value in perturbation_rows[
            "signed_support_json"
        ].tolist()
    ]

    I_values: list[float] = []
    G_values: list[float] = []

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

            # Frozen structural invariant.
            if G_pair > I_pair + 1e-15:
                raise CalibrationContractError(
                    f"G_pair > I_pair for pair ({i}, {j})."
                )

            I_values.append(I_pair)
            G_values.append(G_pair)

    if len(I_values) != 4950:
        raise CalibrationContractError(
            f"Expected 4950 I pairs; got {len(I_values)}."
        )

    if len(G_values) != 4950:
        raise CalibrationContractError(
            f"Expected 4950 G pairs; got {len(G_values)}."
        )

    I_stat = float(
        np.median(
            np.asarray(I_values, dtype=float)
        )
    )

    G_stat = float(
        np.median(
            np.asarray(G_values, dtype=float)
        )
    )

    if G_stat > I_stat + 1e-15:
        raise CalibrationContractError(
            "Frozen invariant G_stat <= I_stat violated."
        )

    first = perturbation_rows.iloc[0]

    selected_counts = Counter(
        float(x)
        for x in perturbation_rows[
            "selected_C_R2"
        ].tolist()
    )

    zero_fit_fraction = float(
        np.mean(
            perturbation_rows["K_t"].to_numpy(
                dtype=float
            ) == 0
        )
    )

    return {
        "scenario": first["scenario"],
        "scenario_id": int(first["scenario_id"]),
        "target_n": int(first["target_n"]),
        "tau": (
            None
            if pd.isna(first["tau"])
            else float(first["tau"])
        ),
        "tau_index": int(first["tau_index"]),
        "rho": (
            None
            if pd.isna(first["rho"])
            else float(first["rho"])
        ),
        "rho_index": int(first["rho_index"]),
        "n_perturbations": 100,
        "P_stat": P_stat,
        "S_stat": S_stat,
        "I_stat": I_stat,
        "G_stat": G_stat,
        "selected_C_counts_json": json.dumps(
            {
                str(k): int(v)
                for k, v in sorted(
                    selected_counts.items()
                )
            },
            separators=(",", ":"),
        ),
        "R2_zero_coefficient_fraction": zero_fit_fraction,
        "stage_A_AUROC_min": float(np.min(auc)),
        "stage_A_AUROC_max": float(np.max(auc)),
        "K_t_min": int(np.min(K)),
        "K_t_max": int(np.max(K)),
    }


# ============================================================
# Execution
# ============================================================

def run_step1(output_dir: Path) -> None:
    """
    Execute calibration Step 1 and persist raw statistics.

    IMPORTANT:
    This function opens calibration seeds 1000-1099.
    """
    output_dir = output_dir.resolve()
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    perturbation_path = (
        output_dir
        / "arm_b_step1_per_perturbation.csv"
    )

    cell_path = (
        output_dir
        / "arm_b_step1_cell_statistics.csv"
    )

    if perturbation_path.exists() or cell_path.exists():
        raise CalibrationContractError(
            "Step-1 output already exists. "
            "Refusing to overwrite a calibration record."
        )

    raw_rows: list[dict] = []
    aggregate_rows: list[dict] = []

    cells = scenario_cells()

    print(
        "OPENING CALIBRATION BLOCK 1000-1099.\n"
        "Validation block 2000-2099 remains sealed.\n"
        "No numerical P/S/I/G threshold is used by this script."
    )

    for cell_index, cell in enumerate(cells, start=1):

        print(
            f"[cell {cell_index}/{len(cells)}] "
            f"{cell.scenario} "
            f"tau={cell.tau} "
            f"rho={cell.rho}"
        )

        cell_rows: list[dict] = []

        # One frozen synthetic dataset per scenario/tau setting.
        # The same generator seed is reused across rho and across all
        # calibration perturbations.
        dataset_ss = dataset_seedsequence(
            cell.scenario_id,
            cell.tau_index,
        )

        dataset_seed = seedsequence_to_uint32(
            dataset_ss
        )

        dataset = generate_cell_dataset(
            cell,
            dataset_seed,
        )

        # One calibration seed = one post-generation perturbation identity.
        for calibration_seed in CALIBRATION_SEEDS:

            for target_n in TARGET_N_VALUES:
                row = run_one_perturbation(
                    cell,
                    calibration_seed=calibration_seed,
                    target_n=target_n,
                    dataset=dataset,
                )

                row["dataset_seed"] = dataset_seed

                raw_rows.append(row)
                cell_rows.append(row)

        cell_df = pd.DataFrame(cell_rows)

        for target_n in TARGET_N_VALUES:
            subset = (
                cell_df[
                    cell_df["target_n"] == target_n
                ]
                .sort_values("calibration_seed")
                .reset_index(drop=True)
            )

            aggregate_rows.append(
                aggregate_cell(subset)
            )

    raw_df = pd.DataFrame(raw_rows)
    agg_df = pd.DataFrame(aggregate_rows)

    # No threshold/gate columns may exist.
    forbidden_columns = {
        "gamma_P",
        "gamma_S",
        "gamma_I",
        "gamma_G",
    }

    if forbidden_columns & set(raw_df.columns):
        raise CalibrationContractError(
            "Threshold/gate column appeared in raw output."
        )

    if forbidden_columns & set(agg_df.columns):
        raise CalibrationContractError(
            "Threshold/gate column appeared in aggregate output."
        )

    raw_df.to_csv(
        perturbation_path,
        index=False,
    )

    agg_df.to_csv(
        cell_path,
        index=False,
    )

    print("\nSTEP 1 COMPLETE.")
    print("Raw perturbations :", perturbation_path)
    print("Cell statistics    :", cell_path)
    print("No threshold was selected.")
    print("No validation seed was used.")
    print("No biological activation was accessed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Experiment 04 Arm-B calibration Step 1: "
            "raw statistics only."
        )
    )

    parser.add_argument(
        "--execute-calibration",
        action="store_true",
        help=(
            "Required explicit switch. "
            "Opens calibration seeds 1000-1099."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE / "calibration_step1",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.execute_calibration:
        raise SystemExit(
            "Calibration was NOT executed. "
            "Pass --execute-calibration only after the runner "
            "has been statically inspected, committed and pushed."
        )

    run_step1(
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
