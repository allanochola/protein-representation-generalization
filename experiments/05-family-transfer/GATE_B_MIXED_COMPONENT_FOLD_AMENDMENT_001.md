# Gate B mixed-component fold amendment 001

**Status:** Frozen specification with disabled implementation. No fold geometry
has been computed and no comparator has been fit.

## Scientific finding inherited from grouping

The committed discovery-wide grouping contains all 278 discovery proteins in
117 indivisible components:

- 94 positive-only components;
- 16 negative-only components;
- 7 mixed-label components.

The two apparent cross-label MMseqs2 relationships were reconciled as
cluster co-membership without a direct historical-rule hit. The historical
negative-filter implementation is therefore not shown to have leaked a direct
qualifying pair. The 25 cross-label Pfam spanning edges remain evidence that
the discovery negative universe was sequence-screened but was not family-clean
relative to the positive universe.

Mixed components are retained whole. No protein or edge is dropped. Label
ambiguity is not assumed to affect the comparator and ESM arms equally and is
not assumed to cancel in the final difference.

## Frozen fold geometry

The sole development geometry is:

- `StratifiedGroupKFold`;
- `n_splits = 5`;
- `shuffle = True`;
- `random_state = 20260829`;
- grouping variable: committed discovery-wide component identifier;
- stratification target: frozen discovery class label;
- input feature: a dummy constant column carrying no biological information.

The scikit-learn implementation used for geometry is frozen to the execution
environment version `1.6.1`.

Every component, including every mixed-label component, must remain intact.
Every protein must appear in exactly one validation fold. No component may
occur in both training and validation within a fold. Every training fold and
every validation fold must contain both labels.

Failure of any condition returns `FOLD_GEOMETRY_INFEASIBLE`. It does not permit
changing the number of folds, seed, grouping, universe, or mixed-component rule.

## Scope firewall

This phase computes fold membership only. It may not:

- extract sequence features;
- load ESM representations;
- define or evaluate comparator candidates;
- fit a model;
- produce predictions or scientific performance statistics;
- access any confirmatory path.

The output schema rejects columns containing `auroc`, `tpr`, `fpr`, `score`, or
`threshold`, case-insensitively.

## Required outputs

The runner emits:

- `fold_assignments.tsv`;
- `fold_summary.tsv`;
- `summary.json`;
- `provenance.json`.

The provenance must record the committed grouping archive identities,
scikit-learn version, split parameters, output hashes, and the literal field
`"confirmatory_accessed": false`.
