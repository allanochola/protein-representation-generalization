# A1 grouping amendment 001 — sequence-defined partition

**Status:** Frozen specification only. No amended runner exists, no MMseqs2
execution has occurred, and no amended component geometry has been computed.

## 1. Trigger and preserved first result

The original Pfam clan-first/family-fallback census is retained unchanged at
commit `894744f8cdf5faa15eb517e120e4ae51d2986ee4`. It routed
`INCONCLUSIVE_UNASSIGNED` because its missingness rule bound first.

| Quantity | Original result |
|---|---:|
| total discovery positives | 139 |
| Pfam-assigned positives | 55 (0.3957) |
| unassigned positives | 84 (0.6043) |
| components among assigned | 19 |
| assigned singletons | 9 (0.1636) |
| largest component | 15 (0.1079 of all positives) |
| `L` among assigned | 0.8364 |
| route | `INCONCLUSIVE_UNASSIGNED` |

Concentration and `L` passed conditionally among the annotated subset, but the
subset covered only 39.57% of the positives. Those conditional values cannot
route Experiment 05.

This amendment is triggered by inadequate Pfam coverage, not by an inconvenient
concentration or `L` result. Pfam gathering thresholds remain frozen:
`--cut_ga` is not loosened and no E-value substitute is permitted.

## 2. Sequence source and canonical FASTA

The sole Git-tracked FASTA reproducing all 139 frozen positive sequence hashes
is:

- path:
  `experiments/03-toxin-representation/stage1_model_blind/precontact_gate/discovery_sequences.fasta`
- source SHA-256:
  `ef17a1231bafc86255bf8ba57aaa64fe7f81c39677fb8d0553fa2d94ca2fb358`
- source records: 278
- positive records matched to the committed A1-S manifest: 139 of 139

A1-M-S must derive its positive-only FASTA through the following byte-level
rule:

1. Read positive identifiers and sequence SHA-256 values from the committed
   `a1_scan_archive/discovery_sequence_manifest.tsv`.
2. Resolve each source FASTA header to exactly one manifest identifier.
3. Reject missing, duplicate, ambiguous, empty, or hash-mismatched sequences.
4. Sort the 139 records by identifier using bytewise ascending order.
5. Serialize each record as an identifier-only header, one unwrapped uppercase
   sequence line, LF line endings, and a final LF:

   `>{identifier}\n{sequence}\n`

The canonical positive-only FASTA must contain 139 records, occupy 31,481
bytes, and have SHA-256:

`35a18f81eec471904c6bceb8671e7531db1ddaeb610bbf34e8b2f2efa6126878`

Any mismatch is a repairable implementation failure. Clustering must not begin.

## 3. Frozen MMseqs2 definition

The amendment inherits the project’s Experiment 03 operational sequence-
independence definition.

| Parameter | Frozen value |
|---|---:|
| MMseqs2 build | `eec9c354be4276d2373996af2e50808b1390d527` |
| command | `easy-cluster` |
| minimum sequence identity | `0.30` |
| coverage | `0.80` |
| coverage mode | `1` — shorter-sequence coverage |
| cluster mode | `0` — greedy set cover |
| sensitivity | `7.5` |
| threads | `8` — operational only |

No alternative identity, coverage, mode, sensitivity, or thread configuration
may be inspected or trialled.

The numerical parameters predate the first A1 census. Their use here is
prospective because no MMseqs2 output for this amended census exists.

## 4. Replay and determinism gate

Experiment 03 established that raw MMseqs2 TSV row order may differ while the
scientific row set remains identical. Experiment 01 also recorded partition
instability under uncontrolled input ordering.

A1-M-S must therefore:

1. generate the byte-identical canonical FASTA defined above;
2. run the frozen command twice from separate empty temporary directories;
3. retain both raw TSV outputs;
4. canonicalize each output as a bytewise-sorted unique
   `(representative, member)` table;
5. derive a member-to-cluster partition for each run;
6. compare both canonical row-set hashes and both partition hashes.

The two canonical row sets and two partitions must match exactly. Raw TSV byte
hashes may differ.

A mismatch is `REPAIRABLE_IMPLEMENTATION_FAILURE`. No scan archive is accepted,
no component structure is computed, and A1-M-C remains unauthorized.

