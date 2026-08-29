# Experiment 02 — Catalytic-residue information in ESM-2 under a 30%-identity family holdout

**Status:** CLOSED PRE-DATA — DRAFT v0.4 never reached v1.0 freeze. Pre-data precision analysis found the planned configuration insufficiently sensitive to the required retention criterion; see `PRE_DATA_PRECISION.md`, `IMPLEMENTATION_NOTES.md`, and `results.md`. No confirmatory catalytic-residue label, ESM embedding, probe result, or test-split result was inspected.

**Repository:** `protein-representation-generalization`
**Predecessor:** `experiments/01-secondary-structure/` (closed, verdict H_repr, Zenodo DOI 10.5281/zenodo.22134890)

---

## 0. Claim boundaries

Four statements govern everything below. They appear in this protocol, in `results.md`, and in the abstract of any write-up.

> **Only manually curated M-CSA catalytic annotations constitute positive labels.**
>
> **M-CSA homology-transferred catalytic annotations are excluded from confirmatory labeling.**
>
> **Unannotated residues within curated reference enzymes are operational benchmark negatives, not claims of experimentally established non-catalytic function.**
>
> **No confirmatory random-test or divergent-test probe performance is inspected before the protocol, label policy, split algorithm, metrics, and decision rule are frozen.**

The object of study is *linearly accessible catalytic-residue information*, not catalytic-site prediction. A linear probe demonstrates accessible correlational information in a fixed representation. It does not identify catalytic machinery, and no result here is described as if it did.

## 1. Question

Does linearly accessible catalytic-residue information in ESM-2 650M layer 17 generalize to enzyme families held out at 30% sequence identity, beyond information recoverable from a ±3-residue amino-acid window?

## 2. What Experiment 01 established, and what it did not

Experiment 01 asked the same question for secondary structure and returned H_repr: ESM beat the ±3 local baseline by +0.155 Q3 on the divergent split, with G = +0.003.

Experiment 01's local baseline degraded by only ~0.0001 across the family holdout. That result did not establish that the holdout lacked biological divergence: a seven-residue window can itself encode family-correlated local motifs, and can therefore degrade under a family holdout for reasons beyond amino-acid composition shift. The deeper problem was that Experiment 01 contained no positive control demonstrating that a family-dependent shortcut was actually available and disrupted by the divergent split. Consequently G ≈ 0 could not distinguish representation robustness from a task for which that particular holdout removed little exploitable predictive information.

Two additions close this.

1. A **homology-transfer arm** (§8, arm C), promoted to a validity gate (§9.5), tests directly whether explicit sequence homology to training proteins enables catalytic-label transfer in-distribution and stops doing so under the holdout.
2. **Retention** (§9.3) separates representation-specific degradation from degradation shared with the local comparator, which is dataset shift rather than representation failure.

## 3. Why catalytic residues are the next stress test

Secondary structure is a local backbone property with near-universal sequence determinants. Catalytic residues are rare and functionally defined. Their amino-acid *composition* is universal — His, Asp, Glu, Cys, Lys, Ser, Arg, Tyr are enriched everywhere — but *which* His in a protein is catalytic is not recoverable from composition. The gap between composition and discrimination is what this experiment probes.

## 4. Outcomes

- **H_repr** — catalytic-residue information transfers across family boundaries. ESM's advantage over the local baseline on the divergent split is large, and most of that advantage survives the family holdout.
- **H_shortcut** — apparent accessibility depends on family-specific structure. The advantage is small on the divergent split, or most of it is lost crossing the holdout.
- **Mixed / unresolved** — neither rule fires.
- **No verdict — null instrument** — Gate V1 fails (§9.5).
- **Generalization unresolved** — Gate V2 fails or is unresolved on prevalence corroboration (§9.5), or the retention prevalence-divergence concordance check fails (§9.3). The advantage result is still reported; the generalization component is not.
- **No verdict — signal below floor** — ESM does not clear five times prevalence on the divergent split (§9.4).
- **No verdict — underpowered** — the curated pool cannot support inference (§11).

## 5. Data

### 5.1 Source (frozen)

Manually curated M-CSA entries only, from the public API:

- Enzyme-level entries: `https://www.ebi.ac.uk/thornton-srv/m-csa/api/entries/?format=json`
- Manually curated catalytic residues: `https://www.ebi.ac.uk/thornton-srv/m-csa/api/residues/?format=json`

