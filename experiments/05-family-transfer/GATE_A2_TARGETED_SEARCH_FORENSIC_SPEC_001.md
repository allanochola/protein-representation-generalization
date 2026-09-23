# Gate A2 targeted sequence-search forensic specification 001

Status: scope frozen; implementation and execution NOT AUTHORIZED.

## Purpose and prior observation

The archived joint sequence partition contains nine clusters with both
confirmatory labels. Each contains one confirmatory positive; together they
contain 687 distinct confirmatory negatives and 687 cross-label co-membership
pairs. These are cluster relationships, not archived pairwise alignments.

This diagnostic follows inspection of those relationships. It is a targeted,
post-geometry forensic, not a blinded confirmatory analysis.

## Immutable inputs and membership

Use the committed A2 joint FASTA, identifier mapping, canonical partition and
representative rows at cc13ffe70a796737c2c240550b551cb0704c2e39. Verify their committed bytes and recorded
hashes. Derive the nine positives and 687 negatives from cluster membership;
do not manually curate identifiers or remove records.

Freeze the derived membership table and canonical diagnostic FASTA identities
in the disabled implementation before execution. No sequence retrieval,
reannotation or reclustering is permitted.

## Direction and search scope

Queries: the 687 confirmatory negatives.
Targets: the nine confirmatory positives.

Use negative-query to positive-target orientation, matching the historical
filter direction. The search may return cross-cluster hits among these inputs;
retain every returned row. Evaluate the 687 preidentified co-membership pairs
explicitly and report other returned relationships separately.

Recover the complete historical command and imported configuration from
preprotocol/toxprot_census/06b_filter_negatives.py. Verify the exact MMseqs2
source/version contract and record the session binary identity.

The next implementation must explicitly document identity and coverage
semantics, coverage orientation, sensitivity, E-value behavior and relevant
defaults for that build. Do not equate a coverage-mode number with
shorter-sequence coverage without checking its actual semantics.

A subset-target search is not an exact historical replay. Target database size,
sequence versions and search heuristics can affect detection.

## Results and classification

Archive the exact commands, stdout, stderr, complete returned alignment table,
input membership, input hashes and toolchain provenance before interpretation.
Output alignment fields must support identity, query/target lengths,
alignment coordinates, coverage and E-value inspection.

For each of the 687 preidentified pairs, distinguish:
1. QUALIFYING_ALIGNMENT_DETECTED_UNDER_DIAGNOSTIC
2. NO_QUALIFYING_ALIGNMENT_DETECTED_UNDER_DIAGNOSTIC
3. EXECUTION_OR_PROVENANCE_UNRESOLVED

Failure is never converted to a no-hit result. A no-hit result does not prove
absence of a qualifying alignment or representative-mediated relatedness.

Qualification must be implemented from the recovered historical rule before
execution; it may not be chosen after inspecting returned alignments.

## Historical-filter attribution

Current qualifying hits alone do not establish historical leakage. Attribution
requires historical positive-reference membership, negative-pool lineage,
sequence identity/version compatibility, direction and command compatibility.
Missing evidence remains unresolved. No automatic filter-failure status.

## Interpretation and firewall

No model loading, feature extraction, predictions, performance metrics,
threshold selection, Gate C simulation or biological label revision.
No record removal or changes to the frozen family definition.
No automatic admissibility decision.

The 27 previously identified cross-universe negative exact-sequence overlaps
remain training overlap regardless of this diagnostic's outcome. No claim of
memorized-correct predictions, optimistic FPR or cancellation in DeltaTPR is
established without model evidence.

This specification does not authorize new searches. Disabled implementation,
audit, and isolated authorization must precede execution. Existing scan and
geometry archives remain immutable.
