
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
    "C_distributed": {
        "index": 3,
        "effects": {
            0: 0.45,
            1: 0.45,
            2: 0.45,
            3: 0.45,
            4: 0.45,
        },
    },
}

PAIRWISE_GRID = [
    0.50, 0.55, 0.60, 0.65, 0.70,
    0.75, 0.80, 0.85, 0.90,
]

MODAL_GRID = [
    0.60, 0.65, 0.70, 0.75,
    0.80, 0.85, 0.90, 0.95,
]


def outer_seed(
    regime_index: int,
    n: int,
    replicate_index: int,
) -> int:
    return (
        100_000 * regime_index
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
                })

    return pd.DataFrame(rows)


def summarize(
    df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for (
        regime,
        n,
    ), group in df.groupby(
        ["regime", "n_per_class"]
    ):
        for metric in [
            "pairwise_agreement",
            "modal_frequency",
        ]:
            values = group[metric].to_numpy()

            rows.append({
                "regime": regime,
                "n_per_class": n,
                "metric": metric,
                "p05": float(
                    np.quantile(
                        values,
                        0.05,
                    )
                ),
                "median": float(
                    np.quantile(
                        values,
                        0.50,
                    )
                ),
                "p95": float(
                    np.quantile(
                        values,
                        0.95,
                    )
                ),
            })

    return pd.DataFrame(rows)


def select_thresholds(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict | None]:
    n139 = df[
        df["n_per_class"] == 139
    ].copy()

    rows = []
    chosen = None

    for pair_thr in PAIRWISE_GRID:
        for modal_thr in MODAL_GRID:
            passed = (
                (
                    n139["pairwise_agreement"]
                    >= pair_thr
                )
                & (
                    n139["modal_frequency"]
                    >= modal_thr
                )
            )

            rates = {}

            for regime in REGIMES:
                mask = (
                    n139["regime"]
                    == regime
                )

                rates[regime] = float(
                    passed[mask].mean()
                )

            acceptable = (
                rates["A_stable_single"] >= 0.90
                and rates["B_near_tie"] <= 0.10
                and rates["C_distributed"] <= 0.10
            )

            rows.append({
                "pairwise_threshold":
                    pair_thr,
                "modal_threshold":
                    modal_thr,
                "pass_rate_stable_single":
                    rates[
                        "A_stable_single"
                    ],
                "pass_rate_near_tie":
                    rates[
                        "B_near_tie"
                    ],
                "pass_rate_distributed":
                    rates[
                        "C_distributed"
                    ],
                "acceptable":
                    int(acceptable),
            })

            if (
                acceptable
                and chosen is None
            ):
                chosen = {
                    "pairwise_threshold":
                        pair_thr,
                    "modal_threshold":
                        modal_thr,
                    "pass_rate_stable_single":
                        rates[
                            "A_stable_single"
                        ],
                    "pass_rate_near_tie":
                        rates[
                            "B_near_tie"
                        ],
                    "pass_rate_distributed":
                        rates[
                            "C_distributed"
                        ],
                }

    return pd.DataFrame(rows), chosen


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

    summary = summarize(raw)

    threshold_grid, chosen = (
        select_thresholds(raw)
    )

    plateau = plateau_descriptives(
        raw
    )

    raw.to_csv(
        HERE / "calibration_raw.csv",
        index=False,
    )

    summary.to_csv(
        HERE / "calibration_summary.csv",
        index=False,
    )

    threshold_grid.to_csv(
        HERE / "threshold_grid.csv",
        index=False,
    )

    plateau.to_csv(
        HERE / "plateau_descriptives.csv",
        index=False,
    )

    result = {
        "status":
            "CALIBRATED"
            if chosen is not None
            else "UNCALIBRATED",
        "n_latents": N_LATENTS,
        "n_outer": N_OUTER,
        "n_perturbations": N_PERTURB,
        "subsample_fraction":
            SUBSAMPLE_FRAC,
        "chosen_thresholds":
            chosen,
    }

    (
        HERE
        / "calibration_result.json"
    ).write_text(
        json.dumps(
            result,
            indent=2,
        )
        + "\n"
    )

    print(
        "\n── CALIBRATION SUMMARY ──"
    )

    print(
        summary.to_string(
            index=False
        )
    )

    print(
        "\n── THRESHOLD RESULT ──"
    )
    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    print(
        "\n── PLATEAU DESCRIPTIVES ──"
    )
    print(
        plateau.to_string(
            index=False
        )
    )

    print(
        "\nOutputs ->",
        HERE,
    )


if __name__ == "__main__":
    run()
