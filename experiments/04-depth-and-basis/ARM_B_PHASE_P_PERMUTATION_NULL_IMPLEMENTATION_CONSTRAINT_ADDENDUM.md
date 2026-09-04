# Arm B Phase-P Permutation-Null Downstream Implementation Constraint Addendum

## Status

**PROSPECTIVE IMPLEMENTATION CONSTRAINT — FROZEN BEFORE DOWNSTREAM NULL ORCHESTRATION**

This addendum supplements, but does not replace or modify, the already-frozen
`ARM_B_PHASE_P_PERMUTATION_NULL_SEED_DERIVATION_AMENDMENT.md` and the
hard-disabled permutation-null addressing plus Stage-A preparation already
encoded in the Phase-P runner.

At this boundary:

- Phase-P biological probing remains hard-disabled;
- null seeds `1100001-1100100` remain authorized, unconsumed, and not materialized;
- downstream null streams 23-27 are not yet wired into null execution;
- no null aggregation or replay has been executed;
- `4000-4099` remains unopened;
- `2000-2099` remains sealed.

This addendum changes no seed namespace, entropy vector, target N, stream
identity, model specification, C grid, stability fraction, representation,
biological decision rule, or interpretation boundary.

## 1. Frozen null ordering

For null perturbation `c`, the frozen order remains:

1. stream 21 selects the target-N pool;
2. target N is exactly 139;
3. selected row identities, feature rows, and row order remain fixed;
4. stream 28 performs exactly one positional permutation of the selected labels;
5. only the row-to-label association changes;
6. stream 22 performs Stage-A splitting using the permuted labels;
7. streams 23-27 retain their inherited downstream roles.

The frozen permutation operation is:

    perm = permutation_rng.permutation(len(yn))
    yn_perm = yn[perm]

`Xn` is not permuted.

Exact class counts are preserved, but class labels are no longer guaranteed
to occupy contiguous row blocks.

## 2. Positives-first ordering is not a null invariant

Before stream 28, inherited target-N selection at N=139 produces all positive
labels followed by all negative labels.

After stream 28, that ordering is intentionally destroyed.

Therefore permutation-null downstream code must not require `yn_perm` to equal
a positives-first / negatives-second label vector, and a legitimate null
perturbation must not fail merely because classes are interleaved across rows.

The post-permutation invariants are instead:

- row identities unchanged;
- feature rows unchanged;
- row order unchanged;
- exact class counts unchanged;
- labels attached to row positions permuted.

## 3. Membership validation is label-at-index based

For the null path, validity of `pos_membership` and `neg_membership` must not
be inferred from fixed index ranges `[0, N)` and `[N, 2N)`.

Validation must test the semantic property directly:

    for every i in pos_membership: yn_perm[i] == 1
    for every i in neg_membership: yn_perm[i] == 0

Equivalent vectorized checks are permitted.

The fixed target-pool index identifies the row; `yn_perm` determines that
row's class for downstream null bookkeeping.

## 4. Stream-26 replay reconstructs the exact permuted labels

Null replay must not synthesize a positives-first label vector.

For the same null perturbation `c`, replay must reproduce in order:

1. the same stream-21 target-N selection;
2. the same selected target-pool label vector `yn`;
3. the same stream-28 positional permutation;
4. the same `yn_perm`;
5. only then the inherited stream-26 stability subsampling.

Thus stream-26 replay is deterministic from the frozen stochastic addresses
for `c`; it does not depend on a class-order assumption or observed result.

## 5. Exact replay equality

Before replayed stream-26 membership is compared with the original membership,
the implementation must verify exact row-level equality:

    replay_yn_perm == original_yn_perm

Any mismatch is an implementation failure.

Matching class counts alone is insufficient because stability membership
depends on the row-level placement of the permuted labels.

## 6. Stream identities remain frozen

- 21 — target-N subsampling
- 22 — Stage-A split
- 23 — shared five-fold CV
- 24 — Stage-A fit seeds
- 25 — Stage-B full-target-N fit
- 26 — independent stability subsampling
- 27 — stability fit
- 28 — permutation-null label-position permutation only

No stream may be reassigned. No additional stochastic stream is authorized.
Stream 28 remains exclusive to permutation-null label permutation.

## 7. One authoritative stream-constant scope

The current disabled runner contains module-level constants for streams 21-28
and inherited function-local aliases for streams 21-27.

This is not a stochastic collision and does not invalidate the frozen patch.
However, before full Phase-P or full null downstream orchestration is encoded,
streams 21-28 must have one authoritative source of truth.

The prospective cleanup must:

1. preserve numeric identities 21-28 exactly;
2. remove or replace duplicated local stream-value assignments;
3. make biological and null code reference the same authoritative constants;
4. preserve every previously frozen stochastic address exactly;
5. introduce no new stream and no outcome-responsive remapping.

This is a scope/maintainability correction only and must change no seed value
or perturbation identity.

## 8. Main biological path is not retrospectively redefined

This addendum addresses the null-specific consequence of stream 28.

It does not retrospectively change the frozen main biological path. Where the
unpermuted biological path legitimately retains positives-first ordering, that
invariant may remain.

Shared helpers must nevertheless be valid for both label layouts or branch
explicitly on already-frozen path identity. No branch may depend on model
performance or any biological/null result.

## 9. No post-hoc adaptation

Downstream implementation must not respond to observed outcomes by changing
membership validation, replay logic, stream assignment, permutation ordering,
seed address, C grid, target N, stability fraction, layer, representation,
pooling, probe type, solver, aggregation rule, null family, or null count.

These constraints are frozen before downstream null execution.

## 10. Interpretation firewall

The permutation null remains descriptive/exploratory and is not a biological
decision gate. Arm B remains exploratory/descriptive/calibration-limited.

The failed S7-v2 stronger sign-instability criterion remains failed.

Null results do not establish causal toxin mechanism, unique toxin specificity,
mechanistic decomposition, cross-family generalization, or a unique causal
explanation for SAE behavior.

## 11. Execution firewall

Writing this addendum authorizes no execution.

- no null SeedSequence is instantiated;
- no RNG is instantiated;
- no seed is materialized or consumed;
- no biological matrix or label is processed for probing;
- no permutation is executed;
- no sklearn model is fit;
- no CV, AUROC, support, stability, or aggregation computation is performed;
- no confirmatory data is accessed.

Main biological namespace:

    1000001-1000100
    AUTHORIZED / UNCONSUMED / NOT MATERIALIZED / FROZEN

Permutation-null namespace:

    1100001-1100100
    AUTHORIZED / UNCONSUMED / NOT MATERIALIZED / FROZEN

Protected namespaces:

    4000-4099: UNOPENED
    2000-2099: SEALED

## 12. Next implementation boundary

Only after this addendum is independently audited and committed may the
hard-disabled runner be modified to encode downstream null streams 23-27 and
aggregation/replay.

Before any Phase-P enablement, that implementation must satisfy:

1. one authoritative stream-constant scope for streams 21-28;
2. no positives-first assertion on `yn_perm`;
3. membership validation by label-at-index;
4. exact stream-21 plus stream-28 reconstruction of replay `yn_perm`;
5. exact replay-label equality before stream-26 membership comparison;
6. inherited stream roles 23-27 unchanged;
7. outer Phase-P gate still literal `False`;
8. secondary premature-enable STOP still effective;
9. no biological or null seed consumed during implementation audit.

No downstream null execution is authorized by this document.
