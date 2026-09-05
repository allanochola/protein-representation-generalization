# Arm B Phase-P Numerical-Conditioning Dry-Run Specification

## Status

**PROSPECTIVE / PRE-EXECUTION / ENGINEERING-ONLY**

This document governs a numerical-conditioning dry run that must occur before Phase-P biological probing is enabled.

Writing or freezing this specification does **not** authorize biological probing.

---

## 1. Purpose

The sole purpose of this dry run is to determine whether the already-frozen Arm-B probe implementation can numerically fit the real frozen Phase-E representations without:

- `ConvergenceWarning`;
- solver failure;
- non-finite coefficients;
- non-finite intercepts; or
- another numerical exception.

This is an implementation and numerical-conditioning test only.

It is not a biological analysis.

---

## 2. Scientific firewall

The dry run must not load, inspect, derive, reconstruct, infer, or use the biological toxin/non-toxin labels.

**Biological labels are forbidden inputs.**

The dry run must not compute AUROC, accuracy, precision, recall, F1, confusion matrices, prediction probabilities, decision scores, biological support statistics, stability statistics, layer rankings, representation rankings, or biological effect sizes.

No dry-run result may be used as evidence for or against a biological hypothesis.

---

## 3. Allowed real data

The dry run may use only the six already-frozen Phase-E raw ESM pooled representation matrices:

- layer 1;
- layer 9;
- layer 18;
- layer 24;
- layer 30;
- layer 33.

No new ESM extraction is permitted.

No alternate representation is permitted.

No scaling, normalization, PCA, whitening, centering, clipping, feature selection, or other transformation is permitted.

Before any matrix is loaded, its frozen SHA-256 must be verified.

### Frozen matrix identities

| Layer | Frozen file | SHA-256 |
|---:|---|---|
| 1 | `raw_esm_layer_1.npy` | `204b2d0901b805ce9221b8318883e29dfe2c9a2c1aa18f37b6fc831ef3b08c15` |
| 9 | `raw_esm_layer_9.npy` | `7eb08b17232cbf34c23ac8e246dbeb07bec2197904d4bb24e6717a93c1d03683` |
| 18 | `raw_esm_layer_18.npy` | `c4e408db0963a0cbb90996ebb59b5e83cd86a9120de1a968cd4b7d80f5fa440e` |
| 24 | `raw_esm_layer_24.npy` | `78c34e2c4419fb1ba850e383ab56b06b864412e65ba5046379983ff9e1190336` |
| 30 | `raw_esm_layer_30.npy` | `ebc98537034ea7946b4c634d4a0a3fff18f503428b3f182c79360a604159c98b` |
| 33 | `raw_esm_layer_33.npy` | `64e626858aa8e2a0a323af5121520f969f942679f8cbec4d27c7116bc8501f0d` |

---

## 4. Frozen row identity

All six matrices correspond to the same frozen discovery row manifest:

`experiments/03-toxin-representation/stage1_model_contact/discovery_extraction/discovery_matrix_rows.tsv`

Frozen manifest SHA-256:

`ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e`

The dry-run implementation must verify this manifest byte identity before any model fit.

The shared Phase-E row order is load-bearing for the later paired biological design.

---

## 5. No experimental seed namespace

This dry run has **no experimental seed namespace**.

It must not use or instantiate any Experiment-04 protected, consumed, rejected, nonexistent, main, null, or candidate namespace.

In particular, it must not use:

- `900001-900100`;
- `910001-910100`;
- `920001-920100`;
- `930001-930100`;
- `940001-940100`;
- `950001-950100`;
- `960001-960100`;
- `970001-970100`;
- `980001-980100`;
- `990001-990100`;
- `1000001-1000100`;
- `1100001-1100100`;
- `1200001-1200100`;
- `1300001-1300100`;
- `1400001-1400100`;
- `1500001-1500100`.

No `numpy.random.SeedSequence` may be instantiated.

No NumPy RNG may be instantiated.

No pseudorandom label generation is permitted.

---

## 6. Artificial labels

The dry-run labels are deterministic, artificial, and independent of protein identity and biological annotation.

For zero-based frozen manifest row index `i`:

```text
y_dry[i] = i mod 2
```

For 278 rows this yields exactly:

