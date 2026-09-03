# Experiment 04 — Arm-B post-failure probe-fitting diagnostic contract

Status: FROZEN PRE-IMPLEMENTATION / PRE-DIAGNOSTIC

This contract operationalizes the diagnostic step required by
`ARM_B_POST_FAILURE_ARCHITECTURE_AMENDMENT.md`.

It is frozen before any amended Arm-B probe-fitting diagnostic is executed.

No numerical `gamma_P`, `gamma_S`, `gamma_I`, or `gamma_G` is selected here.

Calibration reserve `4000-4099` remains unopened.

Independent-validation block `2000-2099` remains sealed.


## 1. Purpose

The purpose of this diagnostic block is to verify that the amended Arm-B
coefficient-stability architecture is operationally capable of measuring the
construct it is intended to measure before any further calibration is opened.

The diagnostic is not a replacement calibration block.

It may fit probes because the amended stability architecture cannot be tested
without fitting the frozen probe model.

Its outputs are diagnostic and descriptive only.


## 2. Dedicated diagnostic seed namespace

The dedicated post-failure Arm-B probe-fitting diagnostic namespace is:

    910001-910100

These seeds are reserved exclusively for the diagnostics governed by this
contract.

They are disjoint from:

    900001-900100
        prior generator-only diagnostics;

    1000-1099
        consumed interrupted calibration;

    3000-3099
        consumed completed calibration;

    2000-2099
        sealed independent validation;

    4000-4099
        next untouched calibration reserve;

    5000-5099
        later calibration reserve.

Once any probe fit using a seed in `910001-910100` is executed, that diagnostic
seed is considered consumed.

Seeds from `910001-910100` may never subsequently be used for:

- calibration;
- numerical threshold selection;
- independent validation;
- biological evaluation.


## 3. Diagnostic firewall

The diagnostic block MAY be used to:

- verify implementation of the amended Stage-B stability refit;
- fit the frozen Arm-B L1 logistic probe;
- execute the frozen Stage-A R2 C-selection procedure;
- characterize realized P, S, I and G values descriptively;
- characterize `K_t_full` and `K_t_stab`;
- inspect exact stability-subsample membership;
- inspect unsigned and signed stability supports;
- count distinct stability subsamples and supports;
- measure identical-support clique sizes;
- verify seed-stream separation;
- identify implementation failures;
- determine whether the amended stability fit collapses to empty or
  near-empty support;
- re-evaluate whether previously observed N=139 identity behavior persists
  after the architectural correction.

The diagnostic block MAY NOT be used to:

- select `gamma_P`;
- select `gamma_S`;
- select `gamma_I`;
- select `gamma_G`;
- choose any final PROBE_STABLE threshold;
- change the inherited 0.80 stability-subsample fraction;
- choose a scenario-specific perturbation fraction;
- change the frozen I or G aggregation statistic;
- change the target-N ladder;
- choose a support-resolution minimum by optimizing against realized
  diagnostic outcomes;
- select a tau or rho subset because it produces favorable diagnostic
  separation;
- access calibration reserve `4000-4099`;
- access validation block `2000-2099`.

No result from consumed calibration block `3000-3099` may be used to choose a
numerical diagnostic acceptance threshold in this contract.


## 4. Frozen diagnostic grid

The architecture diagnostic uses the complete already-frozen Step-1 cell grid.

It includes:

- scenarios `S0` through `S7`;
- every tau value already frozen for each scenario in the Step-1 calibration
  grid;
- every rho value already frozen for each scenario in that grid;
- all target discovery-pool sizes:

      N = 100
      N = 120
      N = 139

No scenario, tau, rho or N subset may be selected after diagnostic execution
begins.

The diagnostic therefore preserves the same 273-cell structural grid used by
the completed Step-1 calibration, while using only the dedicated diagnostic
namespace `910001-910100`.

The purpose of reusing the complete frozen cell grid is architecture
verification, not numerical threshold selection.

No diagnostic outcome may be used to remove, add or preferentially retain a
cell for later recalibration.


## 5. Architecture under diagnostic test

For each perturbation the diagnostic implementation must preserve Stage A
unchanged.

Using the target-N discovery pool:

1. construct the frozen Stage-A stratified 80/20 split;
2. select C under the frozen R2 mechanics;
3. evaluate held-out Stage-A AUROC for P;
4. perform the full-target-N coefficient fit used for `K_t_full` and S;
5. independently select the inherited within-pool stability subsample:
       floor(0.80 * N) positives
       floor(0.80 * N) negatives
   without replacement and independently by class;
6. fit the same frozen L1 logistic model on that stability subsample using
   the C selected by that perturbation's Stage A;
