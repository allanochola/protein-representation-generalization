# Experiment 03 — Interpretable toxin-function signatures in ESM-2 under natural evolutionary divergence

**Status:** DRAFT — must be frozen before any ESM embedding, SAE activation, probe result, or confirmatory toxin statistic is inspected.

**Repository:** `protein-representation-generalization`

**Predecessors:**
- Experiment 01: secondary-structure representation generalization — H_repr.
- Experiment 02: catalytic-residue feasibility study — closed pre-data as underpowered.
- Tox-Prot preprotocol census: closed at commit `f18d8c5`; Gates A–D passed.

## 0. Claim boundary

This experiment asks whether an interpretable internal feature of a frozen protein language model can provide evidence about toxin function that:

1. survives natural evolutionary divergence;
2. is not reducible to simple sequence composition or toxin-family membership;
3. can be inspected mechanistically; and
4. can support contestation of a functional screening decision in disagreement cases.

A positive result does **not** establish robustness to deliberately engineered evasion and does **not** establish a production screening system.

## 1. Primary question

Can a model-derived toxin-relevant feature, nominated without using confirmatory labels, discriminate family-disjoint toxin proteins from sequence-clean family-aware non-toxin proteins beyond a strong model-blind sequence baseline?

## 2. North-star interpretation

The experiment is not a generic toxin-classification benchmark.

The object of study is whether representation-level evidence can support scrutiny of a functional classification when conventional sequence similarity or family membership is insufficient.

The experiment therefore requires three evidence layers:

1. **Representation evidence** — confirmatory performance beyond sequence-only controls.
2. **Mechanistic characterization** — what biological or representational property drives the validated feature.
3. **Contestability analysis** — what happens in cases where the feature disagrees with conventional sequence/family evidence.

## 3. Frozen census inputs

The Tox-Prot preprotocol census was closed before any Experiment 03 model statistic was observed.

### 3.1 Positive support

- cleaned Tox-Prot sequences: 7,534
- 30%-identity clusters: 1,215
- sequence-divergent clusters: 936
- usable divergent clusters after diagnostic burn: 796
- primary V2-B family-disjoint clusters: 180
- Gate A threshold: >=90
- Gate A: PASS
- stricter corpus-wide V2-B sensitivity: 108
- largest divergent Pfam family: PF03496, 0.9%
- Gate B threshold: <=25%
- Gate B: PASS

### 3.2 Negative support

Primary negative pool: family-aware.

- candidate family-aware negatives: 7,110
- retained after >=30% positive-overlap exclusion: 4,862
- permanently burned for Gate D: 742
- untouched confirmatory remainder: 4,120
- Gate C primary threshold: >=1,000 negatives at FPR 0.05
- Gate C secondary threshold: >=3,000 negatives at FPR 0.01
- Gate C primary: PASS
- Gate C secondary: PASS

Secondary robustness pool: phenotype-matched.

Background Swiss-Prot negatives are an easy diagnostic only.

### 3.3 Model-blind shortcut diagnostic

Primary Gate D pool: sequence-clean family-aware negatives.

Features:
- sequence length
- 20 amino-acid composition fractions

Diagnostic geometry:
- burned positive clusters: 187
- selected family-aware diagnostic negatives: 561

Results:
- logistic regression: AUROC 0.8468, AUPRC 0.7182
- random forest: AUROC 0.9494, AUPRC 0.9011

Frozen rejection rule:
- reject if AUROC > 0.95 OR AUPRC > 0.95

Gate D: PASS.

Interpretation boundary:

Gate D passing does not imply that sequence shortcuts are weak. The nonlinear sequence-only baseline is strong and sits close to the frozen rejection boundary. Experiment 03 therefore tests **incremental representation value**, not raw toxin discrimination.

## 4. Evaluation universe

### 4.1 Positive evaluation set

Primary positive universe:

- all 180 V2-B clusters from the frozen census;
- sequence-divergent under the frozen 30%-identity rule;
- family-disjoint under the frozen §4.3 reference-set definition;
- diagnostic-burn clusters excluded from confirmatory evaluation.

Length strata are reported descriptively and as sensitivity analyses. They do not redefine the primary positive universe after outcome inspection.

### 4.2 Negative evaluation set

Primary negative pool:

- sequence-clean family-aware negatives;
- all Step-06B overlap exclusions applied;
- Gate-D diagnostic-burn negatives permanently unavailable;
- 4,120 untouched candidates remain before final model-eligibility filtering.

