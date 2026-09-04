# Experiment 04 — Arm-B Phase-P Biological Probing Inheritance Contract

## Status

**PROSPECTIVE — FROZEN BEFORE PHASE-P BIOLOGICAL RUNNER IMPLEMENTATION,
BEFORE BIOLOGICAL PERTURBATION-SEED AUTHORIZATION, AND BEFORE ANY
EXPERIMENT-04 BIOLOGICAL PROBE FIT.**

Phase E is complete and frozen.

Phase P biological probing remains closed at the time this contract is
written.

This contract freezes which corrected synthetic-calibration mechanics will
be inherited by the exploratory biological Arm-B runner. It does not open a
biological perturbation namespace and does not authorize biological probe
execution.

---

## 1. Authoritative corrected mechanics source

The authoritative corrected Arm-B mechanics source is:

`experiments/04-depth-and-basis/diagnose_arm_b_post_failure_architecture.py`

SHA-256:

`a15420b8a7528eeae9d2d7faf811ccbd19708793fe2e3562306c64c1b377166d`

The later S7-v2 diagnostic:

`experiments/04-depth-and-basis/diagnose_s7_step4b.py`

SHA-256:

`59c54c26d0c8a28d7c3842e611fa1f594934a3f9beb46d30b81d8c112e15017b`

was audited as an implementation-level cross-check.

The following core functions were byte-identical between the corrected
architecture diagnostic and the later S7-v2 diagnostic:

- `seedsequence_to_uint32`
- `dataset_seedsequence`
- `runner_seedsequence`
- `master_tau_index`
- `make_probe`
- `fit_probe_or_fail`
- `select_target_n`
- `stage_a_split`
- `select_C_R2`
- `select_stability_subsample`

`run_one_perturbation` was not byte-identical because the later S7-v2
diagnostic contains S7-specific seed-firewall and namespace logic.

Phase P inherits the corrected probe mechanics, not the synthetic
scenario/tau/rho machinery and not any consumed calibration seed namespace.

---

## 2. Biological discovery universe

Phase P may consume only the frozen Experiment-03 discovery universe:

- 139 toxin-positive proteins;
- 139 family-aware negative proteins;
- exact frozen realized target sizes N = 100, 120, 139 per class.

The frozen Phase-E row manifest is authoritative for biological row identity
and order.

Confirmatory proteins are prohibited from all Phase-P computation,
including:

- perturbation construction;
- regularization selection;
- fitting;
- stability analysis;
- AUROC computation;
- support computation;
- troubleshooting;
- exploratory inspection;
- threshold construction.

No confirmatory example may be loaded into the Phase-P runner.

---

## 3. Frozen Phase-E representation inputs

Phase P consumes immutable Phase-E raw-ESM matrices only.

Frozen layers:

`1, 9, 18, 24, 30, 33`

Each matrix has:

- 278 rows;
- 1280 raw ESM coordinates;
- NumPy float32 archive dtype;
- identical frozen row order.

Phase P must not recompute ESM representations.

Phase P must not alter:

- model identity;
- model revision;
- layer semantics;
- biological-residue slicing;
- coordinate-wise residue max pooling;
- dtype;
- row membership;
- row order.

Layer 18 remains the Experiment-03 protocol-designated anchor layer.

Layers 1, 9, 24, 30, and 33 are fresh Experiment-04 representation layers.

There is no post-hoc best-layer selection.

---

## 4. Frozen simple-sequence baseline

The biological comparison includes the prospectively frozen
21-dimensional simple-sequence baseline:

1. full biological sequence length;
2. fraction of A;
3. fraction of C;
4. fraction of D;
5. fraction of E;
6. fraction of F;
7. fraction of G;
8. fraction of H;
9. fraction of I;
10. fraction of K;
11. fraction of L;
12. fraction of M;
13. fraction of N;
14. fraction of P;
15. fraction of Q;
16. fraction of R;
17. fraction of S;
18. fraction of T;
19. fraction of V;
20. fraction of W;
21. fraction of Y.

