# Experiment 03 — feature-set fallback specification

**Status:** PRE-MODEL / FROZEN BEFORE FEATURE-SET CALIBRATION

## Purpose

The first single-feature synthetic calibration returned `UNCALIBRATED`.

This fallback is defined before any Experiment 03 ESM embedding or SAE activation is observed.

The fallback is not tuned to the observed numerical difficulty of the first calibration. Its parameters are fixed from the existing synthetic superposition setup and interpretability considerations.

## Trigger

The feature-set fallback is used automatically if the preregistered single-feature stability gate does not support a single signed latent.

There is no post-result choice between single-feature and feature-set analyses.

## Feature-set size

Frozen feature-set size:

`k = 5`

No sweep over k is permitted after biological activations are visible.

## Feature ranking

For each latent j:

`score_j = mean_positive(j) - mean_negative(j)`

Latents are ranked by:

`abs(score_j)`

Feature identity retains sign:

- `(j, +)` if `score_j >= 0`
- `(j, -)` if `score_j < 0`

The selected feature set is the top 5 signed latent identities.

Ties are broken by lower latent index.

## Stability metric

For two selected feature sets A and B:

`J(A,B) = |A ∩ B| / |A ∪ B|`

The primary feature-set stability statistic is the median pairwise Jaccard similarity across perturbation-selected top-5 signed feature sets.

Frozen stability gate:

`median pairwise Jaccard >= 0.60`

For two sets of exactly five features:

- 3 shared features gives J = 3/7 = 0.429 -> FAIL
- 4 shared features gives J = 4/6 = 0.667 -> PASS
- 5 shared features gives J = 1.000 -> PASS

Therefore the gate effectively requires at least four of five signed features to recur in a typical pair of selected sets.

## Supporting diagnostics

Report descriptively:

- per-feature inclusion frequency;
- most common signed feature set;
- modal-set frequency;
- pairwise Jaccard distribution.

These diagnostics do not independently change the PASS/FAIL decision unless a later pre-model calibration explicitly freezes an additional rule.

## Synthetic calibration requirement

Before biological model contact, the frozen `k=5`, signed top-k rule, and Jaccard >=0.60 gate must be evaluated on synthetic regimes.

At minimum the calibration must include:

1. stable single-feature signal;
2. near-tied signal;
3. distributed / superposed five-feature signal.

The desired behavior is:

- stable single regime: feature-set stability may pass, but this does not override a valid single-feature claim;
- near-tie regime: fallback should not manufacture evidence for a uniquely interpretable mechanism merely because multiple strong features are retained;
- distributed regime: the top-5 set should be recoverable stably when the signal is genuinely distributed across five latents.

If the feature-set gate cannot distinguish these regimes in a scientifically interpretable way, the fallback remains uncalibrated and biological model contact is not permitted under it.

## Model-contact boundary

This specification and its synthetic calibration are fully model-blind.

No ESM embedding, SAE activation, biological feature score, or confirmatory statistic may be inspected before the fallback calibration and final biological stability-sweep specification are frozen.
