
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent

N_LATENTS = 32
DISCOVERY_NS = [100, 120, 139]
N_OUTER = 500
N_PERTURB = 100
SUBSAMPLE_FRAC = 0.80

REGIMES = {
    "A_stable_single": {
        "index": 1,
        "effects": {
            0: 1.00,
            1: 0.35,
        },
    },
    "B_near_tie": {
        "index": 2,
        "effects": {
            0: 0.80,
            1: 0.78,
        },
    },
    "C_stable_five": {
        "index": 3,
        "effects": {
            0: 0.45,
            1: 0.45,
            2: 0.45,
            3: 0.45,
            4: 0.45,
        },
    },
    "D_diffuse_sixteen": {
        "index": 4,
        "effects": {
            0: 0.25,
            1: 0.25,
            2: 0.25,
            3: 0.25,
            4: 0.25,
            5: 0.25,
            6: 0.25,
            7: 0.25,
            8: 0.25,
            9: 0.25,
            10: 0.25,
            11: 0.25,
            12: 0.25,
            13: 0.25,
            14: 0.25,
            15: 0.25,
        },
    },
}


FEATURE_SET_K = 5
JACCARD_THRESHOLD = 0.60
RECURRENCE_THRESHOLD = 0.80
MIN_RECURRENT_FEATURES = 4

CONCENTRATION_THRESHOLD = 0.35


def outer_seed(
    regime_index: int,
    n: int,
    replicate_index: int,
) -> int:
    return (
        10_000_000
        + 100_000 * regime_index
        + 1_000 * n
        + replicate_index
    )


def perturb_seed(
    outer: int,
    perturbation_index: int,
) -> int:
    return outer * 1_000 + perturbation_index


