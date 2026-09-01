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

**Stage 1 complete — `FAIL / No verdict: unstable feature`. Confirmatory set remained unobserved.**

Experiment 03 asks whether a model-derived toxin-relevant internal feature can
provide functional evidence that survives natural evolutionary divergence and
adds information beyond strong sequence-only controls.

The primary confirmatory question was:

> Can a model-derived toxin-relevant feature, nominated without using
> confirmatory labels, discriminate family-disjoint toxin proteins from
> sequence-clean family-aware non-toxin proteins beyond a strong model-blind
> sequence baseline?

Before that comparison was permitted, the protocol required Stage 1 to
demonstrate that discovery produced a compact, identity-stable SAE feature set.

### Preprotocol Tox-Prot census

Before any Experiment 03 embedding or SAE activation was inspected, a
model-blind Tox-Prot census established the evaluation geometry.

| Gate | Frozen criterion | Observed | Verdict |
|---|---|---:|---|
| A — independent positives | ≥90 usable sequence-divergent, family-disjoint clusters | 180 V2-B clusters | PASS |
| B — family concentration | largest family ≤25% of divergent clusters | 0.9% | PASS |
| C — negative support | ≥1,000 at 5% FPR; ≥3,000 at 1% FPR | 4,120 untouched sequence-clean family-aware negatives after diagnostic burn | PASS |
| D — model-blind shortcut | family-aware AUROC/AUPRC must not exceed frozen 0.95 rejection boundary | RF AUROC 0.9494, AUPRC 0.9011 | PASS |

After the permanent diagnostic burn and ESM-2 sequence-eligibility rule, the
frozen confirmatory universe contained **161 family-disjoint positive
clusters** and **3,541 sequence-clean family-aware negatives**.

The Gate D result was deliberately close to the rejection boundary: simple
sequence properties already carry substantial toxin signal. The intended
confirmatory experiment therefore tested incremental representation value,
not raw toxin discrimination.

### Stage-1 stability instrument

The discovery set contained **139 toxin positives and 139 family-aware
negatives**, jointly matched across the frozen protein-length strata.

Using ESM-2 650M layer 18, the normalized InterPLM SAE, residue-max pooling,
and a frozen `k=5` nomination rule, Stage 1 tested the nominated signed feature
set with three independently calibrated criteria:

1. median pairwise Jaccard ≥ **0.60**;
2. at least **4 of 5** nominated signed features recurring in ≥ **80%** of
   perturbations;
3. median fixed-top-5 concentration ≥ **0.35**.

All three gates failed at the primary `N=139` analysis:

| Stability criterion | Frozen threshold | Observed | Verdict |
|---|---:|---:|---|
| Median pairwise Jaccard | ≥0.60 | **0.4286** | FAIL |
| Recurrent nominated features | ≥4/5 at ≥0.80 | **1/5** | FAIL |
| Median fixed-top-5 concentration | ≥0.35 | **0.00588** | FAIL |

The top five therefore captured only about **0.59% of total absolute latent
mean-difference mass** under the frozen concentration statistic.

One signed latent (`4983:-`) recurred in 95% of perturbations, but the protocol
did not independently calibrate a single-feature decision rule. Single-feature
statistics therefore remain descriptive and cannot rescue the failed set gate.

Length-stratum descriptives showed substantial heterogeneity: the full-sample
top-five effects were strongest and sign-consistent in the `>150`-residue
stratum, while several weakened or reversed sign in shorter strata. The
`>150` stratum was preregistered as exhaustion-limited, so this observation is
descriptive rather than an independent stability claim.

### Experiment 03 conclusion

Under the preregistered **ESM-2 650M layer-18 / normalized InterPLM SAE /
residue-max** representation, the toxin-versus-family-aware-negative discovery
contrast did **not** yield a compact, identity-stable five-feature
representation.

This does **not** establish that ESM-2 contains no toxin-relevant information.
It establishes that this frozen representation and nomination procedure did
not expose that information as the compact, stable feature set required to
enter confirmatory evaluation.

Because Stage 1 failed:

- no confirmatory feature specification was opened;
- no confirmatory sequence was embedded;
- no confirmatory representation statistic was computed;
- the planned `ΔTPR@FPR5` representation-versus-sequence comparison was never
  run.

Experiment 03 therefore terminates as **No verdict — unstable feature**, not
as `H_repr-functional` or `H_sequence`.

### Threat-model boundary

Experiment 03 tests **natural evolutionary divergence**. It does not establish
robustness to deliberately engineered, function-preserving sequence changes
designed to evade screening.

The Stage-1 result is correspondingly narrow: under this frozen
model/layer/SAE/pooling configuration, discovery did not produce the compact,
stable interpretable feature set required for confirmatory evaluation.

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

Stage 1 subsequently demonstrated why this discipline matters. The biological
SAE sweep failed all three frozen stability gates. The confirmatory set
therefore remained dark rather than being used to search for an alternative
feature, layer, pooling rule, feature-set size, or threshold.

Experiment 03 thus provides a third form of controlled outcome in this
program: a preregistered discovery instrument can terminate a biological
experiment before confirmatory evaluation when the representation does not
satisfy the stability assumptions required for the planned claim.

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
│       ├── stage1_model_blind/
│       └── stage1_model_contact/
├── preprotocol/
│   └── toxprot_census/
├── results/
└── figures/
```

---

## Status

**Experiment 01:** complete — `H_repr`.

**Experiment 02:** closed pre-data — insufficient precision for the planned
retention criterion; **no biological verdict**.

**Experiment 03:** Stage 1 complete — **FAIL / No verdict: unstable feature**.
The frozen biological SAE stability instrument failed Jaccard
(`0.4286 < 0.60`), recurrence (`1/5 < 4/5`), and concentration
(`0.00588 < 0.35`). The confirmatory set remained unobserved, so no
representation-versus-sequence confirmatory verdict was made.

The program now demonstrates three distinct outcomes:

- Experiment 01 shows that a fixed protein-model representation can retain
  biological information across explicit sequence divergence.
- Experiment 02 shows that dataset geometry and statistical precision can
  terminate a proposed biological experiment before data are consumed.
- Experiment 03 shows that a model-derived feature nomination can fail a
  preregistered stability requirement before confirmatory evaluation.

Together, these experiments separate representation generalization,
experimental feasibility, and interpretable-feature stability rather than
treating successful downstream prediction as sufficient evidence for all
three.
