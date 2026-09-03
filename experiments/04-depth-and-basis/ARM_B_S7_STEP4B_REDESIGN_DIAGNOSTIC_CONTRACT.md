# Experiment 04 — Arm-B S7 step-4 redesign diagnostic contract

Status: FROZEN PRE-IMPLEMENTATION / PRE-DIAGNOSTIC

This contract implements Experiment-04
`ARM_B_POST_FAILURE_ARCHITECTURE_AMENDMENT.md` §12 step 4.

It is frozen after verification of the amended Arm-B stability architecture
and before any S7 redesign diagnostic seed is opened.

This contract does not select `gamma_P`, `gamma_S`, `gamma_I`, or `gamma_G`.

Calibration reserve `4000-4099` remains unopened.

Independent-validation block `2000-2099` remains sealed.


## 1. Predecessor state

The post-failure architecture diagnostic used namespace:

    910001-910100

That namespace is CONSUMED and CLOSED.

The architecture diagnostic established that the amended 80%-within-target-N
stability refit removes the identified N=139 deterministic support-collapse
mechanism.

In particular, unanimous Stage-A selected C no longer mechanically implies a
single stability support with a largest identical-support clique of 100.

That architecture result does not establish that the existing S7 generator is
adequate.

The existing S7 remains deficient for two distinct reasons identified before
this contract:

1. its planted shortcut coordinates did not exhibit recurring-coordinate
   fitted-sign instability; and

2. its high-signal operating region frequently produced supports too small for
   the frozen pairwise Jaccard statistics to have useful resolution.

This contract addresses those two S7-specific requirements only.


## 2. Purpose

The purpose of the S7 redesign diagnostic is to determine whether a
prospectively frozen S7 replacement can serve as the intended negative control
for signed sparse-probe stability.

The replacement must demonstrate both:

A. genuine recurring-coordinate sign instability, distinct from mere
   coordinate switching; and

B. a non-degenerate support regime in which the frozen unsigned and signed
   pairwise Jaccard statistics have meaningful resolution.

Both requirements must be satisfied before S7 may be frozen for the next
calibration block.


## 3. Dedicated seed namespace

The dedicated S7 step-4 redesign diagnostic namespace is:

    920001-920100

This namespace was checked prospectively against:

- tracked source and protocol files;
- archived Arm-B architecture diagnostic `diagnostic_seed` values;
- the architecture diagnostic manifest; and
- all previously reserved Experiment-04 seed blocks.

No prior semantic use was found.

Upon the first probe fit using any seed in this namespace:

    920001-920100 = CONSUMED

The namespace is reserved exclusively for the S7 redesign diagnostic governed
by this contract.

It may never subsequently be used for:

- numerical P/S/I/G threshold calibration;
- independent validation;
- biological evaluation;
- another S7 redesign after the candidate governed here has been accepted or
  rejected.

If the S7 candidate fails this contract, a subsequent redesign requires a new
prospectively frozen contract and a new untouched diagnostic namespace.


## 4. Protected namespaces

The following states remain fixed:

    1000-1099      = CONSUMED interrupted calibration
    2000-2099      = SEALED independent validation
    3000-3099      = CONSUMED completed calibration
    4000-4099      = UNOPENED next calibration reserve
    5000-5099      = later calibration reserve
    900001-900100  = prior generator-only diagnostic
    910001-910100  = CONSUMED/CLOSED architecture diagnostic
    920001-920100  = S7 step-4 diagnostic only

No protected calibration or validation block may be accessed by this
diagnostic.


## 5. Candidate-generator freeze requirement

This contract does not itself define the replacement S7 generator.

Before `920001` is opened, the complete candidate generator must be committed
and remote-verified.

That candidate-generator freeze must specify at minimum:

- the complete data-generating equations;
- every planted coordinate;
- every latent variable;
- every coefficient or loading;
- every covariance or correlation parameter;
- the label-generating mechanism;
- the tau ladder;
- whether any additional generator parameter exists;
- the exact metadata identifying planted coordinates whose fitted signs are
  expected to be diagnostically meaningful.

