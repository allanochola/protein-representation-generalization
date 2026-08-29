#!/usr/bin/env python3
"""
Experiment 02 pre-data precision diagnostics.

SYNTHETIC DATA ONLY.

No confirmatory M-CSA label pool, ESM embedding, probe output, or
confirmatory test result is accessed by this module.

The primary feasibility question currently supported here is whether the
preregistered retention statistic

    R = Delta_div / Delta_rand

can be estimated precisely enough at the expected sample support.

Important modeling note
-----------------------
generate_scores() tunes signal strength against realized AP inside each
synthetic dataset. This suppresses some between-dataset variation and therefore
makes feasibility diagnostics favorable/optimistic. Failure under this
generator is evidence against feasibility; success would require a more
realistic independently calibrated simulation before a power claim.

Arms B and D within the same split share the same latent residue noise and
cluster difficulty. They differ only in signal strength. This preserves the
positive covariance expected in a paired comparison.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np
import sklearn
from sklearn.metrics import average_precision_score


SEED = 0

CLUSTER_PREVALENCE_SIGMA = 0.75
CLUSTER_DIFFICULTY_SIGMA = 0.60

RETENTION_THRESHOLD = 0.75


def make_cluster_sizes(
    n_clusters: int,
    total_residues: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate heterogeneous synthetic cluster sizes."""
    weights = rng.lognormal(
        mean=0.0,
        sigma=0.9,
        size=n_clusters,
    )
    weights /= weights.sum()

    sizes = np.maximum(
        1,
        np.floor(weights * total_residues).astype(int),
    )

    diff = total_residues - int(sizes.sum())

    if diff > 0:
        idx = rng.choice(
            n_clusters,
            size=diff,
            replace=True,
        )
        np.add.at(sizes, idx, 1)

    elif diff < 0:
        for _ in range(-diff):
            candidates = np.flatnonzero(sizes > 1)
            if len(candidates) == 0:
                break
            sizes[rng.choice(candidates)] -= 1

    assert int(sizes.sum()) == total_residues
    return sizes


def allocate_binary_labels(
    cluster_sizes: np.ndarray,
    target_positives: int,
    rng: np.random.Generator,
):
    """
    Generate binary labels with cluster-level prevalence heterogeneity.

    CLUSTER_PREVALENCE_SIGMA=0 gives no extra cluster enrichment beyond
    variation induced by cluster size. Positive residues are sampled without
    replacement.
    """
    n = int(cluster_sizes.sum())
    n_clusters = len(cluster_sizes)

    target_positives = int(
        min(max(target_positives, 1), n - 1)
    )

    cluster_id = np.repeat(
        np.arange(n_clusters),
        cluster_sizes,
    )

    latent = rng.normal(
        loc=0.0,
        scale=CLUSTER_PREVALENCE_SIGMA,
        size=n_clusters,
    )

    multipliers = np.exp(latent)

    residue_weights = multipliers[cluster_id].astype(float)
    residue_weights /= residue_weights.sum()

    positive_idx = rng.choice(
        n,
        size=target_positives,
        replace=False,
        p=residue_weights,
    )

    y = np.zeros(n, dtype=np.int8)
    y[positive_idx] = 1

    return y, cluster_id


def make_score_latents(
    y: np.ndarray,
    cluster_id: np.ndarray,
    rng: np.random.Generator,
):
    """
    Draw one set of latent difficulties for a split.

    All model arms evaluated on this split reuse these latents.
    """
    n_clusters = int(cluster_id.max()) + 1

    return {
        "residue_noise": rng.normal(size=len(y)),
        "cluster_difficulty": rng.normal(
            loc=0.0,
            scale=CLUSTER_DIFFICULTY_SIGMA,
            size=n_clusters,
        ),
    }


def generate_scores(
    y: np.ndarray,
    cluster_id: np.ndarray,
    target_ap: float,
    latents: dict,
) -> np.ndarray:
    """
    Generate scores from shared latents at a requested realized AP.

    Within a split, B and D must receive the same `latents` object.
    """
    target_ap = float(np.clip(target_ap, 1e-4, 0.999))

    residue_noise = latents["residue_noise"]
    cluster_difficulty = latents["cluster_difficulty"]

    assert len(residue_noise) == len(y)

    difficulty = cluster_difficulty[cluster_id]

    def scores_for_shift(shift: float) -> np.ndarray:
        return (
            residue_noise
            + y * (shift + difficulty)
        )

    lo, hi = 0.0, 12.0

    for _ in range(40):
        mid = (lo + hi) / 2

        ap = average_precision_score(
            y,
            scores_for_shift(mid),
        )

        if ap < target_ap:
            lo = mid
        else:
            hi = mid

    return scores_for_shift((lo + hi) / 2)