Canonical amino-acid fractions use the full biological sequence length as
their denominator.

The one previously identified non-canonical `X` residue is not a 22nd
feature and does not trigger sequence modification, exclusion, or imputation.

The baseline uses the same frozen biological memberships and perturbation
identity as the corresponding raw-ESM comparison wherever applicable.

The baseline does not establish removal of all possible sequence
confounding.

---

## 5. Target-N selection

For each biological perturbation and representation:

- select exactly N positive observations;
- select exactly N negative observations;
- selection is without replacement;
- N is one of 100, 120, 139.

At N = 139, the complete 139-positive / 139-negative discovery universe is
retained.

At N = 100 and N = 120, target-N membership is generated from the
prospectively frozen biological perturbation stream once that stream has
been separately authorized.

No membership may be selected in response to biological performance.

---

## 6. Stage-A split

Within each selected target-N pool, Stage A uses the inherited deterministic
class-stratified exact-count 80/20 split.

The split is generated from a dedicated perturbation stream.

The training and held-out evaluation observations are disjoint.

The same target-N membership underlies the raw-ESM and simple-sequence
baseline comparison for a given perturbation identity.

---

## 7. Probe family

The inherited probe is:

`sklearn.linear_model.LogisticRegression`

with exactly:

- `penalty="l1"`
- `solver="liblinear"`
- `fit_intercept=True`
- `max_iter=10000`
- `tol=1e-6`
- deterministic integer `random_state` derived from the frozen perturbation
  seed construction.

No alternative classifier is introduced.

No elastic-net probe is introduced.

No L2 probe is introduced.

No nonlinear probe is introduced.

---

## 8. Feature transformation

No feature standardization, z-scoring, normalization, whitening, PCA, or
other learned feature transformation is introduced by Phase P.

The raw-ESM probe consumes the frozen 1280-dimensional Phase-E vectors as
archived.

The simple-sequence baseline consumes its frozen 21-dimensional feature
vectors directly.

This preserves the calibrated probe mechanics rather than introducing a new
preprocessing stage after biological representations are available.

---

## 9. Frozen C grid

The regularization grid is exactly:

`1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0`

The grid is ascending.

It must not be expanded, narrowed, shifted, or otherwise altered in response
to biological outcomes.

---

## 10. Stage-A cross-validation and R2 C selection

Stage-A regularization selection inherits the corrected R2 rule exactly:

- five-fold stratified cross-validation;
- folds are shuffled using the dedicated CV random state;
- the same five folds are used for every C;
- fold score is held-out AUROC computed from `decision_function`;
- mean score is the arithmetic mean of the five fold AUROCs;
- standard deviation uses `ddof=1`;
- standard error is `sd / sqrt(5)`;
- best C is the C with largest mean CV AUROC;
- an exact tie in best mean selects the smallest C;
- one-SE floor is:

  `best_mean - SE(best C)`

- selected C is the smallest C whose mean CV AUROC is at least the one-SE
  floor.

Because the C grid is ascending, this selects the strongest L1
regularization among one-SE-admissible C values.

No biological outcome may alter this rule.

---

## 11. Stage-A held-out AUROC

After C selection, Stage A refits the selected-C probe on the complete
Stage-A training subset using its dedicated final-fit random state.

The Stage-A held-out AUROC is computed on the untouched Stage-A evaluation
subset from the model's `decision_function`.

This is the per-perturbation predictive-accessibility quantity.

It is exploratory/descriptive, not confirmatory.

No biological AUROC threshold is introduced.

---

## 12. Stage-B full-target-N refit

After Stage-A C selection, Stage B fits a new selected-C L1 logistic probe
on the complete target-N pool.

The Stage-B refit uses a dedicated random-state stream distinct from:

- target-N membership;
- Stage-A split;
- CV construction;
- Stage-A CV fits;
- Stage-A final fit;
- stability membership;
- stability fit.

