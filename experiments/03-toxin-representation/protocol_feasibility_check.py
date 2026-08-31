#!/usr/bin/env python3
"""
Experiment 03 pre-data feasibility simulator.

Purpose
-------
Size the confirmatory precision of the primary paired estimand

    ΔTPR = TPR_representation - TPR_sequence

using the frozen model-eligible geometry:

    N_POS = 161 V2-B toxin clusters
    N_NEG = 3541 family-aware negatives

No ESM embedding, SAE activation, feature score, or confirmatory label result
is read by this script.

Important modeling boundary
---------------------------
The primary simulation treats the FPR operating threshold as fixed and models
the paired positive hit/miss outcomes at that threshold.

Finite-negative support is analyzed separately. Propagating estimated-threshold
uncertainty into TPR would require assumptions about the score distributions
near the operating threshold; those assumptions are deliberately not invented
for preregistration.

Outputs
-------
results/feasibility_grid.csv
results/candidate_band_summary.csv
results/negative_fpr_precision.csv
results/feasibility_summary.json
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Frozen support geometry
# ---------------------------------------------------------------------

N_POS = 161
N_NEG = 3541

PRIMARY_FPR = 0.05
SECONDARY_FPR = 0.01

SEED = 20260831
N_SIM = 2000
BOOTSTRAP_REPS = 1000

# ---------------------------------------------------------------------
# Pre-data grids
# ---------------------------------------------------------------------

BASELINE_TPR_GRID = [
    0.20,
    0.35,
    0.50,
    0.65,
    0.80,
]

DELTA_TPR_GRID = [
    0.00,
    0.03,
    0.05,
    0.075,
    0.08,
    0.10,
    0.125,
    0.13,
    0.15,
    0.20,
]

# Paired-disagreement geometry.
#
# For fixed baseline TPR b and Δ=d:
#
#     p01 - p10 = d
#
# where:
#     p01 = sequence miss, representation hit  (representation rescue)
#     p10 = sequence hit, representation miss  (representation loss)
#
# LOSS_FRAC defines p10 as a fraction of the maximum feasible discordance
# remaining after enforcing Δ.
#
# 0.0 = all incremental gain comes from rescues, no representation losses.
# Larger values create more two-way discordance and therefore wider paired
# uncertainty while preserving the same marginal ΔTPR.
LOSS_FRAC_GRID = [
    0.00,
    0.25,
    0.50,
    0.75,
]

# Candidate decision bands to test, NOT frozen conclusions.
CANDIDATE_BANDS = [
    {
        "name": "material05_negligible05",
        "material": 0.05,
        "negligible": 0.05,
    },
    {
        "name": "material10_negligible03",
        "material": 0.10,
        "negligible": 0.03,
    },
    {
        "name": "material08_negligible03",
        "material": 0.08,
        "negligible": 0.03,
    },
    {
        "name": "material075_negligible025",
        "material": 0.075,
        "negligible": 0.025,
    },
]

ALPHA = 0.05


def feasible_joint_probabilities(
    baseline_tpr: float,
    delta_tpr: float,
    loss_frac: float,
):
    """
    Construct paired Bernoulli probabilities.

    Cells:
                        Representation
                        miss        hit
    Sequence miss       p00         p01
    Sequence hit        p10         p11

    Marginals:
        TPR_seq  = p10 + p11 = baseline_tpr
        TPR_repr = p01 + p11 = baseline_tpr + delta_tpr

    Difference:
        ΔTPR = p01 - p10
    """
    b = float(baseline_tpr)
    d = float(delta_tpr)

    repr_tpr = b + d

    if not (0 <= b <= 1):
        return None

    if not (0 <= repr_tpr <= 1):
        return None

    # Let p10 = x and p01 = x + d.
    #
    # Constraints:
    #   p11 = b - x >= 0        -> x <= b
    #   p00 = 1-b-d-x >= 0      -> x <= 1-b-d
    #
    # Therefore:
    max_loss = min(
        b,
        1.0 - b - d,
    )

    if max_loss < -1e-12:
        return None

    max_loss = max(0.0, max_loss)

    p10 = loss_frac * max_loss
    p01 = p10 + d
    p11 = b - p10
    p00 = 1.0 - p01 - p10 - p11

    probs = np.array(
        [p00, p01, p10, p11],
        dtype=float,
    )

    if np.any(probs < -1e-10):
        return None

    probs = np.clip(probs, 0, 1)
    probs /= probs.sum()

    return {
        "p00": float(probs[0]),
        "p01": float(probs[1]),
        "p10": float(probs[2]),
        "p11": float(probs[3]),
        "tpr_sequence": b,
        "tpr_representation": repr_tpr,
        "true_delta": d,
    }


def paired_bootstrap_ci(
    seq_hit: np.ndarray,
    repr_hit: np.ndarray,
    rng: np.random.Generator,
):
    """
    Paired cluster bootstrap percentile CI.

    The same cluster indices are resampled for both arms.
    """
    n = len(seq_hit)

    boot_idx = rng.integers(
        0,
        n,
        size=(BOOTSTRAP_REPS, n),
    )

    seq_boot = seq_hit[boot_idx].mean(axis=1)
    repr_boot = repr_hit[boot_idx].mean(axis=1)

    deltas = repr_boot - seq_boot

    low, high = np.quantile(
        deltas,
        [ALPHA / 2, 1 - ALPHA / 2],
    )

    return float(low), float(high)


def simulate_cell(
    baseline_tpr: float,
    delta_tpr: float,
    loss_frac: float,
    seed: int,
):
    joint = feasible_joint_probabilities(
        baseline_tpr,
        delta_tpr,
        loss_frac,
    )

    if joint is None:
        return None

    rng = np.random.default_rng(seed)

    probs = [
        joint["p00"],
        joint["p01"],
        joint["p10"],
        joint["p11"],
    ]

    estimates = np.empty(N_SIM, dtype=float)
    ci_low = np.empty(N_SIM, dtype=float)
    ci_high = np.empty(N_SIM, dtype=float)

    # The preregistered confirmatory decision will use paired cluster-bootstrap
    # intervals, so candidate decision-band probabilities are sized using that
    # same inferential procedure rather than the normal approximation.
    bootstrap_half_widths = np.empty(N_SIM, dtype=float)
    bootstrap_cover = np.empty(N_SIM, dtype=float)
    bootstrap_ci_low = np.empty(N_SIM, dtype=float)
    bootstrap_ci_high = np.empty(N_SIM, dtype=float)

    for i in range(N_SIM):
        cells = rng.choice(
            4,
            size=N_POS,
            p=probs,
        )

        # cell 0: both miss
        # cell 1: seq miss / repr hit
        # cell 2: seq hit / repr miss
        # cell 3: both hit
        seq_hit = (
            (cells == 2)
            | (cells == 3)
        ).astype(float)

        repr_hit = (
            (cells == 1)
            | (cells == 3)
        ).astype(float)

        diff = repr_hit - seq_hit

        estimate = float(diff.mean())
        estimates[i] = estimate

        # Paired difference standard error.
        if len(diff) > 1:
            se = float(
                diff.std(ddof=1)
                / np.sqrt(N_POS)
            )
        else:
            se = 0.0

        low = estimate - 1.959963984540054 * se
        high = estimate + 1.959963984540054 * se

        ci_low[i] = low
        ci_high[i] = high

        boot_rng = np.random.default_rng(
            seed * 1000003 + i
        )

        b_low, b_high = paired_bootstrap_ci(
            seq_hit,
            repr_hit,
            boot_rng,
        )

        bootstrap_ci_low[i] = b_low
        bootstrap_ci_high[i] = b_high

        bootstrap_half_widths[i] = (
            b_high - b_low
        ) / 2

        bootstrap_cover[i] = int(
            b_low
            <= joint["true_delta"]
            <= b_high
        )

    row = {
        "baseline_tpr": baseline_tpr,
        "true_delta_tpr": delta_tpr,
        "loss_frac": loss_frac,
        **joint,
        "mean_estimated_delta": float(
            estimates.mean()
        ),
        "sd_estimated_delta": float(
            estimates.std(ddof=1)
        ),
        "normal_ci_mean_half_width": float(
            np.mean(
                (ci_high - ci_low) / 2
            )
        ),
        "normal_ci_coverage": float(
            np.mean(
                (ci_low <= delta_tpr)
                & (ci_high >= delta_tpr)
            )
        ),
        "bootstrap_mean_half_width": float(
            np.mean(bootstrap_half_widths)
        ),
        "bootstrap_median_half_width": float(
            np.median(bootstrap_half_widths)
        ),
        "bootstrap_coverage": float(
            np.mean(bootstrap_cover)
        ),
    }

    for band in CANDIDATE_BANDS:
        material = band["material"]
        negligible = band["negligible"]
        name = band["name"]

        row[
            f"{name}__p_boot_ci_low_ge_material"
        ] = float(
            np.mean(
                bootstrap_ci_low >= material
            )
        )

        row[
            f"{name}__p_boot_ci_high_le_negligible"
        ] = float(
            np.mean(
                bootstrap_ci_high <= negligible
            )
        )

    return row


def binomial_fpr_precision(
    n_neg: int,
    fpr: float,
):
    """
    Descriptive precision of a finite negative pool at a target FPR.

    This describes tail support only. It is NOT propagated into TPR because
    doing so would require an assumed score-density shape around the threshold.
    """
    expected_fp = n_neg * fpr

    se = np.sqrt(
        fpr
        * (1 - fpr)
        / n_neg
    )

    low = max(
        0.0,
        fpr - 1.959963984540054 * se,
    )

    high = min(
        1.0,
        fpr + 1.959963984540054 * se,
    )

    return {
        "n_negative": n_neg,
        "target_fpr": fpr,
        "expected_false_positives": expected_fp,
        "binomial_fpr_se": se,
        "approx_fpr_ci_low": low,
        "approx_fpr_ci_high": high,
        "approx_fpr_ci_half_width": (
            high - low
        ) / 2,
    }


def main():
    out_dir = (
        Path(__file__).parent
        / "results"
    )

    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    counter = 0

    for baseline_tpr in BASELINE_TPR_GRID:
        for delta_tpr in DELTA_TPR_GRID:
            for loss_frac in LOSS_FRAC_GRID:
                counter += 1

                row = simulate_cell(
                    baseline_tpr=baseline_tpr,
                    delta_tpr=delta_tpr,
                    loss_frac=loss_frac,
                    seed=SEED + counter,
                )

                if row is not None:
                    rows.append(row)

    grid = pd.DataFrame(rows)

    grid.to_csv(
        out_dir
        / "feasibility_grid.csv",
        index=False,
    )

    # -----------------------------------------------------------------
    # Summarize candidate bands by true effect.
    # Worst-case and best-case probabilities across baseline TPR and
    # paired-disagreement geometries.
    # -----------------------------------------------------------------

    band_rows = []

    for band in CANDIDATE_BANDS:
        name = band["name"]

        repr_col = (
            f"{name}__p_boot_ci_low_ge_material"
        )

        seq_col = (
            f"{name}__p_boot_ci_high_le_negligible"
        )

        for delta in sorted(
            grid["true_delta_tpr"].unique()
        ):
            sub = grid[
                grid["true_delta_tpr"] == delta
            ]

            band_rows.append({
                "band": name,
                "material_boundary": band["material"],
                "negligible_boundary": band["negligible"],
                "true_delta_tpr": delta,
                "min_p_H_repr_across_geometry": float(
                    sub[repr_col].min()
                ),
                "median_p_H_repr_across_geometry": float(
                    sub[repr_col].median()
                ),
                "max_p_H_repr_across_geometry": float(
                    sub[repr_col].max()
                ),
                "min_p_H_sequence_across_geometry": float(
                    sub[seq_col].min()
                ),
                "median_p_H_sequence_across_geometry": float(
                    sub[seq_col].median()
                ),
                "max_p_H_sequence_across_geometry": float(
                    sub[seq_col].max()
                ),
                "max_bootstrap_half_width": float(
                    sub["bootstrap_mean_half_width"].max()
                ),
                "median_bootstrap_half_width": float(
                    sub["bootstrap_mean_half_width"].median()
                ),
            })

    band_summary = pd.DataFrame(
        band_rows
    )

    band_summary.to_csv(
        out_dir
        / "candidate_band_summary.csv",
        index=False,
    )

    fpr_rows = [
        binomial_fpr_precision(
            N_NEG,
            PRIMARY_FPR,
        ),
        binomial_fpr_precision(
            N_NEG,
            SECONDARY_FPR,
        ),
    ]

    fpr_df = pd.DataFrame(
        fpr_rows
    )

    fpr_df.to_csv(
        out_dir
        / "negative_fpr_precision.csv",
        index=False,
    )

    summary = {
        "status": "PRE_DATA_ONLY",
        "n_positive_clusters": N_POS,
        "n_family_aware_negatives": N_NEG,
        "primary_fpr": PRIMARY_FPR,
        "secondary_fpr": SECONDARY_FPR,
        "n_sim": N_SIM,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "baseline_tpr_grid": BASELINE_TPR_GRID,
        "delta_tpr_grid": DELTA_TPR_GRID,
        "loss_frac_grid": LOSS_FRAC_GRID,
        "candidate_bands": CANDIDATE_BANDS,
        "modeling_boundary": (
            "Paired positive hit/miss outcomes are simulated at a fixed "
            "operating threshold. Finite-negative FPR precision is reported "
            "separately because propagating threshold uncertainty into TPR "
            "would require an assumed score distribution near the threshold."
        ),
    }

    (
        out_dir
        / "feasibility_summary.json"
    ).write_text(
        json.dumps(
            summary,
            indent=2,
        )
        + "\n"
    )

    print(
        "\n── Experiment 03 pre-data feasibility ───────────────────────"
    )

    print(
        f"Positive clusters: {N_POS}"
    )

    print(
        f"Family-aware negatives: {N_NEG}"
    )

    print(
        "\nNegative operating-point support:"
    )

    print(
        fpr_df.to_string(
            index=False
        )
    )

    print(
        "\nBootstrap half-width envelope by true ΔTPR:"
    )

    hw = (
        grid
        .groupby("true_delta_tpr")
        ["bootstrap_mean_half_width"]
        .agg(
            ["min", "median", "max"]
        )
        .reset_index()
    )

    print(
        hw.to_string(
            index=False
        )
    )

    print(
        "\nCandidate decision-band summary:"
    )

    print(
        band_summary.to_string(
            index=False
        )
    )

    print(
        f"\nOutputs -> {out_dir}/"
    )


if __name__ == "__main__":
    main()