M-CSA held 1,003 hand-curated entries as of 12 August 2026. Reference UniProt sequences are pulled at the accession and version recorded in the entry.

`homologues_residues.json` is **not used for labels under any condition**, including as a power fallback. EBI states that it includes all Swiss-Prot and PDB homologues without regard to residue conservation or function, so an annotated residue in a homologue may perform a different catalytic function or none. Transferred labels are also not independent of the reference entry they derive from, which would contaminate a family holdout in a way sequence identity does not detect. If the curated pool is underpowered, the experiment reports that (§11); it does not substitute weaker labels.

The homologue file may be used *outside* the confirmatory analysis for descriptive statistics only, clearly labelled, with no decision weight.

### 5.2 Unit of sampling and eligibility

- Unit of biological sampling: curated M-CSA reference enzyme sequence.
- Every protein carries at least one curated catalytic residue. Proteins absent from M-CSA are **not** admitted as all-negative proteins; absence from M-CSA is not evidence of lacking catalytic residues.

### 5.3 Sequence reconciliation and exclusion (frozen order)

1. Deduplicate at 100% sequence identity; keep the earliest M-CSA entry ID and merge label sets.
2. Deduplicate on UniProt accession.
3. Drop sequences containing non-standard residues (`B`, `J`, `O`, `U`, `X`, `Z`).
4. Drop sequences shorter than 50 residues.
5. **Exclude sequences longer than 1,022 residues.** Report proteins, residues, and catalytic positives removed. Chunking is rejected: it would introduce a representation-extraction procedure Experiment 01 did not use, and would make residues near window boundaries depend on an arbitrary centrality rule. If exclusion alone causes K2 or K3 to fail, the experiment reports underpowered. The extraction procedure is not redesigned after seeing how many long proteins there are.
6. **Single-chain reference entries only.** Multi-chain catalytic mechanisms create incomplete biological context in what is this project's first functional target. Report the entry count and catalytic-residue count this costs.

### 5.4 Mapping validation (hard gate)

M-CSA gives residue positions in both PDB and UniProt numbering. Off-by-one and insertion-code errors are the primary practical failure mode for this dataset. For every curated catalytic residue:

    assert sequence[resid - 1] == three_to_one(residue_code)

A single mismatch drops the whole protein, logged with M-CSA ID and position. Drop count and drop rate go in `results.md`. This mirrors the TAPE schema and label-length asserts that caught alignment problems in Experiment 01.

## 6. Labels

**Positive:** a residue manually curated as catalytic in its M-CSA reference entry.

**Operational negative:** every other eligible residue in the same curated enzyme. No buffer zone around positives — adjacent residues are genuinely non-catalytic and are the hardest, most informative negatives.

Negatives are **not sampled**, at evaluation or at training. Imposing a sampled prevalence changes the task and makes AP a function of the sampling ratio rather than of the data. Class imbalance is handled in the loss (§8).

Prevalence π = N_positive / N_residues is reported per split, per protein-length decile, and per amino-acid type, before any metric is interpreted.

## 7. Splits

### 7.1 Clustering

MMseqs2 `easy-cluster` at 30% sequence identity, same coverage and mode parameters as Experiment 01, rebuilt from scratch on this pool. Experiment 01 cluster IDs carry no meaning here.

Proportions follow Experiment 01: train ≈ 68%, random test ≈ 12%, divergent test ≈ 20%. The two test splits are constructed at different levels, so the order of operations is specified exactly rather than left to "allocated at cluster level."

**Split algorithm (frozen, seed 0):**

1. Sort clusters by canonical cluster ID. This makes the starting order independent of MMseqs2 output ordering.
2. Shuffle the sorted cluster list with seed 0.
3. Walking that shuffled list in order, assign **whole clusters** to the divergent test until the accumulated protein count first reaches or exceeds 20% of the pool. Clusters are never split across this boundary.
4. All remaining clusters form the residual pool.
5. Shuffle the residual pool's **proteins** with seed 0 and assign the first 15% of them to the random test; the rest become train.
6. Run the §7.2 audits.

Steps 3 and 5 operate at different granularities on purpose:

