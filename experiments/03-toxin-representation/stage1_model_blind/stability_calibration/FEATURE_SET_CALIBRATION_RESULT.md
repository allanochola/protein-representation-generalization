# Experiment 03 — feature-set fallback calibration result

**Status:** NOT YET CALIBRATED

The frozen feature-set fallback was evaluated synthetically before any Experiment 03 ESM embedding or SAE activation was observed.

Frozen fallback:

- feature-set size: k=5
- ranking: absolute signed positive-minus-negative mean difference
- stability metric: median pairwise Jaccard
- stability threshold: Jaccard >= 0.60

## Result at N=139

| Synthetic regime | Median Jaccard | PASS rate |
|---|---:|---:|
| stable single | 0.429 | 0.236 |
| near tie | 0.429 | 0.400 |
| distributed / superposed | 0.667 | 0.980 |

## Interpretation

The frozen fallback strongly recovers the distributed five-feature regime.

However, it also passes 40.0% of near-tie datasets. Therefore median pairwise Jaccard alone does not adequately distinguish a genuinely distributed five-feature signal from a smaller set of strong features accompanied by unstable top-k passengers.

The low PASS rate in the stable-single regime is not itself a failure of the fallback because a successfully calibrated single-feature branch would take precedence.

The feature-set fallback is therefore **not yet accepted as a calibrated biological decision rule**.

## Consequence

No biological SAE stability sweep may yet use this fallback.

The next pre-model redesign must add information about feature recurrence within the top-k set rather than changing k or the frozen Jaccard threshold post hoc.

No Experiment 03 model statistic was observed during this calibration.
