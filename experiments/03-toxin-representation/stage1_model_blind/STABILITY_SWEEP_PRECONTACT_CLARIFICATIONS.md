# Experiment 03 — final pre-contact clarifications

**Status:** PRE-MODEL / FROZEN BEFORE FIRST BIOLOGICAL ESM CONTACT

**Parent artifacts:**

- `STABILITY_SWEEP_SPEC.md`
- `STABILITY_SWEEP_PRECONTACT_AMENDMENT.md`

These clarifications close three implementation details before any
Experiment-03 biological sequence is passed through ESM-2.

No biological ESM embedding, SAE activation, feature nomination, or
confirmatory representation result has been inspected.

## 1. Discovery-negative standardization and confirmatory FPR calibration

The frozen Arm-B score standardizes each nominated latent using only the
139 discovery negatives:

`mu_neg[j] = mean_discovery_negative(z[:,j])`

`sigma_neg[j] = sample_sd_discovery_negative(z[:,j], ddof=1)`

These discovery estimates are then applied unchanged to every later protein,
including confirmatory positives and confirmatory negatives.

This construction deliberately keeps all score-shaping parameters outside the
confirmatory set.

The confirmatory operating threshold is nevertheless estimated empirically
from the full confirmatory-negative distribution of the resulting frozen
Arm-B score.

Therefore a global location or scale shift between discovery negatives and
confirmatory negatives does not by itself invalidate the requested FPR
operating point: the confirmatory-negative quantile determines that operating
threshold.

Discovery-negative standardization remains load-bearing for the relative
weighting of the five nominated latents and is never recomputed from
confirmatory data.

## 2. Fixed-threshold paired positive bootstrap

The confirmatory uncertainty procedure matches the frozen pre-data
feasibility simulator.

For each compared arm:

1. compute all confirmatory-negative scores once;
2. determine the frozen 5% FPR operating threshold once from the complete
   confirmatory-negative set using the preregistered deterministic threshold
   construction;
3. determine the corresponding 1% FPR threshold once for the secondary metric;
4. hold those negative-derived thresholds fixed during the positive-cluster
   bootstrap.

The paired bootstrap then resamples only the 161 confirmatory positive toxin
clusters.

For every bootstrap replicate:

- use the same resampled positive-cluster indices for Arm A and Arm B;
- evaluate both arms using their own already-fixed negative-derived operating
  thresholds;
- compute the paired difference in positive TPR.

Confirmatory negatives are not resampled and operating thresholds are not
re-estimated inside bootstrap replicates.

This matches the feasibility simulator's frozen modeling boundary: positive
cluster uncertainty is propagated through the paired bootstrap, while
finite-negative FPR precision is treated separately rather than converted
into assumed threshold uncertainty.

## 3. Near-degenerate discovery-negative variance guard

The equal-weight signed z-score construction must not permit a nearly constant
latent to dominate the five-feature score through division by an extremely
small standard deviation.

For the five nominated latents, let:

`S = {sigma_neg[j] : j in S5}`

and define:

`sigma_median = median(S)`

The scorer passes the variance guard only if:

1. every `sigma_neg[j]` is finite;
2. every `sigma_neg[j] > 0`;
3. `sigma_median` is finite and strictly positive;
4. for every nominated latent j:

   `sigma_neg[j] >= 1e-3 * sigma_median`

Equivalently, no nominated discovery-negative standard deviation may be more
than three orders of magnitude below the median nominated standard deviation.

If any nominated latent violates this condition:

- Stage 1 terminates as a technical failure;
- no epsilon replacement is added;
- no latent is dropped or replaced;
- no alternative normalization is introduced;
- no confirmatory sequence is embedded.

The complete set of five `mu_neg`, five `sigma_neg`, `sigma_median`, and all
five ratios `sigma_neg[j] / sigma_median` must be recorded in the frozen
discovery-to-confirmatory handoff artifact.

## 4. Confirmatory handoff boundary

A Stage-1 PASS is not sufficient by itself to open the confirmatory set.

Before any confirmatory sequence is passed through ESM-2, all of the following
must already be committed:

- Stage-1 stability result;
- five frozen signed latent identities;
- residue-max pooling rule;
- five discovery-negative means;
- five discovery-negative standard deviations;
- variance-guard result;
- equal-weight signed negative-z-score combination rule;
- confirmatory firewall PASS artifact;
- model/SAE provenance artifact;
- hashes of the discovery membership and Stage-1 result artifacts.

Only after this immutable handoff exists may confirmatory representation
extraction begin.
