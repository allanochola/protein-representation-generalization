# Experiment 04 — Arm-B post-failure architecture amendment

Status: PRE-IMPLEMENTATION / PRE-RECALIBRATION

This amendment is frozen after calibration block `3000-3099` failed before
threshold selection.

It changes the Arm-B perturbation architecture before any further calibration
block is opened.

No numerical `gamma_P`, `gamma_S`, `gamma_I`, or `gamma_G` is selected here.

Validation block `2000-2099` remains sealed.

Calibration reserve block `4000-4099` remains unopened.

## 1. Reason for amendment

The completed calibration block established that the original Arm-B
coefficient-stability perturbation does not preserve a common stability
construct across discovery sizes.

Under the original architecture:

- `N` was defined as the number of observations per class entering the
  Stage-B coefficient refit;
- target-N observations were selected without replacement from a fixed
  synthetic dataset containing 139 positives and 139 negatives;
- therefore at `N=139`, every perturbation retained the same complete
  139/139 dataset.

Post-failure descriptive reconstruction of block `3000-3099` showed that this
has a material consequence for coefficient-identity and sign stability.

At `N=139`, Stage-B support variation was almost completely determined by
variation in the Stage-A-selected C, with only small residual solver-seed
variation.

In particular, among cells where the selected C was unanimous across all
100 perturbations:

- at `N=120`, the median number of distinct Stage-B supports was 100 and
  the median largest identical-support clique was 1;
- at `N=139`, the median number of distinct Stage-B supports was 1 and
  the median largest identical-support clique was 100.

Thus the original `N=139` I/G calculation did not contain the observation-level
sampling perturbation present at `N=100` and `N=120`.

This was not an implementation violation. The complete-dataset behavior at
`N=139` was explicitly frozen in the original protocol. The amendment addresses
an untraced consequence of that design choice.

The alteration rule frozen in §13:1276-1279 permits the target-N and
perturbation architecture to change after calibration seeds have been opened
only if the active calibration block is declared consumed and work moves to a
fresh untouched calibration block.

That condition is satisfied:

    3000-3099 = consumed
    4000-4099 = untouched

This amendment therefore changes the architecture under the protocol's own
post-calibration amendment rule rather than modifying a live calibration block.

## 2. Predecessor-instrument provenance

Experiment 03 already defines and independently validates a different
full-pool stability construction.

For each target discovery-pool size:

    N in {100, 120, 139}

the Experiment-03 stability instrument uses:

    floor(0.80 * N)

positives and the same number of negatives in each perturbation.

Sampling is:

- class-specific;
- without replacement;
- repeated for exactly 100 deterministic perturbations.

The fraction:

    0.80

is therefore inherited from the predecessor stability instrument.

It is not selected, tuned, interpolated, or optimized using calibration block
`3000-3099`.

Experiment 03 subsequently retained the same 100 deterministic 80%-subsample
perturbation rule. Its concentration-calibration specification also states
explicitly that the perturbation rules are not changed in response to prior
calibration results.

That prior freeze is part of the provenance for inheritance here.

Experiment 03 also explicitly limits the interpretation at `N=139`:
perturbation stability is conditional on the frozen realized N=139 discovery
pool and is not evidence that alternative membership of the source universe
would nominate the same features.

Arm B inherits that interpretation.

## 3. Amended meaning of N

Effective immediately for future Arm-B calibration:

    N = target discovery-pool size per class

with:

    N in {100, 120, 139}

This supersedes the earlier Arm-B definition in which N was the number of
observations per class entering every coefficient-stability refit.

The target-N pool continues to contain exactly:

    N positives
    N negatives

selected without replacement from the fixed 139/139 synthetic dataset.

At `N=139`, the target discovery pool is therefore still the complete
139-positive / 139-negative synthetic dataset.

No bootstrap resampling is introduced.

## 4. Stage A remains frozen

Stage A is unchanged.

For each perturbation, using the full target-N pool:

1. construct the existing deterministic stratified 80/20 internal split;
2. select C using the existing frozen R2 mechanics;
3. evaluate the selected C on the untouched Stage-A evaluation portion;
4. record the held-out AUROC used by P.

