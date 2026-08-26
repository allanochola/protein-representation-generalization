# Protein representation generalization

**Does biological information encoded inside a protein foundation model survive explicit sequence-divergence controls?**

This project follows two earlier findings. In [bio-capability-probing](https://github.com/allanochola/bio-capability-probing), linear probes separated training examples perfectly in-distribution but failed out of distribution — a representation can look informative and still not generalize. In [protein-foundation-models](https://github.com/allanochola/protein-foundation-models), protein-language-model scaling behavior varied with evolutionary context and was not consistent across model families — signals should not be assumed to transfer uniformly. This project combines those two lessons in a biological foundation model: it tests whether biological information read from a protein model's internal representations holds up when the test proteins are genuinely divergent from the training proteins, rather than close homologs.

## Experiment 01 — secondary structure

Does per-residue Q3 secondary-structure information in ESM-2 (layer 17, 650M) survive a ≤30%-identity cluster-held-out split, or collapse toward a sequence-local baseline? Frozen design: [`experiments/01-secondary-structure/PROTOCOL.md`](experiments/01-secondary-structure/PROTOCOL.md).

Two preregistered quantities: **Δ_ESM(divergent)** — ESM's Q3 margin over a ±3 local-sequence baseline on divergent proteins — and **G** — the drop from an in-distribution to a divergent test. Metrics (Q3 accuracy, secondary macro-F1) and decision bands are fixed in the protocol before any embedding is extracted, and confidence intervals resample whole sequence-identity clusters, not residues.

## Discipline

One frozen protocol, one experiment. Preregistration is enforced by ordering: the protocol lands before extraction. Experiment 01 earns whether there is ever an Experiment 02 — if the representation generalizes, the natural path is higher-level functional properties and eventually causal validation; if it collapses, that is the result. Linear probing is correlational: a positive result *motivates* causal follow-up (activation patching, SAEs), it does not constitute it, and a positive result is not a claim about function-relevant screening features.

## Structure

```
protein-representation-generalization/
├── README.md                    this file
├── PROTOCOL.md                  program-level scope + shared method discipline
├── src/
│   ├── probe.py                 metrics, local baseline, cluster split + bootstrap (unit-tested)
│   ├── extract_esm2.py          ESM-2 layer-17 per-residue embeddings
│   └── clustering.py            TAPE SS loading + 30% MMseqs2 clustering
├── notebooks/
│   ├── extract_embeddings.py    run first (GPU): cache embeddings + labels + clusters
│   └── probe_and_evaluate.py    fit probe + baseline, both splits, Δ/G, verdict
├── experiments/01-secondary-structure/
│   ├── PROTOCOL.md              the frozen experiment design
│   └── results.md               outcome (pending run)
├── results/
└── figures/
```

## Status

Protocol frozen. Extraction and probe implemented; the parts that break silently — per-residue label alignment and the cluster-level bootstrap — are validated offline (`python src/probe.py`). Awaiting the run.
