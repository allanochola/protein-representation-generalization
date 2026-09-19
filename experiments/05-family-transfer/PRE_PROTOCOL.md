# Experiment 05 Pre-Protocol

**State:** design only; not frozen; no confirmatory computation authorized.

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
- Model checkpoint, layer, pooling, scaling, classifier, and regularization
  must be frozen without protected evaluation performance.
- Experiment 04's layer profile may motivate candidates but may not by itself
  convert its descriptively strongest layer into a confirmatory selection.
- Any cross-layer development must occur only within development families and
  must yield one frozen primary representation before calibration/evaluation.

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
