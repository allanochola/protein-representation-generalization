# Gate B grouping forensic 001 — method-scope reconciliation

**Status:** Complete. The immutable grouping archive is preserved unchanged.
The runner status `HISTORICAL_MMSEQS_FILTER_CONTRADICTION` is retained as an
execution record but is not the final scientific interpretation.

**Final forensic classification:**
`RECONCILED_METHOD_SCOPE_DIFFERENCE`.

No comparator feature was extracted, no comparator was fitted, and no
confirmatory data were accessed.

## 1. Trigger

The committed discovery-wide grouping archive reported:

- 278 discovery proteins: 139 positive and 139 negative;
- 117 final connected components;
- 94 positive-only components;
- 16 negative-only components;
- 7 mixed-label components;
- 62 MMseqs2 spanning edges;
- 192 Pfam spanning edges;
- 2 cross-label MMseqs2 spanning edges;
- 25 cross-label Pfam spanning edges.

The runner assigned status `HISTORICAL_MMSEQS_FILTER_CONTRADICTION` because it
treated each cross-label MMseqs2 spanning edge as evidence of a direct
negative-to-positive hit under the historical overlap-filter rule.

That implication was too strong.

## 2. Why a cluster edge is not necessarily a direct pairwise hit

The grouping runner converts each MMseqs2 cluster into deterministic spanning
edges so the partition can be represented as a graph. Those edges certify
common cluster membership. They do not certify that every displayed endpoint
pair directly satisfies the pairwise search rule.

MMseqs2 `easy-cluster` with greedy set cover may place multiple proteins in one
cluster through a representative. Two non-representative members can therefore
share a cluster without producing a direct pairwise hit. Even a
representative/member relationship under clustering need not reproduce the
directional negative-query/positive-target `easy-search` result used by the
historical filter.

The archive field `edge_source=mmseqs2` must therefore be read as
**MMseqs2 cluster-equivalence spanning edge**, not automatically as a direct
qualifying alignment.

## 3. Historical filter recovered

The historical negative-overlap implementation is:

`preprotocol/toxprot_census/06b_filter_negatives.py`

It ran negative sequences as queries against cleaned positive sequences using
MMseqs2 `easy-search` with:

- minimum sequence identity: 0.30;
- coverage: 0.80;
- coverage mode: 1;
- sensitivity: 7.5;
- the project-frozen thread setting;
- output fields `query,target,fident`;
- no explicit E-value override.

Thus MMseqs2's default E-value behavior applied.

## 4. Case 1

- negative: `P35792`;
- positive: `Q2XXP1`;
- negative length: 164;
- positive length: 242;
- negative sequence SHA-256:
  `37bae0a2e5d35b590d7d2d9f7a3c23c61e9baed62a95f84338d99ce763f6d94d`;
- positive sequence SHA-256:
  `8a4385dec72293971b4ede808e49ad62991cbc806e268e9d46fc698fdfff5c29`;
- exact duplicate: no;
- cluster representative: `Q05968`;
- neither endpoint is the representative;
- direct negative-query/positive-target `easy-search` result: no hit;
- classification:
  `CLUSTER_CO_MEMBERSHIP_WITHOUT_DIRECT_HISTORICAL_RULE_HIT`.

The negative has tracked discovery lineage through:

- `discovery_negative_candidates.tsv`;
- `discovery_sequence_manifest.tsv`;
- realized discovery partitions at N=100, N=120, and N=139.

## 5. Case 2

- negative: `P14369`;
- positive: `A0A834R821`;
- negative length: 148;
- positive length: 498;
- negative sequence SHA-256:
  `23b3c9115db8795aaf50023404afc22b132077c9fa763ae7013a73fd5fbf4894`;
- positive sequence SHA-256:
  `71cefcaa53fce8dfd7b6202d44ea5fc95b92ba08aa5af5ff3a126450c7dcf537`;
- exact duplicate: no;
- cluster representative: `P14369`;
- the negative is the representative;
- direct negative-query/positive-target `easy-search` result: no hit;
- classification:
  `CLUSTER_CO_MEMBERSHIP_WITHOUT_DIRECT_HISTORICAL_RULE_HIT`.

The negative has tracked discovery lineage through:

- `discovery_negative_candidates.tsv`;
- `discovery_sequence_manifest.tsv`;
- realized discovery partitions at N=100, N=120, and N=139.

## 6. Forensic result

Across the two flagged cases:

- confirmed direct historical-rule hits: 0;
- cluster-only co-memberships: 2;
- direct hits below the historical rule: 0.

The historical negative-overlap filter is therefore not contradicted by these
cases. The runner status arose from conflating cluster-equivalence spanning
edges with direct directional search hits.

The immutable archive is not rewritten. Its status remains part of the exact
execution record, while this document supplies the append-only scientific
resolution.

## 7. Negative-side structure

The joint grouping exercise remains necessary and informative.

The 62 MMseqs2 spanning edges decompose as:

- negative-negative: 60;
- negative-positive: 2;
- positive-positive: 0.

The 139 discovery negatives therefore contain substantial internal sequence
relatedness. Treating each negative accession as an independent development
group would permit related negatives to cross folds.

The two cross-label spanning edges also show that adding negatives can connect
proteins that were separate in the positive-only analysis. Joint grouping is
therefore required; positive-only grouping is insufficient for comparator
development.

## 8. Pfam finding remains live

The forensic resolution applies only to the two MMseqs2 spanning edges. It does
not remove:

- 25 cross-label Pfam spanning edges;
- 7 mixed-label final components.

The historical overlap filter tested sequence similarity, not Pfam family or
clan co-membership. These Pfam bridges contradict no historical filter claim.

They instead show that the discovery negative universe is sequence-screened
against positives but is not family-clean under the new clan-first /
family-fallback definition.

## 9. Interpretation boundary

Mixed-label components are not mechanically unusable for grouped development.
They can be retained intact so every related positive and negative remains on
one side of every split.

However, the previous Gate B amendment prospectively declared every mixed-label
component a stop. Comparator fitting therefore remains prohibited until a new
prospective amendment explicitly:

1. retains every mixed component intact;
2. drops no protein or edge;
3. freezes the grouped resampling rule;
4. checks fold-label support without model fitting;
5. records the mixed-family label ambiguity as a benchmark limitation;
6. avoids assuming that label ambiguity affects ESM and the comparator equally.

## 10. Reach-back and A2

The 3,541 confirmatory negatives descend from the same historical
sequence-similarity filter. The discovery result makes cross-label Pfam
co-membership plausible in that universe.

Gate A2 must therefore count, without accessing model outcomes:

- direct cross-label sequence relationships;
- cross-label Pfam family and clan relationships;
- mixed-label combined components;
- component-size and label-support distributions.

This requirement fits A2's already-frozen role as a confirmatory
family-geometry opening. It may not influence layer choice, comparator choice,
the primary estimand, or the `+0.10` materiality boundary.

## 11. Current authorization state

- grouping execution: closed;
- comparator fitting: prohibited;
- A2: prohibited;
- confirmatory outcomes: sealed;
- North Star: unchanged.
