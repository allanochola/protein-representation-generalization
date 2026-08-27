# Protein representation generalization

**Does biological information encoded inside a protein foundation model survive explicit sequence-divergence controls?**

This project tests internal biological representations under explicit sequence divergence rather than assuming that in-distribution probe performance transfers.

## Experiment 01 — secondary structure

**Complete. Frozen verdict: `H_repr`.**

Experiment 01 tests whether per-residue Q3 secondary-structure information in ESM-2 650M layer 17 survives a 30%-sequence-identity cluster holdout, or collapses toward an explicit ±3-residue local-sequence baseline.

| Representation | Random Q3 | Divergent Q3 | Divergent macro-F1 |
|---|---:|---:|---:|
| ESM-2 layer 17 | 0.765166 | 0.762263 | 0.758054 |
| ±3 local sequence | 0.607324 | 0.607224 | 0.568602 |

Preregistered quantities:

- **Δ_ESM(divergent) = +0.155039**, 95% cluster-bootstrap CI **[+0.151, +0.159]**
- **G = +0.002903**, 95% cluster-bootstrap CI **[-0.003, +0.009]**

The frozen `H_repr` criterion required Δ_ESM ≥ 0.08 and G ≤ 0.10. Both conditions are satisfied.

For this target, the fixed ESM-2 representation retains substantial linearly accessible information beyond local sequence context and shows essentially no degradation under the divergent cluster-held-out test.

See the [frozen protocol](experiments/01-secondary-structure/PROTOCOL.md) and [full result](experiments/01-secondary-structure/results.md).

## Split audit

The final canonical dataset contains **11,373 proteins, 11,043 clusters, and 2,875,432 residues**.

The divergent split shares **zero clusters** with training or random test.

The per-split cluster counts sum to 11,091 because **48 clusters contain different proteins in both training and the in-distribution random test**. Subtracting that intentional overlap reconciles exactly to the 11,043 unique clusters.

Protein membership is disjoint across all three splits.

## Implementation discipline

The protocol was frozen before extraction and probing.

Technical failures and implementation corrections are recorded rather than hidden. Before any confirmatory metric was observed, the split was canonicalized using content-derived identifiers and tested for invariance to arbitrary row order and cluster names.

After the primary metrics were observed, the slow cluster-bootstrap implementation was optimized using per-cluster sufficient statistics. The optimization was accepted only after demonstrating equivalence to the frozen residue-concatenation computation.

The final 2,000-replicate cluster bootstrap takes **1.797 seconds**.

Linear probing remains correlational. A positive result motivates testing higher-level biological properties and eventually causal follow-up; it does not establish a causal mechanism or a function-relevant biosecurity screening feature.

## Structure

```text
protein-representation-generalization/
├── README.md
├── PROTOCOL.md
├── src/
├── notebooks/
├── experiments/01-secondary-structure/
│   ├── PROTOCOL.md
│   ├── IMPLEMENTATION_NOTES.md
│   └── results.md
├── results/
│   ├── ss_generalization.csv
│   ├── ss_summary.json
│   └── provenance.json
└── figures/
```

## Status

**Experiment 01 complete — `H_repr`.**

The first modality-transfer test finds divergence-robust structural information in a fixed ESM-2 representation. The next scientific question is whether the same robustness survives for a higher-level biological property closer to function. That should be treated as a new experiment with its own frozen protocol.