The existing integer Stage-A split counts remain unchanged:

    N=100 -> 80 train / 20 evaluation per class
    N=120 -> 96 train / 24 evaluation per class
    N=139 -> 111 train / 28 evaluation per class

No part of this amendment changes:

- the C grid;
- five-fold CV;
- the one-standard-error rule;
- Stage-A model fitting;
- the held-out definition of P.

## 5. Full-N coefficient refit for sparsity

The existing full-target-N coefficient refit is retained for the sparsity limb.

After Stage A selects C, fit the frozen L1 logistic model on all observations
in the target-N pool:

    N positives
    N negatives

using the existing Stage-B full-N model-fitting stream.

For perturbation t, define:

    K_t_full

as the exact number of non-zero feature coefficients returned by this full-N
fit.

The sparsity statistic remains:

    S_stat = median(K_t_full across the 100 perturbations)

The exact-zero semantics remain unchanged.

Thus S remains a property of the full target-N coefficient fit.

## 6. New stability refit for I and G

Coefficient identity and signed stability are no longer computed from the
full-N sparsity refit.

A separate stability refit is added after Stage A selects C.

For each perturbation:

1. start from that perturbation's target-N discovery pool;
2. select, independently by class and without replacement:

       floor(0.80 * N) positives
       floor(0.80 * N) negatives

3. fit the same frozen L1 logistic model using the C selected by that
   perturbation's Stage A;
4. extract exact non-zero coefficient identity and sign from this stability
   fit;
5. record the exact non-zero coefficient count from this stability fit as:

       K_t_stab

   for descriptive stability-fit collapse diagnostics.

`K_t_stab` is descriptive only.

It does not enter `S_stat` and may not replace `K_t_full` in the sparsity gate.

The resulting per-class stability-fit sizes are therefore:

    N=100 -> 80
    N=120 -> 96
    N=139 -> 111

The 0.80 fraction is fixed uniformly across all three N values.

It may not be varied by:

- scenario;
- tau;
- rho;
- calibration outcome;
- selected C;
- discovery size beyond the deterministic floor operation above.

## 7. Stability statistics

For perturbation t, let:

    A_t^stab

be the unsigned exact non-zero support from the new 80%-within-pool stability
refit.

Let:

    B_t^stab

be the corresponding signed support:

    (coordinate, sign)

using the existing exact sign convention.

The existing unsigned and signed pairwise Jaccard definitions remain unchanged.

The aggregate definitions also remain unchanged:

    I_stat =
        median unsigned Jaccard over all 4,950 perturbation pairs

    G_stat =
        median signed Jaccard over all 4,950 perturbation pairs

Only the coefficient fit supplying A_t and B_t changes.

No alternative I or G aggregation statistic is selected by this amendment.

## 8. Limb/sample-size semantics

After this amendment, the Arm-B conjunctive instrument combines:

    P_N
        held-out predictive discrimination selected/evaluated using Stage A
        within the target-N pool;

    S_N
        full-target-N coefficient sparsity;

    I_0.8N
        coefficient-identity stability under inherited 80%-within-pool
        perturbation;

    G_0.8N
        signed coefficient stability under inherited 80%-within-pool
        perturbation.

The joint decision remains:

    PROBE STABLE = P AND S AND I AND G

The four limbs therefore do not all arise from the same coefficient fit.

`K_t_full` is the quantity entering `S_stat`.

`K_t_stab` is recorded only to diagnose whether the 80%-within-pool stability
fit collapses to empty or near-empty support. It does not enter the conjunctive
decision.

This separation is intentional and must be stated whenever the final Arm-B
instrument is described.

## 9. Interpretation at N=139

At `N=139`, the target discovery pool exhausts the available synthetic
139-positive / 139-negative pool.

Therefore:

- P and S are evaluated using that realized full pool under their respective
  frozen Stage-A and full-N-fit definitions;
- I and G measure conditional stability under repeated 80%-within-pool
  subsampling of that realized pool;
- I and G do not establish stability to alternative membership of a larger
  source universe.

This limitation is inherited from the Experiment-03 interpretation.