- **divergent test** — whole clusters held out at step 3. Zero cluster overlap with train or random by construction. The load-bearing split.
- **random test** — proteins drawn at step 5 from the same clusters train draws from. Cluster overlap with train is therefore expected, not leakage: this split is the in-distribution reference point and would stop being one if its clusters were held out. Experiment 01 produced 48 such shared clusters, holding different proteins on each side, and its audit confirmed zero protein overlap.

The expected audit signature is: train ∩ divergent = 0 clusters, random ∩ divergent = 0 clusters, train ∩ random > 0 clusters, and zero protein overlap on all three pairs.

### 7.2 Leakage audits (all must pass before evaluation)

1. Zero cluster overlap between train and divergent test.
2. Zero exact-sequence duplication across any split pair.
3. Zero UniProt accession duplication across any split pair.
4. Zero M-CSA entry ID appearing in more than one split.
5. Cluster union equals total; any naive double-count reconciled explicitly, as in Experiment 01's 48-cluster audit.

### 7.3 EC numbers: reported, not split on

Four-level EC overlap between train and the divergent test is **reported as a descriptive audit** and is **not** used to constrain splits.

A held-out protein may catalyse the same reaction as something in training. That is not leakage. The claim is generalization across sequence families, not across biochemical functions, and forcing an EC holdout would confound two distinct generalization questions in one experiment. Whether the representation generalizes to unseen biochemical function is a separate experiment.

An EC-disjoint subset analysis, if run, is exploratory, carries no decision weight, and does not produce a second verdict.

## 8. Arms

All arms train on the same clusters, evaluate on the same two splits, and score through the same code path.

| Arm | Features | Role |
|---|---|---|
| **A — central AA identity** | one-hot of the residue's own amino acid (20 dims) | Diagnostic floor and reference for Gate V1. Quantifies how much of the task is catalytic amino-acid enrichment alone. |
| **B — local ±3** | one-hot 7-residue window, terminal padding as a 21st symbol (147 dims) | The Experiment 01-comparable local baseline. The comparator in every decision quantity. |
| **C — homology transfer** | see §8.1 | Positive control for exploitable homology. Not a learned probe. |
| **D — ESM-2** | per-residue hidden state, `esm2_t33_650M_UR50D`, layer 17/33, fixed | The arm under test. |

The A → B → D hierarchy reads as: central residue identity → local motif context → learned representation. It tells you whether B's performance comes from motif structure or almost entirely from A's enrichment effect, for negligible extra compute.

Arms A, B, D are linear logistic probes: Adam, learning rate 1e-3, batch 4096, seed 0, class-weighted loss on the full negative set, epoch count fixed at freeze from train-internal CV (§10). Standardisation fit on train only and checkpointed.

Layer 17 is inherited from Experiment 01 for comparability and is not optimised. Catalytic information may peak elsewhere in the stack. Every ESM result is a lower bound on what the representation contains, and the write-up says so.

### 8.1 Arm C definition (frozen before any test evaluation)

For each test protein, MMseqs2 `search` runs against the **training pool only**, at sensitivity, coverage, E-value, and `--max-seqs` settings frozen in `src/homology_transfer.py`. The `--max-seqs` cap keeps "all qualifying hits" tractable and is part of the frozen configuration.

Scoring is **best residue-level evidence across all qualifying hits**, not best global hit. For test residue i:

    C_i = max over (h, j) of  q(h) · 1[i aligned to j] · 1[j is curated catalytic in h]

where h ranges over qualifying training hits, j over that hit's residues, and q(h) is the hit's **normalized alignment score** — bit score divided by alignment length. Residues with no supporting alignment column, residues aligned to gaps, and every residue of a protein with no qualifying hit receive zero. Ties in the max are broken by lowest training-pool protein index, which is deterministic given the frozen split.

Best-global-hit selection is rejected because it is brittle in exactly the case that matters: a hit with the highest overall score may align poorly through the catalytic site while a lower-scoring hit aligns directly through a conserved catalytic motif. Arm C would then miss homology that genuinely exists. Because Gate V2 determines whether retention may be interpreted at all, Arm C is deliberately made strong at the one thing it measures — whether explicit sequence homology to training examples can solve this task.

Normalized rather than raw bit score, because raw bit score grows with alignment length and would rank long homologues above better-matched short ones for reasons unrelated to transfer quality.