7. record `K_t_stab`, unsigned support and signed support from the stability
   refit;
8. compute I and G from those stability-refit supports.

The per-class stability-refit sizes must therefore be exactly:

    N=100 -> 80
    N=120 -> 96
    N=139 -> 111


## 6. Required stochastic streams

The amended runner must use:

    26 = within-target-N 80% stability subsampling
    27 = stability-refit model fitting

Both use the frozen runner construction:

    SeedSequence([
        c,
        s,
        t,
        r,
        N,
        200,
        stream_id
    ])

Operational materialization is:

- stream 26 -> `SeedSequence` passed directly to NumPy `default_rng`;
- stream 27 -> existing `seedsequence_to_uint32` materialization, supplied
  as sklearn `random_state`.

Observation selection and solver stochasticity must not share an RNG stream.

No arithmetic seed shortcuts are permitted.

The diagnostic runner must assert-refuse any diagnostic seed outside:

    910001-910100

and must separately assert that no supplied diagnostic seed belongs to:

    1000-1099
    2000-2099
    3000-3099
    4000-4099
    5000-5099

A seed outside the dedicated diagnostic namespace must terminate execution
before any probe fit occurs.


## 7. Required diagnostic records

Every perturbation record used by this diagnostic must contain enough
information to reconstruct or verify at minimum:

- diagnostic seed;
- scenario;
- tau;
- rho;
- N;
- selected Stage-A C;
- Stage-A held-out AUROC;
- `K_t_full`;
- `K_t_stab`;
- stability-subsample positive membership;
- stability-subsample negative membership;
- unsigned stability support;
- signed stability support;
- stream-26 SeedSequence entropy tuple or complete reproducible identifier;
- stream-27 sklearn random state;
- deterministic stability-subsample membership hash suitable for exact
  duplicate-membership detection.

Cell-level diagnostic summaries must include at minimum:

- P statistic;
- S statistic;
- I statistic;
- G statistic;
- median `K_t_full`;
- median `K_t_stab`;
- minimum `K_t_stab`;
- maximum `K_t_stab`;
- number of empty stability supports;
- number of singleton stability supports;
- number of distinct selected-C values;
- number of distinct stability subsamples;
- number of distinct unsigned stability supports;
- largest identical unsigned-support clique.


## 8. Stability-fit collapse classification

`K_t_stab` is descriptive and does not enter the PROBE_STABLE decision.

For diagnostic interpretation only, each cell is classified as:

    EMPTY
        median(K_t_stab) == 0

    SINGLETON_DOMINATED
        median(K_t_stab) == 1

    NONDEGENERATE_FOR_ARCHITECTURE_DIAGNOSTIC
        median(K_t_stab) >= 2

This classification is not a final support-resolution acceptance rule.

In particular, `median(K_t_stab) >= 2` must not be interpreted as establishing
adequate Jaccard resolution for an eventual S7 instability control.

The final prospective support-resolution requirement for S7 must be frozen
before execution of the S7 redesign diagnostic and may not be selected by
inspecting which minimum support size makes S7 pass.


## 9. Primary architecture diagnostic

The primary question is whether the amended architecture restores genuine
observation-level perturbation to the coefficient-stability fit at every N,
including N=139.

This test is performed directly from stream-26 seed material and recorded
stability-subsample membership. It is not conditioned on the value of the
Stage-A-selected C.

For every diagnostic cell, the 100 perturbations must use 100 distinct
stream-26 seed identities under the frozen SeedSequence construction.

For every perturbation, the recorded stability subsample must:

- contain exactly `floor(0.80 * N)` distinct positive observations;
- contain exactly `floor(0.80 * N)` distinct negative observations;
- contain no observation outside that perturbation's target-N pool;
- contain no within-class duplicate;
- reproduce exactly when stream 26 is reconstructed from the frozen
  SeedSequence contract.

For every cell, record:

- number of distinct stream-26 seed identities;
- number of distinct stability-subsample memberships;
- number of distinct unsigned stability supports;
- largest identical-support clique;
- median `K_t_stab`;
- stability-fit collapse classification;
- I;
- G.

The architecture diagnostic prospectively expects:

    100 distinct stability-subsample memberships
    out of
    100 perturbations

in every cell.

A duplicate stability membership is not, by itself, logically equivalent to
a duplicated seed because independent random draws can in principle coincide.

Nevertheless, any cell with fewer than 100 distinct stability memberships is
a diagnostic failure requiring explicit investigation and resolution before
the architecture may be declared verified.

The diagnostic may not silently accept such a cell or replace it with a
regenerated perturbation.

These criteria test the sampling architecture directly and do not depend on
a numerical P/S/I/G threshold.