## 10. New runner streams

The existing runner streams remain:

    21 = target-N stratified pool selection
    22 = Stage-A stratified train/evaluation split
    23 = Stage-A five-fold CV construction
    24 = Stage-A model fitting
    25 = full-target-N coefficient fit used for S

Two new runner streams are frozen:

    26 = within-target-N 80% stability subsampling
    27 = stability-refit model fitting used for I/G

Both use the existing runner SeedSequence structure:

    SeedSequence([
        c,
        s,
        t,
        r,
        N,
        200,
        stream_id
    ])

The subsampling and model-fit streams are separate so that observation
selection and solver stochasticity do not share one RNG stream.

Operational materialization is frozen as follows:

- stream 26 is passed as its `SeedSequence` directly to NumPy
  `default_rng` for stability-subsample selection;
- stream 27 is converted with the existing `seedsequence_to_uint32`
  materialization and supplied as the stability model's sklearn
  `random_state`.

No arithmetic seed shortcuts are permitted.

## 11. Consequence for the prior failure interpretation

The prior descriptive observations remain valid:

- S7's planted shortcut coordinates never reversed fitted sign;
- pair-level signed/unsigned Jaccard differences were too sparse to change
  any cell median in block `3000-3099`;
- high-signal S7 frequently collapsed to median support sizes of approximately
  one or two selected coordinates, producing coarse small-support Jaccard
  behavior in the intended rejector region;
- S3's `I_stat` reached `1.0` at `N=139`.

However, the causal interpretation is amended.

The `N=139` identity saturation is not treated as an S3-specific
discovery-size phenomenon.

Under the original architecture, the same loss of observation-level Stage-B
perturbation affected all scenarios at `N=139`.

Therefore the amended architecture must be frozen and diagnostically checked
before deciding whether S3 itself requires generator redesign.

## 12. Redesign order

The required post-failure order is now:

1. freeze this Arm-B stability-architecture amendment;
2. freeze a dedicated pre-calibration diagnostic contract for the amended
   probe-fitting architecture;
3. implement and diagnostically verify the amended architecture without using
   calibration reserve `4000-4099`;
4. only after the amended I/G measurement is validated, redesign or replace
   S7 as necessary. The replacement must be diagnostically shown to provide:

       a. genuine recurring-coordinate sign instability capable of producing
          signed instability distinct from coordinate switching; and

       b. a non-degenerate support regime in which the frozen pairwise Jaccard
          statistics have meaningful resolution rather than collapsing to a
          singleton-support binary comparison.

   No numerical minimum support size is frozen by this architecture amendment.
   That requirement must be operationalized prospectively in the dedicated
   redesign-diagnostic contract before diagnostic execution;
5. re-evaluate S3 under the corrected stability architecture;
6. re-evaluate S4/S5 signal-strength coverage;
7. freeze all amended controls and instrument definitions;
8. commit, push, and verify the remote frozen state;
9. only then open calibration reserve `4000-4099`.

## 13. Calibration and validation firewall

Calibration block:

    3000-3099

remains consumed and may never be reused.

Validation block:

    2000-2099

remains sealed.

Next calibration reserve:

    4000-4099

remains unopened.

The pre-calibration diagnostic seed namespace for probe-fitting redesign
diagnostics is NOT assigned by this amendment.

That namespace must be declared in a separate committed diagnostic contract
before any amended probe-fitting diagnostic is executed.

No result from block `3000-3099` may be used to choose:

- the 0.80 perturbation fraction;
- runner stream identifiers;
- a numerical P/S/I/G threshold;
- a scenario-specific perturbation fraction;
- an alternative I/G aggregation definition.

The 0.80 fraction is inherited from the predecessor Experiment-03 stability
instrument and is frozen independently of the failed Arm-B calibration result.

## 14. Implementation boundary

This amendment changes protocol semantics only.

No runner implementation is modified by this commit.

No generator is modified by this commit.

No diagnostic seed is consumed by this commit.

No calibration seed is consumed by this commit.

No validation seed is consumed by this commit.

Implementation must occur only after this amendment has been reviewed,
committed, pushed, and verified against the remote HEAD.
