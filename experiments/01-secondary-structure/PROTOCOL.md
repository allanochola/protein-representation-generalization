# Does secondary-structure information in ESM-2 representations generalize across proteins below 30% sequence identity?

*Preregistered. Frozen before any embedding is extracted or any probe is fit.*

Repository: `protein-representation-generalization` — a standalone project, the modality-transfer continuation of the bio-capability-probing work, kept separate from the scaling repository so its scientific question stands on its own and the scaling repo's five-experiment arc stays closed.

## Question and motivation

This is the modality-transfer step the bio-capability-probing work named as its central open question. There, internal representations that looked perfectly separable in-distribution collapsed out-of-distribution, leaving open whether the features were the target property or a memorization/shortcut. That was found in ordinary language models. The open empirical question is whether it persists in a protein foundation model.

This experiment tests the cleanest version. Take a known per-residue biological property — secondary structure — and ask whether a linear representation of it, read from a frozen ESM-2 model and trained on one set of proteins, survives a genuinely sequence-divergent test, or whether the apparent signal collapses once homologous shortcuts are removed. The scaling project established that protein-model performance depends on evolutionary context and architecture, and that signals should not be assumed to transfer uniformly; this asks the representation-level version of the same caution.

## What this is not

A positive result does **not** establish a function-relevant screening feature. Secondary structure is structural biology, not protein function. Linear probing is correlational: a representation that generalizes would *motivate* causal follow-up (activation patching, SAEs), not constitute it, and causal work is out of scope here — and premature if the representation does not even generalize under a linear read. The sequencing is deliberate: structure generalizes under divergence → then test a higher-level functional property → only then consider causal intervention.

## Design (frozen)

- **Model.** `esm2_t33_650M_UR50D`, a single checkpoint, weights frozen. No ladder — this is not the scaling question. T4-feasible.
- **Target.** Q3 secondary structure per residue: helix (H) / strand (E) / coil (C), from the standard DSSP 8→3 collapse.
- **Representation.** Per-residue hidden states (not mean-pooled — the target is per-residue) from a single layer, **layer 17 of 33**, fixed in advance because it is the architecture-defined middle, not an outcome-selected best. No layer search. Layer 17 is the sole representation this experiment evaluates; varying the layer is a separate follow-up only — run, if at all, after a clear result, never as a sweep to rescue a null.
- **Probe.** One linear probe: multinomial logistic regression on the frozen per-residue embeddings (1280-dim). No nonlinear head. The experiment is about the representation, not classifier engineering.
- **Baseline** (the control the earlier probing lacked). A sequence-local baseline: one-hot amino-acid identity in a fixed ±3-residue window (7 residues × 20 = 140 features), no ESM, same linear probe. Secondary structure carries strong local sequence signal, so without this baseline a generalizing ESM probe could not be distinguished from obvious local cues.
- **Split (load-bearing).** Cluster all proteins at ≤30% sequence identity (MMseqs2 `easy-cluster`, `--min-seq-id 0.3`) and split at the cluster level. From the **same frozen probe**, two evaluations:
  - **random-protein split** — in-distribution reference;
  - **30%-identity cluster-held-out split** — the divergent test.
  The quantity of interest is the generalization gap, not held-out accuracy alone.

## Primary quantities (preregistered, tied to baselines)

Let `Q3(model, split)` be per-residue Q3 accuracy — the **primary metric**. Alongside it, report **macro-F1** over the three classes as a frozen **secondary metric**: Q3 is class-imbalanced (coil and helix prevalence), so a probe can look better by exploiting prevalence; macro-F1 guards against that without multiplying hypotheses. Δ_ESM and G below are defined on the primary metric (accuracy); macro-F1 is reported for the same cells as a check, not as a separate decision axis.

- **Δ_ESM (divergent margin)** = `Q3(ESM, divergent) − Q3(local baseline, divergent)`. Does ESM carry structural information beyond local sequence cues on divergent proteins?
- **G (generalization gap)** = `Q3(ESM, random) − Q3(ESM, divergent)`. How much does ESM's structural signal degrade under divergence?

Both reported with **protein-cluster bootstrap CIs** — resample held-out clusters, not residues, because residues within a protein are not independent.

## Hypotheses and decision (frozen before any data)

| Verdict | Condition (preregistered bands) | Reading |
|---|---|---|
| **H_repr** | Δ_ESM(divergent) ≥ 0.08 **and** G ≤ 0.10 | ESM encodes divergence-robust structural information beyond local cues; the representation generalizes across families under a linear read. |
| **H_shortcut** | Δ_ESM(divergent) ≤ 0.03 **or** G ≥ 0.15 | Apparent separability leans on homologous/local regularities; ESM collapses toward the local baseline under divergence — the same pattern the LLM probes showed. |
| **Intermediate** | anything between | Mixed / unresolved; reported as such, not forced to either pole. |

The bands are relative to the baseline and to the random-split reference — not absolute-accuracy thresholds — and are fixed here, before any embedding is extracted. They are set once and not moved after seeing data.

**Technical kill criteria (not outcome).** Probe fits are finite and non-degenerate; Q3 labels align to sequence positions (verified on a held sample); the ESM random-split Q3 lands in a sane range for a linear probe on 650M embeddings (roughly 0.78–0.86 — a much lower value signals an extraction/alignment bug, not a result); the local baseline sits above the ~0.34 three-class chance rate. A technical failure halts before any interpretation. Cross-split accuracy ordering is never a kill criterion — a collapse under divergence is the result, not a bug.

## Data

**Dataset: TAPE secondary structure** — the supervised SS set, published directly (LMDB/JSON) with a documented download path — used only as the labeled protein source: sequences plus per-residue DSSP Q3. **The experiment does not inherit TAPE's train/test split.** The whole point is the divergence split, so the TAPE sequences are pooled and cleaned, then reclustered here at 30% identity to generate both the random-protein split and the cluster-held-out split from the same pool. Pin the TAPE dataset version, the MMseqs2 version, and the ESM revision in provenance.

## Outputs

- `experiments/01-secondary-structure/PROTOCOL.md` — this file, frozen first
- `src/extract_esm2.py`, `src/clustering.py`, `src/probe.py` — extraction, 30% clustering, and the unit-tested metrics/split/bootstrap utilities
- `notebooks/extract_embeddings.py` — cache ESM-2 layer-17 per-residue embeddings + labels + cluster ids
- `notebooks/probe_and_evaluate.py` — linear probe + local baseline; random and cluster-held-out evals; Δ_ESM and G with cluster bootstrap
- `results/ss_generalization.csv`, `results/ss_summary.json`, `results/provenance.json` — per-cell Q3/macro-F1, the two quantities with CIs, and run provenance (ESM revision, TAPE version, MMseqs2 version, layer, seed, split sizes)
- `experiments/01-secondary-structure/results.md` — the written outcome and verdict

## Sequence of work (frozen)

Freeze this protocol → extract embeddings and build the 30% cluster split → fit the probe and the local baseline on the random-split training data → evaluate both splits with the same frozen probe → compute Δ_ESM and G with cluster bootstrap → interpret against the frozen bands. No probe accuracy is interpreted before the split and the baseline both exist.