def weighted_cluster_bootstrap_retention(
    y_rand,
    b_rand,
    d_rand,
    cluster_rand,
    y_div,
    b_div,
    d_div,
    cluster_div,
    reps=500,
    seed=0,
):
    """
    Whole-cluster bootstrap for R = Delta_div / Delta_rand.

    Cluster resampling is implemented through integer residue sample weights
    rather than explicit duplicated arrays.

    Replicates with Delta_rand <= 0 or Delta_div <= 0 cannot enter log(R) and
    are excluded. valid_fraction is always returned. A materially sub-1 value
    indicates lower-tail truncation and makes the interval unsuitable for
    ordinary interpretation.
    """
    rng = np.random.default_rng(seed)

    rand_clusters = np.unique(cluster_rand)
    div_clusters = np.unique(cluster_div)

    rand_code = np.searchsorted(
        rand_clusters,
        cluster_rand,
    )
    div_code = np.searchsorted(
        div_clusters,
        cluster_div,
    )

    p_rand = np.full(
        len(rand_clusters),
        1.0 / len(rand_clusters),
    )
    p_div = np.full(
        len(div_clusters),
        1.0 / len(div_clusters),
    )

    R_values = []

    for _ in range(reps):
        m_rand = rng.multinomial(
            len(rand_clusters),
            p_rand,
        )
        m_div = rng.multinomial(
            len(div_clusters),
            p_div,
        )

        w_rand = m_rand[rand_code]
        w_div = m_div[div_code]

        if np.dot(w_rand, y_rand) == 0:
            continue
        if np.dot(w_div, y_div) == 0:
            continue

        ap_br = average_precision_score(
            y_rand,
            b_rand,
            sample_weight=w_rand,
        )
        ap_dr = average_precision_score(
            y_rand,
            d_rand,
            sample_weight=w_rand,
        )

        ap_bd = average_precision_score(
            y_div,
            b_div,
            sample_weight=w_div,
        )
        ap_dd = average_precision_score(
            y_div,
            d_div,
            sample_weight=w_div,
        )

        delta_rand = ap_dr - ap_br
        delta_div = ap_dd - ap_bd

        if delta_rand <= 0 or delta_div <= 0:
            continue

        R_values.append(
            delta_div / delta_rand
        )

    R_values = np.asarray(R_values, dtype=float)

    if len(R_values) == 0:
        raise RuntimeError(
            "No valid retention bootstrap replicates."
        )

    log_R = np.log(R_values)

    lo_log, hi_log = np.percentile(
        log_R,
        [2.5, 97.5],
    )

    return {
        "median_R": float(np.median(R_values)),
        "mean_R": float(np.mean(R_values)),
        "ci_low": float(np.exp(lo_log)),
        "ci_high": float(np.exp(hi_log)),
        "log_half_width": float(
            (hi_log - lo_log) / 2
        ),
        "valid_fraction": float(
            len(R_values) / reps
        ),
    }


def clumping_self_test(
    n_clusters=170,
    target_positives=700,
    prevalence=0.01,
    seed=12345,
):
    rng = np.random.default_rng(seed)

    total_residues = int(
        round(target_positives / prevalence)
    )

    sizes = make_cluster_sizes(
        n_clusters,
        total_residues,
        rng,
    )

    y, cluster_id = allocate_binary_labels(
        sizes,
        target_positives,
        rng,
    )

    pos_per_cluster = np.bincount(
        cluster_id,
        weights=y,
        minlength=n_clusters,
    )

    positive_clusters = int(
        (pos_per_cluster > 0).sum()
    )

    positive_values = pos_per_cluster[
        pos_per_cluster > 0
    ]

    assert pos_per_cluster.max() > 1
    assert positive_clusters < int(y.sum())

    return {
        "clusters": n_clusters,
        "positives": int(y.sum()),
        "positive_bearing_clusters":
            positive_clusters,
        "fraction_positive_bearing": float(
            positive_clusters / n_clusters
        ),
        "mean_positives_per_positive_cluster": float(
            positive_values.mean()
        ),
        "max_positives_one_cluster": int(
            pos_per_cluster.max()
        ),
    }