No generator parameter may be selected, altered, interpolated, or removed
after any `920001-920100` probe fit has occurred.

The candidate may not contain an outcome-tuned rho or other parameter sweep
from which a favorable value is selected after diagnostic execution.

If multiple generator variants are to be compared, they require a separately
frozen design and selection rule before `920001` is opened.


## 6. Probe architecture

The S7 redesign diagnostic must use the already-amended frozen Arm-B probe
architecture unchanged.

For each perturbation:

1. construct the target-N discovery pool;
2. execute the unchanged Stage-A train/evaluation split;
3. execute the unchanged R2 C-selection procedure;
4. retain the full-target-N coefficient refit for `K_t_full`;
5. independently select the inherited 80%-within-target-N stability
   subsample;
6. fit the frozen L1 logistic model on that stability subsample using the
   Stage-A-selected C;
7. extract exact unsigned and signed non-zero stability support.

The stability-refit sizes remain:

    N=100 -> 80 positives + 80 negatives
    N=120 -> 96 positives + 96 negatives
    N=139 -> 111 positives + 111 negatives

The inherited stability fraction remains exactly:

    0.80

No architecture change is authorized by this contract.


## 7. Stochastic streams

The existing Arm-B streams remain unchanged:

    21 = target-N pool selection
    22 = Stage-A train/evaluation split
    23 = Stage-A five-fold CV construction
    24 = Stage-A model fitting
    25 = full-target-N coefficient fit
    26 = 80%-within-target-N stability subsampling
    27 = stability-refit model fitting

The existing SeedSequence construction and materialization rules remain
unchanged.

No new stochastic stream may be introduced without a prospective amendment
committed before diagnostic execution.


## 8. Diagnostic grid

The diagnostic evaluates the complete frozen S7 tau ladder at:

    N in {100, 120, 139}

with exactly 100 perturbations per cell.

All S7 tau values are retained descriptively.

No tau value may be removed after diagnostic execution begins.

The prospective S7 acceptance region is the high-signal end of the inherited
tau ladder:

    tau_index in {6, 7, 8}

at:

    N in {100, 120, 139}

This produces exactly nine acceptance cells.

The acceptance region is frozen before the S7 replacement is implemented and
before `920001-920100` is opened.

Lower-tau cells are descriptive only and may not substitute for a failed
high-signal acceptance cell.


## 9. Frozen Jaccard definitions

For perturbation t:

    A_t^stab

is the exact unsigned non-zero support from the amended stability refit.

    B_t^stab

is the exact signed support represented as `(coordinate, sign)`.

The existing pairwise Jaccard definitions remain unchanged.

Across 100 perturbations there are:

    C(100, 2) = 4,950

unordered perturbation pairs.

The aggregate statistics remain:

    I_stat =
        median unsigned Jaccard across the 4,950 pairs

    G_stat =
        median signed Jaccard across the 4,950 pairs

No alternative aggregation statistic is authorized.


## 10. Prospective support-resolution rule — step 4b

A stability support is defined as Jaccard-nondegenerate when:

    K_t_stab >= 3

The threshold of three is frozen for structural reasons.

For equal-size singleton supports, pairwise Jaccard is effectively binary.

For two-coordinate supports, the statistic remains extremely coarse.

At support size three, multiple non-trivial overlap levels become available,
including intermediate values rather than only identity/disjointness.

A cell passes the support-resolution requirement only if:

    number of perturbations with K_t_stab >= 3 >= 71

out of the 100 perturbations.

The value 71 is frozen from the pairwise geometry:

    C(71, 2) = 2,485

and:

    2,485 > 4,950 / 2 = 2,475.

Therefore, when at least 71 perturbations are Jaccard-nondegenerate, strictly
more than half of all perturbation pairs consist of two supports each having
at least three coordinates.

This is a pairwise-coverage criterion. It guarantees that pairs involving an
empty, singleton, or two-coordinate support cannot constitute a majority of
the 4,950 pairwise comparisons.

