# Experiment 03 — Stage 1 stability-gate calibration

**Status:** PRE-MODEL / SYNTHETIC ONLY

This calibration is performed before any Experiment 03 ESM embedding,
SAE activation, feature nomination, or confirmatory representation
statistic is observed.

## Purpose

The purpose is to calibrate the feature-stability decision rule used
during Stage 1 discovery.

The calibration asks whether candidate stability criteria distinguish
three qualitatively different feature-selection regimes.

## Regime A — stable single feature

One latent contains a clearly stronger class-associated signal than
all competing latents.

Desired decision:

- single-feature gate: PASS

## Regime B — near-tied features

Two or more latents contain similar class-associated signal such that
the identity of the top-ranked latent changes across discovery
perturbations.

Desired decision:

- biological signal may be present
- single-feature gate: FAIL

A stable mechanistic interpretation should not be assigned to one
arbitrary winner.

## Regime C — distributed / superposed signal

Class-associated information is distributed across multiple latents
without one reliably dominant latent.

Desired decision:

- single-feature gate: FAIL
- feature-set fallback remains eligible for later evaluation

## Discovery geometry

Calibration mirrors the frozen Stage 1 discovery sizes:

- N=100 positives + N=100 negatives
- N=120 positives + N=120 negatives
- N=139 positives + N=139 negatives

The calibration does not use biological sequences or model-derived
representations.

## Candidate stability statistics

The calibration will evaluate:

1. pairwise agreement in the identity of the top signed latent;
2. modal signed-latent frequency;
3. change in stability between N=120 and N=139.

Long-stratum perturbation stability is a separate biological discovery
diagnostic and is not calibrated from these generic synthetic regimes.

## Calibration principle

Thresholds are selected before biological model contact.

They should:

- reliably accept the stable-single-feature regime;
- reject near-tied feature identity;
- reject distributed/superposed feature identity;
- avoid choosing thresholds merely because they are convenient for the
  later biological result.

No Experiment 03 model statistic may be inspected before this
calibration rule and the subsequent stability specification are frozen.
