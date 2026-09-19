# A1 Scan/Archive and Census Split Amendment

**Status:** frozen prospective repair; both successor implementations exist and
are hard-disabled. Neither is authorized by this document.

## Why this repair is prospective

The combined A1 runner was authorized at remote commit
`34fe26535ea3446f1be7f666fdff501617b1fe2b` but never executed. No domain hit,
assignment, component, coverage value, `L`, or route was produced or viewed.
The authorization was revoked before this amendment. The repair therefore uses
no A1 result and does not adapt to observed family structure.

## Structural separation

A1 is divided into two separately frozen and authorized programs.

### Phase A1-S — scan and immutable archive

A1-S may:

1. validate the exact frozen 278-row discovery manifest and FASTA: 139 positive
   and 139 negative records;
2. validate the frozen Pfam and HMMER inputs;
3. execute the frozen Pfam scan;
4. archive raw `domtblout`, scanner stdout/stderr, accepted versionless Pfam
   family hits, exact command, and provenance;
5. copy the exact compressed clan map and `Pfam.version.gz` into the archive;
6. hash every archived object.

A1-S must not resolve families to clans, construct a protein graph, compute
components, summarize assignment coverage, calculate `L`, calculate family
concentration, or select an outcome-table route. Its output is committed and
remote-verified before A1-C is eligible.

### Phase A1-C — census from committed archive

A1-C may read only the committed A1-S archive plus the already-frozen discovery
manifest. It must re-verify every archive hash before parsing any hit. It may
then resolve identifiers, construct components, calculate the frozen census,
and apply the frozen outcome table. It may not rescan sequences, restage Pfam,
invoke HMMER, access a network, or read an uncommitted scan artifact.

## Binding release-identity gate

The archived `Pfam.version.gz` must have SHA-256
`8e4de54729bb767d68271b440c91ebb3049f89108422833d8b15ae729dba7dfc`
and parse exactly to:

- Pfam release: `37.0`;
- Pfam-A families: `21979`;
- date: `2024-03`;
- based on UniProtKB: `2023_05`.

Any byte-hash or parsed-field mismatch is a repairable implementation failure
and an immediate STOP. The release label is proven from archived bytes, not
inferred from the download URL.

## Binding domain-acceptance rule

The scientific acceptance rule is HMMER `hmmscan --cut_ga`: each Pfam model's
curator-defined gathering threshold decides acceptance. No global sequence or
domain E-value threshold may replace or supplement it. Every accepted domain is
retained. Numeric Pfam version suffixes are removed only after acceptance.

The A1-S provenance must record both the exact command and the semantic rule.

## Binding multidomain resolution rule

The primary rule is full transitive closure, chosen before any A1 assignment
output existed:

1. each protein retains every accepted Pfam family;
2. each family is replaced by its clan accession when a clan mapping exists;
3. a family without a clan retains its versionless Pfam accession;
4. proteins sharing any resulting identifier are connected;
5. connected components are the indivisible equivalence classes.

This rule preserves all observed biological relationships. A single-best-domain
rule is prohibited because it could place proteins sharing an ignored secondary
clan into different partitions. Family-only fallback for clan-mapped families
is also prohibited.

Multidomain bridges may create a dominant component. That is handled only by
the already-frozen ceiling:

`largest component / all 139 discovery positives <= 0.15`

If the ceiling is exceeded, A1 takes the amendment-required third-row outcome.
The result is not repaired by deleting domains, weakening clan resolution, or
choosing a different representative domain.

## Build identity and reproducibility claim

HMMER source version and hash are reproducibility inputs. Session `hmmscan` and
`hmmpress` binary SHA-256 values identify the exact Kaggle build used for the
run but are not claimed to be reproducible-build hashes. Build paths, compiler
details, and timestamps may change their bytes.

The durable scientific objects are the pinned source and Pfam inputs, frozen
command and threshold rule, raw scan archive, accepted-hit table, and their
hashes. A reset reproduction succeeds by reproducing the archived assignments,
not by reproducing byte-identical executable files.

## Authorization order

1. revoke the unused combined-runner authorization;
2. commit and remote-verify this repair;
3. implement A1-S and A1-C while both are hard-disabled;
4. audit and commit the disabled implementations;
5. authorize A1-S alone in an isolated commit;
6. execute A1-S, audit its archive, commit, and remote-verify it;
7. authorize A1-C alone against the committed archive;
8. execute A1-C, audit, commit, and only then interpret the route.

Confirmatory paths remain unreachable in both phases.