Secondary robustness pool:

- phenotype-matched negatives.

Background negatives:
- descriptive easy-control only;
- no primary decision weight.

## 5. Model and representation

- Frozen protein model: `esm2_t33_650M_UR50D`.
- Weights frozen.
- No checkpoint sweep.
- No post-result layer sweep.
- Any representation layer, pooling rule, SAE source, SAE width, normalization rule, and latent-selection procedure must be frozen before confirmatory labels are inspected.

### 5.1 Sequence eligibility

ESM-2 sequence-length eligibility must be checked before any embedding is extracted.

The handling rule for sequences exceeding the model's frozen eligibility limit must be declared before model execution.

No post-result chunking rescue is permitted.

If eligibility filtering causes a frozen support gate to fail, the experiment reports that outcome rather than redesigning after seeing model statistics.

## 6. Discovery versus confirmatory separation

### 6.1 Discovery partition

Feature nomination may use only the designated discovery data.

The confirmatory V2-B positives and confirmatory family-aware negatives are unavailable during feature nomination.

No confirmatory AUROC, AUPRC, TPR, feature activation, probe score, or threshold result may be inspected during discovery.

### 6.2 Feature nomination

The nominated representation object may be:

- one SAE latent; or
- a small frozen feature set if the preregistered stability gate does not support a single feature.

Feature nomination may use discovery labels only under the frozen nomination rule.

Confirmatory labels may not influence:
- feature identity;
- feature sign;
- feature-set size;
- activation transformation;
- threshold;
- layer;
- pooling rule;
- classifier choice.

### 6.3 Stability gate

A pre-data stability rule must determine whether nomination supports:

1. a **single-feature claim**, or
2. a **small frozen feature-set claim**.

If the single-feature stability gate fails, the protocol must fall back to the predeclared feature-set procedure.

No new feature may be selected after confirmatory evaluation is visible.

## 7. Arms

All confirmatory arms evaluate the same untouched positive and negative units.

### Arm A — model-blind sequence baseline

Features:

- sequence length;
- 20 amino-acid composition fractions.

Classifier family and hyperparameters are frozen before confirmatory evaluation.

This is the load-bearing comparator because Gate D established substantial sequence-only discrimination.

### Arm B — representation feature

Frozen nominated SAE latent or frozen feature set.

No confirmatory feature selection.

### Arm C — sequence + representation

Secondary diagnostic.

Tests whether representation evidence adds information conditional on the model-blind sequence baseline.

It does not replace the primary Arm-B-versus-Arm-A comparison.

### Arm D — conventional homology/family evidence

Descriptive evidence only.

Used primarily in disagreement and contestability analysis.

## 8. Primary estimands

The primary claim concerns **incremental representation value**.

Raw ESM or SAE performance alone is not sufficient.

### 8.1 Primary operational estimand

`ΔTPR@FPR5 = TPR_repr@5%FPR − TPR_sequence@5%FPR`

Both TPRs are evaluated on the same untouched confirmatory units.

### 8.2 Secondary operational estimand

`ΔTPR@FPR1 = TPR_repr@1%FPR − TPR_sequence@1%FPR`

Reported because the census supports the 1% FPR negative requirement.

### 8.3 Secondary global estimand

`ΔAUROC = AUROC_repr − AUROC_sequence`

### 8.4 Combined-arm diagnostic

Report:

`ΔTPR_combined = TPR_sequence+repr − TPR_sequence`

at the same frozen FPR operating points.

This is secondary and does not redefine the primary representation claim.

## 9. Uncertainty and statistical unit

The positive biological sampling unit is the toxin cluster.

Confidence intervals must therefore resample positive clusters, not individual proteins as if independent.

Primary comparisons are paired:

- same positive clusters across arms;
- same negative confirmatory set across arms;
- same bootstrap draws across arms.

Negative resampling, if used, must be frozen in advance and preserve the paired arm comparison.

## 10. Decision rule

Exact numerical decision bands are frozen using the pre-data feasibility simulator before any confirmatory ESM/SAE statistic is observed.

Allowed outcomes:

### H_repr-functional

The representation feature provides material incremental value over the frozen sequence-only comparator under natural evolutionary divergence.

### H_sequence

The representation feature does not provide material incremental value over the frozen sequence-only comparator.

