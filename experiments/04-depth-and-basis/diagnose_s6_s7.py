"""Experiment 04 — S6/S7 generator diagnostics.

DIAGNOSTIC ONLY.

Permitted:
- generator arithmetic;
- tau/score-SD checks;
- covariance checks;
- RNG invariance checks;
- class-balance checks;
- metadata/layout checks.

Prohibited:
- probe fitting;
- AUROC;
- prediction metrics;
- regularization selection;
- threshold selection;
- calibration seeds 1000-1099;
- validation seeds 2000-2099;
- biological activations.
"""

from pathlib import Path
import importlib.util
import math
import sys

import numpy as np


REPO = Path("/kaggle/working/protein-representation-generalization")
SRC = REPO / "experiments/04-depth-and-basis/synthetic_generators.py"

DIAGNOSTIC_MIN = 900001
DIAGNOSTIC_MAX = 900100

# Already consumed by earlier S1-S5 diagnostics:
CONSUMED_DIAGNOSTIC_SEEDS = (
    set(range(900001, 900004))
    | set(range(900010, 900040))
    | set(range(900050, 900056))
    | {900060}
)

# New S6 diagnostic seeds.
S6_LARGE_N_SEEDS = (900061, 900062, 900063)
S6_ACTUAL_SEED = 900064

# New S7 diagnostic seeds.
S7_LARGE_N_SEEDS = (900071, 900072, 900073)
S7_ACTUAL_SEED = 900074

NEW_DIAGNOSTIC_SEEDS = (
    set(S6_LARGE_N_SEEDS)
    | {S6_ACTUAL_SEED}
    | set(S7_LARGE_N_SEEDS)
    | {S7_ACTUAL_SEED}
)

LARGE_N = 200_000


# ------------------------------------------------------------------
# Firewall
# ------------------------------------------------------------------

assert SRC.exists()

assert all(
    DIAGNOSTIC_MIN <= seed <= DIAGNOSTIC_MAX
    for seed in NEW_DIAGNOSTIC_SEEDS
)

assert not (
    NEW_DIAGNOSTIC_SEEDS
    & CONSUMED_DIAGNOSTIC_SEEDS
), "New diagnostics reuse an already-consumed diagnostic seed."

assert not (
    NEW_DIAGNOSTIC_SEEDS
    & set(range(1000, 1100))
), "Calibration seed used."

assert not (
    NEW_DIAGNOSTIC_SEEDS
    & set(range(2000, 2100))
), "Validation seed used."

print("── DIAGNOSTIC FIREWALL ──")
print("new S6 seeds:", sorted(
    set(S6_LARGE_N_SEEDS) | {S6_ACTUAL_SEED}
))
print("new S7 seeds:", sorted(
    set(S7_LARGE_N_SEEDS) | {S7_ACTUAL_SEED}
))
print("calibration 1000-1099: untouched")
print("validation  2000-2099: untouched")


# ------------------------------------------------------------------
# Load frozen generator source
# ------------------------------------------------------------------

module_name = "exp04_synthetic_generators_s6s7_diag"

spec = importlib.util.spec_from_file_location(
    module_name,
    SRC,
)

assert spec is not None
assert spec.loader is not None

sg = importlib.util.module_from_spec(spec)
sys.modules[module_name] = sg
spec.loader.exec_module(sg)

assert sg.N_TOTAL == 278
assert sg.P == 1280

print("PASS — frozen generator module imported.")


# ==================================================================
# S6
# ==================================================================

print("\n" + "=" * 72)
print("S6 DIAGNOSTICS")
print("=" * 72)


# ------------------------------------------------------------------
# S6-D1 — large-N tau geometry and nuisance covariance
# ------------------------------------------------------------------

print("\n── S6-D1: LARGE-N GEOMETRY ──")

S6_TAUS = (
    sg.MASTER_TAU[0],
    sg.MASTER_TAU[4],
    sg.MASTER_TAU[-1],
)

S6_RHOS = (0.30, 0.60, 0.90)

