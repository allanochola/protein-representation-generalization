# Experiment 03 — frozen census recovery

This file records reconstruction of model-blind Tox-Prot census intermediates after the Kaggle working environment was reset.

The purpose of reconstruction is to recover exact accession and cluster membership required to freeze the Experiment 03 discovery/confirmatory partition. It is not a new census.

No ESM-2 embedding, SAE activation, feature nomination, or Experiment 03 confirmatory model statistic was inspected during this recovery.

## Recovery rule

Each census stage is regenerated from the frozen code into an isolated recovery directory.

A stage is accepted only if its regenerated outputs match the SHA-256 hashes committed in the preprotocol census snapshots. A mismatch stops recovery rather than substituting a changed dataset.

## Step 01 — raw Tox-Prot pull

Status: **EXACT REPRODUCTION**

- query: `reviewed:true AND keyword:KW-0800`
- entries: 7,916
- regenerated SHA-256: `221b55c00b6aa12742219d1448cfc8dcf58ba013153aa4003b31ea0fd189126f`
- frozen SHA-256: `221b55c00b6aa12742219d1448cfc8dcf58ba013153aa4003b31ea0fd189126f`
- exact hash match: yes

## Step 02 — cleaning

Status: **EXACT REPRODUCTION**

- retained sequences: 7,534
- excluded high-nonstandard: 136
- excluded exact duplicates: 242
- excluded length-out-of-range: 4

Frozen hash checks:

- `cleaned_entries.tsv`: PASS
- `evidence_summary.tsv`: PASS
- `duplicate_report.tsv`: PASS
- `length_composition.tsv`: PASS
- `mature_chain_sensitivity.tsv`: PASS

All committed Step-02 hashes reproduced exactly.

## Step 03 — MMseqs2 clustering

Status: **SCIENTIFIC STATE REPRODUCED; RAW TSV ORDER NONDETERMINISTIC**

The exact frozen MMseqs2 build was restored:

`eec9c354be4276d2373996af2e50808b1390d527`

Frozen parameters were unchanged:

- minimum sequence identity: 0.30
- coverage: 0.80
- coverage mode: 1
- cluster mode: 0
- sensitivity: 7.5
- threads: 8

Recovered aggregate geometry matched the frozen census exactly.

Precursor clustering:

- members: 7,534
- clusters: 1,215
- singletons: 672
- maximum cluster size: 377

Mature-chain clustering:

- members: 7,533
- clusters: 1,279
- singletons: 708
- maximum cluster size: 308

Two independent recovery runs produced:

- identical biological cluster partitions;
- identical `(representative, member)` row sets;
- different raw TSV byte order.

Therefore the original frozen raw TSV SHA-256 values were not reproduced byte-for-byte because MMseqs2 emits the same rows in nondeterministic order.

Stable canonical sorted-row SHA-256 values across both recovery runs:

- precursor: `7b15b9e83c67a998e70790b91523bc99c42ed3ada16fd74d7eb5295497e038a0`
- mature: `ab6fa7a07d6ba2d90f5a96b70da7b99657b59f735d978516b2323f947715cc7f`

The representative assignments and biological cluster membership are therefore reproduced exactly across recovery runs. Step 04 is retained as an independent downstream check that this serialization-order difference does not alter the frozen divergence state.

## Step 04 — divergence assignment

Status: **EXACT REPRODUCTION**

Recovered divergence geometry matched the frozen census exactly:

- total clusters: 1,215
- sequence-divergent clusters: 936
- diagnostic-burn clusters: 187
- usable divergent clusters: 796

Recovered `divergence_assignment.tsv` SHA-256:

`fd2b1e1ac5fdca1657a59fb713e7b0305dd5488f0db16b4bb18ccfdf76912a83`

Frozen SHA-256:

`fd2b1e1ac5fdca1657a59fb713e7b0305dd5488f0db16b4bb18ccfdf76912a83`

Exact hash match: yes.

This independently confirms that the Step-03 raw TSV row-order nondeterminism does not alter the downstream frozen divergence state.

## Step 05 — family annotation / Gate V2

Status: **EXACT REPRODUCTION**

Recovered Gate V2 geometry matched the frozen census exactly:

- usable sequence-divergent V2-A clusters: 796
- family-disjoint V2-B clusters: 180
- missing Pfam within V2-A: 557
- shared Pfam with frozen reference set: 59
- confirmed family-disjoint: 180
- largest divergent Pfam family fraction: 0.0088