def weighted_ap_equivalence_self_test():
    """
    Verify integer sample weights equal explicit cluster duplication.
    """
    y = np.array(
        [1, 0, 1, 0, 0, 1],
        dtype=np.int8,
    )

    scores = np.array(
        [0.9, 0.8, 0.7, 0.4, 0.2, 0.1],
        dtype=float,
    )

    cluster_id = np.array(
        [0, 0, 1, 1, 2, 2],
        dtype=int,
    )

    multiplicity = np.array(
        [2, 0, 1],
        dtype=int,
    )

    weights = multiplicity[cluster_id]

    weighted = average_precision_score(
        y,
        scores,
        sample_weight=weights,
    )

    explicit_idx = np.concatenate(
        [
            np.tile(
                np.flatnonzero(cluster_id == c),
                multiplicity[c],
            )
            for c in range(len(multiplicity))
            if multiplicity[c] > 0
        ]
    )

    explicit = average_precision_score(
        y[explicit_idx],
        scores[explicit_idx],
    )

    assert np.isclose(
        weighted,
        explicit,
        rtol=0.0,
        atol=1e-12,
    ), (weighted, explicit)

    return {
        "weighted_ap": float(weighted),
        "explicit_ap": float(explicit),
        "absolute_difference": float(
            abs(weighted - explicit)
        ),
    }



def calibrate_ap_shifts(
    target_aps,
    prevalence=0.01,
    n_residues=500_000,
    seed=123456,
):
    """
    Calibrate score shifts ONCE on an independent large synthetic sample.

    The resulting shifts are then held fixed across outer simulation
    replicates. Realized AP is therefore free to vary across datasets.

    This calibration is for the maximally favorable sigma=0 scenario:
    score = residue_noise + y * shift.
    """
    rng = np.random.default_rng(seed)

    n_positive = int(round(n_residues * prevalence))

    y = np.zeros(n_residues, dtype=np.int8)
    pos_idx = rng.choice(
        n_residues,
        size=n_positive,
        replace=False,
    )
    y[pos_idx] = 1

    noise = rng.normal(size=n_residues)

    targets = sorted(set(float(x) for x in target_aps))
    shifts = {}

    for target_ap in targets:
        lo, hi = 0.0, 12.0

        for _ in range(45):
            mid = (lo + hi) / 2

            scores = noise + y * mid

            ap = average_precision_score(
                y,
                scores,
            )

            if ap < target_ap:
                lo = mid
            else:
                hi = mid

        shift = (lo + hi) / 2

        achieved = average_precision_score(
            y,
            noise + y * shift,
        )

        shifts[str(target_ap)] = {
            "shift": float(shift),
            "calibration_ap": float(achieved),
        }

    return {
        "prevalence": float(prevalence),
        "n_residues": int(n_residues),
        "n_positive": int(n_positive),
        "seed": int(seed),
        "targets": shifts,
    }


def scores_from_fixed_shift(
    y,
    cluster_id,
    shift,
    latents,
):
    """
    Generate scores using a pre-calibrated fixed signal shift.

    No AP targeting occurs here.
    """
    residue_noise = latents["residue_noise"]
    cluster_difficulty = latents["cluster_difficulty"]

    return (
        residue_noise
        + y * (
            float(shift)
            + cluster_difficulty[cluster_id]
        )
    )


def retention_point_estimate(
    y_rand,
    b_rand,
    d_rand,
    y_div,
    b_div,
    d_div,
):
    ap_br = average_precision_score(
        y_rand,
        b_rand,
    )
    ap_dr = average_precision_score(
        y_rand,
        d_rand,
    )
    ap_bd = average_precision_score(
        y_div,
        b_div,
    )
    ap_dd = average_precision_score(
        y_div,
        d_div,
    )

    delta_rand = ap_dr - ap_br
    delta_div = ap_dd - ap_bd

    R = (
        delta_div / delta_rand
        if delta_rand > 0
        else np.nan
    )

    return {
        "ap_b_rand": float(ap_br),
        "ap_d_rand": float(ap_dr),
        "ap_b_div": float(ap_bd),
        "ap_d_div": float(ap_dd),
        "delta_rand": float(delta_rand),
        "delta_div": float(delta_div),
        "R": float(R),
    }


