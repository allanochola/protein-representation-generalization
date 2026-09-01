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


def _generate_identifiable_sparse(
    seed: int,
    b: float,
    scenario: str,
) -> SyntheticDataset:
    """Shared generator for S1/S2 identifiable five-coordinate signal."""
    if b <= 0:
        raise ValueError("b must be positive")

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
            "b": float(b),
            "n_signal": 5,
            "signal_idx": S1_SIGNAL_IDX.tolist(),
            "signal_signs": S1_SIGNS.astype(int).tolist(),
            "noise_scale": 1.0,
        },
    )

    _validate_dataset(ds)
    return ds


def generate_s1(seed: int, b: float) -> SyntheticDataset:
    """S1: identifiable sparse signal."""
    allowed = {0.50, 0.75, 1.00, 1.25, 1.50}

    if float(b) not in allowed:
        raise ValueError(f"S1 b must be one of {sorted(allowed)}")

    return _generate_identifiable_sparse(
        seed=seed,
        b=float(b),
        scenario="S1",
    )


def generate_s2(seed: int, b: float) -> SyntheticDataset:
    """S2: weak identifiable sparse signal."""
    allowed = {0.10, 0.20, 0.30, 0.40}

    if float(b) not in allowed:
        raise ValueError(f"S2 b must be one of {sorted(allowed)}")

    return _generate_identifiable_sparse(
        seed=seed,
        b=float(b),
        scenario="S2",
    )