## 10. N=120 versus N=139 descriptive comparison

The diagnostic must repeat the post-failure comparison that exposed the
original architecture problem as a secondary descriptive analysis.

Where unanimous-C cells occur naturally, summarize separately for N=120 and
N=139:

- number of qualifying cells;
- distribution of distinct stability-subsample counts;
- distribution of distinct stability-support counts;
- distribution of largest identical-support clique sizes;
- distribution of median `K_t_stab`;
- I;
- G.

The purpose is descriptive verification that N=139 is no longer uniquely
forced into the complete-data Stage-B no-op present under the superseded
architecture.

No minimum number of unanimous-C cells is required for architecture PASS.

If no unanimous-C cell occurs for one of these N values, report that fact and
treat this secondary comparison as unavailable rather than modifying the
diagnostic grid.

No numerical similarity threshold between N=120 and N=139 is frozen here.


## 11. Full-fit versus stability-fit collapse diagnostic

Because S and I/G now arise from different coefficient fits, the diagnostic
must distinguish full-fit sparsity from stability-fit collapse.

For every cell, jointly report:

    median(K_t_full)
    median(K_t_stab)

and the counts of:

    K_t_full == 0
    K_t_full == 1
    K_t_stab == 0
    K_t_stab == 1

The following pattern must be explicitly flagged:

    full-target-N fit retains non-empty support
    AND
    stability refit is EMPTY or SINGLETON_DOMINATED

Such a pattern is evidence that I/G interpretation is being constrained by
stability-fit support collapse rather than by the sparsity limb itself.

It is diagnostic evidence only and does not define a final rejection
threshold.


## 12. S7 boundary

This architecture diagnostic does not rescue, tune or select a replacement
for S7.

The consumed calibration result already established two separate issues that
must remain conceptually distinct:

1. the original S7 planted shortcut construction did not generate genuine
   recurring-coordinate sign reversal;
2. high-signal S7 frequently occupied a one- or two-coordinate support regime
   with coarse pairwise-Jaccard resolution.

The architecture diagnostic may report S7 under the corrected stability
refit descriptively.

It may not use those results to choose:

- a replacement S7 generator;
- a sign-flip magnitude;
- a support-size floor;
- a tau subset;
- a rho subset.

Any S7 replacement must be specified prospectively after the amended
architecture itself has been verified.


## 13. Diagnostic completion conditions

The architecture diagnostic is complete only when:

1. the amended runner implementation reproduces the frozen Stage-A behavior;
2. the full-N S fit remains separate from the 0.8N I/G stability fit;
3. streams 26 and 27 follow the frozen seed derivation and materialization;
4. the diagnostic runner assert-refuses every seed outside `910001-910100`
   before any probe fit;
5. every cell contains exactly 100 distinct stream-26 seed identities;
6. every stability subsample satisfies the exact membership, class-count,
   without-replacement and stream-26 reproducibility invariants in §9,
   including exact per-class sizes of 80, 96 and 111 for N=100, 120 and 139;
7. every cell contains 100 distinct stability-subsample memberships, or any
   duplicate membership has caused the diagnostic to stop for explicit
   investigation rather than being silently accepted;
8. `K_t_stab` and stability-fit collapse diagnostics are persisted;
9. the complete frozen Step-1 273-cell grid is executed without adaptive
   cell removal or addition;
10. the N=120 versus N=139 secondary comparison is persisted where naturally
    available and is explicitly reported unavailable where not;
11. no numerical gamma is selected;
12. no final support-resolution minimum is selected from diagnostic outcomes;
13. no seed from `4000-4099` or `2000-2099` is accessed.

Failure of any implementation-level condition requires correction and
re-execution only under the rules governing this dedicated diagnostic
namespace.

Diagnostic results may motivate a new prospectively written amendment, but
may not silently alter this contract.


## 14. Seed accounting

Before execution:

    910001-910100 = untouched diagnostic namespace
    4000-4099     = untouched calibration reserve
    2000-2099     = sealed independent validation

The diagnostic namespace is considered opened when the first probe fit using
any seed in `910001-910100` begins.

After execution, every diagnostic seed actually used must be recorded as
consumed.

Unused seeds in the namespace remain diagnostic-only and may not be converted
into calibration or validation seeds.


## 15. Implementation boundary

This contract freezes diagnostic semantics only.

This commit must not modify:

- the Arm-B runner;
- any synthetic generator;
- calibration outputs;
- validation outputs.

No diagnostic seed is consumed by writing or committing this contract.

Runner implementation of the amendment occurs only after this contract has
been reviewed, committed, pushed, and verified against the remote HEAD.
