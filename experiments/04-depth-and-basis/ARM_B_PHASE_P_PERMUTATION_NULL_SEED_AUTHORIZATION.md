# Experiment 04 — Arm B Phase-P Permutation-Null Seed Authorization

## Status

**PROSPECTIVE AUTHORIZATION — WRITTEN BEFORE ANY PERMUTATION-NULL EXECUTION**

This document authorizes the dedicated perturbation-identifier namespace
for the Experiment 04 Arm B label-permutation null only.

It does not execute the null, instantiate SeedSequence, instantiate an RNG,
materialize or consume a seed, load biological representations or labels,
fit a probe, perform cross-validation, compute AUROC or support statistics,
or access confirmatory data.

Biological probing remains CLOSED at this boundary.

---

## 1. Authorized permutation-null namespace

Authorized identifiers:

- first identifier: `1100001`
- last identifier: `1100100`
- number of identifiers: `100`

Deterministic perturbation-index mapping:

```text
null_perturbation_id(t) = 1100001 + t
t = 0, 1, ..., 99
```

Thus:

```text
t = 0  -> 1100001
t = 99 -> 1100100
```

---

## 2. Prospective census selection

Before this authorization was written, a read-only conservative textual
collision census used this prospectively frozen candidate ordering:

1. `1100001-1100100`
2. `1200001-1200100`
3. `1300001-1300100`
4. `1400001-1400100`
5. `1500001-1500100`

The prospectively frozen rule was:

> choose the first candidate block with zero conservative textual collisions.

All five candidate blocks had zero textual collisions.

Therefore the deterministic census winner is:

```text
1100001-1100100
```

No later candidate may replace it on discretionary, convenience, or
outcome-responsive grounds.

---

## 3. Frozen permutation-null scope

The null is restricted to:

- raw ESM layer 18 only
- target sample size `N = 139` only
- exactly `100` permutation perturbations
- label permutation only
- descriptive / exploratory use
- not a biological decision gate

It does not authorize additional layers, target-N values, representations,
pooling rules, baselines, C grids, feature scaling, PCA, post-hoc layer
selection, confirmatory claims, or outcome-responsive changes.

---

## 4. Namespace separation

Main biological namespace:

```text
1000001-1000100
```

Permutation-null namespace:

```text
1100001-1100100
```

The namespaces are disjoint and may not be reused for one another.

---

## 5. Historical and protected namespace firewall

- `2000-2099` — SEALED
- `4000-4099` — UNOPENED
- `910001-910100` — CONSUMED
- `920001-920100` — CONSUMED
- `930001-930100` — CONSUMED
- `950001-950100` — REJECTED
- `960001-960100` — REJECTED
- `970001-970100` — REJECTED
- `980001-980100` — REJECTED
- `990001-990100` — REJECTED
- `1000001-1000100` — MAIN BIOLOGICAL / AUTHORIZED / UNCONSUMED

No namespace `940001-940100` exists.

---

## 6. Seed derivation remains separately prospective

This document authorizes permutation-null perturbation identifiers only.

It does not itself define or execute a permutation-null SeedSequence.

The already frozen main-biological entropy-vector contract remains:

```text
[c, 0, 0, 0, N, 200, stream_id]
```

An executable permutation-null seed derivation and label-permutation stream
must be explicitly specified and frozen before any null execution.

No permutation-null seed derivation may depend on AUROC, support size,
coefficient sign, layer performance, biological outcome, or any other
result-responsive quantity.

---

## 7. Non-execution certification

At this authorization boundary:

- no permutation-null SeedSequence has been instantiated;
- no permutation-null RNG has been instantiated;
- no permutation-null seed has been materialized;
- no permutation-null seed has been consumed;
- no biological matrix has been loaded for Phase-P probing;
- no biological label has been processed for Phase-P probing;
- no label permutation has been executed;
- no sklearn model has been fit;
- no cross-validation has been performed;
- no AUROC has been computed;
- no support statistic has been computed;
- no confirmatory data has been accessed;
- biological probing remains CLOSED;
- `4000-4099` remains UNOPENED;
- `2000-2099` remains SEALED.

---

## 8. Interpretation boundary

Arm B remains exploratory / descriptive / calibration-limited.

The failed S7-v2 stronger sign-instability certification remains failed and
must not be weakened, relabeled, or retroactively treated as passed.

Permutation-null results do not establish causal toxin mechanisms, unique
toxin specificity, mechanistic decomposition, cross-family generalization,
or a unique explanation for SAE behavior.

---

## 9. Authorization statement

Subject to the frozen scope and firewalls above:

```text
1100001-1100100
```

is prospectively authorized for the Experiment 04 Arm B label-permutation null.

Current status:

```text
AUTHORIZED / UNCONSUMED / NOT MATERIALIZED
```

This authorization does not itself open Phase-P execution.

Biological probing remains **CLOSED**.