This construct is **exploitable sequence homology to the training pool**, not "family shortcut" in the abstract. That is the precise thing the divergent split is supposed to remove, and the precise thing Experiment 01 never verified was removable.

**Tie handling.** Max-over-hits aggregation makes q(h) vary residue by residue, which substantially reduces the tie structure that best-global-hit scoring would have produced. Ties remain possible, including the block of unsupported residues at zero. AP is computed by stepping through unique score thresholds, with all residues at a given score treated as a single block — never by breaking ties randomly or by input order. The same convention applies to all arms and is asserted against a hand-computed tied example in the probe self-test.

## 9. Metrics, gates, and decision rule

**Primary metric:** average precision (AUPRC), reported alongside π so a reader can see immediately whether AP exceeds the random-ranking baseline.
**Secondary:** AUROC, for every arm and split.
**Diagnostic:** per-protein top-n recall, where n is that protein's true catalytic-residue count — always defined, robust to imbalance and prevalence shift. Recall at precision ≥ 0.50 is added only if the train-internal CV pass shows that precision is reachable; otherwise it is undefined and omitted.

AP is not prevalence-normalized. Normalized AP is descriptively useful but is an unfamiliar inferential object whose behaviour across held-out families is harder to reason about. Raw AP plus π is more transparent. AP values here do not share a scale with Experiment 01's Q3 and are never compared numerically to it.

### 9.1 Advantage

    Δ_div  = AP(D, divergent) − AP(B, divergent)
    Δ_rand = AP(D, random)    − AP(B, random)
    ratio  = AP(D, divergent) / AP(B, divergent)

### 9.2 Family-shift degradation (reported)

    G_ESM    = AP(D, random) − AP(D, divergent)
    G_local  = AP(B, random) − AP(B, divergent)
    G_excess = G_ESM − G_local

All three are reported. G_excess is not itself a decision quantity, because absolute AP differences have no fixed scale across prevalence regimes.

### 9.3 Retention (decision quantity)

    R = Δ_div / Δ_rand

Note the identity: `Δ_rand − Δ_div = G_excess` exactly, so `R = 1 − G_excess / Δ_rand`. Retention is G_excess expressed as a fraction of the in-distribution advantage, which makes it scale-free and directly interpretable as the share of ESM's edge over local sequence that survives the family holdout.

**Prevalence comparability.** R compares AP differences across two splits whose prevalence need not match. An affine chance correction of the form `E = (AP − π)/(1 − π)` is not an adequate answer: it yields `R* = R × (1 − π_rand)/(1 − π_div)`, which at π ≈ 0.01 in both splits differs from R by well under one percent, while AP's actual dependence on prevalence is nonlinear across the whole precision-recall curve. The transform looks like a correction and is close to an identity.

Two safeguards are used instead.

1. **Prevalence divergence check.** π_div and π_rand are compared directly. If `|π_div − π_rand| / π_rand > 0.25`, the retention result must agree in sign and in pass/fail with the AUROC-based equivalent, computed as `R_AUROC = [AUROC(D,div) − AUROC(B,div)] / [AUROC(D,rand) − AUROC(B,rand)]`. AUROC is exactly prevalence-invariant, so this tests the thing the affine transform only appears to test. Disagreement → **generalization unresolved**, with the prevalence gap reported as the reason.
2. **Definition selection is preregistered to the simulation.** §11 compares R against R* on synthetic rankings at varying π with ranking quality held fixed. If the two diverge by more than 5% under realistic prevalence shift, R* becomes the primary retention statistic and R the secondary. Otherwise R stays primary. The rule is committed before the simulation runs; neither definition is chosen after seeing real data.

AUROC-based G_ESM and G_local are computed as frozen secondaries regardless, and AP-vs-AUROC disagreement is reported wherever it occurs.

### 9.4 Inference on ratios

`ratio` and `R` are bootstrapped on the log scale, with numerator and denominator resampled within the same replicate so intervals are paired. Preconditions:

