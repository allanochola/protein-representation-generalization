# Gate A2 sequence recovery and scan split

**Status:** Frozen contract. Both executable phases are hard-disabled.

## Purpose

Gate A2 uses confirmatory metadata to measure family geometry without
accessing model outputs, labels beyond frozen class membership,
representations, predictions, or performance outcomes.

The phase is split into recovery, scanning, and interpretation so every
expensive or externally sourced result is committed before analysis.

## A2-SR — sequence recovery archive

A2-SR consumes only the committed 3,702-record A2-I accession manifest.
It retrieves accessions directly from UniProtKB in bytewise accession
order. It may not issue a biological search query or alter membership.

Frozen recovery requirements:

- expected positives: 161;
- expected negatives: 3,541;
- expected total: 3,702;
- accession membership must remain unique and class-disjoint;
- batches use one frozen batch size and deterministic accession order;
- retries repeat the identical request and do not change membership;
- every response must report one identical UniProt release and date;
- returned accessions must equal the requested set exactly;
- sequences are uppercase and non-empty;
- current length and sequence SHA-256 are recorded per accession;
- canonical FASTA uses bytewise accession order, identifier-only
  headers, one unwrapped uppercase sequence line, LF endings and a
  final LF;
- raw response bytes, request batches and response headers are archived;
- no Pfam scan, clustering, component construction or geometry occurs.

Frozen-length disagreement, missing accession, extra accession, mixed
UniProt releases, duplicate record or malformed sequence produces
`SEQUENCE_SNAPSHOT_DRIFT`. That is a scientific snapshot result, not an
implementation failure. The recovery archive is retained, and A2-SS
remains prohibited pending a prospective response.

The positive source field `annotation_status` is archived byte-for-byte
as a historical claim. A2-SR does not compare or interpret it.

## A2-SS — immutable raw scan archive

A2-SS consumes only a committed, passing A2-SR archive and re-verifies
every tracked input hash before execution.

Pfam scan:

- Pfam release 37.0, 21,979 families;
- exact compressed artifact hashes already frozen in Gate A1;
- `hmmscan --cut_ga`; no global E-value replacement;
- archive raw domtblout, stdout, stderr and accepted-hit projection;
- do not map hits to clans or compute assignment status.

MMseqs2 scan:

- exact source commit `eec9c354be4276d2373996af2e50808b1390d527`;
- `easy-cluster`; minimum identity 0.30; coverage 0.80;
- coverage mode 1; cluster mode 0; sensitivity 7.5; threads 8;
- run twice from the identical canonical FASTA;
- raw row byte order may differ;
- canonical sorted row sets and stable member-defined partitions must
  match exactly across both runs.

A2-SS may not construct combined Pfam/MMseqs2 edges, components,
concentration, cross-label relationships or disjointness results.

## A2-C — interpretation only

A2-C consumes committed A2-SR and A2-SS archives. It alone may:

- compare historical `annotation_status` against fresh Pfam status;
- map Pfam families to clan-first/family-fallback identifiers;
- combine Pfam and MMseqs2 edges through full transitive closure;
- report positive and negative component counts and concentration;
- report discovery-to-confirmatory family relationships;
- count cross-label Pfam edges;
- test whether the 161 confirmatory positives remain family-disjoint;
- provide Gate C with confirmatory clustering geometry.

Historical `annotation_status` is a claim under re-verification, not
ground truth. Disagreement is reported as annotation-snapshot drift.

## Tool identity

- Pfam artifacts: {"Pfam-A.clans.tsv.gz": "1d9d7f054b017733935aae50c69e2c99037461617a0244ef6c188292474fdcd5", "Pfam-A.hmm.dat.gz": "d6f13117e481034be98f799d387a8122cbfa9a0964e29c0c8583d921c2d4556c", "Pfam-A.hmm.gz": "66f57012fe5825c82f2e31447d7a8026367e1ca9e5e91b4b716c594c268db69b", "Pfam.version.gz": "8e4de54729bb767d68271b440c91ebb3049f89108422833d8b15ae729dba7dfc"}
- HMMER 3.4 source archive SHA-256: `ca70d94fd0cf271bd7063423aabb116d42de533117343a9b27a65c17ff06fbf3`;
- HMMER source was obtained through the official HTTP fallback after
  the HTTPS endpoint refused the connection; byte identity is recorded,
  transport security is not claimed;
- MMseqs2 source commit: `eec9c354be4276d2373996af2e50808b1390d527`;
- MMseqs2 git-archive SHA-256: `de5085207c04902c4b8810ab3092859c5a8e22ab70d56427f54001be4e554379`;
- preparation-session manifest SHA-256: `957aef98a65d5dc646cdc33a02fd352bf8b7d8d0afd9d6c4500013acd8873d2e`.

Binary hashes are session identities only. Durable reproducibility rests
on source identity, scientific parameters, canonical inputs and archived
outputs.

## Ordering

1. implement and audit A2-SR and A2-SS while both are disabled;
2. authorize A2-SR alone;
3. execute, audit and commit the recovery archive;
4. close A2-SR;
5. authorize A2-SS only if recovery status is PASS;
6. execute, audit and commit the raw scan archive;
7. close A2-SS;
8. implement and authorize A2-C separately.

Confirmatory outcomes remain sealed throughout.
