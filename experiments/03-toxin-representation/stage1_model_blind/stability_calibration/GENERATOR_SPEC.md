# Experiment 03 — synthetic stability calibration generator

**Status:** PRE-MODEL / FROZEN BEFORE SIMULATION

## Synthetic representation

Each synthetic example has 32 independent latent dimensions.

Classes are balanced:
- positive: N
- negative: N

Base latent values are standard normal.

Class-associated signal is introduced as an additive mean shift in the positive class.

## Regimes

### A — stable single feature

Signal shifts:

- latent 0: +1.00
- latent 1: +0.35
- all others: 0

Expected qualitative behavior:
- one signed latent should dominate reliably.

### B — near tie

Signal shifts:

- latent 0: +0.80
- latent 1: +0.78
- all others: 0

Expected qualitative behavior:
- top-feature identity should switch frequently between the two leading latents.

### C — distributed / superposed

Signal shifts:

- latents 0–4: +0.45 each
- all others: 0

Expected qualitative behavior:
- signal is present but no single latent should dominate reliably.

## Discovery sizes

N per class:

- 100
- 120
- 139

## Outer simulation

For each regime and discovery size:

- 500 independent synthetic datasets

Frozen outer seeds:

`seed = 100000 * regime_index + 1000 * N + replicate_index`

where:
- regime_index A=1, B=2, C=3
- replicate_index = 0,...,499

## Perturbation procedure

Within each synthetic dataset:

- 100 deterministic perturbations
- sample 80% of positives without replacement
- sample 80% of negatives without replacement
- class balance preserved

Frozen perturbation seed:

`seed = outer_seed * 1000 + perturbation_index`

where perturbation_index = 0,...,99.

## Feature ranking

For each latent j:

`score_j = mean_positive(j) - mean_negative(j)`

Signed feature identity is:

- `(j, +)` if score_j >= 0
- `(j, -)` if score_j < 0

Features are ranked by `abs(score_j)`.

The top signed latent is the signed feature with greatest absolute score.

Ties are broken by lower latent index.

## Stability statistics

For each synthetic dataset:

1. **pairwise top-feature agreement**
   - fraction of all perturbation pairs that nominate the same signed latent;

2. **modal signed-latent frequency**
   - fraction of perturbations selecting the most common signed latent.

For each regime × N, report:
- median;
- 5th percentile;
- 95th percentile

for both statistics.

## Threshold-selection rule

Candidate single-feature thresholds are evaluated only after all synthetic outputs are generated.

The chosen gate should satisfy, at N=139:

- at least 90% of stable-single datasets PASS;
- at most 10% of near-tie datasets PASS;
- at most 10% of distributed datasets PASS.

Among threshold pairs satisfying these criteria, choose the least stringent pair in lexicographic order:

1. lowest pairwise-agreement threshold;
2. then lowest modal-frequency threshold.

Candidate threshold grids:

Pairwise agreement:
- 0.50
- 0.55
- 0.60
- 0.65
- 0.70
- 0.75
- 0.80
- 0.85
- 0.90

Modal frequency:
- 0.60
- 0.65
- 0.70
- 0.75
- 0.80
- 0.85
- 0.90
- 0.95

If no threshold pair satisfies the calibration criteria, the single-feature gate is declared uncalibrated and must be redesigned before biological model contact.

## Plateau criterion calibration

The N=120 → N=139 change is descriptive during this synthetic calibration.

No biological plateau threshold is frozen from intuition alone.

After synthetic calibration, a plateau criterion may be added only if its behavior across the three synthetic regimes is documented and frozen before biological model contact.
