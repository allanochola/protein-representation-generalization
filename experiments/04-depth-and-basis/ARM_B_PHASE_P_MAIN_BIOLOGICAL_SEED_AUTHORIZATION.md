# Experiment 04 — Arm-B Phase-P Main Biological Perturbation Seed Authorization

## Status

**PROSPECTIVE — FROZEN AFTER THE HARD-DISABLED PHASE-P RUNNER FREEZE AND
BEFORE ANY EXPERIMENT-04 BIOLOGICAL PROBE EXECUTION.**

This document authorizes integer identifiers for the main Phase-P biological
perturbations only.

It does **not** generate, inspect, materialize, or consume a seed.

Biological probing remains closed at this boundary.

---

## 1. Governing frozen inputs

This authorization inherits without modification:

- the Phase-P biological probing inheritance contract;
- the frozen Phase-E biological representations;
- the authoritative corrected Arm-B mechanics;
- the hard-disabled Phase-P runner.

The runner remains disabled while this authorization is written and frozen.

---

## 2. Namespace selection rule

Before this authorization was written, a read-only repository-wide textual
collision census was run over a predetermined ordered candidate list:

1. `960001-960100`
2. `970001-970100`
3. `980001-980100`
4. `990001-990100`
5. `1000001-1000100`

The prospective selection rule was:

**use the first collision-free candidate in that predetermined order.**

The first four candidates had tracked textual collisions.

The first collision-free candidate was:

`1000001-1000100`

Therefore this namespace is selected without reference to biological probe
outcomes.

The earlier attempted namespace `950001-950100` was rejected before any
authorization document was written because the conservative collision audit
found prior tracked textual use. It remains **REJECTED / UNAUTHORIZED**.

---

## 3. Main biological perturbation namespace

The main Experiment-04 Phase-P biological perturbation namespace is:

`1000001-1000100`

Status at this authorization boundary:

**AUTHORIZED / UNCONSUMED / NOT MATERIALIZED**

There are exactly 100 integer identifiers in this namespace.

The deterministic perturbation-index mapping is:

`perturbation 0 -> 1000001`

through

`perturbation 99 -> 1000100`

equivalently:

`master_seed(t) = 1000001 + t`, for `t in {0,...,99}`.

This arithmetic mapping is a prospective identifier assignment only.

No `SeedSequence`, RNG, child seed, subsample, split, fold assignment, model
random state, or other seed-derived object is created by this document.

---

## 4. Scope of this namespace

This namespace applies only to the **main biological Arm-B perturbation sweep**.

For a given perturbation index, the same authorized master perturbation
identifier must underlie the paired biological comparisons required by the
inheritance contract.

The perturbation identity must therefore be shared across:

- raw ESM layer 1;
- raw ESM layer 9;
- raw ESM layer 18;
- raw ESM layer 24;
- raw ESM layer 30;
- raw ESM layer 33;
- the frozen 21-dimensional simple-sequence baseline.

The paired raw-ESM-minus-baseline comparison must use the same underlying
perturbation identity and corresponding inherited memberships/splits.

Representation choice must not create a new perturbation identity.

---

## 5. Target-N handling

The frozen biological target-N values remain:

`100, 120, 139`

This authorization does not create separate target-N master namespaces.

For each authorized perturbation identity, the inherited corrected mechanics
must determine the target-N-specific selections.

No target-N value may be added, removed, or selected post hoc.

---

## 6. Corrected-mechanics inheritance

This authorization changes none of the corrected Arm-B mechanics.

The following remain inherited unchanged:

- class-stratified target-N selection without replacement;
- Stage-A exact-count class-stratified 80/20 split;
- five-fold stratified shuffled CV;
- common folds across all C values within a fit;
- frozen nine-value C grid;
- one-standard-error C selection;
- Stage-A held-out AUROC;
- Stage-B full-target-N refit;
- exact-zero support semantics;
- independent 80%-within-target-N stability refit;
- convergence warnings treated as fit failures.

The child-seed derivation mechanics must be inherited from the frozen
authoritative corrected implementation.

This document does not invent a replacement derivation scheme.

---

## 7. Pairing boundary

The same perturbation identity must preserve the prospective paired design.

A different:

- layer,
- representation,
- baseline arm,
- target-N analysis output,

does not authorize an independently chosen master perturbation identifier.

The purpose of the namespace is deterministic experimental control and paired
comparability, not optimization.

---

## 8. Separate permutation-null authorization

This document does **not** authorize seed identifiers for the scoped biological
label-permutation null.

The permutation-null seed authorization remains prospective and separate.

Its frozen analytical scope remains:

- layer 18 only;
- N=139 only;
- 100 perturbations;
- label-permutation null;
- descriptive/null-context role only;
- no biological significance gate;
- no rescue of failed S7-v2;
- no post-hoc layer selection;
- no C-grid modification.

No permutation seed is selected, generated, inspected, materialized, or
consumed here.

---

## 9. Closed, rejected, and protected namespaces

The prior diagnostic/calibration ranges remain:

- `910001-910100`: **CONSUMED / CLOSED**
- `920001-920100`: **CONSUMED / CLOSED**
- `930001-930100`: **CONSUMED / CLOSED**

The failed proposed namespace remains:

- `950001-950100`: **REJECTED / UNAUTHORIZED**

The collision-census candidates not selected remain unauthorized:

- `960001-960100`: **REJECTED / UNAUTHORIZED**
- `970001-970100`: **REJECTED / UNAUTHORIZED**
- `980001-980100`: **REJECTED / UNAUTHORIZED**
- `990001-990100`: **REJECTED / UNAUTHORIZED**

The following protected ranges remain unchanged:

- `4000-4099`: **UNOPENED**
- `2000-2099`: **SEALED**

No identifier from either protected range is authorized by this document.

---

## 10. Explicit 940001 boundary

No `940001-940100` namespace exists in the Experiment-04 design.

This authorization does not create one.

---

## 11. No seed consumption at authorization

Writing, auditing, committing, or pushing this authorization document does not
count as seed consumption.

At this boundary, no code may instantiate an authorized biological seed.

Specifically:

- no `SeedSequence` may be instantiated from `1000001-1000100`;
- no RNG may be instantiated from `1000001-1000100`;
- no child seed may be derived or inspected;
- no target-N membership may be generated;
- no Stage-A split may be generated;
- no CV fold may be generated;
- no probe random state may be generated;
- no stability membership may be generated.

The namespace remains:

**AUTHORIZED / UNCONSUMED / NOT MATERIALIZED**

until a later separately frozen implementation boundary permits those mechanics
to exist in source while the runner remains disabled.

---

## 12. Biological probing remains closed

This authorization alone does not enable Phase P.

The hard-disabled runner remains disabled.

This document does not authorize:

- loading Phase-E matrices for probing;
- loading biological labels for probing;
- importing sklearn for biological fitting;
- fitting any biological probe;
- running biological CV;
- computing biological AUROC;
- computing biological support statistics.

Biological probing remains **CLOSED**.

---

## 13. Confirmatory firewall

Confirmatory proteins remain prohibited from Phase-P computation.

This authorization applies only to the frozen discovery universe:

- 139 positive proteins;
- 139 negative proteins.

It does not authorize access to confirmatory data.

---

## 14. No outcome-responsive modification

After this authorization is frozen, the namespace must not be changed because of
biological results.

It must not be replaced because:

- AUROC is weak;
- AUROC is strong;
- one layer performs poorly;
- one layer performs strongly;
- the baseline performs strongly;
- support recurrence is low;
- sign behavior is unstable;
- an expected interpretation is absent.

The seed namespace is an experimental-control device and not a tunable
hyperparameter.

---

## 15. Required next boundary

After this document is independently audited and frozen in Git, the next allowed
implementation step is to add the inherited corrected biological mechanics to
the Phase-P runner **while keeping the biological execution gate disabled**.

At that future source boundary, the authorized namespace may be encoded as
constants.

A disabled static audit and disabled smoke test must still establish that:

- no authorized seed is instantiated;
- no RNG is instantiated;
- no Phase-E matrix is loaded for probing;
- no biological label is loaded for probing;
- no sklearn probe is fit.

Actual biological execution requires a later separate enablement boundary.

---

## 16. State at freeze

At this authorization boundary:

- Phase E: **COMPLETE / FROZEN**
- Phase-P inheritance contract: **COMPLETE / FROZEN**
- Phase-P runner: **HARD-DISABLED / AUDITED / SMOKE-PASSED / FROZEN**
- main biological namespace `1000001-1000100`:
  **AUTHORIZED / UNCONSUMED / NOT MATERIALIZED**
- biological permutation-null namespace:
  **UNRESOLVED / UNAUTHORIZED**
- `950001-950100`: **REJECTED / UNAUTHORIZED**
- `960001-960100`: **REJECTED / UNAUTHORIZED**
- `970001-970100`: **REJECTED / UNAUTHORIZED**
- `980001-980100`: **REJECTED / UNAUTHORIZED**
- `990001-990100`: **REJECTED / UNAUTHORIZED**
- `4000-4099`: **UNOPENED**
- `2000-2099`: **SEALED**
- confirmatory data: **PROHIBITED**
- biological probing: **CLOSED**
