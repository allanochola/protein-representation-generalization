# Experiment 05 Pre-Protocol

**State:** Phase 0. The clauses explicitly marked frozen are binding; the full
confirmatory protocol is not yet frozen, and no confirmatory computation is
authorized.

## 1. Scientific question

Does a frozen raw ESM-2 representation improve sensitivity by at least 0.10
over a competitive frozen sequence-only predictor when both are evaluated at
the same prospectively calibrated 5% false-positive operating point on
biologically held-out families?

Experiment 04 established accessibility inside its discovery universe. It did
not establish family-disjoint transfer or incremental value over a strong
sequence-only predictor. Experiment 05 tests those missing claims.

## 2. Primary estimand

For each model, the decision threshold is estimated only from calibration
families. The thresholds are then applied unchanged to protected evaluation
families.

`DeltaTPR@FPR5 = TPR_ESM@5%FPR - TPR_SEQ@5%FPR`

The independent inferential unit is a biological family/cluster. Protein-level
counts do not define the effective sample size.

The minimum scientifically interesting incremental effect is `+0.10`.
AUROC and AUPRC are secondary descriptive metrics and cannot replace the
primary endpoint.

## 3. Required partition

`development families -> calibration families -> protected evaluation families`

- **Development:** fit models and settle development-only hyperparameters.
- **Calibration:** estimate each frozen model's threshold for 5% FPR.
- **Protected evaluation:** estimate paired family-level sensitivity and its
  uncertainty. It cannot influence model, representation, family definition,
  hyperparameters, or thresholds.

All family components connected under the frozen independence graph must be
assigned as indivisible units to exactly one partition.

## 4. Representation constraints

- Primary representation family: raw ESM-2, not an SAE.
- Primary checkpoint/layer: ESM-2 650M **layer 24**.
- Layer 24 was selected prospectively while the confirmatory universe remained
  dark. This preserves confirmatory validity; it does not establish that layer
  24 is the optimal layer.
- Experiment 04 supports a broad mid-to-late-layer accessibility plateau:
  layers 9, 18, 24, 30, and 33 each exceeded the frozen 21-D baseline by
  approximately 0.33-0.39 AUROC at N=139, with positive paired differences in
  all 100 perturbations for each layer. The choice of layer 24 uses it as one
  admissible representative of that supported class-level finding.
- The Experiment 04 point-estimate ordering does not quantify uncertainty over
  sampled proteins, families, or populations. It is not used to claim that
  layer 24 is uniquely or statistically superior to the plateau.
- A null result supports only: no demonstrated transfer for the frozen layer-24
  representation under the specified family holdout. It is not a universal
  negative claim about ESM-2.
- Layer 18 is secondary and reference-only. It may not replace layer 24 after
  any protected result is observed.
- Pooling, scaling, classifier, and regularization remain to be frozen without
  protected evaluation performance.

## 5. Sequence-only comparator constraints

The comparator must be independent of PLM embeddings, provenance-clean,
competitive, and frozen before evaluation. Amino-acid composition alone is
not adequate as the primary comparator.

The comparator selection procedure must specify a bounded feature family, a
bounded model family, development-only tuning, missing-value handling,
standardization, and determinism. See `COMPARATOR_CENSUS.md`.

## 6. Pre-data gates

| Gate | Required evidence | Failure action |
|---|---|---|
| A — Independence | Defensible family graph and sufficient disconnected positive and negative units | Close or redesign pre-data |
| B — Resolvability | >=80% power for `DeltaTPR=+0.10` and median CI half-width <=0.10 under stated regimes | Close or redesign pre-data |
| C — Comparator | Strong frozen sequence-only comparator with clean provenance | Close or redesign pre-data |
| D — Provenance | Reproducible labels, sequences, exclusions, deduplication, and family assignments | Close or redesign pre-data |
| E — Firewall | No protected result exposure capable of influencing design | Close; do not relabel as confirmatory |

Gate B also requires a separate demonstration that independent calibration and
evaluation negatives can support credible inference around 5% FPR.

### Mapping and ordering of Phase-0 instruments

The earlier A/B/C shorthand maps onto the committed Gates A-E as follows:

| Pre-protocol instrument | Committed gate(s) | Function |
|---|---|---|
| Family census / blocking audit | Gate A, with Gate D provenance support | Establish independent units, `L`, concentration, and leakage status |
| Comparator provenance audit | Gate C, with Gate D provenance support | Establish a strong model-blind comparator and recover its training-universe provenance |
| Resolvability simulator | Gate B, subject to Gate E | Establish that the frozen estimand is resolvable and that the firewall remains intact |

No Experiment 05 work may proceed beyond Phase 0 until all three instruments
are frozen and executed. Passing one does not authorize protected computation.
Gate E remains continuously binding, and any unresolved Gate D defect blocks
the affected instrument.

Simulator acceptance is governed by `RESOLVABILITY_PLAN.md`. Run validity and
scientific gate interpretation are governed by
`IMPLEMENTATION_FAILURE_CLASSIFICATION.md`.

## 7. Permitted Phase-0 analyses

- database/version/source documentation;
- counts and size distributions of candidate family components;
- label-blind sequence quality control and exact-duplicate checks;
- family-graph construction from prespecified metadata/sequence relationships;
- comparator literature and implementation census;
- simulations driven by hypothetical effect/discordance regimes rather than
  observed protected predictions.

No permitted analysis may reveal or approximate the protected ESM-versus-
comparator performance contrast.

## 8. Outcome classes

1. **Transfer plus incremental value:** the frozen ESM system transfers and
   clears the preregistered incremental-effect decision rule.
2. **Transfer without incremental value:** detection transfers, but ESM does
   not show meaningful added sensitivity over the comparator.
3. **No demonstrated transfer:** the design resolves the question but does not
   demonstrate family-disjoint transfer at the operating point.
4. **Unresolved:** independent-family support or precision is insufficient.

Exact confidence-interval construction and decision boundaries remain to be
frozen after the census and simulation audit. Outcome language cannot be
finalized by inspecting protected results.
