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

## Remaining recovery

Not yet accepted:

1. Step 03 — MMseqs2 clustering
2. Step 04 — divergence assignment
3. Step 05 — family annotation / V2-B membership
4. Step 06/06B — negative reconstruction and positive-overlap filtering
5. Step 07 — permanent diagnostic partition

Recovery remains entirely model-blind.
