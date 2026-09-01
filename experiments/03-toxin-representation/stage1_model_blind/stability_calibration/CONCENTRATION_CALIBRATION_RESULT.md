# Experiment 03 — fixed-identity concentration calibration result

**Status:** CALIBRATION THRESHOLD SELECTED; INDEPENDENT VALIDATION REQUIRED

The frozen concentration calibration was run before any Experiment 03
biological ESM embedding or SAE activation was observed.

## Frozen calibration procedure

The preregistered procedure evaluated the concentration threshold grid:

0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80

At N=139, the frozen rule selected the LOWEST threshold satisfying all of:

- stable-five C PASS >= 0.70
- near-tie B PASS <= 0.10
- diffuse-sixteen D PASS <= 0.10

## Selected threshold

The selected concentration threshold is:

`0.35`

At N=139:

- A stable-single PASS: 0.056
- B near-tie PASS: 0.094
- C stable-five PASS: 0.800
- D diffuse-sixteen PASS: 0.062

Threshold 0.30 failed because D PASS was 0.108.

Threshold 0.35 was therefore the first threshold satisfying the frozen
selection rule.

## Regime naming clarification

The implementation label `C_distributed` refers to the planted stable-five
positive control:

- latents 0–4: +0.45
- all other latents: 0

For subsequent reporting this regime is called `C_stable_five`.

`D_diffuse_sixteen` is:

- latents 0–15: +0.25
- all other latents: 0

No planted effects are changed by this naming clarification.

## Interpretation boundary

The 0.35 threshold is a calibration output, not an independent validation
result.

The operating characteristics observed on the calibration datasets must not
be presented as independent validation performance.

A separate validation run using fresh non-overlapping seeds and the fixed
0.35 threshold is required before biological model contact.

No threshold search is permitted in that validation run.

## Model-contact status

No Experiment 03 biological ESM embedding, SAE activation, feature nomination,
or confirmatory representation statistic was observed during this calibration.
