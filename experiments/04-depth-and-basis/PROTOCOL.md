# Experiment 04 — Depth and Basis

## Status

**PRE-DATA / METHOD DEVELOPMENT**

Experiment 04 is designed to distinguish representational-depth effects from
basis misalignment or distributed accessibility following Experiment 03.

No new Experiment-04 biological ESM activations may be inspected until the
supervised sparse-probe stability instrument has been calibrated and
independently validated.

Layer 18 results inherited from Experiment 03 are already observed and may be
used only as a fixed anchor. They must not be reinterpreted as fresh evidence.

---

## 1. Motivation

Experiment 03 tested whether toxin-associated information in ESM-2 650M could
be localized into a compact, identity-stable set of InterPLM SAE features at
layer 18.

The preregistered three-way stability gate failed:

- median pairwise signed top-5 Jaccard = 0.428571;
- 1/5 nominated signed features recurred in at least 80% of perturbations;
- median fixed-top-5 concentration = 0.005882.

Experiment 03 therefore closed as:

> **FAIL / No verdict — unstable feature.**

This does not imply absence of toxin-associated information in ESM-2. Several
competing explanations remain:

1. layer 18 may be the wrong representational depth;
2. toxin-associated information may be distributed rather than compact;
3. the InterPLM SAE basis may be misaligned with information that is nevertheless
   linearly accessible;
4. no stable accessible toxin-associated signal may exist under the frozen
   discovery geometry.

Experiment 04 is designed to distinguish among these explanations rather than
to rescue Experiment 03.

---

## 2. Frozen biological data geometry

Experiment 04 reuses the Experiment 03 discovery geometry.

### Discovery set

- 139 toxin-positive sequences;
- 139 family-aware negative sequences.

### Confirmatory universe

- 161 family-disjoint toxin-positive sequences;
- 3,541 family-aware negative sequences.

The confirmatory universe remains completely unobserved.

No confirmatory sequence may be embedded, pooled, scored, or otherwise inspected
during Experiment 04 method development, calibration, model selection, or
discovery-stage stability analysis.

---

## 3. Model

Protein language model:

- ESM-2 650M;
- hidden width: 1,280.

InterPLM normalized SAEs are evaluated at the six available ESM-2 layers:

- 1
- 9
- 18
- 24
- 30
- 33

Layer 18 is an already-observed anchor from Experiment 03.

Fresh layers are:

- 1
- 9
- 24
- 30
- 33

No best layer will be selected post hoc.

---

# Arm A — ESM depth × InterPLM SAE stability

## 4. Representation

For every evaluated layer:

1. obtain residue-level ESM-2 representations;
2. encode them through the corresponding normalized InterPLM SAE;
3. apply residue-max pooling over each SAE latent;
4. retain the Experiment 03 signed-feature discovery instrument unchanged.

No biological activation from a fresh layer may be computed until the full
Experiment 04 protocol and sparse-probe instrument are frozen.

---

## 5. SAE discovery instrument

The Experiment 03 stability instrument is reused without modification.

### Candidate discovery sizes

- N = 100
- N = 120
- N = 139

### Feature-set size

- k = 5 signed SAE latents.

A signed latent is defined by both latent identity and effect direction.

### Perturbations

- 100 deterministic discovery perturbations per evaluated N and layer.

The perturbation construction must remain identical to Experiment 03.

---

## 6. Frozen SAE stability gates

A layer passes the SAE stability instrument only if all three conditions hold.

### Gate A1 — signed top-5 identity stability

Median pairwise signed top-5 Jaccard:

\[
J_{\mathrm{median}} \ge 0.60
\]

### Gate A2 — nominated-feature recurrence

At least 4 of the 5 nominated signed features must recur in at least 80% of
perturbations.

### Gate A3 — fixed-top-5 concentration

Median fixed-top-5 concentration:

\[
C_{\mathrm{median}} \ge 0.35
\]

### Layer-level decision

\[
\mathrm{SAE\ PASS}
=
A1 \land A2 \land A3
\]

Single-feature statistics are descriptive only and cannot rescue a failed
three-way layer gate.

