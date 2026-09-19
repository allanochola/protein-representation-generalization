# Pfam Provenance Archaeology for Gate A

**Status:** completed repository archaeology; family definition not yet
authorized for execution.

## Recovered historical semantics

The historical census branch is:

`preprotocol-toxprot-census` at `f18d8c5a05bd9815ed333b6f8d9fd81f667a68d1`.

Its frozen configuration and `05_families.py` establish that Experiment 03:

- retrieved Pfam assignments from the UniProt `xref_pfam` field;
- used Pfam family accessions such as `PF00012`, not Pfam clans;
- aggregated the union of Pfam accessions across every member of each frozen
  precursor MMseqs2 cluster;
- treated missing Pfam annotation as unknown, never as evidence of family
  independence;
- used the frozen MMseqs2 parameters recorded below.

The source snapshot was:

- query: `reviewed:true AND keyword:KW-0800`;
- pull timestamp: `2026-08-31T00:47:13.208751Z`;
- raw entries: 7,916;
- retained entries: 7,534;
- raw SHA-256:
  `221b55c00b6aa12742219d1448cfc8dcf58ba013153aa4003b31ea0fd189126f`;
- cleaned-entry SHA-256:
  `057f1bbb551aeb3ff3589e5578391bcca097d0ca0044f037c0cbbabf4a55061d`.

Frozen MMseqs2 state:

- executable build: `eec9c354be4276d2373996af2e50808b1390d527`;
- minimum identity: 0.30;
- coverage: 0.80;
- coverage mode: 1;
- cluster mode: 0;
- sensitivity: 7.5;
- threads: 8.

Historical family-output hashes:

- `gatev2_audit.tsv`:
  `047ecaa58fee2be7c815ddc0aee2b329eb9a9c0708e3adc44c51863f6067d0c9`;
- `annotation_coverage.tsv`:
  `fe2c595ded258f835e4e5fbf5721ae99486bd7338c2a2f16a3a6999cd8d9fe79`;
- `family_concentration.tsv`:
  `7c850e7a3d4ca86595ac54a2d2560508e2067a103c0e042be466ff4345d27cc0`.

## Artifact-availability result

The code, configuration, summary snapshots, and hashes are present in Git.
The full `cleaned_entries.tsv`, `clusters_precursor.tsv`, `gatev2_audit.tsv`,
and family-concentration tables are not present in any reachable Git commit or
named object.

Therefore Git can verify a recovered artifact but cannot itself reconstruct the
discovery family assignment. A1 must not claim inheritance merely because the
historical code and hashes survive.

## Consequence for the Gate-A definition

D1 alone is not informative for A1: the 139 discovery positives are already
representatives of the historical 30%-identity clusters and are therefore
near-singletons under that same partition by construction.

The historically grounded higher-order annotation is Pfam-family membership,
not Pfam clan membership. However, a naive connected-component closure over
"shares any Pfam family" can chain multidomain proteins into a dominant
component. The frozen A1 concentration rule detects this outcome but does not
justify the definition in advance.

Before A1 implementation, provenance may yield either:

1. exact recovery of the historical UniProt/Pfam annotation artifact followed
   by hash verification; or
2. a new, versioned, prospectively frozen annotation snapshot applied through
   the same family-construction function to A1 and later A2.

If exact recovery is attempted, only a byte- or canonical-content match to the
recorded hashes establishes inheritance. A mismatch is not silently accepted as
the historical state. If a new snapshot is used, it is explicitly a new
Experiment 05 definition and may not borrow the old output hashes as validation.

Fresh annotation is the default design path because the historical full
assignments are absent and the new clan-first grouping additionally requires a
versioned Pfam family-to-clan map that the historical census did not record.
An exact recovery attempt may still preserve historical evidence, but it is not
allowed to delay fresh comparator scoping or silently supply missing clan
semantics.

Under fresh annotation, the historical claims that 161 positives were
family-disjoint and that the negative universe was family-aware must be
re-verified in A2. They are not inherited across annotation releases.
