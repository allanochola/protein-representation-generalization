# Experiment 03 — fixed-identity concentration calibration

**Status:** PRE-MODEL / FROZEN BEFORE CONCENTRATION CALIBRATION

## Motivation

The existing synthetic regimes are:

- A: stable single feature
- B: near-tied two-feature signal
- C: stable identity-fixed five-feature signal

Regime C already provides the positive control for the k=5 feature-set
fallback.

What is missing is a negative control in which real class-associated signal
exists but is distributed across substantially more than five latents.

The purpose of this calibration is therefore to test whether the frozen k=5
feature-set instrument can distinguish:

- C: a genuine stable five-feature representation
from
- D: a diffuse higher-dimensional representation that should not support a
  privileged five-feature interpretability claim.

No biological ESM or SAE activation is used.

## Existing frozen feature-set parameters

These are unchanged:

- feature-set size: k = 5
- ranking score: abs(mean_positive - mean_negative)
- signed latent identity retained
- median pairwise Jaccard threshold: >=0.60
- recurrence threshold: >=0.80
- minimum recurrent full-dataset nominated features: 4 of 5
- 100 frozen 80%-subsample perturbations

The Jaccard, recurrence, k, and perturbation rules are not changed in response
to prior calibration results.

## Regime C — stable fixed five

Unchanged from the frozen generator:

- latents 0–4: +0.45
- latents 5–31: 0

Total planted squared signal:

5 * 0.45^2 = 1.0125

This is the positive control for the k=5 fallback.

## Regime D — diffuse fixed sixteen

Add a fourth synthetic regime:

- latents 0–15: +0.25
- latents 16–31: 0

Total planted squared signal:

16 * 0.25^2 = 1.0000

Thus C and D have approximately matched total planted signal energy while
differing strongly in dimensionality.

Desired interpretation:

- C should support a stable k=5 feature-set claim.
- D should fail the k=5 feature-set claim because the signal is distributed
  across substantially more than five latents.

## Fixed-identity concentration statistic

For each complete synthetic dataset:

1. Compute the full-dataset top-5 signed latent set using the frozen ranking
   rule. Call this fixed set S5.

2. For each frozen perturbation b, compute signed latent scores:

   score_bj = mean_positive_b(j) - mean_negative_b(j)

3. Define absolute score mass:

   mass_bj = abs(score_bj)

4. Compute the fraction of total absolute score mass captured by the SAME
   fixed full-dataset identities S5:

   concentration_b =
       sum_{j in S5} mass_bj
       /
       sum_{j=1..32} mass_bj

The identities in the numerator are not reselected inside each perturbation.

The primary concentration statistic is:

median_fixed_top5_concentration =
    median_b(concentration_b)

## Combined feature-set decision

Existing Jaccard and recurrence gates remain necessary.

For concentration threshold T, the candidate combined gate is:

- median pairwise Jaccard >= 0.60
- at least 4 of 5 full-dataset nominated signed latents recur in >=80% of
  perturbations
- median fixed-top5 concentration >= T

All three conditions are required.

## Concentration threshold grid

Candidate thresholds:

- 0.30
- 0.35
- 0.40
- 0.45
- 0.50
- 0.55
- 0.60
- 0.65
- 0.70
- 0.75
- 0.80

## Threshold-selection rule

Threshold selection is performed only at N=139.

Choose the LOWEST concentration threshold satisfying all of:

- Regime C stable-five combined PASS rate >= 0.70
- Regime D diffuse-sixteen combined PASS rate <= 0.10
- Regime B near-tie combined PASS rate <= 0.10

Regime A stable-single is reported diagnostically but is not required to pass
the feature-set fallback.

The C >=0.70 criterion is chosen because the already-frozen recurrence gate
passed C in 0.80 of N=139 synthetic datasets; requiring >=0.90 would be
incompatible with the frozen upstream gate before concentration is evaluated.

If no threshold in the frozen grid satisfies all three conditions, the
feature-set instrument remains uncalibrated.

No threshold may be added, removed, or changed after the calibration result is
observed.

## Required reporting

For every regime and N report:

- median fixed-top5 concentration
- 5th percentile
- 95th percentile
- Jaccard+recurrence PASS rate
- final Jaccard+recurrence+concentration PASS rate for each threshold

At N=139 explicitly report B, C, and D PASS rates under the selected threshold.

## Model-contact boundary

This calibration remains fully synthetic and model-blind.

No Experiment 03 ESM embedding, SAE activation, biological feature score, or
confirmatory statistic may be inspected before:

1. this specification is committed;
2. the implementation is committed;
3. the synthetic calibration is run and recorded;
4. the final biological stability-sweep specification is frozen.