---

## 7. Primary SAE depth-profile criterion

The primary SAE depth-profile hypothesis passes only if both conditions hold:

1. at least **two previously unobserved layers** pass all three SAE gates; and
2. at least one **fresh adjacent pair** passes.

Fresh adjacent pairs are frozen as:

- 1–9
- 24–30
- 30–33

Layer 18 cannot satisfy the requirement for a previously unobserved layer and
cannot by itself create primary depth-profile success.

An isolated fresh-layer PASS is descriptive/localized only.

---

# Arm B — Supervised sparse probe

## 8. Purpose

Arm B tests whether toxin-associated information is stably and sparsely
linearly accessible in the raw ESM representation even when the InterPLM SAE
basis fails to expose a compact stable feature set.

This arm is intended to distinguish:

- absence of a compact SAE feature set;
- SAE-basis misalignment;
- sparse linear accessibility;
- predictive but dense/distributed accessibility.

High discovery discrimination alone is insufficient for a stable sparse-probe
claim.

---

## 9. Probe representation

At each of the six evaluated layers:

1. use the raw 1,280-dimensional ESM-2 residue representation;
2. apply residue-max pooling across residues independently for each hidden
   dimension;
3. fit an L1-regularized logistic regression using discovery data only.

No SAE features are used in the probe arm.

The pooling operator is intentionally matched to Arm A so that the two arms
primarily differ in representation basis rather than sequence-level aggregation.

---

## 10. Candidate regularization grid

The candidate L1 inverse-regularization grid is frozen as:

\[
C \in
\{
10^{-4},
3\times10^{-4},
10^{-3},
3\times10^{-3},
10^{-2},
3\times10^{-2},
10^{-1},
3\times10^{-1},
1
\}
\]

Regularization selection must occur entirely within discovery data.

Confirmatory labels or confirmatory representations may not influence
regularization selection.

---

## 11. Sparse-probe stability requirements

A probe may not be called stable based on predictive discrimination alone.

The final instrument must jointly evaluate:

1. **predictive discrimination**;
2. **sparsity**;
3. **coefficient identity stability**;
4. **coefficient sign stability**.

The exact statistics, perturbation construction, regularization-selection rule,
and numerical PASS thresholds for Arm B are intentionally **NOT YET FROZEN**.

They must be determined through synthetic calibration followed by independent
synthetic validation before any new biological Experiment-04 activations are
inspected.

No threshold may be selected after seeing fresh-layer toxin results.

---

## 12. Sparse-probe instrument development firewall

Instrument development will proceed in two strictly separated phases.

### Phase B0a — calibration

Use synthetic data with known planted sparse and distributed signal structures
to choose:

- perturbation construction;
- regularization-selection procedure;
- sparsity statistic;
- coefficient-identity stability statistic;
- sign-stability statistic;
- predictive statistic;
- joint decision rule;
- numerical thresholds.

Calibration scenarios must include both positive and negative controls.

### Phase B0b — independent validation

After the complete instrument and all thresholds are frozen, evaluate it on
fresh synthetic seeds/scenarios not used during calibration.

The validation suite must test whether the frozen rule:

- accepts sufficiently strong stable sparse signals;
- rejects unstable sparse signals;
- rejects predictive but intentionally dense/distributed signals as a
  **sparse-stability** claim;
- rejects null/no-signal cases;
- behaves sensibly under correlated nuisance features.

If the instrument fails independent validation, it must be revised and
revalidated on another untouched synthetic validation suite before biological
use.

Every revision resets the validation firewall.

---

## 13. Biological-computation firewall

Before successful completion and freezing of Arm B synthetic validation:

**PROHIBITED**

- embedding fresh biological Experiment-04 layers;
- inspecting fresh-layer raw ESM representations;
- inspecting fresh-layer SAE activations;
- fitting toxin probes at fresh layers;
- computing fresh-layer toxin AUROC or other discrimination statistics;
- tuning thresholds using toxin-associated biological results;
- embedding any confirmatory sequence.

**PERMITTED**