Recovered `gatev2_audit.tsv` SHA-256:

`047ecaa58fee2be7c815ddc0aee2b329eb9a9c0708e3adc44c51863f6067d0c9`

Frozen SHA-256:

`047ecaa58fee2be7c815ddc0aee2b329eb9a9c0708e3adc44c51863f6067d0c9`

Exact hash match: yes.

The exact V2-B membership state required for Experiment 03 positive-set reconstruction is therefore recovered.

## Negative-artifact recovery boundary

The original generated negative candidate and partition files were not committed to Git.

Repository policy intentionally ignored:

- `preprotocol/toxprot_census/data/`
- generated `preprotocol/toxprot_census/results/*` except selected snapshots.

The following original files were searched for in:

- all Git objects and branches;
- Git LFS;
- `/kaggle/working`;
- `/kaggle/input`;
- `/tmp`.

No recoverable copy was found for:

- `negatives_family_aware.fasta`
- `negatives_family_aware_filtered.fasta`
- `negative_family_aware.tsv`
- `negative_diagnostic_partition.tsv`

The committed snapshots preserve the original candidate counts and SHA-256 hashes but not the sequence files themselves.

Therefore Step 06 recovery now proceeds as a **single hash-gated regeneration attempt** from the frozen code and live UniProt API.

This is not yet a dataset re-freeze.

### Predeclared Step-06 recovery configuration

The regeneration attempt uses the frozen `06_negatives.py` implementation from candidate-census commit `9fd9347`.

The load-bearing query configuration is unchanged:

- background: `reviewed:true AND NOT keyword:KW-0800 AND existence:1`
- phenotype-short: `reviewed:true AND NOT keyword:KW-0800 AND length:[5 TO 100] AND ft_signal:* AND existence:1`
- phenotype-long: `reviewed:true AND NOT keyword:KW-0800 AND length:[101 TO 1000] AND cc_subcellular_location:Secreted AND existence:1`
- family-aware: `reviewed:true AND NOT keyword:KW-0800 AND xref:pfam-{pf}`
- family-aware scope: first 50 lexicographically sorted positive Pfam families
- maximum 300 returned entries per queried family
- background cap: 15,000
- accession-level deduplication as implemented in the frozen code

The exact expected candidate counts are:

- background: 15,000
- phenotype-matched: 6,113
- family-aware partial census: 7,110

### Predeclared exact-recovery hashes

The committed snapshot preserves hashes for the candidate metadata tables and count table, not for the FASTA files themselves.

Exact Step-06 recovery requires all four regenerated files to match:

- `negative_pool_counts.tsv`:
  `c53f13c9cbb69a0ec90038cef5e7e131ea18f8e80065f08109f9b9dd8ad708b2`
- `negative_background.tsv`:
  `307aaa8a46a82dd44ec762b411ca147398e4383736c4a3f6a2f966f7126fbb08`
- `negative_phenotype.tsv`:
  `081cfa42b2333f7cdb558fab899c542e4fd26a9961fc73e09a8ca155fb3a3a4f`
- `negative_family_aware.tsv`:
  `62bb2ad97679b0dc6eebe48813813b54804e33800501a20a0acb6899de519ec4`

All four hashes must match exactly. Candidate-count agreement without hash agreement is insufficient for exact recovery.

### Expected recovery risk

Exact reproduction is possible but is **not assumed**.

Step 06 depends on live UniProt search results. Database releases, annotation changes, entry additions/removals, or changes affecting the first-50-family query results can alter candidate membership even when the frozen query code is unchanged.

Therefore the outcomes are predeclared:

1. **All four hashes match** — Step 06 is exact recovery and downstream 06B/07 reconstruction may proceed.
2. **Any hash differs** — recovery stops before 06B. The negative set is treated as a genuine post-reset deviation requiring an explicit pre-model amendment/re-freeze rather than silently replacing the frozen membership.

If a deviation occurs, the amendment must re-run the model-blind negative pipeline and verify Gate C, diagnostic burn geometry, <=1,022-residue eligibility, and whether the changed eligible-negative count materially alters the frozen feasibility analysis.

This prediction and acceptance rule are committed before the regeneration result is observed.

## Remaining recovery

Not yet accepted:

1. Step 06 — candidate-negative regeneration and frozen-hash comparison
2. Step 06B — positive-overlap filtering
3. Step 07 — permanent diagnostic partition

Recovery remains entirely model-blind.