- `AP(D, divergent) ≥ 5 × π_divergent` is required before the advantage criterion is evaluated at all. Without it, a ratio can pass on two systems that both sit barely above random ranking — AP_B = 0.015 against AP_D = 0.035 at π = 0.01 gives a ratio of 2.33 on an absolute gain of 0.02. Failure → **no verdict — signal below floor**.
- `ratio` is evaluated only if `AP(B, divergent) > π_divergent`. If the local comparator does not beat random ranking, the ratio is reported but flagged as unstable and the advantage criterion rests on its absolute disjunct alone (§9.6).
- `R` is evaluated only if `CI_low(Δ_rand) > 0`. If ESM holds no in-distribution advantage over local sequence, retention is undefined and the outcome is **no verdict — null instrument**.

### 9.5 Gates

**Gate V1 — probe instrument** (random split only, computed first):

    AP(D, random) ≥ 2.0 × AP(A, random)

Failure → **NO VERDICT — NULL INSTRUMENT**. Stop. Report observed values. A fixed-layer linear probe that cannot detect catalytic residues in-distribution says nothing about generalization. Experiment 01's band structure, applied unchanged, would have labelled that outcome H_shortcut — a false conclusion from an instrument that never worked.

**Gate V2 — exploitable homology** (arm C only, both splits, computed second). Both parts must hold:

    (a) AP(C, random) ≥ 5 × π_random
    (b) CI_high( AP(C, divergent) / AP(C, random) ) < 0.50

Part (a) checks that homology transfer works at all in-distribution. Part (b) checks that the divergent split materially disrupts it.

**Prevalence corroboration.** Part (b) is itself a cross-split AP comparison and is therefore exposed to the same prevalence sensitivity as retention (§9.3). The same trigger applies: if `|π_div − π_rand| / π_rand > 0.25`, the arm C collapse must be corroborated in direction by the already-reported AUROC — `AUROC(C, divergent) < AUROC(C, random)`. AUROC is exactly prevalence-invariant, so this distinguishes a real loss of exploitable homology from an AP shift driven by prevalence. If the trigger fires and AUROC does not corroborate, **V2 is unresolved** and the outcome is generalization unresolved. This adds no statistic and no change to arm C; it applies the §9.3 philosophy consistently to the positive control.

Failure → **GENERALIZATION UNRESOLVED**. The advantage criterion below is still evaluated and reported; the retention criterion is not, and no H_repr / H_shortcut verdict is issued. Arm C involves no learned parameters, so computing it on the divergent split before the verdict creates nothing to tune.

This is deliberately weaker than voiding the whole experiment. `ratio` is a within-split comparison on the divergent set and does not depend on the holdout having teeth — it remains a valid finding that ESM adds information beyond local sequence on this test set. Discarding it because a different question turned out uninformative would throw away a sound result.

### 9.6 Verdict (evaluated only if V1 and V2 both pass, and the §9.4 preconditions hold)

- **Advantage criterion:** `CI_low(ratio) > 2.0` **or** `CI_low(Δ_div) > 10 × π_div`
- **Retention criterion:** `CI_low(R) > 0.75`

Rules:

- **H_repr** — advantage and retention both pass.
- **H_shortcut** — [`CI_high(ratio) ≤ 1.2` **and** `CI_high(Δ_div) ≤ 10 × π_div`] **or** `CI_high(R) ≤ 0.50`.
- **Mixed / unresolved** — otherwise.

The advantage criterion is disjunctive because a ratio alone is scale-blind in both directions. The floor precondition in §9.4 kills the case where a large ratio sits on trivial absolute signal. The absolute disjunct catches the opposite case: AP_B = 0.20 against AP_D = 0.35 gives a ratio of 1.75 and would fail a pure ratio test despite a 0.15 absolute gain that is plainly meaningful. Anchoring the absolute arm to π rather than to a free-standing AP value keeps it scale-appropriate without introducing a data-derived threshold — π is a property of the label set, not of any model's output.

The five constants are fixed here, before any data pull, and are **pre-specified judgment calls rather than derived quantities**. Their rationale: doubling AP over the local comparator is the smallest relative advantage worth calling representational; an absolute advantage of ten times prevalence is the smallest absolute advantage worth the same; below a 20% relative advantage on trivial absolute gain, ESM is effectively the local baseline; retaining three quarters of the in-distribution advantage is what "survives the holdout" should mean; losing more than half of it is a collapse. Stating them as judgment is more honest than manufacturing them from a calibration procedure that would make them an empirical quantile of the training data.