### Mixed / unresolved

The observed effect falls between the frozen decision bands.

### No verdict — unstable feature

The discovery stability gate fails and the predeclared fallback cannot support a stable frozen feature or feature set.

### No verdict — support failure

Final model-eligible positive or negative support fails a frozen feasibility gate.

### No verdict — technical failure

Embedding extraction, SAE loading, sequence eligibility, split integrity, or other predeclared technical requirements fail.

Decision bands are not moved after confirmatory results are visible.

## 11. Mechanistic characterization of validated features

Mechanistic characterization is required if the representation arm clears the confirmatory decision rule.

It does not alter the primary statistical verdict.

Required analyses include:

- activation localization along the protein sequence;
- highest-activation positive examples;
- highest-activation family-aware negative examples;
- activation distribution across positive toxin families;
- relationship to sequence length;
- relationship to cysteine composition and patterning;
- relationship to signal/propeptide regions where annotation exists;
- relationship to known toxin domains or functional annotations where available;
- whether activation is sharply localized or broadly distributed.

Allowed mechanistic outcomes:

1. **Biologically interpretable feature**
2. **Robust but mechanistically unresolved feature**
3. **Feature substantially explained by a known sequence/structural shortcut**

A mechanistic interpretation cannot rescue a failed confirmatory statistical result.

## 12. Contestability and disagreement analysis

The experiment includes a proof-of-concept contestability analysis.

Priority cases include:

1. low conventional homology/family evidence + low sequence-baseline score + high representation evidence;
2. high sequence-baseline score + low representation evidence;
3. representation activation on sequence-clean family-aware negatives;
4. biologically plausible toxins with weak representation evidence.

For each selected disagreement case, report:

- sequence-baseline evidence;
- representation evidence;
- conventional homology/family evidence;
- available biological annotation;
- location of relevant feature activation;
- what evidence supports the feature-derived interpretation;
- what additional evidence could overturn that interpretation.

No production screening threshold is claimed.

The purpose is to show whether representation-level evidence can be inspected, challenged, and revised rather than merely emitted as an opaque score.

## 13. Threat-model boundary

This experiment tests **natural evolutionary divergence**.

It does not establish robustness to deliberately engineered, function-preserving sequence modification designed to evade screening.

Success therefore supports:

> representation-level evidence can survive substantial natural departure from known toxin families.

It does not support:

> the method is robust to adversarial biological design.

Engineered divergence is reserved for a separate subsequent experiment.

## 14. Required pre-model freezes

Before any ESM embedding or SAE activation is computed, freeze:

1. ESM sequence-length eligibility rule;
2. final eligible positive and negative counts;
3. discovery/confirmatory partition algorithm;
4. SAE source and revision;
5. ESM layer and representation extraction rule;
6. feature activation aggregation rule;
7. feature nomination procedure;
8. single-feature stability gate;
9. feature-set fallback rule;
10. sequence-baseline classifier;
11. representation-arm scoring rule;
12. FPR threshold-estimation procedure;
13. bootstrap procedure;
14. exact numerical decision bands.

## 15. Sequence of work

Freeze protocol draft
→ run model-blind eligibility and feasibility checks
→ freeze exact decision bands
→ freeze discovery/confirmatory partition
→ freeze SAE/model extraction configuration
→ commit protocol v1.0
→ extract frozen representations
→ nominate feature using discovery data only
→ freeze feature or feature set
→ run confirmatory evaluation once
→ apply frozen decision rule
→ perform mechanistic characterization
→ perform contestability/disagreement analysis
→ report without changing the confirmatory claim.

## 16. Outputs

- `experiments/03-toxin-representation/PROTOCOL.md`
- `experiments/03-toxin-representation/protocol_feasibility_check.py`
- `experiments/03-toxin-representation/code/01_load_data.py`
- `experiments/03-toxin-representation/code/02_prepare_embeddings.py`
- `experiments/03-toxin-representation/code/03_select_feature.py`
- `experiments/03-toxin-representation/code/04_evaluate_feature.py`
- `experiments/03-toxin-representation/code/05_characterize_feature.py`
- `experiments/03-toxin-representation/code/06_contestability_analysis.py`
- `experiments/03-toxin-representation/code/07_report_results.py`
- `experiments/03-toxin-representation/results.md`

No confirmatory result is interpreted before the protocol reaches frozen v1.0.