- 139 artificial class-0 rows;
- 139 artificial class-1 rows.

These labels have no biological meaning.

Their sole purpose is to let the numerical solver exercise both classes.

The label rule may not be changed after this specification is frozen.

---

## 7. Fit set

This numerical-conditioning test is intentionally not a Phase-P perturbation.

It does not reproduce target-N selection, Stage-A splitting, CV selection, Stage-B evaluation, or stability resampling.

For each of the six frozen Phase-E matrices, the solver is fit directly to the complete 278-row matrix using only the deterministic artificial labels.

This deliberately removes stochastic sampling and biological outcome logic from the engineering test.

---

## 8. Frozen C grid

Every layer must be tested at every frozen Arm-B C value:

```text
1e-4
3e-4
1e-3
3e-3
1e-2
3e-2
1e-1
3e-1
1.0
```

All 6 × 9 = 54 layer/C fits must be attempted unless a frozen STOP condition terminates execution earlier.

No C may be added, removed, substituted, or selected based on dry-run results.

No best C is defined by this dry run.

---

## 9. Probe mechanics

The dry run must use the same production probe family frozen for Arm B:

- logistic regression;
- L1 penalty;
- `liblinear`;
- inherited solver tolerance;
- inherited `max_iter`;
- inherited intercept behavior;
- inherited dtype/input behavior unless separately frozen otherwise.

The implementation must reuse or exactly reproduce the frozen `make_probe` / `fit_probe_or_fail` numerical mechanics.

It may not silently change solver, penalty, tolerance, `max_iter`, class weighting, intercept behavior, input scaling, dtype conversion, or another numerical setting.

---

## 10. Allowed outputs

For each requested layer/C fit, the dry run may record only:

- layer;
- C;
- fit completed: yes/no;
- `ConvergenceWarning`: yes/no;
- exception type/message if fitting fails;
- coefficient finite: yes/no;
- intercept finite: yes/no;
- solver iteration count if exposed by the fitted estimator.

No predictive-performance quantity may be computed or persisted.

---

## 11. STOP rule

Any of the following is an engineering STOP:

1. any `ConvergenceWarning`;
2. solver exception;
3. non-finite coefficient;
4. non-finite intercept;
5. matrix SHA mismatch;
6. manifest SHA mismatch;
7. unexpected matrix shape or dtype;
8. attempted biological-label access;
9. attempted RNG or SeedSequence construction;
10. attempted unapproved transformation.

A STOP is not permission to modify the analysis.

---

## 12. Failure handling

If the dry run reveals a numerical failure, the protected biological and null namespaces remain untouched.

A failed dry run may motivate a separate implementation amendment, but no change may be made automatically.

Failure does not authorize post-hoc changes to:

- `max_iter`;
- tolerance;
- solver;
- C grid;
- scaling;
- normalization;
- dtype;
- representation;
- pooling;
- layer set.

Any proposed change must be scientifically and numerically justified, written prospectively, independently audited, and frozen before protected main/null seeds are touched.

---

## 13. Success interpretation

If all 54 fits complete without warning, exception, or non-finite parameters, the only permitted conclusion is:

> The frozen Arm-B L1/liblinear probe implementation can numerically fit the six frozen real Phase-E representation matrices across the frozen C grid under the deterministic artificial-label conditioning test.

This does not imply biological signal, predictive validity, good generalization, support stability, SAE-basis misalignment, toxin specificity, or success of Experiment 04.

---

## 14. Relationship to Phase P

Passing this dry run is necessary engineering evidence before Phase-P enablement but is not sufficient authorization to open Phase P.

After the dry run is completed and archived, Phase P still requires the separately frozen experiment-level orchestration / transaction implementation and final execution authorization.

The outer biological execution gate remains literal `False` throughout this dry-run stage.

---

## 15. Protected-state declaration

- Patch A is frozen at `1a0027e21526ab87755f434811c81e60d303a9a0`;
- main biological seeds `1000001-1000100` remain AUTHORIZED / UNCONSUMED;
- permutation-null seeds `1100001-1100100` remain AUTHORIZED / UNCONSUMED;
- biological probing remains CLOSED;
- calibration block `4000-4099` remains UNOPENED;
- block `2000-2099` remains SEALED.

No protected namespace is consumed by writing this document.
