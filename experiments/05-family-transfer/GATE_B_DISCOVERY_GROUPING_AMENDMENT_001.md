# Gate B discovery grouping amendment 001

**Status:** Frozen specification with a hard-disabled implementation. No
discovery-wide clustering, grouping geometry, feature extraction, scoring,
tuning, calibration, or model fitting has been performed.

## 1. Reason for the amendment

Gate B cannot proceed under its original grouping language.

First, `GATE_B_FRESH_COMPARATOR_SCOPE.md` predates A1 grouping amendment 001
and says that Pfam-`UNASSIGNED` positives are excluded from family-blocked
development. That rule is superseded. The amended A1 definition combines
MMseqs2 sequence clusters with Pfam clan-first/family-fallback edges and assigns
all 139 discovery positives to a total partition.

Second, A1-M clustered only the discovery positives. No defensible grouping
exists for the 139 discovery negatives. Treating every negative accession as an
independent group would permit related negative sequences to cross development
folds and could inflate comparator selection.

This amendment resolves only the development-group definition. It does not
select comparator features, a classifier, hyperparameters, a tuning metric, a
calibration procedure, or an adequacy threshold.

## 2. Frozen discovery universe

The grouping instrument uses exactly the 278-record discovery universe:

- 139 discovery positives;
- 139 discovery negatives;
- tracked source FASTA:
  `experiments/03-toxin-representation/stage1_model_blind/precontact_gate/discovery_sequences.fasta`;
- source FASTA SHA-256:
  `ef17a1231bafc86255bf8ba57aaa64fe7f81c39677fb8d0553fa2d94ca2fb358`;
- tracked discovery manifest:
  `experiments/05-family-transfer/a1_scan_archive/discovery_sequence_manifest.tsv`;
- discovery manifest SHA-256:
  `7ac8d253d06ab86b67f2f3d42d7b5ad0c770360a2d4959dc8d325bed00b9ce09`.

The runner must reproduce all manifest sequence hashes and lengths before
clustering. FASTA records are serialized in ascending protein-identifier order,
with one unwrapped uppercase sequence line and a terminal newline per record.

The frozen canonical 278-record serialization identity is:

- byte count: `74972`;
- SHA-256:
  `e54ddf390c9569857663c029ec4679a18f4a0384d391c9183f550be3e0ebe94d`.

Both values must be asserted before MMseqs2 execution. Agreement with the
manifest membership alone is insufficient.

No confirmatory sequence, annotation, family geometry, feature, score, label
join, or performance summary is an input.

## 3. Frozen sequence grouping

All 278 discovery sequences are clustered together using the exact inherited
A1-M MMseqs2 contract:

| Parameter | Frozen value |
|---|---|
| source commit | `eec9c354be4276d2373996af2e50808b1390d527` |
| command | `easy-cluster` |
| minimum sequence identity | `0.30` |
| coverage | `0.80` |
| coverage mode | `1` |
| cluster mode | `0` |
| sensitivity | `7.5` |
| threads | `8` |

Input order is the canonical ascending identifier order. The raw MMseqs2 TSV is
archived, but its byte order is not the scientific identity object. The
canonical sorted `(representative, member)` row set and the
representative-independent member partition are the identity objects.

Two independent clustering runs are required. They must produce identical
canonical row sets and identical representative-independent partitions.
Failure of that replay gate is a repairable implementation failure and produces
no valid grouping archive.

## 4. Frozen annotation edges

The instrument reuses, without regeneration:

- `a1_scan_archive/accepted_family_hits.tsv`;
- `a1_scan_archive/Pfam-A.clans.tsv.gz`;
- their committed provenance and SHA-256 identities.

For each accepted family hit:

1. use its Pfam clan when a non-empty clan exists;
2. otherwise use the Pfam family accession;
3. connect proteins sharing that clan-first/family-fallback identifier;
4. connect multiple accepted identifiers carried by the same protein.

These are the existing A1 Pfam edge semantics. No gathering threshold, family
mapping, or annotation release is changed.

## 5. Final development groups

The final graph contains the union of:

1. same-MMseqs2-cluster edges from the 278-sequence run; and
2. existing Pfam clan-first/family-fallback edges.

Full transitive closure defines the development components. Every component is
indivisible in all later comparator tuning, calibration, model selection, and
development evaluation.

This amendment supersedes the earlier Pfam-`UNASSIGNED` exclusion language for
Gate B. All 139 positives inherit the amended total A1 partition, and all 139
negatives receive discovery-wide grouping through this instrument.

## 6. Mixed-label collision rule

After closure, every component must contain exactly one discovery label.

A component containing both positive and negative proteins is a
`MIXED_LABEL_COMPONENT_COLLISION`. It is a scientific collision, not a row-level
data-cleaning problem.

If any collision exists:

- the complete grouping evidence and collision membership are archived;
- Gate B fitting remains prohibited;
- no component may be split;
- no edge source may be dropped;
- no identity, coverage, clan, family, or concentration rule may be changed;
- a prospective scientific amendment is required before Gate B can continue.

