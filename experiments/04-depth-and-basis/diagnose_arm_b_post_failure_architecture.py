#!/usr/bin/env python3
"""
Experiment 04 — Arm-B post-failure architecture diagnostic scaffold.

Purpose
-------
This file is derived from the frozen calibration runner
`calibrate_sparse_probe_step1.py` as the implementation scaffold for the
post-failure Arm-B architecture diagnostic governed by:

- `ARM_B_POST_FAILURE_ARCHITECTURE_AMENDMENT.md`;
- `ARM_B_POST_FAILURE_DIAGNOSTIC_CONTRACT.md`;
- `ARM_B_POST_FAILURE_DIAGNOSTIC_BLINDING_ADDENDUM.md`.

Scaffold provenance
-------------------
The initial scaffold copy was byte-identical to:

    calibrate_sparse_probe_step1.py

with SHA-256:

    90fe845e53142bc284220422b2f437c2537c670caae6e1566c85cd5c1ca2f134

Diagnostic namespace:

    910001-910100

Calibration reserve `4000-4099` remains unopened.
Independent-validation block `2000-2099` remains sealed.

Current status
--------------
This is the complete enabled implementation of the Arm-B post-failure
architecture diagnostic.

Diagnostic namespace:

    910001-910100

must not be opened until this enablement commit has been reviewed, committed,
pushed and remote-verified.

The diagnostic runner must not emit or persist final P/S/I/G statistics or
pairwise-Jaccard summaries for `910001-910100`.
"""


from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
# Frozen diagnostic, calibration-reserve and runner constants
# ============================================================

DIAGNOSTIC_SEEDS = tuple(range(910001, 910101))

VALIDATION_SEEDS = frozenset(range(2000, 2100))

CONSUMED_CALIBRATION_SEEDS = (
    frozenset(range(1000, 1100))
    | frozenset(range(3000, 3100))
)

RESERVED_CALIBRATION_SEEDS = (
    frozenset(range(4000, 4100))
    | frozenset(range(5000, 5100))
)

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
STREAM_STABILITY_SUBSAMPLE = 26
STREAM_STABILITY_FIT = 27

STABILITY_FRACTION = 0.80

EXPECTED_STAGE_A_FIT_CHILDREN = 9 * 5 + 1
assert EXPECTED_STAGE_A_FIT_CHILDREN == 46

# Diagnostic namespace firewall.
_DIAGNOSTIC_SET = frozenset(DIAGNOSTIC_SEEDS)

assert len(DIAGNOSTIC_SEEDS) == 100
assert len(_DIAGNOSTIC_SET) == 100

assert _DIAGNOSTIC_SET.isdisjoint(VALIDATION_SEEDS)
assert _DIAGNOSTIC_SET.isdisjoint(CONSUMED_CALIBRATION_SEEDS)
assert _DIAGNOSTIC_SET.isdisjoint(RESERVED_CALIBRATION_SEEDS)

assert VALIDATION_SEEDS.isdisjoint(CONSUMED_CALIBRATION_SEEDS)
assert VALIDATION_SEEDS.isdisjoint(RESERVED_CALIBRATION_SEEDS)
assert CONSUMED_CALIBRATION_SEEDS.isdisjoint(
    RESERVED_CALIBRATION_SEEDS
)


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


