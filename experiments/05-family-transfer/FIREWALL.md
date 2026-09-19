# Experiment 05 Protected-Data Firewall

**Current authorization:** Phase-0 metadata-only work.

## Protected objects

Once candidate families are allocated, the following are protected for the
evaluation partition:

- model-ready sequences and labels in joined form;
- ESM embeddings or derived representation features;
- sequence-comparator features when joined to evaluation labels;
- all classifier scores, predictions, metrics, plots, and thresholds;
- any summary that reveals comparative performance.

## Allowed before protocol freeze

- provenance manifests and source checksums;
- label-blind sequence QC;
- prespecified family-relationship metadata;
- component counts and size distributions;
- hypothetical simulation results independent of observed model predictions;
- implementation tests on synthetic data.

## Spend prerequisites

Protected evaluation is not eligible until a committed frozen protocol records:

1. exact candidate-universe provenance and exclusions;
2. frozen family graph and deterministic partition;
3. frozen ESM checkpoint, layer, pooling, classifier, and hyperparameters;
4. frozen comparator features, implementation, classifier, and hyperparameters;
5. nested calibration procedure and 5% FPR threshold rule;
6. primary weighting, uncertainty method, and decision boundaries;
7. passed Gates A-E;
8. hashes of the execution code and protected manifests;
9. a one-time spend authorization naming the eligible outputs.

## Exposure response

Any accidental exposure must be logged immediately with object, timestamp,
scope, and design decisions made before and after exposure. If the exposure
could influence a still-unfrozen decision, Gate E fails for the affected
evaluation set. The set may not be rescued by claiming the result was ignored.

## Experiment 04 boundary

Experiment 04 protected objects are outside Experiment 05. This firewall does
not authorize their reuse or further analysis.
