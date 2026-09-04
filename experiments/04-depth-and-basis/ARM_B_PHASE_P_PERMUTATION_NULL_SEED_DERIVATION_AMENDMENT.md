# Experiment 04 — Arm B Phase-P Permutation-Null Seed-Derivation Amendment

## Status

Prospective specification only.

This amendment defines the executable stochastic addressing for the
previously authorized Experiment 04 Arm B label-permutation null.

It does not enable Phase-P biological probing and does not itself instantiate
a SeedSequence, RNG, permutation, model fit, or biological analysis.

## 1. Frozen upstream authorization

The permutation-null perturbation namespace is already frozen as:

- `1100001-1100100`
- exactly 100 perturbation identifiers
- `null_perturbation_id(t) = 1100001 + t` for `t = 0,...,99`

These identifiers remain:

`AUTHORIZED / UNCONSUMED / NOT MATERIALIZED / FROZEN`

The main biological namespace remains separate:

- `1000001-1000100`

The main and null namespaces are disjoint and must not be reused for one
another.

## 2. Frozen null scientific scope

The label-permutation null remains limited to:

- raw ESM layer 18 only;
- target `N = 139` only;
- exactly 100 null perturbations;
- label permutation only;
- descriptive / exploratory use only;
- not a biological decision gate.

No additional layer, target N, representation, baseline, null family, or
biological threshold is authorized by this amendment.

## 3. Inherited entropy-vector architecture

The frozen biological seed-derivation architecture is:

`[c, 0, 0, 0, N, 200, stream_id]`

For the permutation-null namespace, this same seven-position architecture is
used unchanged.

For null execution:

- `c` is the authorized null perturbation identifier in
  `1100001-1100100`;
- the three synthetic-only positions remain `0, 0, 0`;
- `N = 139`;
- `RUNNER_NAMESPACE = 200` remains unchanged;
- the final position remains the stochastic stream identifier.

Layer identity and representation identity do not enter the entropy vector.

## 4. Inherited stochastic streams

The existing inherited Phase-P stochastic streams remain unchanged:

- stream 21 — target-N subsampling;
- stream 22 — Stage-A split;
- stream 23 — shared 5-fold CV;
- stream 24 — Stage-A fit seeds;
- stream 25 — Stage-B full-target-N fit;
- stream 26 — independent stability subsampling;
- stream 27 — stability fit.

No existing stream is reassigned.

## 5. New null-only stochastic stream

The following new stochastic stream is prospectively frozen:

`STREAM_LABEL_PERMUTATION = 28`

Stream 28 is reserved exclusively for the Experiment 04 Arm B
label-permutation-null label shuffle.

It must not be used for target-N subsampling, Stage-A splitting, CV, model
fitting, stability subsampling, stability fitting, or any other stochastic
operation.

## 6. Null label-permutation entropy vector

For null perturbation identifier `c`, the label-permutation SeedSequence
address is:

`[c, 0, 0, 0, 139, 200, 28]`

where:

- `c ∈ 1100001-1100100`;
- `139` is the only authorized target N for this null;
- `200` is the inherited `RUNNER_NAMESPACE`;
- `28` is the newly frozen label-permutation stream.

The same integer materialization convention already frozen for the inherited
mechanics remains applicable where an integer random_state is required.

For stream 28 itself, the permutation RNG is rooted directly from its
SeedSequence using NumPy's Generator architecture rather than by borrowing
or reusing another stochastic stream.

## 7. Frozen operation ordering

For every authorized null perturbation, the operation order is:

1. Use stream 21 to perform the inherited target-N selection and obtain the
   fixed `N = 139` target pool.
2. Preserve the selected feature matrix and selected observations exactly.
3. Construct stream 28 from
   `[c, 0, 0, 0, 139, 200, 28]`.
4. Use stream 28 to generate exactly one permutation of the 139 label
   positions.
5. Replace the selected target-pool label vector with the permuted label
   vector.