def run_one_perturbation(
    cell: ScenarioCell,
    *,
    diagnostic_seed: int,
    target_n: int,
    dataset,
) -> dict:
    if diagnostic_seed not in DIAGNOSTIC_SEEDS:
        raise CalibrationContractError(
            f"Architecture diagnostic accepts diagnostic seeds 910001-910100 only; "
            f"got {diagnostic_seed}."
        )

    if diagnostic_seed in VALIDATION_SEEDS:
        raise CalibrationContractError(
            "Validation seed access is prohibited in the architecture diagnostic."
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


# ============================================================
# Diagnostic blinding and architecture aggregation
# ============================================================

def assert_blinded_output_schema(
    columns,
    *,
    context: str,
) -> None:
    """
    Enforce the diagnostic blinding firewall on persisted/output schemas.

    This checks field names only. The procedural firewall governing
    reconstructible quantities from retained supports remains separately
    frozen by the blinding addendum.
    """
    names = {
        str(column)
        for column in columns
    }

    forbidden_exact = {
        "P_stat",
        "S_stat",
        "I_stat",
        "G_stat",
        "PROBE_STABLE",
        "probe_stable",
        "stage_A_heldout_AUROC",
        "R1_best_mean_CV_AUROC",
        "R1_best_SE",
        "R2_one_se_floor",
        "cv_mean_by_C_json",
        "cv_se_by_C_json",
        "cv_fold_AUROC_json",
    }

    exact_hits = sorted(
        names & forbidden_exact
    )

    gamma_hits = sorted(
        name
        for name in names
        if name.lower().startswith("gamma_")
    )

    jaccard_hits = sorted(
        name
        for name in names
        if "jaccard" in name.lower()
    )

    auroc_hits = sorted(
        name
        for name in names
        if "auroc" in name.lower()
    )

    stable_gate_hits = sorted(
        name
        for name in names
        if "probe_stable" in name.lower()
    )

    hits = sorted(
        set(
            exact_hits
            + gamma_hits
            + jaccard_hits
            + auroc_hits
            + stable_gate_hits
        )
    )

    if hits:
        raise CalibrationContractError(
            f"Blinding violation in {context}: "
            f"forbidden output fields {hits}."
        )



def aggregate_architecture_cell(
    perturbation_rows: pd.DataFrame,
) -> dict:
    """
    Aggregate exactly 100 diagnostic perturbations into architecture-only
    quantities and enforce the frozen §9 architecture invariants.

    This function deliberately computes no P/S/I/G statistic and no
    pairwise-Jaccard quantity.
    """
    if len(perturbation_rows) != 100:
        raise CalibrationContractError(
            f"Expected exactly 100 perturbation rows, "
            f"got {len(perturbation_rows)}."
        )

    assert_blinded_output_schema(
        perturbation_rows.columns,
        context="per-perturbation diagnostic table",
    )

    required = {
        "scenario",
        "scenario_id",
        "diagnostic_seed",
        "target_n",
        "tau",
        "tau_index",
        "rho",
        "rho_index",
        "selected_C_R2",
        "K_t_full",
        "K_t_stab",
        "full_support_indices_json",
        "full_signed_support_json",
        "stability_support_indices_json",
        "stability_signed_support_json",
        "stability_positive_membership_json",
        "stability_negative_membership_json",
        "stability_membership_sha256",
        "stability_n_per_class",
        "stage_A_final_fit_seed",
        "stage_B_fit_seed",
        "stability_subsample_seed_identity_json",
        "stability_fit_seed",
    }

    missing = sorted(
        required - set(perturbation_rows.columns)
    )

    if missing:
        raise CalibrationContractError(
            f"Architecture aggregation missing required columns: "
            f"{missing}."
        )

    seeds = tuple(
        sorted(
            int(x)
            for x in perturbation_rows[
                "diagnostic_seed"
            ].tolist()
        )
    )

    if seeds != DIAGNOSTIC_SEEDS:
        raise CalibrationContractError(
            "Architecture cell does not contain exactly "
            "diagnostic seeds 910001-910100."
        )

    if perturbation_rows[
        "diagnostic_seed"
    ].duplicated().any():
        raise CalibrationContractError(
            "Architecture cell contains duplicate diagnostic seeds."
        )

    identity_columns = [
        "scenario",
        "scenario_id",
        "target_n",
        "tau_index",
        "rho_index",
    ]

    for column in identity_columns:
        if perturbation_rows[column].nunique(dropna=False) != 1:
            raise CalibrationContractError(
                f"Architecture cell mixes values in {column}."
            )

    first = perturbation_rows.iloc[0]

    scenario_id = int(first["scenario_id"])
    tau_index = int(first["tau_index"])
    rho_index = int(first["rho_index"])
    N = int(first["target_n"])

    expected_stability_n = {
        100: 80,
        120: 96,
        139: 111,
    }.get(N)

    if expected_stability_n is None:
        raise CalibrationContractError(
            f"Unexpected target N in architecture aggregation: {N}."
        )

    observed_stability_n = {
        int(x)
        for x in perturbation_rows[
            "stability_n_per_class"
        ].tolist()
    }

    if observed_stability_n != {expected_stability_n}:
        raise CalibrationContractError(
            "Stability per-class size does not match the frozen "
            f"0.80 rule for N={N}: {sorted(observed_stability_n)}."
        )

    # --------------------------------------------------------
    # §9 deterministic stream-26 identity and membership audit
    # --------------------------------------------------------

    observed_stream26_identities = []

    direct_memberships = []

    for _, row in perturbation_rows.iterrows():
        diagnostic_seed = int(
            row["diagnostic_seed"]
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
            N,
            RUNNER_NAMESPACE,
            STREAM_STABILITY_SUBSAMPLE,
        )

        if observed_identity != expected_identity:
            raise CalibrationContractError(
                "Stored stream-26 seed identity does not match "
                f"the frozen derivation for diagnostic seed "
                f"{diagnostic_seed}."
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

        # Membership indices are in target-N-pool index space.
        # select_target_n currently returns all positives then all negatives,
        # so direct range checks are exact for the frozen implementation.
        if any(
            not (0 <= idx < N)
            for idx in pos_membership
        ):
            raise CalibrationContractError(
                "Stored positive stability membership lies outside "
                "the positive target-pool range."
            )

        if any(
            not (N <= idx < 2 * N)
            for idx in neg_membership
        ):
            raise CalibrationContractError(
                "Stored negative stability membership lies outside "
                "the negative target-pool range."
            )

        membership_payload = {
            "positive_target_pool_indices": list(
                pos_membership
            ),
            "negative_target_pool_indices": list(
                neg_membership
            ),
        }

        membership_json = json.dumps(
            membership_payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        recomputed_sha256 = hashlib.sha256(
            membership_json.encode("utf-8")
        ).hexdigest()

        if (
            recomputed_sha256
            != str(
                row["stability_membership_sha256"]
            )
        ):
            raise CalibrationContractError(
                "Stored stability-membership SHA-256 does not "
                "match the persisted membership."
            )

        # Reconstruct stream 26 directly from the frozen SeedSequence
        # and verify exact ordered membership equality.
        stream26_ss = runner_seedsequence(
            diagnostic_seed,
            scenario_id,
            tau_index,
            rho_index,
            N,
            STREAM_STABILITY_SUBSAMPLE,
        )

        replay_rng = np.random.default_rng(
            stream26_ss
        )

        # Reconstruct the frozen target-pool labels. In the current
        # select_target_n implementation Xn/yn are positive rows first,
        # negative rows second.
        replay_y = np.concatenate(
            [
                np.ones(N, dtype=int),
                np.zeros(N, dtype=int),
            ]
        )

        (
            _,
            replay_pos,
            replay_neg,
            replay_sha256,
        ) = select_stability_subsample(
            replay_y,
            target_n=N,
            rng=replay_rng,
        )

        if tuple(
            int(x)
            for x in replay_pos.tolist()
        ) != pos_membership:
            raise CalibrationContractError(
                "Positive stability membership is not reproducible "
                "from the frozen stream-26 construction."
            )

        if tuple(
            int(x)
            for x in replay_neg.tolist()
        ) != neg_membership:
            raise CalibrationContractError(
                "Negative stability membership is not reproducible "
                "from the frozen stream-26 construction."
            )

        if replay_sha256 != recomputed_sha256:
            raise CalibrationContractError(
                "Replayed stability-membership SHA-256 mismatch."
            )

        direct_memberships.append(
            (
                pos_membership,
                neg_membership,
            )
        )

    n_distinct_stream26_identities = int(
        len(set(observed_stream26_identities))
    )

    if n_distinct_stream26_identities != 100:
        raise CalibrationContractError(
            "Architecture diagnostic requires exactly 100 distinct "
            "stream-26 identities per cell."
        )

    n_distinct_stability_memberships = int(
        len(set(direct_memberships))
    )

    # Duplicate realized membership is probabilistically possible even
    # under correct sampling. It is not declared logically impossible,
    # but the frozen contract requires diagnostic execution to halt for
    # explicit investigation rather than silently accepting it.
    duplicate_membership_count = int(
        100 - n_distinct_stability_memberships
    )

    if duplicate_membership_count != 0:
        raise CalibrationContractError(
            "Architecture diagnostic observed duplicate realized "
            "stability-subsample membership within a cell. "
            "Execution must stop for explicit investigation."
        )

    # --------------------------------------------------------
    # Architecture support/C/cardinality summaries
    # --------------------------------------------------------

    support_counts = perturbation_rows[
        "stability_support_indices_json"
    ].value_counts(dropna=False)

    n_distinct_stability_supports = int(
        len(support_counts)
    )

    largest_identical_support_clique = int(
        support_counts.iloc[0]
    )

    selected_C_values = perturbation_rows[
        "selected_C_R2"
    ]

    n_distinct_selected_C = int(
        selected_C_values.nunique(dropna=False)
    )

    K_full = perturbation_rows[
        "K_t_full"
    ].to_numpy(dtype=float)

    K_stab = perturbation_rows[
        "K_t_stab"
    ].to_numpy(dtype=float)

    median_K_t_full = float(
        np.median(K_full)
    )

    median_K_t_stab = float(
        np.median(K_stab)
    )

    min_K_t_stab = int(
        np.min(K_stab)
    )

    max_K_t_stab = int(
        np.max(K_stab)
    )

    empty_full_support_count = int(
        np.sum(K_full == 0)
    )

    singleton_full_support_count = int(
        np.sum(K_full == 1)
    )

    empty_stability_support_count = int(
        np.sum(K_stab == 0)
    )

    singleton_stability_support_count = int(
        np.sum(K_stab == 1)
    )

    if median_K_t_stab == 0:
        stability_collapse_class = "EMPTY"
    elif 0 < median_K_t_stab < 2:
        stability_collapse_class = "SINGLETON_DOMINATED"
    else:
        stability_collapse_class = (
            "NONDEGENERATE_FOR_ARCHITECTURE_DIAGNOSTIC"
        )

    if median_K_t_full == 0:
        full_collapse_class = "EMPTY"
    elif 0 < median_K_t_full < 2:
        full_collapse_class = "SINGLETON_DOMINATED"
    else:
        full_collapse_class = (
            "NONDEGENERATE_FOR_ARCHITECTURE_DIAGNOSTIC"
        )

    joint_collapse_class = (
        f"FULL_{full_collapse_class}"
        f"__STABILITY_{stability_collapse_class}"
    )

    full_fit_collapse = bool(
        median_K_t_full < 2
    )

    stability_fit_specific_collapse = bool(
        median_K_t_full >= 2
        and median_K_t_stab < 2
    )

    result = {
        "scenario": str(first["scenario"]),
        "scenario_id": scenario_id,
        "target_n": N,
        "tau": first["tau"],
        "tau_index": tau_index,
        "rho": first["rho"],
        "rho_index": rho_index,
        "n_perturbations": 100,
        "stability_n_per_class": expected_stability_n,
        "n_distinct_stream26_identities":
            n_distinct_stream26_identities,
        "n_distinct_stability_memberships":
            n_distinct_stability_memberships,
        "duplicate_stability_membership_count":
            duplicate_membership_count,
        "n_distinct_selected_C":
            n_distinct_selected_C,
        "n_distinct_stability_supports":
            n_distinct_stability_supports,
        "largest_identical_stability_support_clique":
            largest_identical_support_clique,
        "median_K_t_full": median_K_t_full,
        "median_K_t_stab": median_K_t_stab,
        "min_K_t_stab": min_K_t_stab,
        "max_K_t_stab": max_K_t_stab,
        "empty_full_support_count":
            empty_full_support_count,
        "singleton_full_support_count":
            singleton_full_support_count,
        "empty_stability_support_count":
            empty_stability_support_count,
        "singleton_stability_support_count":
            singleton_stability_support_count,
        "full_collapse_class":
            full_collapse_class,
        "stability_collapse_class":
            stability_collapse_class,
        "joint_collapse_class":
            joint_collapse_class,
        "full_fit_collapse":
            full_fit_collapse,
        "stability_fit_specific_collapse":
            stability_fit_specific_collapse,
    }

    assert_blinded_output_schema(
        result.keys(),
        context="architecture cell summary",
    )

    return result





# ============================================================
# Checkpoint persistence
# ============================================================

CELL_KEY_COLUMNS = (
    "scenario",
    "tau_index",
    "rho_index",
    "target_n",
)


def build_n120_n139_architecture_comparison(
    cell_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construct the frozen secondary N=120 versus N=139 architecture
    comparison.

    This is a terminal derivative of the completed authoritative cell-summary
    table. It exposes architecture quantities only and computes no P/S/I/G
    or pairwise-Jaccard statistic.
    """
    if cell_summary.empty:
        raise CalibrationContractError(
            "Cannot build N=120/N=139 comparison from an empty cell summary."
        )

    assert_blinded_output_schema(
        cell_summary.columns,
        context="N=120/N=139 comparison input",
    )

    required = {
        "scenario",
        "scenario_id",
        "tau",
        "tau_index",
        "rho",
        "rho_index",
        "target_n",
        "n_perturbations",
        "stability_n_per_class",
        "n_distinct_stream26_identities",
        "n_distinct_stability_memberships",
        "duplicate_stability_membership_count",
        "n_distinct_selected_C",
        "n_distinct_stability_supports",
        "largest_identical_stability_support_clique",
        "median_K_t_full",
        "median_K_t_stab",
        "min_K_t_stab",
        "max_K_t_stab",
        "empty_full_support_count",
        "singleton_full_support_count",
        "empty_stability_support_count",
        "singleton_stability_support_count",
        "full_collapse_class",
        "stability_collapse_class",
        "joint_collapse_class",
        "full_fit_collapse",
        "stability_fit_specific_collapse",
    }

    missing = sorted(
        required - set(cell_summary.columns)
    )

    if missing:
        raise CalibrationContractError(
            "N=120/N=139 architecture comparison missing "
            f"required columns: {missing}."
        )

    subset = cell_summary[
        cell_summary["target_n"].isin([120, 139])
    ].copy()

    key_columns = [
        "scenario",
        "scenario_id",
        "tau",
        "tau_index",
        "rho",
        "rho_index",
    ]

    if subset.duplicated(
        key_columns + ["target_n"]
    ).any():
        raise CalibrationContractError(
            "Duplicate architecture cell identity in "
            "N=120/N=139 comparison."
        )

    n120 = (
        subset[
            subset["target_n"] == 120
        ]
        .drop(columns=["target_n"])
        .set_index(key_columns)
        .sort_index()
    )

    n139 = (
        subset[
            subset["target_n"] == 139
        ]
        .drop(columns=["target_n"])
        .set_index(key_columns)
        .sort_index()
    )

    if n120.empty or n139.empty:
        raise CalibrationContractError(
            "N=120/N=139 comparison requires non-empty "
            "matched tables at both discovery sizes."
        )

    if not n120.index.equals(n139.index):
        only_120 = n120.index.difference(
            n139.index
        )
        only_139 = n139.index.difference(
            n120.index
        )

        raise CalibrationContractError(
            "N=120 and N=139 architecture cells are not exactly matched. "
            f"Only N=120: {len(only_120)}; "
            f"only N=139: {len(only_139)}."
        )

    comparison = (
        n120.join(
            n139,
            how="inner",
            lsuffix="_N120",
            rsuffix="_N139",
        )
        .reset_index()
    )

    if len(comparison) != len(n120):
        raise CalibrationContractError(
            f"N=120/N=139 join lost rows: {len(n120)} matched cells in, "
            f"{len(comparison)} out. Check NaN-keyed rho matching."
        )

    comparison.insert(
        len(key_columns),
        "comparison",
        "N120_vs_N139",
    )

    for suffix in ("N120", "N139"):
        identity_col = (
            f"n_distinct_stream26_identities_{suffix}"
        )

        if not (
            comparison[identity_col]
            .astype(int)
            .eq(100)
            .all()
        ):
            raise CalibrationContractError(
                "Terminal N=120/N=139 comparison contains a cell "
                f"without 100 stream-26 identities at {suffix}."
            )

    assert_blinded_output_schema(
        comparison.columns,
        context="N=120/N=139 architecture comparison",
    )

    return comparison

def cell_key_from_values(
    scenario: str,
    tau_index: int,
    rho_index: int,
    target_n: int,
) -> tuple[str, int, int, int]:
    return (
        str(scenario),
        int(tau_index),
        int(rho_index),
        int(target_n),
    )


def cell_key_from_row(row) -> tuple[str, int, int, int]:
    return cell_key_from_values(
        row["scenario"],
        row["tau_index"],
        row["rho_index"],
        row["target_n"],
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


def empty_or_read_csv(
    path: Path,
) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def load_manifest(
    manifest_path: Path,
) -> dict:
    if not manifest_path.exists():
        return {
            "diagnostic_seeds": list(DIAGNOSTIC_SEEDS),
            "completed_cells": [],
        }

    payload = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("diagnostic_seeds") != list(DIAGNOSTIC_SEEDS):
        raise CalibrationContractError(
            "Checkpoint manifest diagnostic-seed block "
            "does not match active DIAGNOSTIC_SEEDS."
        )

    if not isinstance(
        payload.get("completed_cells"),
        list,
    ):
        raise CalibrationContractError(
            "Checkpoint manifest completed_cells must be a list."
        )

    return payload


def completed_keys_from_manifest(
    manifest: dict,
) -> set[tuple[str, int, int, int]]:
    keys = set()

    for item in manifest["completed_cells"]:
        required = {
            "scenario",
            "tau_index",
            "rho_index",
            "target_n",
        }

        if set(item) != required:
            raise CalibrationContractError(
                "Malformed completed-cell manifest entry."
            )

        key = cell_key_from_values(
            item["scenario"],
            item["tau_index"],
            item["rho_index"],
            item["target_n"],
        )

        if key in keys:
            raise CalibrationContractError(
                f"Duplicate completed-cell manifest entry: {key}"
            )

        keys.add(key)

    return keys


def cell_mask(
    df: pd.DataFrame,
    key: tuple[str, int, int, int],
) -> pd.Series:
    scenario, tau_index, rho_index, target_n = key

    return (
        (df["scenario"].astype(str) == scenario)
        & (df["tau_index"].astype(int) == tau_index)
        & (df["rho_index"].astype(int) == rho_index)
        & (df["target_n"].astype(int) == target_n)
    )


def validate_completed_cell(
    key: tuple[str, int, int, int],
    raw_df: pd.DataFrame,
    agg_df: pd.DataFrame,
) -> None:
    """
    Frozen restart integrity checks for one authoritative cell.
    """
    if raw_df.empty or agg_df.empty:
        raise CalibrationContractError(
            f"Manifest marks {key} complete but checkpoint tables are empty."
        )

    required_raw_columns = {
        "scenario",
        "tau_index",
        "rho_index",
        "target_n",
        "diagnostic_seed",
    }

    required_agg_columns = {
        "scenario",
        "tau_index",
        "rho_index",
        "target_n",
        "n_perturbations",
    }

    if not required_raw_columns.issubset(raw_df.columns):
        raise CalibrationContractError(
            "Raw checkpoint table is missing required identity columns."
        )

    if not required_agg_columns.issubset(agg_df.columns):
        raise CalibrationContractError(
            "Aggregate checkpoint table is missing required identity columns."
        )

    raw_cell = raw_df.loc[
        cell_mask(raw_df, key)
    ].copy()

    agg_cell = agg_df.loc[
        cell_mask(agg_df, key)
    ].copy()

    if len(raw_cell) != 100:
        raise CalibrationContractError(
            f"Completed cell {key} has {len(raw_cell)} "
            "perturbation rows; expected 100."
        )

    observed_seeds = sorted(
        raw_cell["diagnostic_seed"]
        .astype(int)
        .tolist()
    )

    if observed_seeds != list(DIAGNOSTIC_SEEDS):
        raise CalibrationContractError(
            f"Completed cell {key} does not contain exactly "
            "diagnostic seeds 910001-910100."
        )

    if raw_cell["diagnostic_seed"].duplicated().any():
        raise CalibrationContractError(
            f"Completed cell {key} contains duplicate diagnostic seeds."
        )

    if len(agg_cell) != 1:
        raise CalibrationContractError(
            f"Completed cell {key} has {len(agg_cell)} aggregate rows; "
            "expected exactly one."
        )

    if int(agg_cell.iloc[0]["n_perturbations"]) != 100:
        raise CalibrationContractError(
            f"Completed cell {key} aggregate n_perturbations != 100."
        )

    if cell_key_from_row(agg_cell.iloc[0]) != key:
        raise CalibrationContractError(
            f"Aggregate identity mismatch for completed cell {key}."
        )

    assert_blinded_output_schema(
        raw_cell.columns,
        context=f"restarted raw checkpoint cell {key}",
    )

    assert_blinded_output_schema(
        agg_cell.columns,
        context=f"restarted architecture-summary cell {key}",
    )

    recomputed_summary = aggregate_architecture_cell(
        raw_cell
        .sort_values("diagnostic_seed")
        .reset_index(drop=True)
    )

    persisted_summary = agg_cell.iloc[0]

    for field, expected in recomputed_summary.items():
        if field not in persisted_summary.index:
            raise CalibrationContractError(
                f"Completed cell {key} aggregate is missing "
                f"recomputed field {field!r}."
            )

        observed = persisted_summary[field]

        if pd.isna(expected) and pd.isna(observed):
            continue

        if isinstance(expected, (float, np.floating)):
            if not np.isclose(
                float(observed),
                float(expected),
                rtol=0.0,
                atol=1e-12,
                equal_nan=True,
            ):
                raise CalibrationContractError(
                    f"Completed cell {key} aggregate mismatch for "
                    f"{field}: persisted={observed!r}, "
                    f"recomputed={expected!r}."
                )
        else:
            if observed != expected:
                raise CalibrationContractError(
                    f"Completed cell {key} aggregate mismatch for "
                    f"{field}: persisted={observed!r}, "
                    f"recomputed={expected!r}."
                )


def validate_checkpoint_identity_state(
    manifest: dict,
    raw_df: pd.DataFrame,
    agg_df: pd.DataFrame,
) -> set[tuple[str, int, int, int]]:
    """
    Cheap global checkpoint-consistency validation.

    Verifies only that authoritative raw/aggregate cell identities match the
    manifest. Scientific/deep validation is performed separately.
    """
    completed = completed_keys_from_manifest(
        manifest
    )

    if not raw_df.empty:
        raw_keys = {
            cell_key_from_row(row)
            for _, row in raw_df.iterrows()
        }

        if raw_keys != completed:
            raise CalibrationContractError(
                "Raw checkpoint table cell identities do not match manifest."
            )

    if not agg_df.empty:
        agg_keys = {
            cell_key_from_row(row)
            for _, row in agg_df.iterrows()
        }

        if agg_keys != completed:
            raise CalibrationContractError(
                "Aggregate checkpoint table cell identities "
                "do not match manifest."
            )

    return completed


def validate_checkpoint_state(
    manifest: dict,
    raw_df: pd.DataFrame,
    agg_df: pd.DataFrame,
) -> set[tuple[str, int, int, int]]:
    """
    Validate every manifest-completed cell and reject authoritative
    rows that are not represented by the manifest.
    """
    completed = completed_keys_from_manifest(
        manifest
    )

    for key in sorted(completed):
        validate_completed_cell(
            key,
            raw_df,
            agg_df,
        )

    return validate_checkpoint_identity_state(
        manifest,
        raw_df,
        agg_df,
    )


def append_completed_cell(
    *,
    cell_rows: pd.DataFrame,
    aggregate_row: dict,
    raw_df: pd.DataFrame,
    agg_df: pd.DataFrame,
    manifest: dict,
    raw_path: Path,
    cell_path: Path,
    manifest_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:

    if len(cell_rows) != 100:
        raise CalibrationContractError(
            f"Checkpoint candidate has {len(cell_rows)} rows; "
            "expected exactly 100."
        )

    observed_seeds = sorted(
        cell_rows["diagnostic_seed"]
        .astype(int)
        .tolist()
    )

    if observed_seeds != list(DIAGNOSTIC_SEEDS):
        raise CalibrationContractError(
            "Checkpoint candidate does not contain exactly diagnostic seeds 910001-910100."
        )

    if cell_rows["diagnostic_seed"].duplicated().any():
        raise CalibrationContractError(
            "Checkpoint candidate contains duplicate diagnostic seeds."
        )

    key = cell_key_from_row(
        cell_rows.iloc[0]
    )

    if any(
        cell_key_from_row(row) != key
        for _, row in cell_rows.iterrows()
    ):
        raise CalibrationContractError(
            "Checkpoint candidate contains mixed cell identities."
        )

    if cell_key_from_values(
        aggregate_row["scenario"],
        aggregate_row["tau_index"],
        aggregate_row["rho_index"],
        aggregate_row["target_n"],
    ) != key:
        raise CalibrationContractError(
            "Aggregate row identity does not match perturbation cell."
        )

    if int(aggregate_row["n_perturbations"]) != 100:
        raise CalibrationContractError(
            "Aggregate row n_perturbations != 100."
        )

    completed = completed_keys_from_manifest(
        manifest
    )

    if key in completed:
        raise CalibrationContractError(
            f"Refusing to recompute already completed cell: {key}"
        )

    if raw_df.empty:
        new_raw = cell_rows.copy()
    else:
        new_raw = pd.concat(
            [raw_df, cell_rows],
            ignore_index=True,
        )

    new_agg_row = pd.DataFrame(
        [aggregate_row]
    )

    if agg_df.empty:
        new_agg = new_agg_row
    else:
        new_agg = pd.concat(
            [agg_df, new_agg_row],
            ignore_index=True,
        )

    # Authoritative tables first.
    atomic_write_csv(
        new_raw,
        raw_path,
    )

    atomic_write_csv(
        new_agg,
        cell_path,
    )

    # Manifest only after BOTH tables have been atomically replaced.
    new_manifest = {
        "diagnostic_seeds": list(DIAGNOSTIC_SEEDS),
        "completed_cells": list(
            manifest["completed_cells"]
        )
        + [
            {
                "scenario": key[0],
                "tau_index": key[1],
                "rho_index": key[2],
                "target_n": key[3],
            }
        ],
    }

    atomic_write_json(
        new_manifest,
        manifest_path,
    )

    # Re-read and verify authoritative state immediately.
    verify_raw = pd.read_csv(raw_path)
    verify_agg = pd.read_csv(cell_path)
    verify_manifest = load_manifest(
        manifest_path
    )

    # Deep-validate only the newly written cell here.
    # All prior completed cells were already validated at startup or
    # immediately after their own atomic checkpoint.
    validate_completed_cell(
        key,
        verify_raw,
        verify_agg,
    )

    # Then retain the cheap global identity invariant.
    validate_checkpoint_identity_state(
        verify_manifest,
        verify_raw,
        verify_agg,
    )

    return (
        verify_raw,
        verify_agg,
        verify_manifest,
    )



# ============================================================
# Execution
# ============================================================

def run_architecture_diagnostic(output_dir: Path) -> None:
    """
    Execute the complete frozen Arm-B post-failure architecture diagnostic.

    This function opens diagnostic namespace `910001-910100` and therefore
    must be invoked only after the enablement commit containing this code has
    been pushed and remote-verified.
    """
    output_dir = output_dir.resolve()
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_path = (
        output_dir
        / "arm_b_post_failure_architecture_per_perturbation.csv"
    )

    cell_path = (
        output_dir
        / "arm_b_post_failure_architecture_cell_summary.csv"
    )

    manifest_path = (
        output_dir
        / "arm_b_post_failure_architecture_checkpoint_manifest.json"
    )

    comparison_path = (
        output_dir
        / "arm_b_post_failure_architecture_N120_vs_N139.csv"
    )

    raw_df = empty_or_read_csv(
        raw_path
    )

    agg_df = empty_or_read_csv(
        cell_path
    )

    manifest = load_manifest(
        manifest_path
    )

    completed = validate_checkpoint_state(
        manifest,
        raw_df,
        agg_df,
    )

    cells = scenario_cells()

    total_cells = (
        len(cells)
        * len(TARGET_N_VALUES)
    )

    if len(completed) > total_cells:
        raise CalibrationContractError(
            "Checkpoint manifest contains more cells than the frozen grid."
        )

    start_time = time.monotonic()

    print(
        "OPENING/RESUMING ARCHITECTURE DIAGNOSTIC 910001-910100.\n"
        "Validation block 2000-2099 remains sealed.\n"
        "No numerical P/S/I/G threshold is used by this script.\n"
        f"Completed cells already checkpointed: "
        f"{len(completed)}/{total_cells}"
    )

    for cell_index, cell in enumerate(
        cells,
        start=1,
    ):

        # One frozen synthetic dataset per scenario/tau setting.
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

        for target_n in TARGET_N_VALUES:

            key = cell_key_from_values(
                cell.scenario,
                cell.tau_index,
                cell.rho_index,
                target_n,
            )

            if key in completed:
                # Already integrity-validated at startup.
                print(
                    "[checkpoint skip] "
                    f"scenario={cell.scenario} "
                    f"tau_index={cell.tau_index} "
                    f"rho_index={cell.rho_index} "
                    f"N={target_n}"
                )
                continue

            rows: list[dict] = []

            print(
                "[cell start] "
                f"scenario={cell.scenario} "
                f"tau={cell.tau} "
                f"rho={cell.rho} "
                f"N={target_n}"
            )

            for diagnostic_seed in DIAGNOSTIC_SEEDS:
                row = run_one_perturbation(
                    cell,
                    diagnostic_seed=diagnostic_seed,
                    target_n=target_n,
                    dataset=dataset,
                )

                row["dataset_seed"] = dataset_seed
                rows.append(row)

            cell_df = (
                pd.DataFrame(rows)
                .sort_values(
                    "diagnostic_seed"
                )
                .reset_index(drop=True)
            )

            aggregate_row = aggregate_architecture_cell(
                cell_df
            )

            # Blinding firewall at the authoritative-output boundary.
            assert_blinded_output_schema(
                cell_df.columns,
                context="per-perturbation authoritative output",
            )

            assert_blinded_output_schema(
                aggregate_row.keys(),
                context="architecture-summary authoritative output",
            )

            (
                raw_df,
                agg_df,
                manifest,
            ) = append_completed_cell(
                cell_rows=cell_df,
                aggregate_row=aggregate_row,
                raw_df=raw_df,
                agg_df=agg_df,
                manifest=manifest,
                raw_path=raw_path,
                cell_path=cell_path,
                manifest_path=manifest_path,
            )

            completed = completed_keys_from_manifest(
                manifest
            )

            elapsed = time.monotonic() - start_time

            print(
                "[cell checkpointed] "
                f"scenario={cell.scenario} "
                f"tau_index={cell.tau_index} "
                f"rho_index={cell.rho_index} "
                f"N={target_n} "
                f"| completed={len(completed)}/{total_cells} "
                f"| elapsed_seconds={elapsed:.1f} "
                f"| raw={raw_path} "
                f"| aggregate={cell_path} "
                f"| manifest={manifest_path}"
            )

    # Final authoritative integrity validation.
    raw_df = pd.read_csv(raw_path)
    agg_df = pd.read_csv(cell_path)
    manifest = load_manifest(
        manifest_path
    )

    completed = validate_checkpoint_state(
        manifest,
        raw_df,
        agg_df,
    )

    if len(completed) != total_cells:
        raise CalibrationContractError(
            f"Architecture diagnostic terminated with "
            f"{len(completed)}/{total_cells} completed cells."
        )

    # --------------------------------------------------------
    # Terminal architecture derivative.
    #
    # This is intentionally outside the per-cell checkpoint transaction.
    # If absent after a restart with all cells complete, it is reconstructed
    # from the authoritative cell-summary table without rerunning any seed.
    # --------------------------------------------------------

    final_cell_summary = pd.read_csv(
        cell_path
    )

    assert_blinded_output_schema(
        final_cell_summary.columns,
        context="completed architecture cell-summary table",
    )

    comparison_df = (
        build_n120_n139_architecture_comparison(
            final_cell_summary
        )
    )

    atomic_write_csv(
        comparison_df,
        comparison_path,
    )

    print("\nARCHITECTURE DIAGNOSTIC COMPLETE.")
    print("Raw perturbations :", raw_path)
    print("Cell statistics    :", cell_path)
    print("N=120/N=139 compare:", comparison_path)
    print("Checkpoint manifest:", manifest_path)
    print("Completed cells    :", len(completed))
    print("No threshold was selected.")
    print("No validation seed was used.")
    print("No biological activation was accessed.")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Experiment 04 Arm-B post-failure architecture diagnostic."
        )
    )

    parser.add_argument(
        "--execute-architecture-diagnostic",
        action="store_true",
        help=(
            "Required explicit switch that opens or resumes diagnostic "
            "namespace 910001-910100."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE / "architecture_diagnostic",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.execute_architecture_diagnostic:
        raise SystemExit(
            "Architecture diagnostic was NOT executed. "
            "Pass --execute-architecture-diagnostic only after this "
            "enablement commit has been pushed and remote-verified."
        )

    run_architecture_diagnostic(
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