Cluster identity must not depend on the representative label. The durable
cluster identifier is the SHA-256 of the LF-joined, bytewise-sorted member list.
The archive must contain:

- canonical positive-only FASTA;
- two raw cluster TSV files;
- canonical sorted representative/member table;
- canonical member-to-cluster table;
- all hashes;
- exact command and binary/session identity;
- literal `"confirmatory_accessed": false`.

A1-M-S computes no Pfam/MMseqs union, components, `L`, concentration, or route.

## 5. Amended grouping rule

A1-M-C operates only after the A1-M-S archive is committed.

1. Every discovery positive receives its MMseqs2 cluster membership, including
   singleton clusters.
2. The committed Pfam clan-first/family-fallback relationships remain edges.
3. Membership in the same MMseqs2 cluster adds edges.
4. Full transitive closure over the union of both edge sources defines the
   amended equivalence classes.
5. The resulting partition must contain each of the 139 positives exactly once.
6. Unassigned count must equal zero.

The union-of-edges definition is new to this amendment. It does not predate the
first Pfam census. It is frozen here before any amended MMseqs2 output exists.

The MMseqs2 partition is total, so singleton clusters are valid assigned
classes. `L` is the fraction of all 139 positives belonging to amended
components of size at least two. Largest-component share also uses all 139
positives as its denominator.

## 6. Frozen amended routing

A nonzero unassigned count is an integrity failure and raises; it is not a
scientific route.

For a valid total partition, evaluate:

1. largest-component share `> 0.15`:
   `AMENDMENT_REQUIRED_CONCENTRATION`;
2. otherwise, `L >= 0.25`:
   `TWO_STAGE_ELIGIBLE`;
3. otherwise:
   `SKIP_STAGE1_NEAR_VACUOUS`.

The `0.15` concentration ceiling and `L_min = 0.25` are unchanged.

If concentration binds, neither Stage 1 nor direct confirmatory execution is
authorized by Gate A1. Any subsequent route requires a separate prospective
amendment. It is forbidden to drop an edge source, raise the ceiling, change
MMseqs2 parameters, or restrict the positive set to obtain a pass.

## 7. Foreseeability and interpretation

The 139 discovery positives may already be representatives of distinct
Experiment 03 clusters. Re-clustering may therefore contribute mostly
singletons. That is a legitimate result and cannot trigger parameter changes.

Because the first Pfam census is already open, a mostly-singleton MMseqs2 result
would make the amended route partly foreseeable: the Pfam graph plus 84
singletons would give `L` near 0.33 and leave the largest component near 0.108.
This amendment does not claim blindness to that implication.

Adding MMseqs2 edges can only merge components. The largest existing component
contains 15 proteins, while the ceiling permits at most 20 of 139 without
exceeding 0.15. Concentration failure remains a live outcome.

Validity rests on the inherited MMseqs2 parameters, unchanged numerical
thresholds, prospective union rule, replay gate, and prohibition on inspecting
alternative configurations.

## 8. Implementation sequence

1. Implement A1-M-S and A1-M-C in a hard-disabled state.
2. Extend the behavioral audit to cover:
   - canonical FASTA identity;
   - absence of confirmatory access;
   - exact MMseqs2 command;
   - two-run replay;
   - representative-independent cluster identifiers;
   - phase separation;
   - union-edge transitive closure;
   - total-partition integrity;
   - routing precedence and schema firewall.
3. Commit and remote-verify the disabled implementation.
4. Authorize A1-M-S alone.
5. Execute A1-M-S; audit and commit its immutable archive.
6. Authorize A1-M-C alone.
7. Execute A1-M-C; audit and commit its outputs.
8. Read the amended route only after the output commit is remote-verified.

A1-M-C must read only committed A1-S and A1-M-S archives, reverify every input
hash, and have no scanner, network, staging, model, SAE, seed, or probe-fitting
capability.

## 9. Scope

This amendment changes only the Gate A1 grouping instrument used to decide the
architecture fork. It does not alter:

- the North Star;
- the frozen layer-24 primary representation or its non-optimality statement;
- the `DeltaTPR@FPR5` estimand;
- the `+0.10` minimum meaningful gain;
- the fresh discovery-only sequence comparator requirement;
- Gate A2, Gate C, or the confirmatory seal.

The original Pfam census remains a committed descriptive result and cannot
independently route Experiment 05 after this amendment.
