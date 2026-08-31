# Experiment 03 — stability calibration result

**Status:** UNCALIBRATED

The preregistered synthetic calibration was run from the frozen generator implementation before any Experiment 03 ESM embedding or SAE activation was observed.

## Result

No candidate pair of:

- pairwise top-signed-latent agreement threshold; and
- modal signed-latent frequency threshold

satisfied the frozen calibration requirements at N=139:

- >=90% PASS in the stable-single regime;
- <=10% PASS in the near-tie regime;
- <=10% PASS in the distributed/superposed regime.

Therefore the proposed single-feature stability gate is **not calibrated** and must not be used on biological model activations.

## Diagnostic finding

The failure is structural rather than a lack of apparent within-dataset stability.

At N=139:

- stable-single median pairwise agreement: 1.000
- stable-single median modal frequency: 1.000
- near-tie median pairwise agreement: 0.835
- near-tie median modal frequency: 0.910
- distributed median pairwise agreement: 0.555
- distributed median modal frequency: 0.700

The near-tie regime frequently produces a stable dataset-specific winner. Repeated 80% subsampling of one realized dataset therefore does not reliably distinguish a uniquely dominant latent from two nearly equivalent population-level features.

The current statistics measure conditional stability within a realized discovery dataset more strongly than population-level identifiability.

## Consequence

No biological feature-stability sweep may run under this gate.

The stability design must be revised and frozen in a new pre-model commit before any ESM/SAE contact.

No Experiment 03 model statistic was observed during this calibration.
