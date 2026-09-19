# A1 Fresh-Annotation Snapshot and Disabled Runner Freeze

**Status:** frozen implementation candidate; execution is hard-disabled.

## Classification

This is **fresh annotation**, not historical recovery. The lost Experiment-03
assignment table has not been reproduced against its surviving canonical hash.
No result produced here may inherit the historical Pfam-family provenance.

The discovery sequences themselves remain the frozen Experiment-03 records:
278 sequences from UniProt release `2026_02`, comprising 139 positives and 139
negatives. A1 does not re-query UniProt and therefore cannot replace or update
those sequences, accessions, or per-sequence hashes.

## Frozen annotation snapshot

A1 assigns domains by scanning the frozen discovery FASTA directly against
Pfam 37.0. It does not consume live UniProt `xref_pfam` fields.

Required Pfam artifacts are downloaded only from the immutable release root:

`https://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam37.0/`

The binding MD5 and SHA-256 values, URLs, release identity, discovery-input
hashes, and HMMER source identity are stored in
`a1_annotation_snapshot.json`. The official Pfam MD5 values were checked
against the archived `md5_checksums`; SHA-256 values were computed over the
same downloaded compressed bytes. Any mismatch is a STOP, not a warning.

Frozen scanner:

- HMMER 3.4, built from the source tarball pinned in the snapshot;
- `hmmscan --cut_ga --noali --domtblout`;
- every Pfam hit accepted by the model-specific gathering threshold is kept;
- the numeric version suffix is removed from each Pfam accession;
- clan accession replaces family accession when the family appears in
  `Pfam-A.clans.tsv.gz`; otherwise the versionless family accession is used.

This direct sequence scan is byte-reproducible and usable later through the
same code path for A2. It deliberately avoids a live database cross-reference
whose contents can change independently of the frozen sequence record.
The A2 runner must import the frozen clan-map, domain-table parsing, identifier
resolution, and connected-component functions from `run_gate_a1.py`; copying
or reimplementing them does not satisfy the byte-identical-code-path rule.

## Frozen grouping semantics

Assignments are made per protein. Annotations are never unioned across members
of an MMseqs2 cluster. Proteins sharing at least one clan-first/family-fallback
identifier form transitive connected components. Multiple accepted domains may
therefore still create a biological component bridge; the component-size and
0.15 concentration gates expose that result rather than deleting inconvenient
domains.

A protein with no accepted Pfam hit is `UNASSIGNED`. It is not inserted into
the component graph. A1 reports assignment coverage before `L` and applies the
already-frozen 0.10 missingness rule.

Denominators remain distinct and explicit: `L` and singleton fraction use
assigned positives, while unassigned share and largest-component share use all
139 discovery positives. The snapshot carries the binding 0.25, 0.15, and 0.10
routing values rather than leaving them implicit in runner source.

## Runner state

`run_gate_a1.py` contains the complete deterministic construction but has two
independent execution locks:

1. source constant `EXECUTION_AUTHORIZED = False`; and
2. snapshot field `execution_authorized: false`.

Both must be changed in a later, isolated authorization commit after audit.
The current commit must not produce census outputs.

The runner accepts no caller-supplied discovery or confirmatory path. All
discovery inputs are fixed repository-relative constants, and all Pfam inputs
are fixed filenames under the A1 input directory. There is no network code.

## Pre-execution audit

`audit_gate_a1.py` statically enforces:

- successful `ast.parse`;
- both execution locks remain false;
- no model, ESM, SAE, probe, ML, or RNG import;
- no `SeedSequence` or fit/predict/score call;
- no confirmatory input path or confirmatory-reading code;
- no network import or call;
- output-table schema rejection for column names containing `auroc`, `tpr`,
  `fpr`, `score`, or `threshold`;
- frozen repository-input hashes and snapshot self-consistency.

Passing this audit certifies only the disabled source. It does not authorize
execution. After the Pfam files and HMMER executable are staged, a separate
preflight must verify their hashes and version before an authorization commit.

## Required outputs after later authorization

The runner will emit, in canonical order:

- per-positive clan-first/family-fallback assignments;
- connected-component memberships;
- full component-size distribution;
- a routing summary containing assignment coverage, unassigned share,
  largest-component share, assigned-singleton fraction, and `L`;
- provenance with source/input/code/output hashes, the definition hash, exact
  scanner command, and literal `"confirmatory_accessed": false`.

No output exists or is authorized by this freeze.
