# Experiment 04 — Arm-B Phase-P Biological Seed-Derivation Specification

## Status

**PROSPECTIVE — FROZEN AFTER MAIN BIOLOGICAL PERTURBATION-SEED AUTHORIZATION
AND BEFORE PHASE-P BIOLOGICAL MECHANICS IMPLEMENTATION OR ANY BIOLOGICAL PROBE
EXECUTION.**

This document freezes the biological translation of the corrected Arm-B
runner-level randomization architecture.

It does not instantiate, inspect, materialize, or consume any seed.

Biological probing remains **CLOSED**.

---

## 1. Governing frozen boundaries

This specification inherits:

- the Phase-P biological probing inheritance contract;
- the authoritative corrected Arm-B mechanics;
- the hard-disabled Phase-P runner;
- the main biological perturbation authorization `1000001-1000100`.

The main biological namespace remains:

**AUTHORIZED / UNCONSUMED / NOT MATERIALIZED / FROZEN**

at the time this specification is written.

---

## 2. Why a biological translation is required

The corrected calibration runner used the runner-level entropy vector:

`[c, s, t, r, N, 200, stream_id]`

where:

- `c` was the diagnostic perturbation seed;
- `s` was synthetic scenario ID;
- `t` was synthetic tau index;
- `r` was synthetic rho index;
- `N` was target N;
- `200` was the frozen runner namespace;
- `stream_id` identified the randomization operation.

Experiment-04 biological Phase P has no synthetic scenario, tau, or rho axes.

Those calibration-only coordinates therefore cannot carry biological meaning.

The biological translation must nevertheless preserve the calibrated entropy
vector structure rather than inventing a new shorter seed-address architecture.

---

## 3. Frozen biological runner-level entropy vector

For biological Phase P, every runner-level SeedSequence root must use exactly:

`[c, 0, 0, 0, N, 200, stream_id]`

where:

- `c` is the authorized main biological perturbation identifier;
- the first `0` is the fixed biological sentinel replacing synthetic scenario ID;
- the second `0` is the fixed biological sentinel replacing synthetic tau index;
- the third `0` is the fixed biological sentinel replacing synthetic rho index;
- `N` is the frozen target-N value;
- `200` is the inherited runner namespace;
- `stream_id` is the inherited corrected-mechanics stream ID.

No other entropy component may be added.

In particular, the entropy vector must not include:

- ESM layer;
- raw-ESM versus baseline identity;
- feature coordinate;
- selected C;
- biological outcome;
- AUROC;
- support size;
- support sign;
- any confirmatory-data identifier.

---

## 4. Biological perturbation identity

The authorized main biological perturbation identifiers are exactly:

`1000001-1000100`

with the frozen mapping:

`perturbation 0 -> 1000001`

through:

`perturbation 99 -> 1000100`.

For perturbation `p`, the same `c` must be used across:

- ESM layer 1;
- ESM layer 9;
- ESM layer 18;
- ESM layer 24;
- ESM layer 30;
- ESM layer 33;
- the frozen 21-dimensional sequence baseline.

Representation identity must not alter the entropy vector.

This preserves the prospectively frozen paired design.

---

## 5. Target-N identity

The only authorized target-N values remain:

`100, 120, 139`

`N` enters the entropy vector in the same positional location used by the
corrected calibration architecture.

Thus, for fixed biological perturbation identifier `c`, target-N values receive
distinct runner-level randomization roots through the inherited `N` coordinate.

No additional target-N value is authorized.

---

## 6. Frozen runner namespace

The corrected calibration architecture used:

`RUNNER_NAMESPACE = 200`

Biological Phase P inherits this value exactly.

The biological runner must not allocate a new runner namespace merely because
the data source changes from synthetic calibration to biological representations.

Separation from calibration is already provided by the disjoint authorized
biological perturbation identifiers.

---

## 7. Frozen stream IDs

The following corrected-mechanics stream identities are inherited exactly:

- stream `21`: target-N class-stratified subsampling;
- stream `22`: Stage-A class-stratified train/evaluation split;
- stream `23`: shared five-fold CV construction;
- stream `24`: Stage-A model-fit root;
- stream `25`: Stage-B full-target-N model fit;
- stream `26`: independent within-target-N stability subsampling;
- stream `27`: stability-refit model fit.

No stream ID may be repurposed.

No additional main-sweep stream ID is authorized by this specification.

---

## 8. Exact runner-level mapping

For each authorized biological perturbation identifier `c`, each target-N value
`N`, and each stream ID in `21,...,27`, the root entropy vector is:

`[c, 0, 0, 0, N, 200, stream_id]`

Therefore:

- target-N subsample root:
  `[c, 0, 0, 0, N, 200, 21]`
- Stage-A split root:
  `[c, 0, 0, 0, N, 200, 22]`
- shared CV root:
  `[c, 0, 0, 0, N, 200, 23]`
- Stage-A fit root:
  `[c, 0, 0, 0, N, 200, 24]`
- Stage-B fit root:
  `[c, 0, 0, 0, N, 200, 25]`
- stability-subsample root:
  `[c, 0, 0, 0, N, 200, 26]`
- stability-fit root:
  `[c, 0, 0, 0, N, 200, 27]`.

These are prospective entropy-vector definitions only.

Writing this document does not instantiate them.

---

## 9. Stream-24 child architecture

The corrected architecture requires the Stage-A fit root, stream `24`, to spawn
exactly **46 child SeedSequences**.

The child assignment is frozen as:

- children `0-44`: the 45 CV model fits from
  `9 C values x 5 folds`;
- child `45`: the final Stage-A selected-C refit.

No child may be skipped, reordered, reused for another purpose, or replaced by
a separately invented seed.

The 46-child architecture is inherited exactly from the corrected calibration
mechanics.

---

## 10. CV child ordering

The frozen C grid remains ascending:

`1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0`

Within stream `24`, children `0-44` are consumed in the inherited nested order:

1. iterate C values in frozen C-grid order;
2. within each C, iterate the five frozen shared CV folds in their returned
   order;
3. consume exactly one child for each fit.

Thus:

- 9 C values;
- 5 fits per C;
- 45 CV-fit children total.

Child `45` remains reserved for the final Stage-A selected-C refit.

---

## 11. Integer materialization rule

Where the corrected mechanics require an integer sklearn random state, the
SeedSequence-to-uint32 materialization rule remains exactly:

`int(ss.generate_state(1, dtype=np.uint32)[0])`

This applies to:

- stream `23` for StratifiedKFold random state;
- stream-24 children for CV fit random states;
- stream-24 child `45` for Stage-A final fit;
- stream `25` for Stage-B fit;
- stream `27` for the stability fit.

This document specifies that inherited rule prospectively but does not execute
it.

---

## 12. Direct RNG streams

The corrected mechanics use SeedSequence roots directly to initialize RNGs for:

- stream `21`: target-N subsampling;
- stream `22`: Stage-A split;
- stream `26`: stability subsampling.

The implementation must preserve that distinction.

Those streams must not first be converted to uint32 merely for stylistic
uniformity.

---

## 13. Calibration-only address machinery excluded

The following synthetic-calibration concepts do not enter biological Phase P:

- synthetic scenario ID;
- synthetic tau value;
- synthetic tau index;
- synthetic rho value;
- synthetic rho index;
- `MASTER_TAU`;
- `S1_TAU`;
- `S2_TAU`;
- synthetic data generators;
- `master_tau_index`;
- `dataset_seedsequence`.

Biological Phase P uses the frozen biological representations and therefore
does not generate a synthetic dataset.

No import from `synthetic_generators` is required or permitted merely to
reproduce calibration addressing.

---

## 14. Exact-mechanics inheritance boundary

The biological implementation must preserve the corrected statistical mechanics,
including:

- `C_GRID`;
- five-fold shuffled stratified CV;
- common CV folds across all C values;
- one-standard-error C selection;
- L1 `liblinear` logistic regression;
- exact fit settings;
- convergence-warning failure behavior;
- class-stratified target-N selection;
- exact-count Stage-A 80/20 split;
- Stage-A held-out AUROC;
- Stage-B full-target-N refit;
- exact `beta != 0.0` support semantics;
- independent 80%-within-target-N stability subsampling;
- stability refit at the Stage-A-selected C.