- repository and protocol work;
- reuse of already-observed Experiment 03 layer-18 summary statistics;
- synthetic simulations containing no biological ESM activations;
- implementation tests on synthetic arrays;
- software/unit testing unrelated to biological outputs.

---

# Joint interpretation

## 14. Frozen interpretation matrix

### SAE stable + sparse probe stable

Supports a compact, interpretable and sparsely linearly accessible
toxin-associated representation under this design.

### SAE fails + sparse probe stable

Supports toxin-associated linear accessibility that is not localized into a
compact stable InterPLM SAE feature set.

This pattern is consistent with SAE-basis misalignment and/or a sparse direction
in raw representation space not aligned to individual SAE latents.

### SAE fails + probe predictive but dense or unstable

Supports predictive accessibility without a stable sparse representation under
the frozen probe instrument.

This is interpreted as distributed accessibility rather than compact
contestable representation.

### SAE fails + probe fails

Provides no evidence for either a stable compact SAE representation or a stable
sparse linearly accessible toxin-associated signal under this design.

It is not evidence of information absence in ESM-2.

### Isolated SAE-layer PASS

Descriptive/localized only.

It does not satisfy the primary SAE depth-profile criterion.

### Preferential early-layer success

Strengthens the sequence/composition-shortcut interpretation.

### Adjacent later-layer success

Is consistent with toxin-associated functional abstraction becoming more compact
with representational depth.

This interpretation remains conditional on the frozen adjacent-layer criterion
and may not be reconstructed post hoc around whichever layers perform best.

---

## 15. Anti-rescue rules

The following may not rescue a failed primary criterion:

- selecting a best-performing layer post hoc;
- changing k from 5 after seeing biological results;
- changing residue-max pooling after seeing biological results;
- relaxing any Experiment 03 SAE stability threshold;
- replacing the three-way SAE AND gate with a partial gate;
- interpreting individual stable latents as a layer PASS;
- using high probe AUROC to override failed sparsity/stability requirements;
- changing the probe regularization grid based on biological results;
- modifying sparse-probe thresholds after fresh biological activations are
  inspected;
- using confirmatory data for discovery, model selection, threshold selection,
  or method development.

Exploratory analyses after the primary analysis must be clearly labeled as such
and cannot alter the preregistered verdict.

---

## 16. Experiment-level outcome language

Experiment 04 is a representational-diagnostic experiment.

Its claims concern evidence available under the frozen combination of:

- ESM-2 650M;
- specified representational layers;
- InterPLM normalized SAEs;
- raw ESM sparse linear probes;
- residue-max sequence pooling;
- frozen discovery geometry;
- frozen stability instruments.

Failure of either arm is not proof that toxin-function information is absent
from ESM-2.

---

## 17. Current freeze state

### Frozen now

- research motivation;
- biological discovery/confirmatory geometry;
- six evaluated layers;
- fresh versus previously observed layer distinction;
- Arm A representation;
- Arm A k = 5;
- Arm A N = 100/120/139;
- Arm A perturbation count;
- all three SAE stability thresholds;
- SAE three-way AND rule;
- primary depth-profile success criterion;
- raw 1,280-dimensional representation for Arm B;
- residue-max pooling for Arm B;
- L1 logistic-regression model class;
- candidate C grid;
- requirement that regularization selection use discovery data only;
- requirement for discrimination + sparsity + identity/sign stability;
- synthetic calibration → untouched validation firewall;
- biological-computation firewall;
- joint interpretation matrix;
- anti-rescue rules.

### Not yet frozen

The sparse-probe stability instrument:

- perturbation construction;
- C-selection rule;
- predictive-discrimination statistic and threshold;
- sparsity statistic and threshold;
- coefficient-identity stability statistic and threshold;
- coefficient-sign stability statistic and threshold;
- exact joint PASS/FAIL rule.

These must be frozen only after synthetic calibration and successful independent
synthetic validation.

---

## 18. Next methodological step

Design the synthetic sparse-probe calibration suite.

No new biological Experiment-04 activation may be computed before that
instrument is independently validated and this protocol is updated with the
frozen Arm B specification.
