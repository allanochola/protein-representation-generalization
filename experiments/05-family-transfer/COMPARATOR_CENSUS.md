# Strong Sequence-Only Comparator Census

**State:** candidate census; no primary comparator selected.

## Comparator claim

The comparator must test whether ESM-2 adds family-transfer information beyond
a serious conventional sequence-derived detector. It cannot use pretrained
protein-language-model embeddings, PLM logits, or any feature derived from the
protected evaluation labels.

## Candidate feature blocks

Candidate blocks to review for provenance, dimensionality, leakage risk, and
computational feasibility:

1. normalized amino-acid and grouped residue composition;
2. dipeptide and bounded k-mer features, with hashing only if specified;
3. composition/transition/distribution descriptors;
4. physicochemical autocorrelation and quasi-sequence-order descriptors;
5. predicted local properties only if the prediction tool is provenance-clean
   and does not itself rely on disallowed PLM representations;
6. alignment-free sequence kernels or string-kernel approximations.

Composition alone may appear as an ablation but is not the primary comparator.

## Candidate classifier families

- regularized logistic regression;
- linear SVM with calibrated development-only scores;
- gradient-boosted trees on bounded handcrafted descriptors;
- a prespecified sequence kernel with a regularized classifier.

The final development search must be bounded before labels are combined with
features. Hyperparameters are selected within development families using
family-grouped resampling. Calibration families are not tuning data.

## Adequacy criteria to freeze after census

The chosen comparator must satisfy all of the following:

- reproducible implementation and version pinning;
- deterministic feature extraction;
- no PLM-derived inputs;
- family-grouped development and tuning;
- competitive development-only performance relative to simpler ablations;
- manageable dimensionality and regularization for the number of development
  families;
- no protected-family score inspection before freeze.

"Competitive" requires a prospective rule. A candidate rule is to select the
simplest comparator within a prespecified tolerance of the best development-
only family-grouped score, but the metric, tolerance, and resampling design
must be simulation-audited and frozen before use.

## Required census table

For each candidate record:

`feature_block, implementation, version, PLM_free, dimensionality, fit_cost,`
`provenance_risk, family_grouped_tuning_support, known_failure_modes, status`

No candidate is approved merely because it is easy to run.

## Prior 0.9494 comparator provenance recovery

The earlier family-aware random-forest diagnostic with AUROC 0.9494 is prior
shortcut evidence and is not an admissible Experiment 05 comparator. Historical
provenance recovery may document, but cannot promote, that model. Any recovery
must record:

- its exact training records, accessions, sequence hashes, and family
  assignments;
- whether any training protein is present in the protected confirmatory set
  under the same accession;
- whether the same protein sequence appears under a different accession;
- whether a training protein and protected protein belong to the same frozen
  biological-family component despite differing accession and sequence;
- the database releases and annotation sources used on both sides.

Accession non-overlap is insufficient. Any same-sequence or same-family bridge
between prior-model training data and the protected set is contamination of the
historical record. Experiment 05 uses the fresh discovery-only comparator path
specified in `GATE_B_FRESH_COMPARATOR_SCOPE.md` regardless of recovery outcome.