def run_fixed_shift_retention_curve(
    true_R_values=(0.85, 0.90, 0.95, 1.00),
    outer_reps=100,
    bootstrap_reps=300,
    seed=120000,
):
    """
    Corrected retention sensitivity.

    Maximally favorable assumptions:
    - shared B/D latent noise within each split;
    - cluster prevalence sigma = 0;
    - cluster difficulty sigma = 0;
    - equal random/divergent support;
    - 170 clusters and 700 positives per split;
    - signal shifts calibrated ONCE independently and then held fixed.

    Unlike the earlier AP-pinned diagnostic, realized AP varies freely
    across outer datasets.
    """
    global CLUSTER_PREVALENCE_SIGMA
    global CLUSTER_DIFFICULTY_SIGMA

    old_prev = CLUSTER_PREVALENCE_SIGMA
    old_diff = CLUSTER_DIFFICULTY_SIGMA

    CLUSTER_PREVALENCE_SIGMA = 0.0
    CLUSTER_DIFFICULTY_SIGMA = 0.0

    try:
        true_R_values = [
            float(x) for x in true_R_values
        ]

        prevalence = 0.01
        n_clusters = 170
        n_positive = 700
        total_residues = int(
            round(n_positive / prevalence)
        )

        ap_b_rand_target = 0.05
        ap_d_rand_target = 0.20
        delta_rand_target = (
            ap_d_rand_target
            - ap_b_rand_target
        )

        target_aps = {
            ap_b_rand_target,
            ap_d_rand_target,
        }

        target_by_R = {}

        for R0 in true_R_values:
            ap_b_div_target = 0.05
            ap_d_div_target = (
                ap_b_div_target
                + R0 * delta_rand_target
            )

            target_by_R[R0] = {
                "ap_b_div": ap_b_div_target,
                "ap_d_div": ap_d_div_target,
            }

            target_aps.add(ap_b_div_target)
            target_aps.add(ap_d_div_target)

        calibration = calibrate_ap_shifts(
            target_aps=target_aps,
            prevalence=prevalence,
            n_residues=500_000,
            seed=seed - 1,
        )

        shift_map = {
            float(k): v["shift"]
            for k, v in calibration["targets"].items()
        }

        results = {}

        for R_index, R0 in enumerate(true_R_values):

            print(f"\n=== true R = {R0:.2f} ===")

            rng = np.random.default_rng(
                seed + R_index * 10000
            )

            ap_b_div_target = target_by_R[R0][
                "ap_b_div"
            ]
            ap_d_div_target = target_by_R[R0][
                "ap_d_div"
            ]

            ci_lows = []
            log_half_widths = []
            bootstrap_median_R = []
            point_R = []
            realized = []
            valid_fractions = []

            for i in range(outer_reps):

                # ----------------------
                # Random split
                # ----------------------
                sizes_r = make_cluster_sizes(
                    n_clusters,
                    total_residues,
                    rng,
                )

                y_r, c_r = allocate_binary_labels(
                    sizes_r,
                    n_positive,
                    rng,
                )

                latents_r = make_score_latents(
                    y_r,
                    c_r,
                    rng,
                )

                b_r = scores_from_fixed_shift(
                    y_r,
                    c_r,
                    shift_map[ap_b_rand_target],
                    latents_r,
                )

                d_r = scores_from_fixed_shift(
                    y_r,
                    c_r,
                    shift_map[ap_d_rand_target],
                    latents_r,
                )

                # ----------------------
                # Divergent split
                # ----------------------
                sizes_d = make_cluster_sizes(
                    n_clusters,
                    total_residues,
                    rng,
                )

                y_d, c_d = allocate_binary_labels(
                    sizes_d,
                    n_positive,
                    rng,
                )

                latents_d = make_score_latents(
                    y_d,
                    c_d,
                    rng,
                )

                b_d = scores_from_fixed_shift(
                    y_d,
                    c_d,
                    shift_map[ap_b_div_target],
                    latents_d,
                )

                d_d = scores_from_fixed_shift(
                    y_d,
                    c_d,
                    shift_map[ap_d_div_target],
                    latents_d,
                )

                point = retention_point_estimate(
                    y_r,
                    b_r,
                    d_r,
                    y_d,
                    b_d,
                    d_d,
                )

                out = weighted_cluster_bootstrap_retention(
                    y_r,
                    b_r,
                    d_r,
                    c_r,
                    y_d,
                    b_d,
                    d_d,
                    c_d,
                    reps=bootstrap_reps,
                    seed=(
                        seed
                        + R_index * 100000
                        + 1000
                        + i
                    ),
                )

                realized.append(point)
                point_R.append(point["R"])
                ci_lows.append(out["ci_low"])
                log_half_widths.append(
                    out["log_half_width"]
                )
                bootstrap_median_R.append(
                    out["median_R"]
                )
                valid_fractions.append(
                    out["valid_fraction"]
                )

                if (i + 1) % 10 == 0:
                    print(
                        f"{i+1:3d}/{outer_reps} | "
                        f"mean point R="
                        f"{np.nanmean(point_R):.3f} | "
                        f"CI_low="
                        f"{np.mean(ci_lows):.3f} | "
                        f"detect="
                        f"{np.mean(np.asarray(ci_lows) > RETENTION_THRESHOLD):.3f}"
                    )

            ci_lows = np.asarray(ci_lows)
            point_R = np.asarray(point_R)
            log_half_widths = np.asarray(
                log_half_widths
            )

            results[str(R0)] = {
                "target_true_R": float(R0),
                "outer_replicates": int(
                    outer_reps
                ),
                "bootstrap_replicates": int(
                    bootstrap_reps
                ),
                "mean_point_R": float(
                    np.nanmean(point_R)
                ),
                "sd_point_R": float(
                    np.nanstd(
                        point_R,
                        ddof=1,
                    )
                ),
                "point_R_percentiles": [
                    float(x)
                    for x in np.nanpercentile(
                        point_R,
                        [5, 50, 95],
                    )
                ],
                "mean_bootstrap_median_R": float(
                    np.mean(
                        bootstrap_median_R
                    )
                ),
                "mean_log_R_half_width": float(
                    np.mean(
                        log_half_widths
                    )
                ),
                "mean_CI_low": float(
                    np.mean(ci_lows)
                ),
                "CI_low_percentiles": [
                    float(x)
                    for x in np.percentile(
                        ci_lows,
                        [5, 50, 95],
                    )
                ],
                "detection_probability": float(
                    np.mean(
                        ci_lows
                        > RETENTION_THRESHOLD
                    )
                ),
                "mean_valid_fraction": float(
                    np.mean(
                        valid_fractions
                    )
                ),
                "mean_realized_AP": {
                    key: float(
                        np.mean([
                            row[key]
                            for row in realized
                        ])
                    )
                    for key in (
                        "ap_b_rand",
                        "ap_d_rand",
                        "ap_b_div",
                        "ap_d_div",
                        "delta_rand",
                        "delta_div",
                    )
                },
            }

        return {
            "scenario":
                "fixed_shift_maximally_favorable_retention",
            "environment":
                environment_info(),
            "shared_arm_latents": True,
            "cluster_prevalence_sigma": 0.0,
            "cluster_difficulty_sigma": 0.0,
            "clusters_per_split": n_clusters,
            "positives_per_split": n_positive,
            "prevalence": prevalence,
            "retention_threshold":
                RETENTION_THRESHOLD,
            "calibration": calibration,
            "results": results,
        }

    finally:
        CLUSTER_PREVALENCE_SIGMA = old_prev
        CLUSTER_DIFFICULTY_SIGMA = old_diff