It does not guarantee that the central ordered observations defining the
sample median themselves arise from two supports of size at least three;
that depends on the realized ordering of the Jaccard values.

Accordingly, this support-resolution rule is not by itself evidence that the
aggregate statistic distinguishes signed from unsigned instability. That
separate requirement is imposed prospectively by §13 through `G_stat < I_stat`.

This threshold is not selected from realized S7 diagnostic outcomes.


## 11. Empty- and singleton-support accounting

The diagnostic must separately record for every cell:

- count of `K_t_stab == 0`;
- count of `K_t_stab == 1`;
- count of `K_t_stab == 2`;
- count of `K_t_stab >= 3`;
- minimum `K_t_stab`;
- median `K_t_stab`;
- maximum `K_t_stab`.

Distinct-support counts alone are insufficient for the resolution verdict.

A cell containing repeated empty or singleton supports may not be described as
an architecture failure merely because it has few distinct supports.

The step-4b verdict is determined by §10, not by
`n_distinct_stability_supports` alone.


## 12. Prospective recurring-coordinate sign-instability rule — step 4a

Only coordinates prospectively identified as planted S7 signal/proxy
coordinates in the frozen candidate-generator metadata may satisfy this limb.

For a planted coordinate j in one diagnostic cell, define:

    R_j =
        number of the 100 stability fits in which coordinate j
        has a non-zero coefficient

The coordinate is recurring only if:

    R_j >= 71.

For a recurring coordinate define:

    n_plus_j  =
        number of stability fits where coefficient j is positive

    n_minus_j =
        number of stability fits where coefficient j is negative

and:

    M_j = min(n_plus_j, n_minus_j).

A recurring coordinate demonstrates genuine two-sign instability only if:

    M_j >= 8.

The recurrence threshold 71 ensures that the coordinate is present in a
majority-pair regime rather than appearing sporadically.

The minority-sign threshold 8 is frozen from pairwise materiality.

At the weakest permitted recurrence:

    R_j = 71

and weakest permitted minority count:

    M_j = 8,

the number of opposite-sign pairs containing that same recurring coordinate is
at least:

    8 * (71 - 8) = 504.

Since:

    504 / 4,950 > 0.10,

the sign reversal affects more than ten percent of all perturbation pairs even
at the acceptance boundary.

A one-off or rare solver sign flip therefore cannot satisfy this limb.

Coordinate switching between differently oriented planted coordinates does not
satisfy this rule unless the same recurring coordinate itself appears with both
signs.


## 13. Aggregate signed-versus-unsigned requirement

Structural sign reversal alone is not sufficient.

For every acceptance cell the frozen aggregate statistics must also satisfy:

    G_stat < I_stat.

No minimum numerical difference is imposed.

The purpose of this strict inequality is diagnostic only: the recurring sign
instability must reach the frozen median signed-Jaccard statistic rather than
existing only in rare pairwise comparisons.

This is not selection of `gamma_I` or `gamma_G`.

The numerical values of I and G from `920001-920100` may never be used as final
calibration thresholds.


## 14. Cell-level acceptance

Each of the nine acceptance cells defined in §8 must independently satisfy all
three conditions:

1. SUPPORT RESOLUTION

       count(K_t_stab >= 3) >= 71

2. RECURRING-COORDINATE SIGN INSTABILITY

       at least one prospectively planted coordinate j has:
           R_j >= 71
           M_j >= 8

3. AGGREGATE SIGN EFFECT

       G_stat < I_stat

A cell passes only if all three conditions hold.


## 15. S7 candidate-level decision rule

The candidate S7 replacement passes this diagnostic only if:

    all 9 of 9 acceptance cells PASS.

No majority rule is permitted.

No failed N may be discarded.

No failed tau in the acceptance region may be discarded.

No lower-tau cell may substitute for a failed acceptance cell.

No post-diagnostic change to the acceptance region is permitted.


## 16. Failure semantics

If any of the nine acceptance cells fails any required limb:

    S7 CANDIDATE = REJECTED

and:

    920001-920100 = CONSUMED