Ratio and π-anchored forms are used specifically to keep the decision rule independent of model output. Absolute AP thresholds cannot be specified in advance without knowing the AP scale, and deriving them from training-internal cross-validation would make the decision boundary endogenous to the very distribution whose generalization is under test.

Experiment 01's Q3-scale thresholds (0.08 / 0.03 / 0.10 / 0.15) are not carried over.

## 10. Calibration — what is set where

**Nothing in the decision rule is calibrated on data.** All thresholds in §9.5 and §9.6 are fixed above.

Train-internal cluster-fold cross-validation — 5 folds over training clusters — sets only:

- epoch count for arms A, B, D
- the class-weighting scheme

Both are optimization choices selected exclusively within training data. They affect probe performance, and therefore every decision quantity, but they are fixed before either test split is evaluated. That is the property that matters, not an implausible claim of no effect.

**Frozen sequence of work:**

1. Run the §11 precision simulation. Commit its output and the derived K2/K3.
2. Build and clean the labelled pool. Freeze sequences and labels.
3. Build clusters and splits. Run the §7.2 audits and the §11 precision gates.
4. Run the train-internal CV pass for epoch count and class weighting. Commit its outputs.
5. Commit this document as **v1.0 FROZEN**.
6. Evaluate arm A and arm D on `random_test`. Apply Gate V1.
7. Evaluate arm C on both splits. Apply Gate V2.
8. Only then evaluate arms B and D on `divergent_test` and compute the verdict.

Both commits are timestamped in repository history. The preregistration boundary claimed in any write-up is the v1.0 commit.

## 11. Precision floors, derived rather than assumed

Order-of-magnitude expectation from public M-CSA counts alone: ~1,000 entries, ~600–850 clusters at 30% identity, ~3,500 positives, ~350,000 residues, π ≈ 0.01. The divergent split would then hold ~170 clusters and ~700 positives.

K2 and K3 are **not** set by judgment. They are derived from a pre-data simulation using only publicly known M-CSA counts and no real labels, embeddings, or model outputs:

1. Generate synthetic clusters with a size distribution matching plausible M-CSA cluster sizes, at π ≈ 0.01.
2. Generate arm B and arm D score vectors from a parametric model tuned to produce a target `ratio` of exactly 2.0 and a target `R` of exactly 0.75 — the decision boundaries.
3. Run the §12 cluster bootstrap.
4. Sweep cluster count and divergent-positive count. Record the expected 95% CI half-width on `log(ratio)`.

**Precision criterion:** the minimum cluster count and divergent-positive count at which the expected 95% CI half-width on `log(ratio)` is at most `log(1.5)`.

These are **precision floors, not power floors**, and the section is named accordingly. A confidence interval centred on a true effect of exactly 2.0 will generally have its lower bound below 2.0, so meeting K2 and K3 does not imply a high probability of passing `CI_low(ratio) > 2.0` when the true effect sits at the boundary. Precision floors make fewer assumptions than a power calculation, which would require nominating an alternative effect size. Below the floor, the planned inference cannot resolve the smallest effect this protocol defines as meaningful, and the correct report is underpowered rather than a weak verdict.

For context only, and attached to no gate, the simulation additionally reports `P(CI_low(ratio) > 2.0)` at alternatives `r_alt ∈ {2.5, 3.0}`. This is free once the simulation exists and tells a reader what the design can actually detect.

**Retention definition selection.** The same simulation compares `R = Δ_div / Δ_rand` against `R* = Δ*_div / Δ*_rand` with `Δ*_s = E(D,s) − E(B,s)` and `E(m,s) = [AP(m,s) − π_s] / (1 − π_s)`, on synthetic rankings at varying π with ranking quality held fixed. If the two diverge by more than 5% under realistic prevalence shift, R* becomes the primary retention statistic. Otherwise R stays primary. The rule is committed before the simulation runs.

The simulation depends on its score-generating assumption. That assumption is written into `src/power_sim.py` and committed before it runs, and K2/K3 are reported across a sensitivity range over the assumed cluster-size distribution and effect size, not as single numbers. The frozen floors are the most conservative values in that range.

Kill criteria, checked in order, before modelling:

- **K1 — mapping loss.** §5.4 drops more than 20% of entries → the pull is treated as broken and debugged, not accepted.
- **K2 — cluster count.** Below the simulated precision floor → **no verdict — underpowered**.
- **K3 — divergent positives.** Below the simulated precision floor → **no verdict — underpowered**.
- **K4 — bootstrap degeneracy.** More than 1% of replicates contain zero positives in an evaluated split → AP intervals for that split are reported as unreliable and per-protein top-n recall becomes the primary reported quantity there.

Closure by a preregistered rule is a valid endpoint, as with the Exp 05 Stage 3 runtime gate. An underpowered result is reported as underpowered; it is not rescued with homology-transferred labels.

## 12. Inference

Cluster-level bootstrap, 2,000 replicates, 95% percentile intervals, seed 0 — identical to Experiment 01. Resampling runs over precomputed per-cluster residue counts and precomputed predictions, not by reconstructing index arrays per draw. Experiment 01's 8-hour hang came from the latter; the optimised implementation runs in under 2 seconds and reproduced the original bootstrap exactly under identical predictions.

All arms are scored on the same resampled clusters within each replicate, so `ratio`, `R`, and `G_excess` intervals are paired rather than independent.

## 13. Preregistered predictions

Written before any data pull, checked in `results.md`, reported whether or not they hold. These are predictions, not decision rules — the decision rules are §9.5 and §9.6.

- **P1** — `AP(A, divergent) ≥ 5π`. Amino-acid identity alone is informative for catalytic residues.
- **P2** — `AP(B, divergent) < 2 × AP(A, divergent)`. The ±3 window adds little over the residue's own identity. This is the concrete form of "the local baseline is expected to be substantially less informative" for this target.
- **P3** — Gate V2 passes.
- **P4** — advantage criterion passes, and passes on the ratio disjunct rather than only the absolute one.
- **P5** — retention criterion passes.

## 14. Limitations, stated in advance

1. **Operational negatives.** Unannotated residues are benchmark negatives, not established non-catalytic residues. Operational label noise is shared across arms because every arm is evaluated against the same labels, but it need not affect their metrics equally. In particular, a model that ranks genuinely catalytic but unannotated residues highly may be penalized by the benchmark — so a stronger model can be scored lower for being right about something the annotation does not record.
2. **Whole-protein divergence, not domain independence.** The confirmatory divergence definition is whole-protein MMseqs2 identity, not structural-domain independence; remote homologous catalytic domains may remain across splits. Some M-CSA enzymes are multidomain and a 30%-identity full-sequence cluster can fail to recognise local domain-level homology. This is stated, not solved; adding a CATH-level holdout would turn Experiment 02 into three experiments.
3. **ESM-2 has seen these sequences.** UniRef50 pretraining covers essentially the whole pool. "Unseen family" means unseen by the probe, never unseen by the model.
4. **Single layer, single checkpoint.** No layer or model-size sweep. Results bound ESM-2 650M layer 17 only.
5. **Linear probes only.** A negative result bounds linear accessibility, not the presence of the information.
6. **Small pool, and biased small by exclusions.** Excluding sequences over 1,022 residues and multi-chain entries biases the pool toward small single-chain enzymes. Both costs are reported. Intervals will be substantially wider than Experiment 01's, and an unresolved verdict is a plausible and acceptable outcome.
7. **Decision constants are judgment.** The five constants in §9.4 and §9.6 are pre-specified, not derived. A reader who disagrees with them can recompute the verdict from the reported intervals, which is why `ratio` and `R` are reported with full intervals rather than only as pass/fail.

## 15. Deviations log

Any departure from frozen v1.0 is recorded here with date, reason, and the commit at which it was made, before the affected analysis runs. An unlogged deviation invalidates the preregistration claim.

## 16. Outputs

Committed alongside `results.md`, matching the Experiment 01 artifact set:

- `results/catalytic_generalization.csv` — per-arm, per-split metrics with intervals
- `results/catalytic_summary.json` — ratio, R, Δ_div, Δ_rand, G_ESM, G_local, G_excess, V1 and V2 outcomes, verdict
- `results/power_sim.json` — simulation output, sensitivity range, derived K2/K3, detection probabilities at r_alt, and the R-vs-R* comparison with the selected retention definition
- `results/provenance.json` — repository commit; M-CSA API retrieval timestamp and entry count; UniProt release; MMseqs2 version and database build hash; ESM-2 checkpoint hash; all seeds; counts at each cleaning stage; §7.2 audit results
