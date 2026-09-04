"""Synthetic generators for Experiment 04 sparse-probe calibration.

BIOLOGICAL FIREWALL:
This module generates synthetic arrays only. It must not load ESM embeddings,
protein sequences, toxin labels, SAE activations, or confirmatory data.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


N_POS = 139
N_NEG = 139
N_TOTAL = N_POS + N_NEG
P = 1280

S1_SIGNAL_IDX = np.array([0, 1, 2, 3, 4], dtype=int)
S1_SIGNS = np.array([1.0, 1.0, -1.0, 1.0, -1.0])

SQRT5 = float(np.sqrt(5.0))

S2_TAU_BASE = (0.10, 0.20, 0.30, 0.40)
S1_TAU_BASE = (0.50, 0.75, 1.00, 1.25, 1.50)
MASTER_TAU_BASE = S2_TAU_BASE + S1_TAU_BASE

S2_TAU = tuple(SQRT5 * x for x in S2_TAU_BASE)
S1_TAU = tuple(SQRT5 * x for x in S1_TAU_BASE)
MASTER_TAU = tuple(SQRT5 * x for x in MASTER_TAU_BASE)


@dataclass(frozen=True)
class SyntheticDataset:
    X: np.ndarray
    y: np.ndarray
    beta: np.ndarray
    scenario: str
    seed: int
    metadata: dict


def _rng(seed: int) -> np.random.Generator:
    """Return a fresh deterministic NumPy generator."""
    if not isinstance(seed, (int, np.integer)):
        raise TypeError("seed must be an integer")
    return np.random.default_rng(int(seed))


def _balanced_labels_from_score(
    score: np.ndarray,
    rng: np.random.Generator,
    noise_scale: float = 1.0,
) -> np.ndarray:
    """Create exactly balanced labels from a noisy latent score.

    A continuous logistic-noise term is added to the latent score. The top
    N_POS observations are assigned class 1 and the remainder class 0.

    This preserves the exact 139/139 discovery geometry while ensuring labels
    are generated from a stochastic latent decision variable.
    """
    score = np.asarray(score, dtype=float)

    if score.shape != (N_TOTAL,):
        raise ValueError(f"score must have shape ({N_TOTAL},)")

    if noise_scale < 0:
        raise ValueError("noise_scale must be non-negative")

    logistic_noise = rng.logistic(
        loc=0.0,
        scale=noise_scale,
        size=N_TOTAL,
    )

    latent = score + logistic_noise

    order = np.argsort(latent, kind="mergesort")

    y = np.zeros(N_TOTAL, dtype=np.int8)
    y[order[-N_POS:]] = 1

    assert int(y.sum()) == N_POS
    return y


def _validate_dataset(ds: SyntheticDataset) -> None:
    """Hard structural checks shared by every scenario."""
    if ds.X.shape != (N_TOTAL, P):
        raise AssertionError(f"X shape is {ds.X.shape}, expected {(N_TOTAL, P)}")

    if ds.y.shape != (N_TOTAL,):
        raise AssertionError("y has wrong shape")

    if ds.beta.shape != (P,):
        raise AssertionError("beta has wrong shape")

    if int(ds.y.sum()) != N_POS:
        raise AssertionError("positive count is not 139")

    if int((ds.y == 0).sum()) != N_NEG:
        raise AssertionError("negative count is not 139")

    if not np.isfinite(ds.X).all():
        raise AssertionError("X contains non-finite values")

    if not np.isfinite(ds.beta).all():
        raise AssertionError("beta contains non-finite values")


def generate_s0(seed: int) -> SyntheticDataset:
    """S0: null signal.

    X and y are generated independently. This is the hard false-positive
    control for the sparse-stability instrument.
    """
    rng = _rng(seed)

    X = rng.normal(size=(N_TOTAL, P))
    beta = np.zeros(P, dtype=float)

    # Independent balanced labels.
    perm = rng.permutation(N_TOTAL)
    y = np.zeros(N_TOTAL, dtype=np.int8)
    y[perm[:N_POS]] = 1

    ds = SyntheticDataset(
        X=X,
        y=y,
        beta=beta,
        scenario="S0",
        seed=int(seed),
        metadata={
            "signal": "null",
            "n_signal": 0,
        },
    )

    _validate_dataset(ds)
    return ds


def _tau_to_b(tau: float, k: int) -> float:
    """Convert frozen population score-SD target tau to equal-magnitude b."""
    tau = float(tau)

    if tau <= 0:
        raise ValueError("tau must be positive")

    if k <= 0:
        raise ValueError("k must be positive")

    return tau / float(np.sqrt(k))


def _matches_allowed_tau(tau: float, allowed: tuple[float, ...]) -> bool:
    """Floating-point-safe membership check for symbolic tau ladders."""
    return any(np.isclose(float(tau), x, rtol=0.0, atol=1e-12) for x in allowed)


def _generate_identifiable_sparse(
    seed: int,
    tau: float,
    scenario: str,
) -> SyntheticDataset:
    """Shared S1/S2 generator using tau as the public strength parameter."""
    tau = float(tau)
    b = _tau_to_b(tau=tau, k=5)

    rng = _rng(seed)

    X = rng.normal(size=(N_TOTAL, P))

    beta = np.zeros(P, dtype=float)
    beta[S1_SIGNAL_IDX] = b * S1_SIGNS

    score = X @ beta
    y = _balanced_labels_from_score(
        score=score,
        rng=rng,
        noise_scale=1.0,
    )

    ds = SyntheticDataset(
        X=X,
        y=y,
        beta=beta,
        scenario=scenario,
        seed=int(seed),
        metadata={
            "tau": tau,
            "b": b,
            "n_signal": 5,
            "signal_idx": S1_SIGNAL_IDX.tolist(),
            "signal_signs": S1_SIGNS.astype(int).tolist(),
            "noise_scale": 1.0,
        },
    )

    _validate_dataset(ds)
    return ds


def generate_s1(seed: int, tau: float) -> SyntheticDataset:
    """S1: identifiable sparse signal on the frozen S1 tau subset."""
    if not _matches_allowed_tau(tau, S1_TAU):
        raise ValueError(f"S1 tau must be one of {S1_TAU}")

    return _generate_identifiable_sparse(
        seed=seed,
        tau=float(tau),
        scenario="S1",
    )


def generate_s2(seed: int, tau: float) -> SyntheticDataset:
    """S2: weak identifiable sparse signal on the frozen S2 tau subset."""
    if not _matches_allowed_tau(tau, S2_TAU):
        raise ValueError(f"S2 tau must be one of {S2_TAU}")

    return _generate_identifiable_sparse(
        seed=seed,
        tau=float(tau),
        scenario="S2",
    )


def generate_s3(
    seed: int,
    rho: float,
    tau: float,
) -> SyntheticDataset:
    """S3: correlated interchangeable sparse signal.

    Five latent factors carry the predictive signal. Each latent factor is
    represented by five correlated observed coordinates.

    Labels depend on the latent factors themselves, not on a uniquely
    privileged observed coordinate. As rho increases, observed coordinates
    within each block become increasingly interchangeable.

    This scenario tests whether the sparse-probe instrument mistakes stable
    latent-factor predictability for stable observed-coordinate identity.
    """
    allowed_rho = {0.70, 0.90, 0.99}

    if float(rho) not in allowed_rho:
        raise ValueError(
            f"S3 rho must be one of {sorted(allowed_rho)}"
        )

    if not _matches_allowed_tau(tau, MASTER_TAU):
        raise ValueError(f"S3 tau must be one of {MASTER_TAU}")

    tau = float(tau)
    b = _tau_to_b(tau=tau, k=5)

    rng = _rng(seed)

    n_factors = 5
    block_size = 5
    n_block_features = n_factors * block_size

    # Five independent latent signal factors.
    Z = rng.normal(size=(N_TOTAL, n_factors))

    # Independent residual variation for the 25 block coordinates.
    E = rng.normal(size=(N_TOTAL, n_block_features))

    # Background coordinates are independent Gaussian noise.
    X = rng.normal(size=(N_TOTAL, P))

    # For:
    # x_j = sqrt(rho) * z + sqrt(1-rho) * e_j
    #
    # two coordinates from the same block have population correlation rho.
    for factor in range(n_factors):
        start = factor * block_size
        stop = start + block_size

        X[:, start:stop] = (
            np.sqrt(rho) * Z[:, [factor]]
            + np.sqrt(1.0 - rho) * E[:, start:stop]
        )

    latent_signs = S1_SIGNS.copy()
    latent_beta = float(b) * latent_signs

    # Critically, labels are generated from Z, not from one arbitrarily
    # privileged member of each observed feature block.
    score = Z @ latent_beta

    y = _balanced_labels_from_score(
        score=score,
        rng=rng,
        noise_scale=1.0,
    )

    # There is deliberately no unique ground-truth coefficient vector in
    # observed coordinate space. A zero beta avoids falsely designating one
    # member of each interchangeable block as "the" correct coordinate.
    beta = np.zeros(P, dtype=float)

    blocks = [
        list(range(i * block_size, (i + 1) * block_size))
        for i in range(n_factors)
    ]

    ds = SyntheticDataset(
        X=X,
        y=y,
        beta=beta,
        scenario="S3",
        seed=int(seed),
        metadata={
            "rho": float(rho),
            "tau": tau,
            "b": b,
            "n_latent_factors": n_factors,
            "block_size": block_size,
            "signal_blocks": blocks,
            "latent_signs": latent_signs.astype(int).tolist(),
            "noise_scale": 1.0,
            "observed_beta_identifiable": False,
        },
    )

    _validate_dataset(ds)
    return ds


def generate_s4(
    seed: int,
    tau: float,
) -> SyntheticDataset:
    """S4: dense distributed signal over 128 observed coordinates.

    Signal is intentionally spread across many coordinates so that strong
    prediction need not imply a compact sparse representation.

    The coefficient signs are deterministic and balanced as closely as
    possible. All 128 signal coordinates have equal absolute magnitude.
    """
    if not _matches_allowed_tau(tau, MASTER_TAU):
        raise ValueError(f"S4 tau must be one of {MASTER_TAU}")

    tau = float(tau)

    n_signal = 128
    b = _tau_to_b(tau=tau, k=n_signal)

    rng = _rng(seed)

    signal_idx = np.arange(n_signal, dtype=int)

    # Deterministic alternating signs.
    signs = np.ones(n_signal, dtype=float)
    signs[1::2] = -1.0

    X = rng.normal(size=(N_TOTAL, P))

    beta = np.zeros(P, dtype=float)
    beta[signal_idx] = float(b) * signs

    score = X @ beta

    y = _balanced_labels_from_score(
        score=score,
        rng=rng,
        noise_scale=1.0,
    )

    ds = SyntheticDataset(
        X=X,
        y=y,
        beta=beta,
        scenario="S4",
        seed=int(seed),
        metadata={
            "tau": tau,
            "b": b,
            "n_signal": n_signal,
            "signal_idx": signal_idx.tolist(),
            "sign_pattern": "alternating",
            "noise_scale": 1.0,
            "representation": "dense_distributed",
        },
    )

    _validate_dataset(ds)
    return ds


def generate_s5(
    seed: int,
    tau: float,
) -> SyntheticDataset:
    """S5: very dense weak signal across all 1,280 coordinates.

    Every observed coordinate carries weak predictive signal. This is the
    strongest negative control against equating predictive discrimination with
    sparse accessibility.

    Signs are deterministic and balanced by alternating across coordinates.
    """
    if not _matches_allowed_tau(tau, MASTER_TAU):
        raise ValueError(f"S5 tau must be one of {MASTER_TAU}")

    tau = float(tau)
    b = _tau_to_b(tau=tau, k=P)

    rng = _rng(seed)

    signal_idx = np.arange(P, dtype=int)

    signs = np.ones(P, dtype=float)
    signs[1::2] = -1.0

    X = rng.normal(size=(N_TOTAL, P))

    beta = float(b) * signs

    score = X @ beta

    y = _balanced_labels_from_score(
        score=score,
        rng=rng,
        noise_scale=1.0,
    )

    ds = SyntheticDataset(
        X=X,
        y=y,
        beta=beta,
        scenario="S5",
        seed=int(seed),
        metadata={
            "tau": tau,
            "b": b,
            "n_signal": P,
            "signal_idx": signal_idx.tolist(),
            "sign_pattern": "alternating",
            "noise_scale": 1.0,
            "representation": "very_dense_distributed",
        },
    )

    _validate_dataset(ds)
    return ds


def _spawn_rng(seed: int, stream_id: int) -> np.random.Generator:
    """Deterministic independent RNG stream derived from scenario seed."""
    if not isinstance(stream_id, (int, np.integer)):
        raise TypeError("stream_id must be an integer")

    ss = np.random.SeedSequence([int(seed), int(stream_id)])
    return np.random.default_rng(ss)


def generate_s6(
    seed: int,
    tau: float,
    rho: float,
) -> SyntheticDataset:
    """S6: stable sparse signal plus correlated nuisance.

    Public arguments must be supplied by keyword at experiment call sites.

    Tau controls only the five-coordinate true label-generating signal.
    Rho controls only covariance between each true signal coordinate and
    its 20 zero-direct-effect nuisance coordinates.
    """
    allowed_rho = {0.30, 0.60, 0.90}

    if not _matches_allowed_tau(tau, MASTER_TAU):
        raise ValueError(f"S6 tau must be one of {MASTER_TAU}")

    if float(rho) not in allowed_rho:
        raise ValueError(
            f"S6 rho must be one of {sorted(allowed_rho)}"
        )

    tau = float(tau)
    rho = float(rho)

    b = _tau_to_b(tau=tau, k=5)

    # Frozen observed-space layout.
    signal_idx = np.arange(0, 5, dtype=int)
    nuisance_idx = np.arange(5, 105, dtype=int)
    background_idx = np.arange(105, P, dtype=int)

    nuisance_per_signal = 20

    nuisance_blocks = [
        list(
            range(
                5 + j * nuisance_per_signal,
                5 + (j + 1) * nuisance_per_signal,
            )
        )
        for j in range(5)
    ]

    # Separate deterministic RNG streams.
    rng_signal = _spawn_rng(seed, 1)
    rng_nuisance = _spawn_rng(seed, 2)
    rng_background = _spawn_rng(seed, 3)
    rng_label = _spawn_rng(seed, 4)

    X = np.zeros((N_TOTAL, P), dtype=float)

    # True signal coordinates.
    signal_values = rng_signal.normal(
        size=(N_TOTAL, 5)
    )
    X[:, signal_idx] = signal_values

    # Correlated nuisance residuals are drawn independently of rho.
    nuisance_eps = rng_nuisance.normal(
        size=(N_TOTAL, 100)
    )

    residual_scale = np.sqrt(1.0 - rho ** 2)

    for j, block in enumerate(nuisance_blocks):
        X[:, block] = (
            rho * signal_values[:, [j]]
            + residual_scale
            * nuisance_eps[
                :,
                j * nuisance_per_signal:
                (j + 1) * nuisance_per_signal
            ]
        )

    # Independent background.
    X[:, background_idx] = rng_background.normal(
        size=(N_TOTAL, len(background_idx))
    )

    # Only the five true signal coordinates have direct effect.
    beta = np.zeros(P, dtype=float)
    beta[signal_idx] = b * S1_SIGNS

    score = X[:, signal_idx] @ beta[signal_idx]

    y = _balanced_labels_from_score(
        score=score,
        rng=rng_label,
        noise_scale=1.0,
    )

    ds = SyntheticDataset(
        X=X,
        y=y,
        beta=beta,
        scenario="S6",
        seed=int(seed),
        metadata={
            "tau": tau,
            "rho": rho,
            "b": b,
            "signal_idx": signal_idx.tolist(),
            "signal_signs": S1_SIGNS.astype(int).tolist(),
            "nuisance_idx": nuisance_idx.tolist(),
            "nuisance_blocks": nuisance_blocks,
            "background_idx": background_idx.tolist(),
            "nuisance_per_signal": nuisance_per_signal,
            "n_nuisance": 100,
            "nuisance_direct_beta": 0.0,
            "residual_scale": float(residual_scale),
            "noise_scale": 1.0,
        },
    )

    _validate_dataset(ds)
    return ds


def generate_s7(
    seed: int,
    tau: float,
) -> SyntheticDataset:
    """S7-v2: stable anchors plus heterogeneous signed post-label shortcut.

    Five independent observed anchor coordinates generate the latent label
    score with the frozen S1 sign template. Coordinate 5 is constructed only
    after the exactly balanced labels have been realized. Its heterogeneous
    signed amplitudes prospectively plant a mechanism for empirical
    orientation reversal of the same recurring coordinate under subsampling.
    """
    if not _matches_allowed_tau(tau, MASTER_TAU):
        raise ValueError(f"S7 tau must be one of {MASTER_TAU}")

    def _require(condition: bool, message: str) -> None:
        if not condition:
            raise AssertionError(f"S7-v2 invariant failed: {message}")

    tau = float(tau)
    b = tau / np.sqrt(5.0)

    anchor_idx = np.arange(0, 5, dtype=int)
    shortcut_idx = 5
    background_idx = np.arange(6, P, dtype=int)

    shortcut_base_amplitude = 0.02
    shortcut_aligned_amplitude = 8.0
    shortcut_anti_amplitude = -8.0
    shortcut_residual_sd = 0.25

    n_aligned_per_class = 10
    n_anti_per_class = 10
    n_base_per_class = 119

    # Frozen anchor and label RNG streams.
    rng_anchor = _spawn_rng(seed, 31)
    rng_label = _spawn_rng(seed, 32)

    # Five clean independent anchors.
    Z = rng_anchor.normal(
        size=(N_TOTAL, len(anchor_idx))
    )

    X = np.zeros((N_TOTAL, P), dtype=float)
    X[:, anchor_idx] = Z

    # §20.25: labels are realized before shortcut construction.
    eta = b * (Z @ S1_SIGNS)

    y = _balanced_labels_from_score(
        score=eta,
        rng=rng_label,
        noise_scale=1.0,
    )

    # §20.26-28:
    # Regime assignment begins only after realized y exists.
    # It depends only on seed (via stream 33) and realized class membership.
    # Stream 33 is consumed sequentially in class order 0, then 1.
    rng_regime = _spawn_rng(seed, 33)

    aligned_idx_by_class = {}
    anti_idx_by_class = {}
    base_idx_by_class = {}

    aligned_members = []
    anti_members = []
    base_members = []

    for class_value in (0, 1):
        class_idx = np.flatnonzero(y == class_value)
        class_idx = np.sort(class_idx)

        _require(
            len(class_idx) == 139,
            f"class {class_value} must contain 139 observations",
        )

        permuted = rng_regime.permutation(class_idx)

        aligned = permuted[:n_aligned_per_class]
        anti = permuted[
            n_aligned_per_class:
            n_aligned_per_class + n_anti_per_class
        ]
        base = permuted[
            n_aligned_per_class + n_anti_per_class:
        ]

        _require(
            len(aligned) == n_aligned_per_class,
            f"class {class_value} aligned count",
        )
        _require(
            len(anti) == n_anti_per_class,
            f"class {class_value} anti-aligned count",
        )
        _require(
            len(base) == n_base_per_class,
            f"class {class_value} base count",
        )

        aligned_sorted = sorted(int(x) for x in aligned)
        anti_sorted = sorted(int(x) for x in anti)
        base_sorted = sorted(int(x) for x in base)

        key = str(class_value)

        aligned_idx_by_class[key] = aligned_sorted
        anti_idx_by_class[key] = anti_sorted
        base_idx_by_class[key] = base_sorted

        aligned_members.extend(aligned_sorted)
        anti_members.extend(anti_sorted)
        base_members.extend(base_sorted)

    aligned_idx = sorted(aligned_members)
    anti_idx = sorted(anti_members)
    base_idx = sorted(base_members)

    aligned_set = set(aligned_idx)
    anti_set = set(anti_idx)
    base_set = set(base_idx)

    # §20.13-17 and §20.29-30.
    _require(
        not (aligned_set & anti_set),
        "aligned and anti-aligned sets must be disjoint",
    )
    _require(
        not (aligned_set & base_set),
        "aligned and base sets must be disjoint",
    )
    _require(
        not (anti_set & base_set),
        "anti-aligned and base sets must be disjoint",
    )
    _require(
        aligned_set | anti_set | base_set == set(range(N_TOTAL)),
        "regime sets must cover all observations exactly",
    )

    _require(
        len(aligned_idx) == 20,
        "overall aligned count must equal 20",
    )
    _require(
        len(anti_idx) == 20,
        "overall anti-aligned count must equal 20",
    )
    _require(
        len(base_idx) == 238,
        "overall base count must equal 238",
    )

    _require(
        aligned_idx == sorted(aligned_idx),
        "overall aligned membership list must be sorted",
    )
    _require(
        anti_idx == sorted(anti_idx),
        "overall anti-aligned membership list must be sorted",
    )
    _require(
        base_idx == sorted(base_idx),
        "overall base membership list must be sorted",
    )

    for key in ("0", "1"):
        _require(
            aligned_idx_by_class[key]
            == sorted(aligned_idx_by_class[key]),
            f"class {key} aligned membership list must be sorted",
        )
        _require(
            anti_idx_by_class[key]
            == sorted(anti_idx_by_class[key]),
            f"class {key} anti membership list must be sorted",
        )
        _require(
            base_idx_by_class[key]
            == sorted(base_idx_by_class[key]),
            f"class {key} base membership list must be sorted",
        )

    # Coordinate 5 is constructed only after y and regime assignment exist.
    ell = np.where(y == 1, 1.0, -1.0)

    amplitude = np.full(
        N_TOTAL,
        shortcut_base_amplitude,
        dtype=float,
    )
    amplitude[aligned_idx] = shortcut_aligned_amplitude
    amplitude[anti_idx] = shortcut_anti_amplitude

    # §20.18-21.
    _require(
        np.all(
            amplitude[aligned_idx]
            == shortcut_aligned_amplitude
        ),
        "all aligned observations must use amplitude +8.0",
    )
    _require(
        np.all(
            amplitude[anti_idx]
            == shortcut_anti_amplitude
        ),
        "all anti-aligned observations must use amplitude -8.0",
    )
    _require(
        np.all(
            amplitude[base_idx]
            == shortcut_base_amplitude
        ),
        "all base observations must use amplitude +0.02",
    )
    _require(
        shortcut_residual_sd == 0.25,
        "shortcut residual standard deviation must equal 0.25",
    )

    rng_shortcut_noise = _spawn_rng(seed, 34)

    epsilon = rng_shortcut_noise.normal(
        loc=0.0,
        scale=shortcut_residual_sd,
        size=N_TOTAL,
    )

    X[:, shortcut_idx] = amplitude * ell + epsilon

    rng_background = _spawn_rng(seed, 35)

    X[:, background_idx] = rng_background.normal(
        size=(N_TOTAL, len(background_idx))
    )

    beta = np.zeros(P, dtype=float)
    beta[anchor_idx] = b * S1_SIGNS

    # §20.1-24 directly checkable construction invariants.
    _require(
        X.shape == (278, 1280),
        "X.shape must equal (278, 1280)",
    )
    _require(
        y.shape == (278,),
        "y.shape must equal (278,)",
    )
    _require(
        beta.shape == (1280,),
        "beta.shape must equal (1280,)",
    )

    _require(
        int(np.sum(y == 1)) == 139,
        "exactly 139 observations must have y == 1",
    )
    _require(
        int(np.sum(y == 0)) == 139,
        "exactly 139 observations must have y == 0",
    )

    _require(
        np.isfinite(X).all(),
        "every value in X must be finite",
    )
    _require(
        np.isfinite(beta).all(),
        "every value in beta must be finite",
    )

    _require(
        anchor_idx.tolist() == [0, 1, 2, 3, 4],
        "anchor coordinates must equal [0,1,2,3,4]",
    )
    _require(
        S1_SIGNS.astype(int).tolist()
        == [1, 1, -1, 1, -1],
        "anchor signs must equal [1,1,-1,1,-1]",
    )
    _require(
        shortcut_idx == 5,
        "shortcut coordinate must equal 5",
    )
    _require(
        background_idx.tolist() == list(range(6, 1280)),
        "background coordinates must equal [6,...,1279]",
    )

    _require(
        beta[5] == 0.0,
        "beta[5] must equal 0.0",
    )
    _require(
        np.all(beta[6:] == 0.0),
        "beta[6:] must be identically zero",
    )
    _require(
        np.array_equal(
            beta[0:5],
            b * S1_SIGNS,
        ),
        "beta[0:5] must equal b*S1_SIGNS",
    )

    metadata = {
        "design_version": "S7-v2",
        "design_name":
            "stable_anchors_heterogeneous_signed_shortcut",
        "tau": tau,
        "b": float(b),
        "anchor_idx": anchor_idx.tolist(),
        "anchor_signs": S1_SIGNS.astype(int).tolist(),
        "shortcut_idx": shortcut_idx,
        "planted_sign_instability_idx": [5],
        "background_idx": background_idx.tolist(),
        "shortcut_base_amplitude": shortcut_base_amplitude,
        "shortcut_aligned_amplitude": shortcut_aligned_amplitude,
        "shortcut_anti_amplitude": shortcut_anti_amplitude,
        "shortcut_residual_sd": shortcut_residual_sd,
        "n_aligned_per_class": n_aligned_per_class,
        "n_anti_per_class": n_anti_per_class,
        "n_base_per_class": n_base_per_class,
        "shortcut_is_post_label": True,
        "shortcut_direct_beta_nonzero": False,
        "observed_beta_identifiable": True,
        "rng_stream_anchor": 31,
        "rng_stream_label": 32,
        "rng_stream_regime": 33,
        "rng_stream_shortcut_noise": 34,
        "rng_stream_background": 35,
        "aligned_idx": aligned_idx,
        "anti_idx": anti_idx,
        "base_idx": base_idx,
        "aligned_idx_by_class": aligned_idx_by_class,
        "anti_idx_by_class": anti_idx_by_class,
        "base_idx_by_class": base_idx_by_class,
        "noise_scale": 1.0,
    }

    # §20.11 and §20.31-35.
    _require(
        metadata["planted_sign_instability_idx"] == [5],
        "planted_sign_instability_idx must equal [5]",
    )
    _require(
        metadata["shortcut_is_post_label"] is True,
        "shortcut_is_post_label must be True",
    )
    _require(
        metadata["shortcut_direct_beta_nonzero"] is False,
        "shortcut_direct_beta_nonzero must be False",
    )
    _require(
        metadata["observed_beta_identifiable"] is True,
        "observed_beta_identifiable must be True",
    )

    _require(
        metadata["aligned_idx"] == aligned_idx,
        "metadata aligned membership must match realized assignment",
    )
    _require(
        metadata["anti_idx"] == anti_idx,
        "metadata anti membership must match realized assignment",
    )
    _require(
        metadata["base_idx"] == base_idx,
        "metadata base membership must match realized assignment",
    )
    _require(
        metadata["aligned_idx_by_class"]
        == aligned_idx_by_class,
        "metadata aligned by-class membership must match realization",
    )
    _require(
        metadata["anti_idx_by_class"]
        == anti_idx_by_class,
        "metadata anti by-class membership must match realization",
    )
    _require(
        metadata["base_idx_by_class"]
        == base_idx_by_class,
        "metadata base by-class membership must match realization",
    )

    # Ensure metadata and the amplitude vector used for coordinate 5 agree.
    _require(
        np.all(
            amplitude[metadata["aligned_idx"]]
            == metadata["shortcut_aligned_amplitude"]
        ),
        "metadata aligned memberships/amplitude must agree with coordinate 5",
    )
    _require(
        np.all(
            amplitude[metadata["anti_idx"]]
            == metadata["shortcut_anti_amplitude"]
        ),
        "metadata anti memberships/amplitude must agree with coordinate 5",
    )
    _require(
        np.all(
            amplitude[metadata["base_idx"]]
            == metadata["shortcut_base_amplitude"]
        ),
        "metadata base memberships/amplitude must agree with coordinate 5",
    )

    ds = SyntheticDataset(
        X=X,
        y=y,
        beta=beta,
        scenario="S7",
        seed=int(seed),
        metadata=metadata,
    )

    # §20.36: existing general validation follows S7-specific checks.
    _validate_dataset(ds)

    return ds