A failed candidate may not be repaired and rerun on unused members of the same
namespace.

A redesigned replacement requires:

1. a written explanation of the failure;
2. a prospectively frozen generator amendment;
3. a new untouched diagnostic seed namespace;
4. a committed and remote-verified diagnostic contract or contract amendment;
5. execution only after that freeze.

This rule prevents iterative fitting of the generator to a single diagnostic
seed block.


## 17. Diagnostic outputs permitted

The S7 redesign diagnostic may persist:

- diagnostic seed;
- N;
- tau and tau index;
- selected C;
- `K_t_full`;
- `K_t_stab`;
- exact unsigned stability support;
- exact signed stability support;
- planted-coordinate coefficient sign;
- planted-coordinate recurrence counts;
- planted-coordinate positive/negative sign counts;
- stability-subsample identity and hash;
- required seed provenance;
- pairwise unsigned Jaccard values;
- pairwise signed Jaccard values;
- `I_stat`;
- `G_stat`;
- the structural counts required by this contract;
- cell-level PASS/FAIL for the three frozen S7 diagnostic limbs;
- overall S7 candidate PASS/REJECT verdict.

These outputs are restricted to S7 redesign diagnostics.

They are not calibration outputs.


## 18. Diagnostic outputs prohibited

The S7 redesign diagnostic may not:

- select `gamma_P`;
- select `gamma_S`;
- select `gamma_I`;
- select `gamma_G`;
- emit or choose a final `PROBE_STABLE` threshold;
- use `4000-4099`;
- use `2000-2099`;
- access biological activation;
- access toxin labels;
- access ESM embeddings;
- access SAE activations;
- modify the 0.80 stability fraction;
- modify the frozen Jaccard definitions;
- change the nine-cell acceptance region after execution;
- select a favorable generator parameter after diagnostic outcomes are known.


## 19. Biological firewall

This remains a synthetic diagnostic.

The S7 redesign implementation must not load or inspect:

- biological protein sequences;
- biological labels;
- ESM activations;
- SAE activations;
- Experiment-04 confirmatory biological outcomes.

Violation invalidates the diagnostic.


## 20. Required implementation checks

Before `920001` is opened, the runner must be audited to verify:

- seed-namespace hard refusal outside `920001-920100`;
- explicit refusal of calibration and validation blocks;
- unchanged Stage-A mechanics;
- unchanged stability fraction;
- unchanged streams 21-27;
- exact 100 perturbations per cell;
- exact target-N and stability-refit sizes;
- planted-coordinate metadata comes only from the frozen generator;
- recurrence/sign counts are reconstructed from persisted signed supports;
- I and G use the unchanged 4,950-pair median definitions;
- acceptance logic exactly implements §§10-15;
- no biological file imports or paths are reachable;
- checkpoint/resume semantics do not change the deterministic result.


## 21. Order after this contract

The required sequence is:

1. commit this contract alone;
2. push and remote-verify the contract checkpoint;
3. freeze the complete S7 replacement generator;
4. commit and remote-verify the generator freeze;
5. implement the S7 redesign diagnostic runner;
6. audit the implementation against this contract;
7. commit and remote-verify the disabled runner;
8. explicitly enable diagnostic execution in a separate commit;
9. remote-verify the enabled checkpoint;
10. only then open `920001-920100`;
11. archive diagnostic outputs before scientific interpretation;
12. apply the frozen 9-of-9 decision rule;
13. if PASS, continue to Experiment-04 §12 step 5;
14. if REJECTED, consume `920001-920100` and freeze a new redesign before any
    additional S7 probe-fitting diagnostic.

At no point in this sequence is `4000-4099` opened.


## 22. Current firewall state

At the freeze represented by this contract:

    910001-910100 = CONSUMED / CLOSED
    920001-920100 = ASSIGNED TO S7 STEP-4, UNOPENED
    4000-4099     = UNOPENED
    2000-2099     = SEALED

No gamma is selected.

No S7 redesign diagnostic seed has been opened.

No biological activation has been accessed.