def run_favorable_retention(
    outer_reps=30,
    bootstrap_reps=300,
    seed=91000,
):
    """
    Maximally favorable feasibility diagnostic.

    Assumptions:
    - shared B/D latent draws;
    - zero cluster prevalence heterogeneity;
    - zero cluster ranking-difficulty heterogeneity;
    - equal random/divergent support;
    - 170 clusters and 700 positives per split;
    - true R = 0.90.

    This is intentionally favorable to retention precision.
    """
    global CLUSTER_PREVALENCE_SIGMA
    global CLUSTER_DIFFICULTY_SIGMA

    old_prev = CLUSTER_PREVALENCE_SIGMA
    old_diff = CLUSTER_DIFFICULTY_SIGMA

    CLUSTER_PREVALENCE_SIGMA = 0.0
    CLUSTER_DIFFICULTY_SIGMA = 0.0

    try:
        rng = np.random.default_rng(seed)

        true_R = 0.90
        prevalence = 0.01
        n_clusters = 170
        n_positive = 700
        total_residues = int(
            round(n_positive / prevalence)
        )

        ap_b_rand = 0.05
        ap_d_rand = 0.20

        delta_rand_true = (
            ap_d_rand - ap_b_rand
        )

        ap_b_div = 0.05
        ap_d_div = (
            ap_b_div
            + true_R * delta_rand_true
        )

        ci_lows = []
        log_half_widths = []
        median_Rs = []
        valid_fractions = []

        for i in range(outer_reps):
            sizes_r = make_cluster_sizes(
                n_clusters,
                total_residues,
                rng,
            )

            y_r, c_r = allocate_binary_labels(
                sizes_r,
                n_positive,
                rng,
            )

            latents_r = make_score_latents(
                y_r,
                c_r,
                rng,
            )

            b_r = generate_scores(
                y_r,
                c_r,
                ap_b_rand,
                latents_r,
            )
            d_r = generate_scores(
                y_r,
                c_r,
                ap_d_rand,
                latents_r,
            )

            sizes_d = make_cluster_sizes(
                n_clusters,
                total_residues,
                rng,
            )

            y_d, c_d = allocate_binary_labels(
                sizes_d,
                n_positive,
                rng,
            )

            latents_d = make_score_latents(
                y_d,
                c_d,
                rng,
            )

            b_d = generate_scores(
                y_d,
                c_d,
                ap_b_div,
                latents_d,
            )
            d_d = generate_scores(
                y_d,
                c_d,
                ap_d_div,
                latents_d,
            )

            out = weighted_cluster_bootstrap_retention(
                y_r,
                b_r,
                d_r,
                c_r,
                y_d,
                b_d,
                d_d,
                c_d,
                reps=bootstrap_reps,
                seed=seed + 1000 + i,
            )

            ci_lows.append(out["ci_low"])
            log_half_widths.append(
                out["log_half_width"]
            )
            median_Rs.append(
                out["median_R"]
            )
            valid_fractions.append(
                out["valid_fraction"]
            )

            if (i + 1) % 5 == 0:
                print(
                    f"{i+1:3d}/{outer_reps} | "
                    f"CI_low={np.mean(ci_lows):.3f} | "
                    f"detect="
                    f"{np.mean(np.asarray(ci_lows) > RETENTION_THRESHOLD):.3f}"
                )

        ci_lows = np.asarray(ci_lows)

        return {
            "scenario": "maximally_favorable_retention",
            "true_R": true_R,
            "retention_threshold":
                RETENTION_THRESHOLD,
            "cluster_prevalence_sigma": 0.0,
            "cluster_difficulty_sigma": 0.0,
            "shared_arm_latents": True,
            "clusters_per_split": n_clusters,
            "positives_per_split": n_positive,
            "prevalence": prevalence,
            "outer_replicates": outer_reps,
            "bootstrap_replicates":
                bootstrap_reps,
            "seed": seed,
            "mean_median_R": float(
                np.mean(median_Rs)
            ),
            "mean_log_R_half_width": float(
                np.mean(log_half_widths)
            ),
            "mean_CI_low": float(
                np.mean(ci_lows)
            ),
            "detection_probability": float(
                np.mean(
                    ci_lows
                    > RETENTION_THRESHOLD
                )
            ),
            "mean_valid_fraction": float(
                np.mean(valid_fractions)
            ),
        }

    finally:
        CLUSTER_PREVALENCE_SIGMA = old_prev
        CLUSTER_DIFFICULTY_SIGMA = old_diff