## 7. Archive contract

The grouping archive must contain at minimum:

- canonical 278-record FASTA;
- two raw MMseqs2 cluster TSVs;
- canonical cluster rows;
- representative-independent MMseqs2 partition;
- Pfam edge table;
- final component membership table;
- component summary;
- collision report;
- non-circular provenance JSON;
- SHA-256 for every durable member;
- literal `"confirmatory_accessed": false`.

The output schema rejects any column containing, case-insensitively:

- `auroc`;
- `auprc`;
- `tpr`;
- `fpr`;
- `score`;
- `prediction`;
- `probability`;
- `threshold`;
- `feature`;
- `metric`.

Grouping counts and component sizes are permitted. Comparator performance is
not.

## 8. Authorization boundary

The committed runner is hard-disabled.

Authorization must be a separate commit whose only behavioral change is:

`GROUPING_AUTHORIZED = False` to `GROUPING_AUTHORIZED = True`

with matching self-description text. Authorization does not authorize
comparator feature extraction or fitting.

The grouping run must be audited and committed before any comparator candidate
is evaluated.

## 9. Historical comparator boundary

Repository archaeology establishes that the historical Gate-D diagnostic used:

- sequence length plus 20 amino-acid composition fractions;
- a 300-tree random forest;
- `min_samples_leaf=2`;
- five-fold `StratifiedGroupKFold`;
- seed `20260829`.

That result remains historical evidence only. It neither selects the new
comparator nor authorizes composition alone as the primary comparator.

## 10. Scope

This amendment changes only Gate B discovery grouping. It does not alter:

- the North Star;
- layer 24;
- `DeltaTPR@FPR5`;
- the `+0.10` materiality boundary;
- the A1 scientific result;
- A2 authorization;
- Gate C;
- the confirmatory seal.

No comparator feature family, classifier family, tuning metric, tolerance rule,
calibration method, or development score is frozen or computed here.

## 11. Pre-execution predictions and provenance clarification

This section was appended while the grouping runner remained disabled and
before any discovery-wide MMseqs2 clustering or component geometry existed.

### 11.1 Edge-source-specific prediction

The Experiment 03 negative-overlap filter excluded any candidate negative with
a qualifying MMseqs2 hit to any cleaned positive at at least 30% identity and
at least 80% shorter-sequence coverage under coverage mode 1. Those are the
same sequence-similarity parameters used here.

The prospective prediction is therefore:

- **zero direct positive-negative MMseqs2 cluster edges**.

This prediction does not extend to the combined graph. The historical filter
did not prohibit a discovery negative from sharing a Pfam family or clan with a
positive while remaining below the MMseqs2 sequence threshold. Because the
negative pool was designed to be family-aware, cross-label Pfam bridges remain
a live possibility.

The interpretations are frozen separately:

1. A direct cross-label MMseqs2 edge contradicts the historical overlap-filter
   claim and triggers a provenance investigation.
2. A cross-label bridge created only by a Pfam family or clan is a valid
   scientific collision under the new, coarser family definition. It stops
   Gate B fitting but does not retroactively invalidate Experiments 03 or 04.
3. Any mixed-label final component remains indivisible and requires a
   prospective amendment. It may never be silently split.

The archive must retain edge-level provenance sufficient to distinguish these
cases.

### 11.2 Toolchain comparability and limitation

In the preparation session, the resolved Gate B binary SHA-256 was
`16c2df62ad552650e1ad3c20746812438d300ba861148243edf503af0a72c162`,
matching the session-validation binary recorded for A1-M. When that same binary
remains available at execution, the A1-M positive-only partition and the Gate B
278-record partition use identical executable bytes. Structural differences
between those runs are then attributable to their input universes rather than
to binary-byte differences.

This is supporting session evidence, not a durable binary requirement.
`mmseqs version` authenticates the source commit but does not prove every build
flag. The snapshot records `Release` build type and a Rust-enabled build as
expected construction conditions, while the durable identities remain the
source commit, canonical git-archive SHA-256, exact command parameters, input
identity, and replayed scientific outputs.

### 11.3 Historical model-blind results are not commensurable targets

Three earlier results use nominally similar length-plus-composition features
but different universes, estimators, and resampling designs:

| Result | Evaluation universe and design | Estimator |
|---|---|---|
| approximately 0.587 AUROC | Experiment 04 matched 139-positive/139-negative discovery universe under its frozen perturbation evaluation | 21-dimensional logistic baseline |
| AUROC 0.8468; AUPRC 0.7182 | Experiment 03 Gate-D diagnostic-burn universe under grouped cross-validation | length-plus-composition logistic regression |
| AUROC 0.9494; AUPRC 0.9011 | the same Experiment 03 Gate-D diagnostic-burn universe | 300-tree random forest with `min_samples_leaf=2` |

The spread is evidence that evaluation universe and classifier matter. None of
these values is a performance target or acceptance threshold for the fresh
Gate B comparator.

