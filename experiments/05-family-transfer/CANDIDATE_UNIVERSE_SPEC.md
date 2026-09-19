# Candidate-Universe and Provenance Specification

**State:** Phase-0 specification; no candidate retrieval executed here.

## Positive source questions

The census must record, before retrieval:

- source database and release/version;
- exact query or downloadable artifact;
- retrieval date and content checksum;
- evidence level accepted for toxin annotation;
- reviewed/unreviewed policy;
- fragment, precursor, chain, isoform, and synthetic-sequence policy;
- multi-function and ambiguous toxin-label policy;
- exact-sequence deduplication and conflicting-record rules.

Tox-Prot is the leading positive source because it preserves continuity with
the prior program, but Experiment 05 must establish its current version and
annotation semantics afresh. Prior Experiment 03/04 memberships are not
automatically the Experiment 05 universe.

## Negative source questions

The negative universe requires an explicit claim. "Not annotated as toxin" is
not equivalent to "confirmed non-toxin."

The census must compare defensible negative definitions and document:

- database and release/version;
- evidence and annotation filters;
- removal of toxin, venom, virulence, antimicrobial, secreted-effector, and
  other ambiguous functional neighborhoods as scientifically justified;
- taxonomic and subcellular-location handling;
- length and sequence-quality rules;
- homology/domain exclusion relative to positives;
- whether matching is used, on which variables, and at what stage.

## Common sequence rules

- one canonical sequence per resolved record under a frozen rule;
- exclude exact positive/negative sequence collisions;
- preserve accessions and source-record hashes separately from model inputs;
- record all exclusions with machine-readable reason codes;
- do not use protected predictions or embeddings for quality control.

## Metadata-only outputs

The initial census may expose only:

- record counts before/after each exclusion;
- sequence-length summaries;
- missingness for candidate family metadata;
- exact-duplicate counts;
- family-component counts and size distributions under prespecified candidate
  definitions;
- provenance and checksums.

It must not expose model scores, embeddings, performance, or thresholds.

## Required artifact schema

The eventual census manifest should minimally contain:

`record_id, source_accession, source_release, retrieval_date, label_source,`
`evidence_code, sequence_sha256, sequence_length, inclusion_status,`
`exclusion_reason, family_metadata_source, family_metadata_id`

Partition identity must not be added until the family graph is frozen.
