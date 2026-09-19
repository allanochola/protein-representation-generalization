# Resolvability and Operating-Point Plan

**State:** simulation specification; no protected performance inputs allowed.

## Targets

The design must demonstrate:

- at least 80% power for `DeltaTPR@FPR5 = +0.10`; and
- median confidence-interval half-width no greater than 0.10.

The effect grid must include `0, +0.05, +0.10, +0.15, +0.20`.

## Unit and pairing

Simulation operates on biological-family units. It must preserve paired ESM
and comparator outcomes within each family. Protein-level Bernoulli draws that
treat family members as independent are invalid.

At minimum, simulate:

- several positive-family size distributions matching metadata-only census
  geometry;
- within-family outcome correlation/heterogeneity regimes;
- paired ESM/comparator discordance regimes at each effect size;
- family-weighted and protein-weighted summaries, with one designated primary;
- uncertainty in the calibration-derived thresholds.

The primary weighting estimand must be chosen before confirmatory evaluation.
Equal-family weighting is the default candidate because family is the intended
generalization unit; protein weighting answers a different question and may be
reported secondarily.

## Five-percent FPR audit

The calibration and evaluation negative-family counts must be audited
separately.

The simulation must quantify:

- attainable empirical quantile resolution at 5% FPR;
- threshold variability across calibration-family resamples;
- realized evaluation FPR uncertainty after threshold transfer;
- sensitivity of `DeltaTPR` to plausible threshold error;
- effects of negative-family size concentration.

A nominally large number of negative proteins cannot compensate for a small
number of independent negative families.

## Confidence interval candidates

Compare only methods valid for clustered paired data, such as:

- paired family bootstrap with calibration refit nested inside each replicate;
- hierarchical bootstrap when within-family protein sampling is part of the
  target estimand;
- a prespecified paired family-level model with simulation-verified coverage.

Coverage, type-I error, power, interval width, failure rate, and boundary
behavior must be reported for every candidate method. The selected method must
be frozen before protected evaluation.

## Gate-B output

The Phase-0 report must provide a decision table indexed by:

`n_positive_families, n_calibration_negative_families,`
`n_evaluation_negative_families, DeltaTPR, discordance_regime,`
`family_heterogeneity`

For each cell report power, median interval half-width, empirical coverage,
and operating-point error. If no realistic allocation clears both primary
targets, Experiment 05 closes unresolved before ESM extraction.
