# Gate A2 joint scan amendment 001

Status: prospective scope freeze; A2-SS remains disabled.
Joint-input implementation is pending. This commit does not authorize
retrieval, scanning, clustering, geometry, or model contact.

## Archive publication repair

A2-SS staging must reside under OUTPUT.parent so publication by rename
stays on the destination filesystem. The disabled runner receives
only this repair in this commit.

## Joint-input requirement

Separate discovery and confirmatory MMseqs2 partitions cannot establish
discovery-to-confirmatory cluster relationships. A2-SS must therefore
cluster the frozen discovery and recovered confirmatory sequences
jointly under the existing frozen parameters, with two-run replay.

Inputs:
- 278 discovery records, preserving their existing frozen bytes;
- 3,702 confirmatory records from the committed A2-SR archive.

Each input record receives a namespaced identifier:
discovery::<accession> or confirmatory::<accession>.
This preserves all 3,980 records without assuming accession
disjointness across universes or silently collapsing overlap.

Archive a deterministic identifier-to-universe/class/accession mapping
and canonical joint FASTA sorted by ASCII identifier bytes. Use
identifier-only headers, uppercase unwrapped sequences, LF line
endings, and a final LF. Verify each sequence against its own frozen
manifest. Do not re-query or replace discovery sequences.

Pfam scanning must use the same pinned Pfam 37 --cut_ga rule and
accepted-hit projection for both universes. The implementation must
preserve all records and record the exact scan input scope.

A2-SS archives raw scanner outputs, canonical MMseqs2 rows, stable
partitions, input identities and provenance. It does not interpret
cross-universe overlap, construct combined Pfam/MMseqs2 components,
calculate concentration, or decide family disjointness. Those actions
remain confined to separately authorized A2-C.

## Sequence provenance limitation

A2-SR passed accession-membership and frozen-length checks using
UniProt 2026_03. Discovery bytes remain frozen from 2026_02.
Passing those checks does not demonstrate historical confirmatory
sequence-byte identity: same-length substitutions are not excluded
without historical per-sequence hashes.

## Authorization conditions

Before any A2-SS authorization:
1. implement the joint-input scope while disabled;
2. independently test membership, canonicalization and hash checks;
3. verify complete committed recovery-archive contents against Git;
4. validate Pfam artifacts, including pressed database members;
5. test malformed partitions and two-run replay failures;
6. define an explicit archive-member allowlist excluding disposable
   MMseqs2 scratch databases;
7. retain both original archives and the original A2-SR PASS unchanged.

Neither this amendment nor its publication regression test satisfies
the outstanding joint-input implementation requirements.
