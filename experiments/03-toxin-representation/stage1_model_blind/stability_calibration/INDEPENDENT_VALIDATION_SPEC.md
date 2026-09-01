# Experiment 03 — independent synthetic validation

**Status:** PRE-MODEL / FROZEN BEFORE VALIDATION RUN

## Purpose

The concentration threshold was selected by the previously preregistered
synthetic calibration procedure.

The selected frozen threshold is:

`CONCENTRATION_THRESHOLD = 0.35`

This independent validation does not search, tune, or replace that threshold.

The purpose is to estimate out-of-calibration operating characteristics on
fresh synthetic datasets drawn from the same frozen regimes.

No Experiment 03 biological ESM or SAE activation is used.

## Frozen feature-set instrument

The complete feature-set PASS rule is:

1. feature-set size: k = 5
2. ranking: abs(mean_positive - mean_negative)
3. signed latent identities retained
4. median pairwise Jaccard >= 0.60
5. at least 4 of the 5 full-dataset nominated signed latents recur in >=80%
   of the 100 frozen perturbations
6. median fixed-top-5 concentration >= 0.35

All conditions are required.

No component of this rule may change after validation results are observed.

## Regime definitions

### A — stable single

- latent 0: +1.00
- latent 1: +0.35
- all others: 0

Diagnostic control only for the feature-set branch.

### B — near tie

- latent 0: +0.80
- latent 1: +0.78
- all others: 0

Negative control for an over-interpreted feature set.

### C — stable five

Prior code label: `C_distributed`.

Interpretive label from this point forward: `C_stable_five`.

Planted structure is unchanged:

- latents 0–4: +0.45
- all others: 0

This is the positive control for the k=5 feature-set instrument.

### D — diffuse sixteen

- latents 0–15: +0.25
- all others: 0

Negative control for a representation whose signal is too diffuse to justify
a privileged k=5 interpretation.

No planted effect is changed from the calibration run.

## Validation geometry

Validation is performed at:

- N=100 per class
- N=120 per class
- N=139 per class

Primary validation decision uses N=139.

For every regime and N:

- 500 independent outer datasets
- 100 deterministic 80%-subsample perturbations per outer dataset

## Independent seed namespace

Calibration outer seeds were:

`100000 * regime_index + 1000 * N + replicate_index`

for replicate_index = 0,...,499.

Validation uses:

`10000000 + 100000 * regime_index + 1000 * N + replicate_index`

where:

- A regime_index = 1
- B regime_index = 2
- C regime_index = 3
- D regime_index = 4
- replicate_index = 0,...,499

Perturbation seeds are:

`outer_seed * 1000 + perturbation_index`

with perturbation_index = 0,...,99.

No calibration outer seed is reused.

## Validation success criteria

At N=139, independent validation PASS requires ALL:

- C stable-five PASS rate >= 0.70
- B near-tie PASS rate <= 0.10
- D diffuse-sixteen PASS rate <= 0.10

A stable-single is reported descriptively and does not determine feature-set
validation.

## Failure rule

If any primary validation criterion fails:

- the feature-set instrument is not independently validated;
- the biological Stage 1 SAE sweep does not proceed under this instrument;
- no threshold, k, recurrence rule, concentration rule, planted effect size,
  seed rule, or success criterion may be changed in response.

This is the final synthetic validation of this feature-set instrument.

## Reporting

For every regime and N report:

- pairwise top-feature agreement
- modal top-feature frequency
- median pairwise Jaccard
- recurrence-only PASS rate
- Jaccard+recurrence PASS rate
- median fixed-top-5 concentration
- final frozen-instrument PASS rate

At N=139 explicitly report:

- B near-tie PASS rate
- C stable-five PASS rate
- D diffuse-sixteen PASS rate
- overall validation PASS/FAIL

No threshold grid or threshold-selection result is generated during validation.

## Model-contact boundary

This validation remains fully synthetic and model-blind.

No Experiment 03 ESM embedding, SAE activation, biological feature score, or
confirmatory representation statistic may be inspected before:

1. this specification is committed;
2. the validation implementation is committed;
3. the validation run is completed and recorded;
4. the biological stability-sweep specification is frozen.
