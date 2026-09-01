# Experiment 03 — feature-set recurrence gate specification

**Status:** PRE-MODEL / FROZEN BEFORE RECURRENCE CALIBRATION

## Motivation

The frozen k=5 feature-set calibration showed high sensitivity to the
distributed five-feature synthetic regime but insufficient specificity
against the near-tie regime.

At N=139 and median pairwise Jaccard >=0.60:

- distributed regime PASS rate: 0.980
- near-tie regime PASS rate: 0.400

The failure mode is interpretable: in the near-tie regime the two genuine
signal latents can recur while unstable noise features occupy the remaining
top-k positions.

The Jaccard threshold and k are not changed in response to this result.

## Frozen existing parameters

- feature-set size: k = 5
- ranking score: abs(mean_positive - mean_negative)
- signed latent identity is retained
- median pairwise Jaccard threshold: >=0.60
- perturbations: the existing frozen 100 80%-subsample perturbations

## Full-dataset nominated feature set

For each realized dataset, compute the signed top-5 feature set using the
complete dataset before perturbation subsampling.

This set is the nominated feature set whose reproducibility is evaluated.

## Inclusion frequency

For each signed latent in the full-dataset nominated top-5 set, define:

inclusion_frequency =
    number of perturbation top-5 sets containing that signed latent
    / number of perturbations

A signed latent is recurrent when:

inclusion_frequency >= 0.80

The 0.80 threshold is frozen before recurrence-calibration results are
observed.

## Recurrence gate

Count how many of the five full-dataset nominated signed latents are recurrent.

The recurrence gate passes when:

n_recurrent >= 4

Thus at least four of the five features nominated on the complete discovery
dataset must recur in at least 80% of perturbation-selected feature sets.

## Combined feature-set gate

The feature-set fallback passes only when BOTH conditions hold:

1. median pairwise Jaccard >= 0.60
2. at least 4 of 5 full-dataset nominated signed latents have
   inclusion_frequency >= 0.80

Neither condition may substitute for the other.

## Branch precedence

A successfully calibrated single-feature decision has precedence over the
feature-set fallback.

The feature-set rule is intended to support a reproducible distributed
feature-set claim, not to reinterpret a stable single latent as a five-feature
mechanism.

## Synthetic calibration objective

The combined gate will be evaluated without changing the existing synthetic
regime parameters.

Desired behavior at N=139:

- distributed / superposed regime: high PASS rate
- near-tie regime: low PASS rate

The stable-single regime is reported diagnostically but is not required to
pass the feature-set fallback because it belongs to the single-feature branch.

No recurrence threshold, recurrent-feature count, k, Jaccard threshold, or
synthetic effect size may be changed after the recurrence-calibration result
is observed merely to obtain separation.

If the combined rule remains insufficiently discriminative, the feature-set
fallback remains uncalibrated.

## Model-contact boundary

This specification and its subsequent synthetic calibration remain
model-blind.

No Experiment 03 ESM embedding, SAE activation, biological feature score, or
confirmatory representation statistic may be inspected before calibration is
closed and the biological stability-sweep specification is frozen.
