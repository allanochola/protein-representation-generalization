# Protein representation generalization

**Can biological information inside protein foundation models survive explicit sequence-divergence controls — and can interpretable internal features provide functional evidence beyond sequence and family shortcuts?**

This project studies whether biological information encoded inside protein foundation models remains accessible when homologous shortcuts are explicitly disrupted.

The research progresses from representation generalization to function-relevant interpretability:

1. test whether a fixed representation survives sequence divergence;
2. determine whether the available biological labels can support the intended inference;
3. test whether interpretable internal features carry function-relevant evidence beyond strong model-blind sequence controls;
4. examine whether that evidence can be inspected and contested rather than treated as an opaque prediction.

The experiments use frozen representation choices, explicit sequence comparators, sequence-identity and family controls, cluster-level uncertainty estimates, model-blind feasibility checks, and pre-data decision rules.

The current work does **not** claim a production biosecurity screening system or robustness to deliberately engineered evasion. Those require separate evaluation beyond natural evolutionary divergence.

---

## Experiment 01 — Secondary structure

**Complete. Frozen verdict: `H_repr`.**

Experiment 01 tests whether per-residue Q3 secondary-structure information in ESM-2 650M layer 17 survives a 30%-sequence-identity cluster holdout, or collapses toward an explicit ±3-residue local-sequence baseline.

<p align="center">
  <img src="figures/exp01_q3_generalization.png" width="700">
</p>

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