def environment_info():
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "command",
        choices=[
            "self-test",
            "retention-favorable",
            "retention-fixed",
        ],
    )

    parser.add_argument(
        "--outer",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--bootstrap",
        type=int,
        default=300,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=91000,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )

    args = parser.parse_args()

    if args.command == "self-test":
        result = {
            "environment":
                environment_info(),
            "clumping":
                clumping_self_test(),
            "weighted_ap_equivalence":
                weighted_ap_equivalence_self_test(),
        }

    elif args.command == "retention-favorable":
        result = {
            "environment":
                environment_info(),
            "result":
                run_favorable_retention(
                    outer_reps=args.outer,
                    bootstrap_reps=args.bootstrap,
                    seed=args.seed,
                ),
        }

    else:
        result = run_fixed_shift_retention_curve(
            true_R_values=(
                0.85,
                0.90,
                0.95,
                1.00,
            ),
            outer_reps=args.outer,
            bootstrap_reps=args.bootstrap,
            seed=args.seed,
        )

    text = json.dumps(
        result,
        indent=2,
    )

    print(text)

    if args.output is not None:
        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.output.write_text(
            text + "\n",
            encoding="utf-8",
        )
        print(
            f"\nsaved: {args.output}"
        )


if __name__ == "__main__":
    main()