Only the synthetic address coordinates are translated to fixed biological
sentinels.

The statistical mechanics are not redesigned.

---

## 15. Representation pairing firewall

For fixed `(c, N)`, the randomization identity must be identical for every raw
ESM layer and for the 21-dimensional baseline.

Therefore neither `layer` nor `representation_id` may appear in the entropy
vector.

This is necessary for the frozen paired raw-ESM-minus-baseline AUROC comparison.

Representation-specific fitting operates on different feature matrices but the
underlying memberships, splits, folds, and randomization identities are paired.

---

## 16. No permutation-null authorization

This specification governs only the authorized main biological perturbation
sweep.

It does not authorize the scoped label-permutation-null seed namespace.

Permutation-null seeds remain:

**UNRESOLVED / UNAUTHORIZED**

and require a separate prospective authorization.

---

## 17. Protected and rejected namespaces

The existing boundaries remain unchanged:

- `910001-910100`: **CONSUMED / CLOSED**
- `920001-920100`: **CONSUMED / CLOSED**
- `930001-930100`: **CONSUMED / CLOSED**
- `950001-950100`: **REJECTED / UNAUTHORIZED**
- `960001-960100`: **REJECTED / UNAUTHORIZED**
- `970001-970100`: **REJECTED / UNAUTHORIZED**
- `980001-980100`: **REJECTED / UNAUTHORIZED**
- `990001-990100`: **REJECTED / UNAUTHORIZED**
- `4000-4099`: **UNOPENED**
- `2000-2099`: **SEALED**

No `940001-940100` namespace exists.

---

## 18. No seed materialization at this boundary

Writing, auditing, committing, or pushing this specification must not:

- instantiate `SeedSequence`;
- instantiate an RNG;
- call `generate_state`;
- spawn any stream-24 child;
- generate target-N membership;
- generate a Stage-A split;
- construct CV folds;
- generate any sklearn random state;
- fit a biological probe;
- compute biological AUROC;
- compute biological support.

The main biological namespace therefore remains:

**AUTHORIZED / UNCONSUMED / NOT MATERIALIZED / FROZEN**

at this boundary.

---

## 19. Implementation boundary

After this specification is independently audited and committed, the Phase-P
runner may be modified to encode this seed architecture and the inherited
corrected mechanics.

During that implementation:

- the existing biological execution gate must remain literal `False`;
- disabled execution must return before numpy/sklearn imports needed by the
  enabled path;
- disabled execution must return before biological matrices or labels are
  loaded;
- disabled execution must return before any authorized SeedSequence is
  instantiated;
- disabled smoke testing must consume no biological seed.

Implementation while disabled is not biological probe execution.

---

## 20. No outcome-responsive modification

This seed architecture must not be changed after biological results because of:

- AUROC magnitude;
- layer performance;
- baseline performance;
- selected C;
- support size;
- support recurrence;
- sign behavior;
- preferred scientific interpretation.

It is a frozen experimental-control mechanism.

---

## 21. State at specification freeze

At this boundary:

- Phase E: **COMPLETE / FROZEN**
- Phase-P inheritance contract: **COMPLETE / FROZEN**
- hard-disabled Phase-P runner: **FROZEN**
- main biological namespace `1000001-1000100`:
  **AUTHORIZED / UNCONSUMED / NOT MATERIALIZED / FROZEN**
- biological runner entropy vector:
  **`[c, 0, 0, 0, N, 200, stream_id]`**
- main streams `21-27`: **FROZEN**
- stream-24 child count: **46**
- children `0-44`: **CV FITS**
- child `45`: **STAGE-A FINAL REFIT**
- permutation-null seeds: **UNRESOLVED / UNAUTHORIZED**
- confirmatory data: **PROHIBITED**
- biological probing: **CLOSED**
- `4000-4099`: **UNOPENED**
- `2000-2099`: **SEALED**