def generate_dataset(
    n: int,
    effects: dict[int, float],
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    x_neg = rng.normal(
        loc=0.0,
        scale=1.0,
        size=(n, N_LATENTS),
    )

    x_pos = rng.normal(
        loc=0.0,
        scale=1.0,
        size=(n, N_LATENTS),
    )

    for latent, effect in effects.items():
        x_pos[:, latent] += effect

    return x_pos, x_neg


def top_signed_latent(
    x_pos: np.ndarray,
    x_neg: np.ndarray,
) -> tuple[int, int]:
    scores = (
        x_pos.mean(axis=0)
        - x_neg.mean(axis=0)
    )

    abs_scores = np.abs(scores)

    # np.argmax returns the first occurrence, which implements
    # the frozen lower-latent-index tie break.
    latent = int(np.argmax(abs_scores))

    direction = 1 if scores[latent] >= 0 else -1

    return latent, direction



def top_k_signed_latents(
    x_pos: np.ndarray,
    x_neg: np.ndarray,
    k: int = FEATURE_SET_K,
) -> frozenset[tuple[int, int]]:
    scores = (
        x_pos.mean(axis=0)
        - x_neg.mean(axis=0)
    )

    # Primary ordering: descending absolute score.
    # Frozen tie-break: ascending latent index.
    order = sorted(
        range(len(scores)),
        key=lambda j: (
            -abs(scores[j]),
            j,
        ),
    )

    selected = []

    for latent in order[:k]:
        direction = (
            1 if scores[latent] >= 0
            else -1
        )

        selected.append(
            (int(latent), direction)
        )

    return frozenset(selected)


def perturbation_nominations(
    x_pos: np.ndarray,
    x_neg: np.ndarray,
    outer: int,
) -> list[tuple[int, int]]:
    n_pos = len(x_pos)
    n_neg = len(x_neg)

    k_pos = int(np.floor(SUBSAMPLE_FRAC * n_pos))
    k_neg = int(np.floor(SUBSAMPLE_FRAC * n_neg))

    nominations = []

    for perturb_idx in range(N_PERTURB):
        rng = np.random.default_rng(
            perturb_seed(
                outer,
                perturb_idx,
            )
        )

        pos_idx = rng.choice(
            n_pos,
            size=k_pos,
            replace=False,
        )

        neg_idx = rng.choice(
            n_neg,
            size=k_neg,
            replace=False,
        )

        nominations.append(
            top_signed_latent(
                x_pos[pos_idx],
                x_neg[neg_idx],
            )
        )

    return nominations



def perturbation_feature_sets(
    x_pos: np.ndarray,
    x_neg: np.ndarray,
    outer: int,
) -> list[frozenset[tuple[int, int]]]:
    n_pos = len(x_pos)
    n_neg = len(x_neg)

    k_pos = int(
        np.floor(SUBSAMPLE_FRAC * n_pos)
    )
    k_neg = int(
        np.floor(SUBSAMPLE_FRAC * n_neg)
    )

    feature_sets = []

    for perturb_idx in range(N_PERTURB):
        rng = np.random.default_rng(
            perturb_seed(
                outer,
                perturb_idx,
            )
        )

        pos_idx = rng.choice(
            n_pos,
            size=k_pos,
            replace=False,
        )

        neg_idx = rng.choice(
            n_neg,
            size=k_neg,
            replace=False,
        )

        feature_sets.append(
            top_k_signed_latents(
                x_pos[pos_idx],
                x_neg[neg_idx],
            )
        )

    return feature_sets


def jaccard(
    a: frozenset,
    b: frozenset,
) -> float:
    return len(a & b) / len(a | b)


def pairwise_jaccards(
    feature_sets: list[frozenset],
) -> np.ndarray:
    values = []

    for i, j in itertools.combinations(
        range(len(feature_sets)),
        2,
    ):
        values.append(
            jaccard(
                feature_sets[i],
                feature_sets[j],
            )
        )

    return np.asarray(
        values,
        dtype=float,
    )



def nominated_set_recurrence(
    x_pos: np.ndarray,
    x_neg: np.ndarray,
    feature_sets: list[frozenset[tuple[int, int]]],
) -> dict:
    nominated = top_k_signed_latents(
        x_pos,
        x_neg,
        FEATURE_SET_K,
    )

    counts = {
        feature: 0
        for feature in nominated
    }

    for feature_set in feature_sets:
        for feature in nominated:
            if feature in feature_set:
                counts[feature] += 1

    frequencies = {
        feature: count / len(feature_sets)
        for feature, count in counts.items()
    }

    n_recurrent = sum(
        freq >= RECURRENCE_THRESHOLD
        for freq in frequencies.values()
    )

    serializable = {
        f"{latent}:{'+' if direction > 0 else '-'}":
            frequencies[(latent, direction)]
        for latent, direction in sorted(frequencies)
    }

    return {
        "frequencies": serializable,
        "n_recurrent": int(n_recurrent),
        "recurrence_pass": int(
            n_recurrent >= MIN_RECURRENT_FEATURES
        ),
    }



def fixed_identity_concentration(
    x_pos: np.ndarray,
    x_neg: np.ndarray,
    outer: int,
) -> tuple[float, float, float]:
    """
    Freeze S5 on the full dataset, then measure what fraction
    of total absolute score mass those SAME five latent IDs
    capture under each frozen perturbation.
    """
    nominated = top_k_signed_latents(
        x_pos,
        x_neg,
        FEATURE_SET_K,
    )

    nominated_ids = {
        latent
        for latent, _direction in nominated
    }

    n_pos = len(x_pos)
    n_neg = len(x_neg)

    k_pos = int(
        np.floor(SUBSAMPLE_FRAC * n_pos)
    )
    k_neg = int(
        np.floor(SUBSAMPLE_FRAC * n_neg)
    )

    values = []

    for perturb_idx in range(N_PERTURB):
        rng = np.random.default_rng(
            perturb_seed(
                outer,
                perturb_idx,
            )
        )

        pos_idx = rng.choice(
            n_pos,
            size=k_pos,
            replace=False,
        )

        neg_idx = rng.choice(
            n_neg,
            size=k_neg,
            replace=False,
        )

        scores = (
            x_pos[pos_idx].mean(axis=0)
            - x_neg[neg_idx].mean(axis=0)
        )

        mass = np.abs(scores)
        denominator = float(mass.sum())

        if denominator <= 0.0:
            concentration = 0.0
        else:
            numerator = float(
                mass[list(nominated_ids)].sum()
            )
            concentration = numerator / denominator

        values.append(concentration)

    values = np.asarray(
        values,
        dtype=float,
    )

    return (
        float(np.median(values)),
        float(np.quantile(values, 0.05)),
        float(np.quantile(values, 0.95)),
    )


def feature_inclusion_frequencies(
    feature_sets: list[frozenset],
) -> dict[str, float]:
    counts = {}

    for feature_set in feature_sets:
        for latent, direction in feature_set:
            key = (
                f"{latent}:"
                f"{'+' if direction > 0 else '-'}"
            )

            counts[key] = (
                counts.get(key, 0)
                + 1
            )

    return {
        key: count / len(feature_sets)
        for key, count in sorted(
            counts.items()
        )
    }


def pairwise_agreement(
    nominations: list[tuple[int, int]],
) -> float:
    n = len(nominations)

    agree = 0
    total = 0

    for i, j in itertools.combinations(
        range(n),
        2,
    ):
        total += 1
        agree += int(
            nominations[i]
            == nominations[j]
        )

    return agree / total


def modal_frequency(
    nominations: list[tuple[int, int]],
) -> float:
    counts = {}

    for item in nominations:
        counts[item] = counts.get(item, 0) + 1

    return max(counts.values()) / len(nominations)


def modal_identity(
    nominations: list[tuple[int, int]],
) -> tuple[int, int]:
    counts = {}

    for item in nominations:
        counts[item] = counts.get(item, 0) + 1

    # Deterministic tie-break:
    # higher count first, then lower latent, then + before -.
    return sorted(
        counts.items(),
        key=lambda kv: (
            -kv[1],
            kv[0][0],
            -kv[0][1],
        ),
    )[0][0]


def simulate() -> pd.DataFrame:
    rows = []

    for regime_name, regime in REGIMES.items():
        regime_index = regime["index"]
        effects = regime["effects"]

        for n in DISCOVERY_NS:
            print(
                f"Running {regime_name}, N={n}..."
            )

            for rep in range(N_OUTER):
                seed = outer_seed(
                    regime_index,
                    n,
                    rep,
                )

                x_pos, x_neg = generate_dataset(
                    n=n,
                    effects=effects,
                    seed=seed,
                )

                nominations = (
                    perturbation_nominations(
                        x_pos,
                        x_neg,
                        seed,
                    )
                )

                modal = modal_identity(
                    nominations
                )

                feature_sets = perturbation_feature_sets(
                    x_pos,
                    x_neg,
                    seed,
                )

                jaccards = pairwise_jaccards(
                    feature_sets
                )

                inclusion = feature_inclusion_frequencies(
                    feature_sets
                )

                recurrence = nominated_set_recurrence(
                    x_pos,
                    x_neg,
                    feature_sets,
                )

                (
                    concentration_median,
                    concentration_p05,
                    concentration_p95,
                ) = fixed_identity_concentration(
                    x_pos,
                    x_neg,
                    seed,
                )

                rows.append({
                    "regime": regime_name,
                    "n_per_class": n,
                    "replicate": rep,
                    "outer_seed": seed,
                    "pairwise_agreement":
                        pairwise_agreement(
                            nominations
                        ),
                    "modal_frequency":
                        modal_frequency(
                            nominations
                        ),
                    "modal_latent": modal[0],
                    "modal_direction": modal[1],
                    "feature_set_k": FEATURE_SET_K,
                    "median_pairwise_jaccard": float(
                        np.median(jaccards)
                    ),
                    "jaccard_p05": float(
                        np.quantile(
                            jaccards,
                            0.05,
                        )
                    ),
                    "jaccard_p95": float(
                        np.quantile(
                            jaccards,
                            0.95,
                        )
                    ),
                    "feature_set_pass": int(
                        np.median(jaccards)
                        >= JACCARD_THRESHOLD
                    ),
                    "feature_inclusion_frequencies":
                        json.dumps(
                            inclusion,
                            sort_keys=True,
                        ),
                    "n_recurrent_features":
                        recurrence["n_recurrent"],
                    "recurrence_pass":
                        recurrence["recurrence_pass"],
                    "nominated_feature_recurrence":
                        json.dumps(
                            recurrence["frequencies"],
                            sort_keys=True,
                        ),
                    "combined_feature_set_pass":
                        int(
                            (
                                np.median(jaccards)
                                >= JACCARD_THRESHOLD
                            )
                            and (
                                recurrence["recurrence_pass"] == 1
                            )
                        ),
                    "fixed_top5_concentration_median":
                        concentration_median,
                    "fixed_top5_concentration_p05":
                        concentration_p05,
                    "fixed_top5_concentration_p95":
                        concentration_p95,
                    "final_instrument_pass":
                        int(
                            (
                                np.median(jaccards)
                                >= JACCARD_THRESHOLD
                            )
                            and (
                                recurrence["recurrence_pass"] == 1
                            )
                            and (
                                concentration_median
                                >= CONCENTRATION_THRESHOLD
                            )
                        ),
                })

    return pd.DataFrame(rows)


def independent_validation_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for (regime, n), group in df.groupby(
        ["regime", "n_per_class"]
    ):
        concentration = group[
            "fixed_top5_concentration_median"
        ].to_numpy()

        rows.append({
            "regime": regime,
            "n_per_class": int(n),
            "pairwise_agreement_median":
                float(
                    np.median(
                        group["pairwise_agreement"]
                    )
                ),
            "modal_frequency_median":
                float(
                    np.median(
                        group["modal_frequency"]
                    )
                ),
            "pairwise_jaccard_median":
                float(
                    np.median(
                        group["median_pairwise_jaccard"]
                    )
                ),
            "recurrence_only_pass_rate":
                float(
                    group["recurrence_pass"].mean()
                ),
            "jaccard_recurrence_pass_rate":
                float(
                    group[
                        "combined_feature_set_pass"
                    ].mean()
                ),
            "fixed_top5_concentration_p05":
                float(
                    np.quantile(
                        concentration,
                        0.05,
                    )
                ),
            "fixed_top5_concentration_median":
                float(
                    np.quantile(
                        concentration,
                        0.50,
                    )
                ),
            "fixed_top5_concentration_p95":
                float(
                    np.quantile(
                        concentration,
                        0.95,
                    )
                ),
            "final_instrument_pass_rate":
                float(
                    group[
                        "final_instrument_pass"
                    ].mean()
                ),
        })

    return pd.DataFrame(rows)


def validation_decision(
    summary: pd.DataFrame,
) -> dict:
    n139 = summary[
        summary["n_per_class"] == 139
    ].set_index("regime")

    b = float(
        n139.loc[
            "B_near_tie",
            "final_instrument_pass_rate",
        ]
    )

    c = float(
        n139.loc[
            "C_stable_five",
            "final_instrument_pass_rate",
        ]
    )

    d = float(
        n139.loc[
            "D_diffuse_sixteen",
            "final_instrument_pass_rate",
        ]
    )

    passed = (
        c >= 0.70
        and b <= 0.10
        and d <= 0.10
    )

    return {
        "status":
            "PASS"
            if passed
            else "FAIL",
        "concentration_threshold":
            CONCENTRATION_THRESHOLD,
        "N": 139,
        "pass_rate_B_near_tie": b,
        "pass_rate_C_stable_five": c,
        "pass_rate_D_diffuse_sixteen": d,
        "criteria": {
            "B_near_tie_max": 0.10,
            "C_stable_five_min": 0.70,
            "D_diffuse_sixteen_max": 0.10,
        },
    }


def plateau_descriptives(
    df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for regime in REGIMES:
        sub = df[
            df["regime"] == regime
        ].copy()

        medians = (
            sub.groupby("n_per_class")
            [
                [
                    "pairwise_agreement",
                    "modal_frequency",
                ]
            ]
            .median()
        )

        rows.append({
            "regime": regime,
            "pairwise_median_n100":
                float(
                    medians.loc[
                        100,
                        "pairwise_agreement",
                    ]
                ),
            "pairwise_median_n120":
                float(
                    medians.loc[
                        120,
                        "pairwise_agreement",
                    ]
                ),
            "pairwise_median_n139":
                float(
                    medians.loc[
                        139,
                        "pairwise_agreement",
                    ]
                ),
            "pairwise_delta_120_to_139":
                float(
                    medians.loc[
                        139,
                        "pairwise_agreement",
                    ]
                    - medians.loc[
                        120,
                        "pairwise_agreement",
                    ]
                ),
            "modal_median_n100":
                float(
                    medians.loc[
                        100,
                        "modal_frequency",
                    ]
                ),
            "modal_median_n120":
                float(
                    medians.loc[
                        120,
                        "modal_frequency",
                    ]
                ),
            "modal_median_n139":
                float(
                    medians.loc[
                        139,
                        "modal_frequency",
                    ]
                ),
            "modal_delta_120_to_139":
                float(
                    medians.loc[
                        139,
                        "modal_frequency",
                    ]
                    - medians.loc[
                        120,
                        "modal_frequency",
                    ]
                ),
        })

    return pd.DataFrame(rows)


def run():
    raw = simulate()

    validation_summary = (
        independent_validation_summary(
            raw
        )
    )

    validation_result = validation_decision(
        validation_summary
    )

    raw.to_csv(
        HERE / "independent_validation_raw.csv",
        index=False,
    )

    validation_summary.to_csv(
        HERE / "independent_validation_summary.csv",
        index=False,
    )

    result = {
        "status": validation_result["status"],
        "validation_type": "independent_synthetic",
        "n_latents": N_LATENTS,
        "n_outer": N_OUTER,
        "n_perturbations": N_PERTURB,
        "subsample_fraction": SUBSAMPLE_FRAC,
        "feature_set": {
            "k": FEATURE_SET_K,
            "jaccard_threshold":
                JACCARD_THRESHOLD,
            "recurrence_threshold":
                RECURRENCE_THRESHOLD,
            "min_recurrent_features":
                MIN_RECURRENT_FEATURES,
            "concentration_threshold":
                CONCENTRATION_THRESHOLD,
        },
        "decision": validation_result,
    }

    (
        HERE
        / "independent_validation_result.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
        )
        + "\n"
    )

    print(
        "\n── INDEPENDENT VALIDATION SUMMARY ──"
    )

    print(
        validation_summary.to_string(
            index=False
        )
    )

    print(
        "\n── INDEPENDENT VALIDATION DECISION ──"
    )

    print(
        json.dumps(
            validation_result,
            indent=2,
        )
    )

    print(
        "\nOutputs ->",
        HERE,
    )


if __name__ == "__main__":
    run()