for seed in S6_LARGE_N_SEEDS:
    for tau in S6_TAUS:
        rng_signal = np.random.default_rng(
            np.random.SeedSequence([seed, 1])
        )
        rng_nuisance = np.random.default_rng(
            np.random.SeedSequence([seed, 2])
        )

        signal = rng_signal.normal(
            size=(LARGE_N, 5)
        )

        eps = rng_nuisance.normal(
            size=(LARGE_N, 100)
        )

        b = sg._tau_to_b(
            tau=tau,
            k=5,
        )

        score = signal @ (
            b * sg.S1_SIGNS
        )

        score_sd = float(
            np.std(score, ddof=0)
        )

        score_rel_error = abs(
            score_sd - tau
        ) / tau

        assert score_rel_error < 0.01

        for rho in S6_RHOS:
            residual_scale = np.sqrt(
                1.0 - rho ** 2
            )

            nuisance = np.empty(
                (LARGE_N, 100),
                dtype=float,
            )

            for j in range(5):
                start = j * 20
                stop = start + 20

                nuisance[:, start:stop] = (
                    rho * signal[:, [j]]
                    + residual_scale
                    * eps[:, start:stop]
                )

            nuisance_var = float(
                np.var(nuisance, ddof=0)
            )

            own_corrs = []

            for j in range(5):
                start = j * 20
                stop = start + 20

                for col in range(start, stop):
                    corr = np.corrcoef(
                        signal[:, j],
                        nuisance[:, col],
                    )[0, 1]

                    own_corrs.append(
                        float(corr)
                    )

            mean_own_corr = float(
                np.mean(own_corrs)
            )

            # Cross-block nuisance correlations should have no planted
            # covariance. Use one fixed representative nuisance coordinate
            # from each of the five nuisance blocks.
            representative_cols = [0, 20, 40, 60, 80]

            representative = nuisance[
                :,
                representative_cols
            ]

            cross_corr = np.corrcoef(
                representative,
                rowvar=False,
            )

            cross_values = cross_corr[
                np.triu_indices_from(
                    cross_corr,
                    k=1,
                )
            ]

            max_abs_cross_corr = float(
                np.max(
                    np.abs(cross_values)
                )
            )

            assert abs(
                nuisance_var - 1.0
            ) < 0.01

            assert abs(
                mean_own_corr - rho
            ) < 0.01

            assert max_abs_cross_corr < 0.02

            print(
                f"seed={seed} "
                f"tau={tau:.6f} "
                f"rho={rho:.2f} "
                f"scoreSD={score_sd:.6f} "
                f"nuisanceVar={nuisance_var:.6f} "
                f"meanOwnCorr={mean_own_corr:.6f} "
                f"maxCrossCorr={max_abs_cross_corr:.6f}"
            )

print(
    "PASS — S6 population tau, variance, "
    "and Corr(signal,nuisance)=rho geometry."
)


# ------------------------------------------------------------------
# S6-D2 — actual-generator rho isolation
# ------------------------------------------------------------------

print("\n── S6-D2: ACTUAL-GENERATOR RHO ISOLATION ──")

s6_tau = sg.MASTER_TAU[4]

s6_ds = {
    rho: sg.generate_s6(
        seed=S6_ACTUAL_SEED,
        tau=s6_tau,
        rho=rho,
    )
    for rho in S6_RHOS
}

s6_ref = s6_ds[0.30]

