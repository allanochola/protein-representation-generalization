# Experiment 03 Stage 1 — discovery/confirmatory partition specification

**Status:** PRE-MODEL — freeze before any Experiment 03 ESM embedding or SAE activation is computed.

## 1. Confirmatory universes

### Positives

All 161 eligible V2-B cluster representatives are confirmatory.

No confirmatory positive may be used for:
- feature nomination;
- feature stability analysis;
- threshold selection;
- sign selection;
- feature-set construction;
- hyperparameter choice.

### Negatives

All 3,541 eligible untouched family-aware negatives are confirmatory.

No confirmatory negative may be used during discovery or feature nomination.

## 2. Discovery candidate universes

### Positives

Discovery-positive candidates are restricted to the 845 eligible toxin clusters outside V2-B already frozen in:

`stage1_model_blind/discovery_positive_candidates.tsv`

Composition:
- divergent non-V2-B: 615
- frozen reference-set clusters: 230

All 845 passed a model-blind MMseqs2 leakage check against the 161 confirmatory V2-B representatives:

- minimum identity: 0.30
- minimum shorter-sequence coverage: 0.80
- cov-mode: 1
- qualifying hits: 0

### Negatives

Discovery negatives are restricted to the 638 eligible permanently burned family-aware negatives frozen in:

`stage1_model_blind/discovery_negative_candidates.tsv`

These are permanently disjoint from the 3,541 confirmatory negatives.

## 3. Length strata

The frozen strata are:

- `<30`
- `30-75`
- `76-150`
- `>150`

Discovery composition is matched to the eligible V2-B confirmatory-positive proportions.

## 4. Primary discovery size

The realized maximum discovery set contains:

- 139 positives
- 139 negatives

Target counts by length stratum are identical in both classes:

| stratum | positives | negatives |
|---|---:|---:|
| `<30` | 9 | 9 |
| `30-75` | 22 | 22 |
| `76-150` | 29 | 29 |
| `>150` | 79 | 79 |
| **Total** | **139** | **139** |

N=139 is the maximum practical target-matched discovery size.

It exhausts:
- all 79 available `>150` positive discovery candidates;
- all 9 available `<30` burned family-aware negative candidates.

No confirmatory example is used to enlarge the discovery pool.

## 5. Deterministic ordering

Within each class and length stratum, candidates are ordered by SHA-256 of:

`<salt>|<stable_identifier>`

Frozen salts:

- positives: `exp03-stage1-positive-v1`
- negatives: `exp03-stage1-negative-v1`

Stable identifiers:

- positives: `cluster_rep`
- negatives: `accession`

Ascending hexadecimal SHA-256 order defines membership priority.

No pseudo-random generator or mutable seed state is used.

## 6. Realized N=139 discovery membership

For each length stratum, take the first required number of candidates under the frozen deterministic hash order.

The realized N=139 discovery membership is frozen before model contact.

## 7. Nested stability subsets

The later stability sweep uses nested subsets of the realized N=139 pool:

### N=120

Length targets:

- `<30`: 8
- `30-75`: 19
- `76-150`: 25
- `>150`: 68

Within each stratum, take the first N-specific count from the same frozen hash ordering.

### N=100

Length targets:

- `<30`: 7
- `30-75`: 16
- `76-150`: 21
- `>150`: 56

Within each stratum, take the first N-specific count from the same frozen hash ordering.

Therefore:

`N=100 ⊂ N=120 ⊂ N=139`

for both discovery positives and discovery negatives.

## 8. Leakage invariants

Before first model contact, the realized partition must satisfy:

1. zero positive cluster overlap between discovery and confirmatory positives;
2. zero negative accession overlap between discovery and confirmatory negatives;
3. zero qualifying MMseqs2 hit from any discovery-positive representative to any confirmatory V2-B representative at >=30% identity and >=80% shorter-sequence coverage;
4. every discovery sequence satisfies the frozen 1–1,022 residue eligibility rule;
5. exact class and length-stratum counts match this specification.

Any failure stops model contact.

## 9. Model-contact boundary

Partition construction and validation are model-blind.

The first permitted Experiment 03 model contact occurs only after:
- this specification is committed;
- realized membership files are generated;
- all leakage invariants pass;
- realized membership files and hashes are committed.

The feature-stability sweep is model contact because it requires ESM/SAE activations.
