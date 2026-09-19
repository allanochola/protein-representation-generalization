# Prior Comparator Provenance Archaeology

**Status:** repository archaeology complete; historical model inadmissible as
the Experiment 05 comparator.

## Recovered Gate-D construction

Historical source:

`preprotocol-toxprot-census` at `f18d8c5a05bd9815ed333b6f8d9fd81f667a68d1`.

The 0.9494 AUROC was produced by:

- 187 permanently burned positive MMseqs2 cluster representatives;
- 561 deterministically burned family-aware negative accessions;
- sequence length plus 20 amino-acid composition fractions;
- a 300-tree random forest with `min_samples_leaf=2`;
- five-fold `StratifiedGroupKFold` with frozen seed 20260829;
- one group per positive cluster representative and one group per negative
  accession.

It was a cross-validated diagnostic result, not a single fitted model intended
for reuse. The positive and negative inputs were selected before model fitting.

Historical snapshot:

- random-forest AUROC: 0.9494;
- random-forest AUPRC: 0.9011;
- selected diagnostic negatives: 561;
- remaining confirmatory negatives: 4,120 before the later ESM-eligibility
  restriction;
- diagnostic partition SHA-256:
  `e2354c3e97c347abd6a6f0a3433ba47dfa0090d5bed2e233cdba3434f4196761`;
- results SHA-256:
  `ad37f0c935d9884f582d3a55ccc0f76e40f950fed3aa5f9dd68fd9db9453d4c5`.

## What construction establishes

- Positive diagnostic and later confirmatory memberships were selected from
  distinct frozen cluster partitions.
- Negative diagnostic and later confirmatory accessions were selected from
  disjoint deterministic burn partitions.
- Confirmatory examples were not passed to the Gate-D fitting function under
  their recorded diagnostic accessions.

These facts establish partition intent and accession-level separation by
construction. They do not establish cross-accession sequence or biological-
family independence.

## Missing artifacts

The following full artifacts are not present in any reachable Git commit or
named object:

- `negative_diagnostic_partition.tsv`;
- the family-aware negative FASTA used by Gate D;
- the corresponding full confirmatory-negative FASTA;
- the full positive cluster-membership/Pfam tables used for the diagnostic and
  confirmatory partitions;
- saved fold estimators or fold-level training manifests.

Consequently, the repository alone cannot answer whether:

1. an identical sequence appeared under different negative accessions;
2. a diagnostic negative and confirmatory negative belonged to the same
   biological family;
3. a burned positive cluster and confirmatory positive cluster were linked by
   the final Experiment 05 family definition.

## Gate-B consequence

The 0.9494 result remains valid as a historical diagnostic statistic, but its
training universe is not provenance-clean enough to serve as or select the
Experiment 05 comparator.

Gate B therefore constructs a fresh discovery-only sequence comparator under a
new frozen provenance manifest. This is the default and only confirmatory path,
not a fallback conditional on recovery failure. Exact external recovery may
clarify the historical record but cannot promote the 0.9494 model into the
Experiment 05 comparator.

No absence of contamination may be inferred from missing artifacts. Fresh
comparator construction must finish before any A2 access.