**Zenodo:** [10.5281/zenodo.22134890](https://doi.org/10.5281/zenodo.22134890)


---

## Experiment 02 — Catalytic residues

**Closed pre-data. No biological verdict.**

Experiment 02 was designed to ask a harder question:

> Does linearly accessible catalytic-site information in ESM-2 survive a 30%-identity family holdout beyond what can be recovered from local amino-acid context?

The experiment never reached confirmatory M-CSA label construction or ESM evaluation.

Its pre-data precision analysis found that the **planned split could not estimate the required retention quantity reliably enough to support the confirmatory decision rule**.

<p align="center">
  <img src="figures/exp02_retention_feasibility.png" width="700">
</p>

The binding quantity was

`R = Δ_div / Δ_rand`

with `H_repr` requiring:

`CI_low(R) > 0.75`.

Under a favorable synthetic configuration with equal support and zero cluster heterogeneity, near-complete retention was detectable:

| True R | Detection probability |
|---:|---:|
| 0.85 | 0.19 |
| 0.90 | 0.37 |
| 0.95 | 0.70 |
| 1.00 | 0.81 |

But under the planned support — approximately **100 random-test clusters / 420 positives** and **170 divergent-test clusters / 700 positives**, with cluster heterogeneity active — sensitivity collapsed:

| True R | Mean R̂ | Mean log-R half-width | Calibration ratio | Detection |
|---:|---:|---:|---:|---:|
| 0.95 | 0.949 | 0.411 | 0.967 | 0.18 |
| 1.00 | 1.027 | 0.412 | 0.928 | 0.29 |

The bootstrap remained calibrated against across-dataset variability, and all retention bootstrap replicates were valid.

So the stopping result is about the **experimental design**, not the biological hypothesis:

> Even when true retention is complete, the planned configuration satisfies the required lower confidence bound in only 29% of calibrated simulations.

No confirmatory M-CSA label pool was built, no ESM-2 embeddings were extracted, no probe was fit, and no test split was evaluated.

See the [draft protocol](experiments/02-catalytic-residues/PROTOCOL.md), [pre-data precision analysis](experiments/02-catalytic-residues/PRE_DATA_PRECISION.md), [implementation audit](experiments/02-catalytic-residues/IMPLEMENTATION_NOTES.md), and [result](experiments/02-catalytic-residues/results.md).

---

**Zenodo:** [10.5281/zenodo.22164680](https://doi.org/10.5281/zenodo.22164680)

---

## Experiment 03 — Interpretable toxin-function signatures

**Preregistered pre-data. No Experiment 03 model result has been observed.**

Experiment 03 asks whether a model-derived toxin-relevant internal feature can provide functional evidence that survives natural evolutionary divergence and adds information beyond strong sequence-only controls.

The primary question is:

> Can a model-derived toxin-relevant feature, nominated without using confirmatory labels, discriminate family-disjoint toxin proteins from sequence-clean family-aware non-toxin proteins beyond a strong model-blind sequence baseline?

This is deliberately **not** a generic toxin-classification benchmark.

The experiment requires three evidence layers:

1. **Representation evidence** — confirmatory performance beyond sequence-only controls.
2. **Mechanistic characterization** — inspection of what biological or representational property drives a validated feature.
3. **Contestability analysis** — examination of cases where representation evidence disagrees with conventional sequence or family evidence.

### Preprotocol Tox-Prot census

Before any Experiment 03 embedding or SAE activation was inspected, a model-blind Tox-Prot census tested whether the intended evaluation geometry was viable.

| Gate | Frozen criterion | Observed | Verdict |
|---|---|---:|---|
| A — independent positives | ≥90 usable sequence-divergent, family-disjoint clusters | 180 V2-B clusters | PASS |
| B — family concentration | largest family ≤25% of divergent clusters | 0.9% | PASS |
| C — negative support | ≥1,000 at 5% FPR; ≥3,000 at 1% FPR | 4,120 untouched sequence-clean family-aware negatives after diagnostic burn | PASS |
| D — model-blind shortcut | family-aware AUROC/AUPRC must not exceed frozen 0.95 rejection boundary | RF AUROC 0.9494, AUPRC 0.9011 | PASS |

The Gate D result is intentionally close to the rejection boundary. Simple sequence properties already carry substantial toxin signal. Experiment 03 therefore tests **incremental representation value**, not raw toxin discrimination.

After the permanent diagnostic burn and the frozen ESM-2 sequence-eligibility rule:

- **161** family-disjoint V2-B positive cluster representatives remain eligible;
- **3,541** untouched sequence-clean family-aware negatives remain eligible;
- both positive and negative support gates still pass.

Sequences longer than 1,022 biological residues are excluded rather than truncated or chunked. This removes 19 of the original 180 V2-B clusters, so the primary claim is explicitly scoped to the ESM-eligible universe.

### Frozen primary estimand

The primary quantity is:

`ΔTPR@FPR5 = TPR_representation@5%FPR − TPR_sequence@5%FPR`

with a 95% paired cluster-bootstrap confidence interval over the 161 eligible positive clusters.

The preregistered materiality boundary is **+0.05**:

- **H_repr-functional** — `CI_low(ΔTPR@FPR5) >= +0.05`
- **H_sequence** — `CI_high(ΔTPR@FPR5) <= +0.05`
- **Mixed / unresolved** — the interval overlaps `+0.05`

The pre-data feasibility simulator showed that the design is substantially better at establishing a moderate-to-large positive representation increment than at proving equivalence to the sequence baseline. A null effect may therefore remain Mixed rather than automatically producing `H_sequence`.

`ΔTPR@FPR1` and `ΔAUROC` are frozen secondary quantities and carry no independent verdict.

### Threat-model boundary

Experiment 03 tests **natural evolutionary divergence**. It does not establish robustness to deliberately engineered, function-preserving sequence changes designed to evade screening.

The intended contribution is narrower: determine whether interpretable representation-level evidence can survive substantial natural departure from known toxin families, add information beyond model-blind sequence evidence, and support inspection of disagreement cases.

See the [frozen Experiment 03 protocol](experiments/03-toxin-representation/PROTOCOL.md).

**Preregistration tag:** `exp03-predata-protocol-v1.0`

---

## Split audit — Experiment 01

The final canonical dataset contains **11,373 proteins, 11,043 clusters, and 2,875,432 residues**.

The divergent split shares **zero clusters** with training or random test.

The per-split cluster counts sum to 11,091 because **48 clusters contain different proteins in both training and the in-distribution random test**. Subtracting that intentional overlap reconciles exactly to the 11,043 unique clusters.

Protein membership is disjoint across all three splits.

---

## Citable releases

### Experiment 01 — secondary-structure representation generalization

Ochola, A. (2026). *Protein representation generalization: ESM-2 secondary-structure information under a 30%-identity cluster holdout*. Zenodo.  
https://doi.org/10.5281/zenodo.22134890

### Experiment 02 — catalytic-residue pre-data feasibility

Ochola, A. (2026). *Pre-data feasibility analysis for catalytic-residue representation generalization under a 30%-identity family holdout* (Version 1.0.0). Zenodo.  
https://doi.org/10.5281/zenodo.22164680

---

## Implementation discipline

The project treats experimental design and the tools used to validate that design as objects that themselves require testing.

Experiment 01 froze its protocol before extraction and probing. Before any confirmatory metric was observed, the split was canonicalized using content-derived identifiers and tested for invariance to arbitrary row order and cluster names.

After the primary Exp 01 metrics were observed, the slow cluster bootstrap was optimized using per-cluster sufficient statistics. The optimization was accepted only after demonstrating equivalence to the frozen residue-concatenation computation. The final 2,000-replicate cluster bootstrap takes **1.797 seconds**.

Experiment 02 exposed a second lesson: a **feasibility simulator is itself an instrument**.

Early simulations incorrectly suggested that the experiment should close. Two defects were subsequently identified:

1. baseline and ESM arms were generated independently, artificially inflating variance in difference-based statistics;
2. signal strength was re-tuned to target AP inside every outer dataset, suppressing the across-dataset variation required for a valid power estimate.

Both defects were corrected before any confirmatory biological data were accessed.

The final simulator was accepted only after its bootstrap uncertainty agreed with actual across-dataset variation. Under the final planned-support configuration, calibration ratios were **0.967** and **0.928**.

The final stopping decision therefore rests on a validated feasibility instrument rather than the earlier defective simulations.

Experiment 03 extends the same discipline one step further.

Before any Experiment 03 embedding, SAE activation, feature nomination, or confirmatory representation statistic was inspected:

- the Tox-Prot positive and negative support census was closed;
- sequence-divergence and family-disjointness rules were committed;
- family-aware negatives were filtered against all positives at the frozen 30% identity rule;
- a permanent model-blind diagnostic burn was created;
- simple sequence shortcuts were measured;
- the ESM-2 sequence-length eligibility rule was frozen at 1–1,022 biological residues;
- the final eligible geometry was fixed at 161 positive clusters and 3,541 family-aware negatives;
- a paired-outcome feasibility simulator was used to size the confirmatory decision rule;
- the +0.05 ΔTPR materiality boundary was frozen;
- the complete pre-data protocol was tagged `exp03-predata-protocol-v1.0`.

The protocol and the simulation outputs used to select the decision rule are committed together, so the inferential standard is traceable to the state that existed before model contact.

---

## Structure

```text
protein-representation-generalization/
├── README.md
├── src/
│   └── power_sim.py
├── notebooks/
├── experiments/
│   ├── 01-secondary-structure/
│   ├── 02-catalytic-residues/
│   └── 03-toxin-representation/
│       ├── PROTOCOL.md
│       ├── protocol_feasibility_check.py
│       ├── code/
│       └── results/
├── preprotocol/
│   └── toxprot_census/
├── results/
└── figures/
```

---

## Status

**Experiment 01:** complete — `H_repr`.

**Experiment 02:** closed pre-data — insufficient precision for the planned retention criterion; **no biological verdict**.

**Experiment 03:** **preregistered pre-data** at tag `exp03-predata-protocol-v1.0`; no Experiment 03 ESM embedding, SAE activation, feature nomination, or confirmatory representation result has yet been inspected.

The program now separates three questions that are easy to conflate:

- Does a fixed protein-model representation retain biological information across explicit sequence divergence?
- Is the available biological dataset large and independent enough to support the intended inferential claim?
- Can an interpretable internal feature provide function-relevant evidence beyond sequence and family shortcuts, and can that evidence be inspected when it disagrees with conventional signals?

Experiment 01 answers the first positively for secondary structure.

Experiment 02 demonstrates that the second question can become the binding constraint before a functional biological hypothesis is tested.

The Tox-Prot preprotocol census establishes sufficient support for a harder function-relevant experiment while revealing a strong sequence-only shortcut baseline.

Experiment 03 is the preregistered test of the third question under **natural evolutionary divergence**. Its confirmatory result remains unknown.