Stage-B coefficients are used for full-target-N support quantities.

---

## 13. Exact support semantics

For Stage-B coefficients `beta`:

`selected = beta != 0.0`

defines selected coordinates.

No epsilon threshold is introduced.

No coefficient-magnitude cutoff is introduced.

Unsigned support is the tuple of selected coordinate indices.

Signed support is the tuple:

`(coordinate_index, +1)` for positive nonzero coefficients;

`(coordinate_index, -1)` for negative nonzero coefficients.

These semantics are inherited exactly from the corrected calibration
mechanics.

---

## 14. Independent 80%-within-target-N stability refit

For every perturbation, an independent observation-level stability sample is
drawn from the already-selected target-N pool.

Per class:

`floor(0.80 * N)`

observations are selected without replacement.

Therefore the frozen per-class stability sizes are:

- N=100 -> 80;
- N=120 -> 96;
- N=139 -> 111.

The stability membership stream is distinct from the Stage-A split stream.

The stability refit uses:

- the same selected C chosen by Stage A;
- only the independently selected stability observations;
- its own dedicated fit random state.

Stability support and stability signed support use the same exact-zero
coefficient semantics as Stage B.

This corrected independent observation-level stability refit is essential:
Phase P must not revert to the earlier architecture in which the N=139
stability limb could collapse onto repeated fits of identical observations.

---

## 15. Convergence handling

Any sklearn fit exception is a perturbation-level instrument fit failure.

Any `sklearn.exceptions.ConvergenceWarning` emitted during a fit is also
treated as a fit failure.

Phase P must not:

- silently ignore convergence warnings;
- increase `max_iter` after observing biological results;
- change solver after observing biological results;
- alter tolerance after observing biological results;
- substitute a different C after a failed fit.

The inherited settings remain:

- `max_iter=10000`;
- `tol=1e-6`.

---

## 16. Paired raw-ESM minus baseline comparison

For each matched perturbation identity:

`delta_AUROC_t = AUROC_raw_ESM_t - AUROC_sequence_baseline_t`

The raw-ESM and baseline AUROCs must therefore use the same:

- target N;
- target-N biological membership;
- Stage-A split membership;
- perturbation identity.

The paired delta distribution is descriptive.

Permitted summaries include its median and spread.

No significance threshold, biological PASS/FAIL boundary, or new gate is
introduced.

---

## 17. Six-layer depth profile

All six frozen raw-ESM layers are evaluated:

`1, 9, 18, 24, 30, 33`

Layer results are reported as a depth profile.

No layer may be selected post hoc as the sole reported biological result.

Layer 18 may be described as the Experiment-03 protocol-designated anchor
layer.

The experiment does not support claiming that the Experiment-04 layer-18
raw vector was generated by an implementation proven byte-identical to the
unavailable historical Experiment-03 full-discovery raw extractor.

---

## 18. Scoped label-permutation null

The prospectively scoped biological label-permutation null remains limited
to:

- layer 18 only;
- N=139 only;
- 100 perturbations;
- frozen representation matrix unchanged;
- biological labels permuted;
- corrected Arm-B probe machinery retained where applicable.

Its purpose is contextualization of support behavior under the real
anisotropic/correlated ESM representation geometry.

It may contextualize:

- support size;
- recurrence;
- related unsigned-support stability quantities.

It does not create a biological threshold.

It does not replace the failed S7-v2 strong signed-instability criterion.

It does not select a layer.

It does not tune C.

It does not redefine the scientific question.

The exact permutation seed authorization remains prospective and separate
from this inheritance contract.

---

## 19. Signed-support interpretation boundary

S7-v2 failed its frozen stronger signed-instability calibration criterion.

Therefore biological signed-support and coefficient-orientation behavior
remain descriptive and calibration-limited.

A biological signed-support pattern cannot be promoted into a validated
PASS/FAIL gate.

