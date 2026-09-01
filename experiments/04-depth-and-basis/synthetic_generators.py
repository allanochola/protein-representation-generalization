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
