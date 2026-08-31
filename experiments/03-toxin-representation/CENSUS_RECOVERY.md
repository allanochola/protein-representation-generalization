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

## Remaining recovery

Not yet accepted:

1. Step 04 — divergence assignment
2. Step 05 — family annotation / V2-B membership
3. Step 06/06B — negative reconstruction and positive-overlap filtering
4. Step 07 — permanent diagnostic partition

Recovery remains entirely model-blind.