The failed S7-v2 thresholds must not be lowered, reinterpreted, or replaced.

---

## 20. Family / cluster interpretation boundary

Phase-P protein-level resampling measures robustness within the frozen
discovery universe.

It does not establish cross-family toxin generalization.

Where frozen family or cluster identifiers already exist, their composition
within perturbations may be recorded as descriptive metadata.

They may not be used to redesign the experiment after biological results.

No family-held-out arm is introduced in Experiment 04.

---

## 21. Interpretive hierarchy

Primary biological interpretation:

1. raw-ESM predictive accessibility;
2. raw-ESM versus the frozen 21-dimensional simple-sequence baseline;
3. paired per-perturbation raw-ESM minus baseline AUROC difference;
4. six-layer depth profile.

Supporting interpretation:

5. unsigned support size and recurrence, contextualized by the scoped
   layer-18/N=139 label-permutation null.

Descriptive / calibration-limited interpretation:

6. signed-support and coefficient-orientation behavior.

A particularly informative pattern would be:

- weak SAE stability in Experiment 03;
- stronger raw-ESM predictive accessibility in Experiment 04;
- raw ESM outperforming the frozen simple-sequence baseline.

Such a pattern would be consistent with a representation-basis gap,
SAE-basis misalignment, or distributed accessibility.

It would not establish:

- a causal toxin mechanism;
- unique toxin specificity;
- a mechanistic decomposition;
- cross-family generalization;
- proof that the SAE failed for one uniquely identified causal reason.

---

## 22. Biological perturbation namespace — deliberately unresolved here

This contract does **not** authorize or select a new biological perturbation
seed namespace.

Existing seed status remains:

- `910001-910100`: CONSUMED / CLOSED;
- `920001-920100`: CONSUMED / CLOSED;
- `930001-930100`: CONSUMED / CLOSED;
- `4000-4099`: UNOPENED;
- `2000-2099`: SEALED.

No `940001-940100` namespace exists in the Experiment-04 design.

No biological seed may be generated, inspected, materialized, or consumed
until a separate prospective seed-authorization boundary has been frozen.

The future hard-disabled Phase-P runner must therefore remain incapable of
opening biological perturbation seeds until that separate authorization
occurs.

---

## 23. Confirmatory firewall

Confirmatory data remain completely prohibited from Phase P.

No confirmatory example may be used for:

- representation extraction;
- model selection;
- regularization selection;
- perturbation construction;
- probe fitting;
- stability analysis;
- support analysis;
- threshold construction;
- exploratory inspection;
- performance troubleshooting.

Experiment-04 biological Arm-B outputs remain exploratory/descriptive.

---

## 24. Implementation boundary

After this contract is committed and remote-verified, the next permitted
implementation step is a **hard-disabled Phase-P runner**.

That runner may encode and statically expose the mechanics frozen above, but
must exit before:

- loading biological Phase-E matrices;
- loading biological labels for probing;
- generating biological perturbation seeds;
- fitting a biological probe;
- computing biological AUROC;
- computing biological support statistics.

The hard-disabled runner must be separately audited and smoke-tested without
biological probe execution.

Only after that disabled runner is committed and remote-verified may a
separate prospective biological perturbation seed authorization be frozen.

Enablement and first biological probe execution must remain separate,
auditable repository-history boundaries.

---

## 25. No outcome-responsive modification

Nothing in Phase P may be modified in response to whether the biological
result appears scientifically interesting.

In particular, biological outcomes must not cause:

- C-grid changes;
- solver changes;
- tolerance changes;
- feature scaling;
- alternate pooling;
- layer selection;
- target-N changes;
- support-threshold changes;
- replacement of failed S7-v2 criteria;
- creation of a new biological significance threshold;
- confirmatory-data access;
- family-held-out redesign within Experiment 04.

The purpose of Phase P is to measure what the frozen instrument reports,
not to make the experiment pass.