for rho, ds in s6_ds.items():
    assert ds.X.shape == (278, 1280)
    assert int(ds.y.sum()) == 139
    assert int((ds.y == 0).sum()) == 139

    assert ds.metadata["signal_idx"] == list(range(0, 5))
    assert ds.metadata["nuisance_idx"] == list(range(5, 105))
    assert ds.metadata["background_idx"] == list(range(105, 1280))

    assert ds.metadata["nuisance_direct_beta"] == 0.0
    assert ds.metadata["noise_scale"] == 1.0

    assert np.all(
        ds.beta[5:] == 0.0
    )

    expected_b = sg._tau_to_b(
        tau=s6_tau,
        k=5,
    )

    assert math.isclose(
        ds.metadata["b"],
        expected_b,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

    # True signal and background must be exactly rho-invariant.
    assert np.array_equal(
        ds.X[:, 0:5],
        s6_ref.X[:, 0:5],
    )

    assert np.array_equal(
        ds.X[:, 105:1280],
        s6_ref.X[:, 105:1280],
    )

    # Labels must be exactly rho-invariant.
    assert np.array_equal(
        ds.y,
        s6_ref.y,
    )

    # Reconstructed true score must be identical.
    score = (
        ds.X[:, 0:5]
        @ ds.beta[0:5]
    )

    ref_score = (
        s6_ref.X[:, 0:5]
        @ s6_ref.beta[0:5]
    )

    assert np.array_equal(
        score,
        ref_score,
    )

    # Actual finite-N own-block correlations.
    own_corrs = []

    blocks = ds.metadata["nuisance_blocks"]

    for j, block in enumerate(blocks):
        for col in block:
            own_corrs.append(
                float(
                    np.corrcoef(
                        ds.X[:, j],
                        ds.X[:, col],
                    )[0, 1]
                )
            )

    mean_own_corr = float(
        np.mean(own_corrs)
    )

    nuisance_var = float(
        np.var(
            ds.X[:, 5:105],
            ddof=0,
        )
    )

    background = ds.X[:, 105:1280]

    background_mean = float(
        np.mean(background)
    )

    background_var = float(
        np.var(
            background,
            ddof=0,
        )
    )

    # Fixed subset for finite-N independence sanity checking.
    background_subset = background[
        :,
        [0, 100, 300, 600, 900, 1174],
    ]

    background_corr = np.corrcoef(
        background_subset,
        rowvar=False,
    )

    background_offdiag = background_corr[
        np.triu_indices_from(
            background_corr,
            k=1,
        )
    ]

    max_abs_background_corr = float(
        np.max(
            np.abs(background_offdiag)
        )
    )

    print(
        f"rho={rho:.2f} "
        f"meanOwnCorr={mean_own_corr:.4f} "
        f"nuisanceVar={nuisance_var:.4f} "
        f"backgroundMean={background_mean:.4f} "
        f"backgroundVar={background_var:.4f} "
        f"maxBgCorr={max_abs_background_corr:.4f} "
        f"labelsSame={np.array_equal(ds.y, s6_ref.y)}"
    )

    assert abs(
        mean_own_corr - rho
    ) < 0.08

    assert abs(
        nuisance_var - 1.0
    ) < 0.10

    assert abs(
        background_mean
    ) < 0.02

    assert abs(
        background_var - 1.0
    ) < 0.05

    # N=278 finite-sample sanity bound, not a calibration threshold.
    assert max_abs_background_corr < 0.20

# Only nuisance region may change across rho.
for rho in (0.60, 0.90):
    assert not np.array_equal(
        s6_ds[rho].X[:, 5:105],
        s6_ref.X[:, 5:105],
    )

print(
    "PASS — S6 rho changes only nuisance geometry "
    "at fixed seed/tau."
)


# ==================================================================
# S7
# ==================================================================

print("\n" + "=" * 72)
print("S7 DIAGNOSTICS")
print("=" * 72)


# ------------------------------------------------------------------
# S7-D1 — large-N tau and proxy geometry
# ------------------------------------------------------------------

print("\n── S7-D1: LARGE-N GEOMETRY ──")

S7_TAUS = (
    sg.MASTER_TAU[0],
    sg.MASTER_TAU[4],
    sg.MASTER_TAU[-1],
)

rho_shortcut = 0.95

orientations = np.array(
    [1.0, 1.0, -1.0, 1.0, -1.0],
    dtype=float,
)

for seed in S7_LARGE_N_SEEDS:
    rng_z = np.random.default_rng(
        np.random.SeedSequence([seed, 11])
    )
    rng_proxy = np.random.default_rng(
        np.random.SeedSequence([seed, 12])
    )

    z = rng_z.normal(
        size=LARGE_N
    )

    eps = rng_proxy.normal(
        size=(LARGE_N, 5)
    )

    shared_scale = np.sqrt(
        rho_shortcut
    )

    residual_scale = np.sqrt(
        1.0 - rho_shortcut
    )

    proxy = (
        shared_scale * z[:, None]
        + residual_scale * eps
    )

    proxy *= orientations[None, :]

    corr = np.corrcoef(
        proxy,
        rowvar=False,
    )

    same_pairs = [
        (0, 1),
        (0, 3),
        (1, 3),
        (2, 4),
    ]

    opposite_pairs = [
        (0, 2),
        (0, 4),
        (1, 2),
        (1, 4),
        (3, 2),
        (3, 4),
    ]

    same_mean = float(
        np.mean([
            corr[i, j]
            for i, j in same_pairs
        ])
    )

    opposite_mean = float(
        np.mean([
            corr[i, j]
            for i, j in opposite_pairs
        ])
    )

    proxy_var = float(
        np.var(proxy, ddof=0)
    )

    assert abs(
        same_mean - 0.95
    ) < 0.01

    assert abs(
        opposite_mean + 0.95
    ) < 0.01

    assert abs(
        proxy_var - 1.0
    ) < 0.01

    for tau in S7_TAUS:
        score = tau * z

        score_sd = float(
            np.std(score, ddof=0)
        )

        assert abs(
            score_sd - tau
        ) / tau < 0.01

        print(
            f"seed={seed} "
            f"tau={tau:.6f} "
            f"scoreSD={score_sd:.6f} "
            f"proxyVar={proxy_var:.6f} "
            f"sameCorr={same_mean:.6f} "
            f"oppCorr={opposite_mean:.6f}"
        )

print(
    "PASS — S7 population tau and ±rho_shortcut "
    "proxy geometry."
)


# ------------------------------------------------------------------
# S7-D2 — actual-generator structure
# ------------------------------------------------------------------

print("\n── S7-D2: ACTUAL-GENERATOR STRUCTURE ──")

s7_tau = sg.MASTER_TAU[4]

s7 = sg.generate_s7(
    seed=S7_ACTUAL_SEED,
    tau=s7_tau,
)

assert s7.X.shape == (278, 1280)
assert int(s7.y.sum()) == 139
assert int((s7.y == 0).sum()) == 139

assert s7.metadata["shortcut_idx"] == [0, 1, 2, 3, 4]

assert s7.metadata["shortcut_orientations"] == [
    1, 1, -1, 1, -1
]

assert s7.metadata["background_idx"] == list(
    range(5, 1280)
)

assert s7.metadata["rho_shortcut"] == 0.95
assert s7.metadata["n_shortcut"] == 5
assert s7.metadata["n_background"] == 1275
assert s7.metadata["observed_beta_identifiable"] is False
assert s7.metadata["noise_scale"] == 1.0

assert np.all(
    s7.beta == 0.0
)

# Reconstruct latent z from the frozen RNG stream.
z = sg._spawn_rng(
    S7_ACTUAL_SEED,
    11,
).normal(
    size=sg.N_TOTAL
)

score = s7_tau * z

# Reconstruct labels independently from the frozen label stream.
expected_y = sg._balanced_labels_from_score(
    score=score,
    rng=sg._spawn_rng(
        S7_ACTUAL_SEED,
        14,
    ),
    noise_scale=1.0,
)

assert np.array_equal(
    s7.y,
    expected_y,
)

# Actual shortcut correlation geometry.
shortcut = s7.X[:, 0:5]

corr = np.corrcoef(
    shortcut,
    rowvar=False,
)

same_pairs = [
    (0, 1),
    (0, 3),
    (1, 3),
    (2, 4),
]

opposite_pairs = [
    (0, 2),
    (0, 4),
    (1, 2),
    (1, 4),
    (3, 2),
    (3, 4),
]

same_mean = float(
    np.mean([
        corr[i, j]
        for i, j in same_pairs
    ])
)

opposite_mean = float(
    np.mean([
        corr[i, j]
        for i, j in opposite_pairs
    ])
)

background = s7.X[:, 5:1280]

background_mean = float(
    np.mean(background)
)

background_var = float(
    np.var(background, ddof=0)
)

# Fixed background subset for finite-N independence sanity checking.
background_subset = background[
    :,
    [0, 100, 300, 600, 900, 1274],
]

background_corr = np.corrcoef(
    background_subset,
    rowvar=False,
)

background_offdiag = background_corr[
    np.triu_indices_from(
        background_corr,
        k=1,
    )
]

max_abs_background_corr = float(
    np.max(
        np.abs(background_offdiag)
    )
)

# Background should also not systematically track the latent direction.
z_background_corr = [
    float(
        np.corrcoef(
            z,
            background[:, j],
        )[0, 1]
    )
    for j in [0, 100, 300, 600, 900, 1274]
]

max_abs_z_background_corr = float(
    np.max(
        np.abs(z_background_corr)
    )
)

print(
    f"sameCorr={same_mean:.4f} "
    f"oppCorr={opposite_mean:.4f} "
    f"backgroundMean={background_mean:.4f} "
    f"backgroundVar={background_var:.4f} "
    f"maxBgCorr={max_abs_background_corr:.4f} "
    f"maxZBgCorr={max_abs_z_background_corr:.4f}"
)

assert same_mean > 0.90
assert opposite_mean < -0.90

assert abs(
    background_mean
) < 0.02

assert abs(
    background_var - 1.0
) < 0.05

# N=278 finite-sample software-verification bounds only.
assert max_abs_background_corr < 0.20
assert max_abs_z_background_corr < 0.20

print(
    "PASS — S7 actual generator matches frozen "
    "signed-proxy and background structure."
)


# ------------------------------------------------------------------
# Final firewall
# ------------------------------------------------------------------

print("\n── FINAL FIREWALL ──")

print("No probe was fit.")
print("No AUROC was computed.")
print("No threshold was selected.")
print("No regularization was selected.")
print("No calibration seed was used.")
print("No validation seed was used.")
print("No biological activation was computed.")

print("\nPASS — S6/S7 generator diagnostics complete.")