6. Use streams 22-27 unchanged for Stage-A splitting, CV, Stage-A fitting,
   Stage-B fitting, independent stability subsampling, and stability fitting.

The label permutation therefore occurs after target-N selection and before
Stage-A splitting.

## 8. Permutation operation

The null operation must be a permutation of the existing selected label
positions.

Conceptually:

`perm = rng.permutation(len(yn))`

`yn_perm = yn[perm]`

Independent Bernoulli resampling, replacement sampling, synthetic label
generation, class-rebalancing, or any procedure that can alter the selected
pool's original class counts is not permitted.

Because only positions are permuted, the exact class counts of the selected
`N = 139` target pool are preserved by construction.

## 9. Feature matrix and membership invariance

The null permutation must not modify:

- the identities of the 139 selected observations;
- the target-N feature matrix;
- raw ESM layer-18 activations;
- feature ordering;
- observation ordering before the label permutation;
- representation dimensionality;
- feature scaling;
- pooling;
- any biological sequence or representation artifact.

Only the association between selected observations and their labels is
randomized.

## 10. Per-perturbation stochastic bundle

For each null perturbation identifier `c`, streams 21-28 form one coherent
reproducible stochastic bundle:

- `[c, 0, 0, 0, 139, 200, 21]` — target-N selection;
- `[c, 0, 0, 0, 139, 200, 22]` — Stage-A split;
- `[c, 0, 0, 0, 139, 200, 23]` — shared CV;
- `[c, 0, 0, 0, 139, 200, 24]` — Stage-A fits;
- `[c, 0, 0, 0, 139, 200, 25]` — Stage-B fit;
- `[c, 0, 0, 0, 139, 200, 26]` — stability subsampling;
- `[c, 0, 0, 0, 139, 200, 27]` — stability fit;
- `[c, 0, 0, 0, 139, 200, 28]` — label permutation.

The stochastic roles remain separated by stream identifier.

## 11. No outcome-responsive derivation

No seed, stream, permutation, ordering, or stochastic address may depend on:

- AUROC;
- support size;
- recurrence;
- coefficient magnitude;
- coefficient sign;
- layer performance;
- biological outcome;
- null outcome;
- calibration outcome;
- any result-responsive quantity.

The null derivation is fixed entirely before null execution.

## 12. Interpretation boundary

The permutation null remains descriptive / exploratory and is not a
biological gate.

Arm B remains exploratory / descriptive / calibration-limited.

The failed S7-v2 stronger sign-instability certification remains failed and
must not be weakened, relabeled, or retroactively treated as passed.

This amendment does not authorize claims of:

- causal toxin mechanisms;
- unique toxin specificity;
- mechanistic decomposition;
- cross-family generalization;
- a unique causal explanation for SAE behavior.

## 13. Execution firewall

At the time this amendment is written:

- no null SeedSequence has been instantiated;
- no null RNG has been instantiated;
- no null child seed has been spawned;
- no null seed has been materialized;
- no null seed has been consumed;
- no biological matrix has been loaded for Phase-P probing;
- no biological label has been processed for Phase-P probing;
- no label permutation has been executed;
- no sklearn model has been fit;
- no cross-validation has been performed;
- no AUROC has been computed;
- no support statistic has been computed;
- no confirmatory data has been accessed;
- biological probing remains CLOSED.

The main biological seeds `1000001-1000100` remain authorized, unconsumed,
and not materialized.

The permutation-null seeds `1100001-1100100` remain authorized, unconsumed,
and not materialized.

`4000-4099` remains UNOPENED.

`2000-2099` remains SEALED.

No namespace `940001-940100` exists.

## 14. Required next boundary

After this amendment is independently audited and committed, the runner may
be updated prospectively under the existing hard-disable to encode stream 28
and the frozen null operation ordering.

That implementation must itself be audited before Phase-P biological probing
is enabled.
