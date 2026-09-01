# Experiment 04 — Sparse-Probe Synthetic Calibration Design

## Status

**PRE-BIOLOGICAL / SYNTHETIC INSTRUMENT DEVELOPMENT**

This document freezes the synthetic environment used to design and independently
validate the Experiment 04 supervised sparse-probe stability instrument.

This calibration applies **exclusively to Arm B**, the supervised probe on the
raw 1,280-dimensional ESM representation. It does not recalibrate, modify, or
provide new validation for Arm A's 10,240-latent InterPLM SAE stability
instrument, which is inherited unchanged from Experiment 03.

It does **not** freeze the final numerical sparse-probe PASS thresholds.

No fresh Experiment-04 biological ESM activation may be inspected during this
process.

---

## 1. Objective

Arm B asks whether toxin-associated information is not merely predictive, but
is represented by a **stable sparse linear direction** in raw ESM space.

The instrument must distinguish:

1. stable sparse signal;
2. unstable or non-identifiable sparse signal;
3. predictive but distributed/dense signal;
4. no usable signal.

A useful instrument must not collapse these cases into a single AUROC-based
decision.

---

## 2. Synthetic geometry

Each synthetic dataset contains:

- 139 positive observations;
- 139 negative observations;
- total N = 278;
- p = 1,280 features.

This matches the balanced Experiment-04 discovery geometry and the ESM-2 650M
hidden width.

Feature scaling parameters must be estimated from the fitting subset only and
applied unchanged to held-out observations.

No evaluation-row information may enter preprocessing.

---

## 3. Generative framework

Unless overridden by a scenario:

\[
x_i \sim \mathcal{N}(0,\Sigma)
\]

and

\[
P(y_i=1|x_i)=\sigma(\alpha+x_i^\top\beta)
\]

where:

- \(\sigma\) is the logistic sigmoid;
- \(\beta\) specifies the planted signal;
- \(\Sigma\) specifies feature covariance.

The implementation must preserve an approximately balanced class geometry and
must be frozen before calibration statistics are interpreted.

---

# Scenario families

## 4. S0 — Null signal

Purpose: false-positive control.

- \(\beta=0\)
- features and labels independent.

Required behavior:

- discrimination near chance;
- no stable-sparse PASS.

---

## 5. S1 — Identifiable sparse signal

Purpose: positive control for the target construct.

- exactly 5 non-zero coefficients;
- planted coordinates mutually independent;
- all remaining coordinates null;
- fixed signs.

Coefficient template:

\[
(+b,+b,-b,+b,-b)
\]

Candidate strength ladder:

- 0.50
- 0.75
- 1.00
- 1.25
- 1.50

The final instrument should reliably recognize sufficiently strong members of
this family.

---

## 6. S2 — Weak identifiable sparse signal

Purpose: characterize the lower-power boundary.

Same geometry as S1 with:

- b = 0.10
- b = 0.20
- b = 0.30
- b = 0.40

These cases are not required to PASS.

They characterize transition behavior only.

---

## 7. S3 — Correlated interchangeable sparse signal

Purpose:

Test whether coordinate identity appears stable when multiple observed features
are interchangeable representations of the same latent factor.

Specification:

- 5 latent signal factors;
- each factor represented by a block of 5 correlated observed coordinates;
- total signal-associated observed coordinates = 25;
- signal belongs to the latent factor rather than uniquely to one coordinate.

Within-block correlation:

- rho = 0.70
- rho = 0.90
- rho = 0.99

Required behavior:

Prediction may remain strong, but observed-coordinate identity stability should
decrease as interchangeability increases.

Repeated arbitrary selection among equivalent coordinates must not count as an
identity-stable sparse representation.


---

## 8. S4 — Dense distributed signal

Purpose:

Distinguish predictive accessibility from sparse accessibility.

Specification:

- 128 non-zero coefficients;
- equal absolute coefficient magnitude;
- deterministic fixed signs;
- signal distributed broadly.

Signal magnitude must include cases whose discrimination overlaps S1.

Required behavior:

Prediction may be strong, but the representation should not receive a
stable-sparse PASS.

---

## 9. S5 — Very dense weak signal

Purpose:

Test strongly distributed representation.

Specification:

- all 1,280 coordinates carry weak signal;
- signs deterministically balanced;
- total signal scaled to permit meaningful prediction.

High discrimination alone must not produce sparse-stability PASS.

---

## 10. S6 — Stable sparse signal plus correlated nuisance

Purpose:

Test whether the sparse-probe stability instrument can recover a genuine stable
five-coordinate signal when many observed nuisance coordinates are correlated
with the true signal coordinates but have zero direct effect on the
label-generating score.

S6 is a robustness-positive control.

It is not intended to create a second predictive mechanism.

---

### True sparse signal

S6 retains the same five true signal coordinates and fixed sign template as S1:

    (+1, +1, -1, +1, -1)

The five true signal coordinates are independent standard-normal variables.

For frozen tau:

    b = tau / sqrt(5)

and the noiseless label-generating score is:

    score =
        b * (
            +x_1
            +x_2
            -x_3
            +x_4
            -x_5
        )

Therefore:

    population SD(score) = tau

exactly.

Labels use the same frozen mechanism as S1-S5:

    latent = score + Logistic(0, 1)

followed by the exact 139/139 rank-based split.

Tau is the sole public signal-strength parameter.

---

### Correlated nuisance structure

S6 contains:

- 5 true signal coordinates;
- 20 nuisance coordinates associated with each true signal coordinate;
- 100 correlated nuisance coordinates total;
- 1,175 additional independent standard-normal background coordinates.

The observed-space coordinate layout is frozen as:

- true signal indices: 0-4;
- nuisance indices: 5-104;
- background indices: 105-1279.

The nuisance coordinates are arranged in five contiguous 20-coordinate blocks:

- signal index 0 -> nuisance indices 5-24;
- signal index 1 -> nuisance indices 25-44;
- signal index 2 -> nuisance indices 45-64;
- signal index 3 -> nuisance indices 65-84;
- signal index 4 -> nuisance indices 85-104.

No coordinate permutation may be introduced after S6 diagnostic execution
begins.

For true signal coordinate x_j and nuisance replicate l:

    nuisance_(j,l) =
        rho * x_j
        + sqrt(1 - rho^2) * epsilon_(j,l)

where:

    epsilon_(j,l) ~ Normal(0, 1)

independently.

Because both x_j and epsilon_(j,l) are independent unit-variance variables:

    Var(nuisance_(j,l))
        = rho^2 + (1 - rho^2)
        = 1

and:

    Corr(x_j, nuisance_(j,l)) = rho

in the population.

Thus each nuisance coordinate remains marginally standard normal while its
simple Pearson correlation with its own true signal coordinate is exactly rho.

The implementation must use:

    sqrt(1 - rho^2)

for the residual scale.

It must not use:

    sqrt(1 - rho)

or any other alternative scaling.

Nuisance coordinates attached to different true signal coordinates share no
planted covariance beyond finite-sample variation.

---

### Zero direct nuisance effect

Only the five true signal coordinates enter the label-generating score.

Every nuisance coordinate has direct coefficient:

    beta_nuisance = 0

The 100 nuisance coordinates may therefore be predictive marginally because
they correlate with true signal coordinates, but they do not generate the
label independently.

This distinction is frozen.

The generator must not add nuisance coordinates to the true score and must not
rescale tau as rho changes.

---

### Frozen covariance ladder

The nuisance-correlation ladder is:

    rho in {
        0.30,
        0.60,
        0.90
    }

Rho is a frozen covariance axis, not a signal-strength parameter.

S6 uses the full master tau ladder at every frozen rho value.

No S6-specific tau subset or rho subset may be selected after diagnostic or
calibration execution begins.

The full frozen S6 grid is therefore:

    9 tau values x 3 rho values = 27 settings

---

### Separation of tau and rho

Tau controls the population SD of the noiseless label-generating score.

Rho controls only covariance between true signal coordinates and zero-direct-
effect nuisance coordinates.

Changing rho must not change:

- the five true signal coordinates for a fixed underlying diagnostic draw;
- their direct coefficient magnitudes;
- the noiseless score definition;
- tau;
- the logistic-noise scale.

Thus S6 varies nuisance ambiguity while holding generative difficulty fixed.

### Deterministic RNG stream separation

For a fixed scenario seed, the generator must derive separate deterministic RNG
streams for:

1. the five true signal coordinates;
2. nuisance residual epsilon draws;
3. the 1,175 independent background coordinates;
4. logistic label-generating noise.

Changing rho must affect only the deterministic transformation applied to the
already-fixed true-signal and nuisance-residual draws.

At fixed seed and tau, changing rho must therefore leave exactly unchanged:

- the five true signal coordinates;
- the noiseless label-generating score;
- the logistic-noise realization;
- the final class labels;
- the 1,175 background coordinates.

Only nuisance indices 5-104 may change as a function of rho.

This stream separation is part of the frozen S6 construction, not an
implementation convenience.

---

### Intended probe behavior

S6 is intended to test robustness rather than create an automatic failure case.

At moderate nuisance correlation:

    rho = 0.30
    rho = 0.60

a well-calibrated sparse-stability instrument should remain capable of
recognizing the underlying stable sparse signal at tau values where S1 itself
is detectable.

At extreme nuisance correlation:

    rho = 0.90

degradation in coefficient identity, sparsity, or prediction is permitted as a
stress response, but it must be reported rather than silently reclassified.

The empirical behavior remains a calibration result; it is not guaranteed by
generator construction.

---

### Distinction from S3 and S7

S3 tests non-identifiable observed coordinate identity when several correlated
coordinates represent the same latent factor without a unique observed-space
ground-truth coefficient.

S7 tests signed instability when one predictive latent direction is represented
by a mixed-orientation interchangeable shortcut block.

S6 differs from both.

In S6:

- exactly five observed coordinates are the true direct-effect coordinates;
- their signed identity is globally defined;
- the additional 100 coordinates are correlated distractors with zero direct
  coefficient.

S6 therefore asks whether a stable sparse basis remains recoverable in the
presence of correlated nuisance structure.

---

### Frozen S6 public interface

The intended generator interface is:

    generate_s6(seed, tau, rho)

For implementation and all experiment call sites, S6 arguments must be supplied
by keyword:

    generate_s6(seed=..., tau=..., rho=...)

This avoids confusion with the already-frozen S3 interface, whose positional
order differs. S3 is not reopened by this convention.

Tau must come from the full frozen master tau ladder.

Rho must be exactly one of:

    0.30
    0.60
    0.90

Frozen structural constants:

- true signal coordinates = 5;
- true signal indices = 0-4;
- true signal signs = (+1, +1, -1, +1, -1);
- nuisance coordinates per signal coordinate = 20;
- nuisance indices = 5-104;
- total nuisance coordinates = 100;
- background indices = 105-1279;
- independent background coordinates = 1,175;
- nuisance direct coefficient = 0;
- logistic noise scale = 1.0.

Any change to these constants after S6 diagnostic execution begins requires an
explicit pre-calibration protocol amendment.

---

### S6 diagnostics before calibration

Before any calibration seed is used, diagnostic-only checks from the reserved
900001-900100 block must verify:

1. the internal true-signal coefficient magnitude is
   `b = tau / sqrt(5)`;
2. population SD(score) tracks tau at every tested rho;
3. exact 139/139 class balance is retained;
4. empirical simple Pearson correlations between each true signal coordinate
   and its own nuisance coordinates track rho itself at 0.30, 0.60 and 0.90;
5. nuisance coordinates have empirical variance near 1.0 at every frozen rho,
   verifying the `sqrt(1 - rho^2)` residual scaling;
6. nuisance coordinates associated with different true signal coordinates have
   no planted cross-block covariance;
7. nuisance direct coefficients are exactly zero;
8. at fixed seed and tau, changing rho leaves the true signal coordinates,
   noiseless score, logistic-noise realization, final labels and background
   coordinates exactly unchanged;
9. only nuisance indices 5-104 change as rho changes;
10. true signal indices are exactly 0-4, nuisance indices exactly 5-104, and
    background indices exactly 105-1279;
11. the 1,175 background coordinates remain independent standard-normal noise;
12. metadata records tau, rho, true signal indices, true signal signs, nuisance
    indices, nuisance block assignments and background indices.

These diagnostics may not:

- fit a probe;
- compute AUROC;
- select a threshold;
- inspect calibration seeds;
- inspect validation seeds;
- alter the frozen S6 construction.

---

### Calibration-stage robustness requirement

Generator diagnostics verify only construction.

During calibration with seeds 1000-1099, S6 must be evaluated across its full
frozen tau-by-rho grid.

For each moderate rho value:

    rho = 0.30
    rho = 0.60

the calibration report must determine whether there is at least one identical
frozen tau value at which:

1. S1 satisfies the stable-sparse positive-control behavior; and
2. S6 also satisfies the stable-sparse behavior despite correlated nuisance.

This common-tau comparison tests whether moderate nuisance correlation causes a
false stability failure that is absent in the corresponding clean S1 control.

The rho = 0.90 condition is a stress condition.

Failure at rho = 0.90 does not by itself invalidate the instrument, but the
failure mode and affected gate or gates must be reported.

Tau may not be rescaled, interpolated, or selected outside the frozen master
ladder to manufacture S6 robustness.

If no common frozen tau satisfies the required S1/S6 behavior at rho = 0.30 or
rho = 0.60, the calibration suite fails its moderate-covariance robustness
requirement and must be reviewed before independent validation or biological
use.

## 11. S7 — Predictive signed-interchangeable shortcut

Purpose:

Provide a negative control that can remain predictively useful and sparse while
failing observed-coordinate identity and/or signed-recurrence stability.

S7 is intended to challenge the stability limbs directly rather than fail
because prediction is absent, because the representation is dense, or because
the shortcut is restricted to a small sample subgroup.

---

### Label-generating score

For each observation:

    z ~ Normal(0, 1)

The noiseless label-generating score is:

    score = tau * z

Therefore:

    population SD(score) = tau

exactly.

Labels are produced by the same frozen balanced-label mechanism used by the
other non-null scenarios:

    latent = score + Logistic(0, 1)

followed by the exact 139/139 rank-based split.

Tau is the sole public signal-strength parameter.

No second shortcut-strength parameter is introduced.

---

### Shortcut block

S7 contains one globally active block of five observed shortcut coordinates.

All 278 observations contain all five shortcut coordinates.

The five coordinates are redundant signed proxies for the same hidden z.

The frozen orientation template is:

    (+1, +1, -1, +1, -1)

The frozen proxy-quality constant is:

    rho_shortcut = 0.95

This is a structural constant, not a public calibration axis.

For shortcut coordinate j:

    x_j =
        orientation_j * (
            sqrt(rho_shortcut) * z
            + sqrt(1 - rho_shortcut) * epsilon_j
        )

where:

    epsilon_j ~ Normal(0, 1)

independently.

The remaining 1,275 coordinates are independent standard-normal noise.

---

### Correlation structure

Under this construction:

- same-orientation shortcut proxies have population correlation
  approximately +rho_shortcut;
- opposite-orientation shortcut proxies have population correlation
  approximately -rho_shortcut.

The mixed sign orientation belongs only to the observed shortcut basis.

It does not alter:

- z;
- the noiseless label-generating score;
- tau;
- the fixed logistic-noise scale.

Thus tau controls generative difficulty while the signed proxy basis controls
observed-coordinate instability.

---

### Intended sparse predictive representation

Because all five shortcut coordinates carry the same underlying signal,
a sparse linear model can predict using one or a small number of them.

The planted shortcut representation is therefore sparse relative to:

    p = 1,280

despite having five interchangeable signal-associated coordinates.

At sufficiently strong frozen tau values, S7 is intended to satisfy the
predictive limb P without requiring a dense coefficient vector.

---

### Intended instability mechanism

The five shortcut coordinates are highly correlated representations of the same
underlying z.

Several coordinates therefore provide nearly interchangeable predictive
directions.

Because the frozen basis contains both positive and negative orientations,
equivalent predictive directions can be represented by different
coordinate/sign combinations.

Across finite-sample discovery perturbations, an L1 probe may therefore:

- select different members of the shortcut block;
- change which signed coordinate identity represents the same underlying
  predictive direction;
- retain useful discrimination while coefficient identity and/or signed
  recurrence deteriorate.

S7 is therefore intended to produce:

- useful predictive discrimination at sufficiently strong tau;
- sparse fitted solutions;
- unstable observed-coordinate identity and/or signed recurrence.

The final empirical behavior is a calibration result and is not guaranteed by
construction.

---

### Distinction from S3

S3 and S7 test different failure modes.

S3 contains five latent signal factors, each represented by its own correlated
observed block. Its primary purpose is to test instability caused by
interchangeable observed coordinates for multiple stable latent factors.

S7 contains one latent predictive direction represented by a single
mixed-orientation shortcut block.

Its primary purpose is to test whether signed coordinate identity and recurrence
remain stable when several positive- and negative-oriented observed coordinates
encode the same predictive direction.

S7 therefore serves as the intended signed-instability control rather than a
subpopulation-conditional shortcut control.

Any future subpopulation-conditional shortcut scenario must be specified
separately rather than folded into S7.

---

### Required interpretation

S7 must not be rejected merely because its shortcut is predictive.

A successful sparse-stability instrument should distinguish stable sparse
accessibility from this signed-interchangeable shortcut.

If S7 is predictive and sparse but fails coefficient-identity and/or
signed-recurrence stability, that is the intended negative-control behavior.

If S7 instead:

- consistently fails the predictive limb;
- consistently requires a dense solution; or
- becomes strongly coordinate/sign stable;

then S7 is not serving its intended calibration role and the
generator/instrument design must be reviewed before biological use.

---

### Frozen S7 public interface

The intended generator interface is:

    generate_s7(seed, tau)

S7 uses every value in the frozen master tau ladder.

No S7-specific tau subset may be selected after diagnostic or calibration
execution begins.

Frozen structural constants:

- latent signal dimensions = 1;
- shortcut coordinates = 5;
- shortcut coordinates active for every observation;
- orientation template = (+1, +1, -1, +1, -1);
- rho_shortcut = 0.95;
- background noise coordinates = 1,275;
- logistic noise scale = 1.0.

Any change to these structural constants after S7 diagnostic execution begins
requires an explicit pre-calibration protocol amendment.

---

### S7 diagnostics before calibration

Before any calibration seed is used, diagnostic-only checks from the reserved
900001-900100 block must verify:

1. population SD(score) tracks tau;
2. labels remain exactly 139/139;
3. tau maps to the label-generating score without a second strength parameter;
4. same-orientation shortcut correlations are near +rho_shortcut;
5. opposite-orientation shortcut correlations are near -rho_shortcut;
6. the shortcut orientation template is exactly (+1, +1, -1, +1, -1);
7. the remaining 1,275 coordinates contain independent standard-normal noise;
8. metadata records tau, rho_shortcut, shortcut indices and shortcut
   orientations.

These diagnostics may not:

- fit a probe;
- compute AUROC;
- select a threshold;
- inspect calibration seeds;
- inspect validation seeds;
- alter the frozen S7 construction.

---

### Calibration-stage operating-window requirement

Generator diagnostics do not determine whether S7 occupies the intended probe
operating regime.

During calibration with seeds 1000-1099, the realized S7 behavior across the
frozen master tau ladder must be characterized.

The calibration report must determine whether there is a non-empty tau region
in which S7 is:

- predictively useful;
- sparse under the candidate probe instrument; and
- unstable on coefficient identity and/or signed recurrence.

The calibration suite requires at least one **identical frozen tau value** at
which both of the following hold:

1. S1 satisfies the frozen stable-sparse positive-control behavior; and
2. S7 satisfies the predictive and sparsity limbs while failing coefficient
   identity and/or signed-recurrence stability.

This common-tau requirement prevents trivial instrument validation in which S1
and S7 can be distinguished only because one scenario is predictive and the
other is not.

The common tau value must come from the already-frozen master ladder.

Tau may not be altered, scenario-specifically rescaled, interpolated, or
selected outside the frozen ladder to manufacture this overlap.

If no common frozen tau value satisfies the required S1/S7 operating behaviors,
the calibration suite fails this control-design requirement and must be reviewed
before independent validation or biological use.

# Discrimination overlap

## 12. Signal-strength targeting

### Frozen cross-scenario strength parameter

The sole public signal-strength parameter for synthetic scenarios S1-S5 is:

    tau

defined as the **population standard deviation of the noiseless
label-generating score** before logistic label noise is added and before the
exact 139/139 class split is constructed.

The fixed logistic-noise scale remains:

    noise_scale = 1.0

for every non-null scenario.

All scenario-specific coefficient magnitudes are internal implementation
details derived deterministically from tau.

Raw coefficient magnitude `b` is no longer a caller-facing calibration
parameter.

This establishes one common generative-strength scale across sparse, correlated
and distributed scenarios.

---

### Generative SNR versus recoverable discrimination

Tau equalizes the population scale of the noiseless label-generating score
relative to the fixed logistic-noise process.

Tau therefore equalizes **generative signal-to-noise ratio**.

It does **not** require equal fitted-probe AUROC across scenario families.

At equal tau, differences in probe discrimination caused by:

- sparsity;
- dimensionality;
- observed-coordinate interchangeability;
- correlation;
- nuisance structure;
- distributed coding;

are part of the construct being tested.

For example, at fixed tau, a five-coordinate sparse signal may be substantially
more recoverable at N=278 and p=1,280 than a 128-coordinate or 1,280-coordinate
distributed signal.

That residual discrimination gap is not a calibration defect.

Scenario-specific tau values must **not** be increased or decreased post hoc to
force fitted-probe AUROC matching across scenario families.

Doing so would remove the sparse-versus-distributed recoverability distinction
that the instrument is designed to measure.

Predictive discrimination is a necessary limb of the final probe instrument,
but it is never sufficient for a stable-sparse PASS.

AUROC or any other discrimination statistic may not be used to infer synthetic
scenario family, substitute for the sparsity/identity/sign-stability limbs, or
rescue failure of those limbs.

### Discrimination coverage is descriptive only

The realized predictive-discrimination range produced by the frozen tau ladder
must be reported for each scenario family during calibration.

This may include descriptive characterization of datasets as approximately
chance, weak, moderate, strong, or very strong discrimination regimes.

These descriptions are not calibration targets.

There is no requirement that every scenario family attain a particular AUROC,
that sparse and dense scenarios overlap in AUROC, or that tau be modified to
produce a desired discrimination range.

Observed discrimination coverage may characterize the operating regime of the
frozen synthetic suite but may not determine scenario-specific tau values.

---

### S1 and S2

S1 and S2 use five independent unit-variance observed coordinates with
equal-magnitude coefficients.

For k = 5:

    SD(score) = ||beta||_2 = sqrt(5) * b

Therefore:

    b = tau / sqrt(5)

The old S1/S2 raw-b ladders are retired as public interfaces.

Their implied generative strengths are preserved exactly through the tau ladder
defined below.

---

### S3

S3 generates labels from five independent unit-variance latent factors:

    score = Z @ latent_beta

with five equal-magnitude latent coefficients.

Therefore:

    SD(score) = sqrt(5) * b

and:

    b = tau / sqrt(5)

The S3 correlation parameter rho changes how each latent factor is represented
by correlated observed proxy coordinates.

Rho does not enter the label-generating score.

Therefore rho varies observed-coordinate interchangeability at fixed population
generative difficulty.

Tau and rho are separate experimental axes.

---

### S4

S4 contains 128 independent unit-variance signal coordinates with equal
coefficient magnitude.

Therefore:

    SD(score) = sqrt(128) * b

and:

    b = tau / sqrt(128)

---

### S5

S5 contains 1,280 independent unit-variance signal coordinates with equal
coefficient magnitude.

Therefore:

    SD(score) = sqrt(1280) * b

and:

    b = tau / sqrt(1280)

---

### Frozen tau ladder

The master tau ladder preserves exactly the generative strengths implied by the
previous S1 and S2 raw-b ladders.

The authoritative symbolic ladder is:

    tau in sqrt(5) * {
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.75,
        1.00,
        1.25,
        1.50
    }

S2 owns the weak-signal subset:

    tau in sqrt(5) * {
        0.10,
        0.20,
        0.30,
        0.40
    }

S1 owns the identifiable-sparse subset:

    tau in sqrt(5) * {
        0.50,
        0.75,
        1.00,
        1.25,
        1.50
    }

S3, S4 and S5 use the full master tau ladder.

No scenario-specific subset of the master tau ladder may be selected after
synthetic execution begins.

Any computationally motivated reduction requires an explicit protocol amendment
made before any diagnostic or calibration result from the affected scenario is
inspected.

The symbolic values above are authoritative.

Rounded decimal values are descriptive only and must not replace the symbolic
definitions in validation or implementation checks.

---

### Public generator interface

After refactoring, the synthetic generators must expose strength as tau:

    generate_s1(seed, tau)
    generate_s2(seed, tau)
    generate_s3(seed, rho, tau)
    generate_s4(seed, tau)
    generate_s5(seed, tau)

Each generator computes its internal coefficient magnitude from tau.

No S1-S5 generator may expose unrestricted raw `b` as the calibration-facing
strength parameter.

The internally derived `b` value may be retained in metadata for auditability.

---

### Implementation diagnostics

Before calibration seeds are used, the refactored generators must pass
diagnostic-only implementation checks using seeds outside all calibration and
validation blocks.

The reserved diagnostic seed block is:

    900001-900100

These seeds are permanently excluded from calibration and independent
validation.

These diagnostics may verify:

1. the expected mapping from tau to internal b;
2. empirical score SD near tau using N = 200,000 diagnostic observations per
   scenario/strength setting, so the population-scale derivation can be checked
   with negligible sampling uncertainty relative to the biological N;
3. empirical SD(score) for S3 remains invariant across rho = 0.70, 0.90 and
   0.99 at fixed tau over independent diagnostic seeds;
4. no generator changes the fixed logistic-noise scale;
5. exact 139/139 class balance remains intact at biological-matched N = 278.

Diagnostic outputs must not be used to select thresholds, alter the tau ladder,
or tune scenario-specific strengths.

They are software verification only.

Calibration seeds 1000-1099 and validation seeds 2000-2099 remain untouched
during these diagnostics.

Diagnostic seeds 900001-900100 may never be reused for threshold calibration or
independent validation.

---

### S6 and S7

S6 and S7 must also be parameterized from the same tau definition before their
implementations are frozen.

Their internal coefficient or shortcut-strength parameters must be derived so
that tau retains the same meaning:

    population SD of the noiseless label-generating score.

No S6 or S7 implementation may introduce a second public strength scale without
a protocol amendment made before calibration execution.

## 13. Discovery sizes and frozen perturbation architecture

Discovery sizes are:

- N = 100 per class;
- N = 120 per class;
- N = 139 per class.

Here N means the number of observations per class available to the final
coefficient-stability refit.

This meaning must remain identical across all three discovery sizes.

### Outer discovery perturbation

For each deterministic perturbation:

- N positives and N negatives are selected without replacement from the
  available 139 positives and 139 negatives;
- selection is stratified by class;
- the perturbation seed determines the selected observations and all subsequent
  internal splits;
- no observation outside the synthetic dataset may enter the perturbation.

For N = 139, the selected target-N dataset is therefore the complete 139/139
synthetic discovery dataset.

No bootstrap resampling is used in the primary perturbation architecture.

Repeated K-fold training subsets are not treated as substitutes for N = 139,
because doing so would change the effective coefficient-fit sample size.

### Separation of prediction estimation from coefficient-stability fitting

Each perturbation has two distinct stages.

#### Stage A — internal model selection and held-out prediction

Within the target-N dataset:

1. construct a deterministic stratified internal split;
2. use only the internal-training portion to select C under candidate rule
   R1, R2 or R3;
3. evaluate the selected C on the untouched internal-evaluation portion;
4. record held-out AUROC for the predictive limb P.

No training AUROC may enter P.

The internal-evaluation observations may not influence C selection.

#### Stage B — full target-N coefficient refit

After C has been selected using Stage A:

1. refit the same L1 logistic model using all N positives and all N negatives
   in the target-N perturbation;
2. use this full target-N refit only for:
   - non-zero coefficient count;
   - selected-feature identity;
   - coefficient sign;
   - sparsity statistic S;
   - coefficient-identity statistic I;
   - sign-stability statistic G.

The Stage-B full-N refit must not replace the Stage-A held-out AUROC.

Thus:

    P = held-out prediction from Stage A

while:

    S, I, G = coefficient properties from Stage B

This separation is frozen because at N = 139 there is no discovery observation
outside the target-N set that can simultaneously serve as an untouched
evaluation set while preserving a 139-per-class coefficient fit.

### Internal split fraction

The candidate internal split fraction is frozen initially as:

    80% internal training
    20% internal evaluation

with class stratification and deterministic seed control.

The exact integer class counts must be deterministic for each N.

For each class:

- N = 100 -> 80 train / 20 evaluation;
- N = 120 -> 96 train / 24 evaluation;
- N = 139 -> 111 train / 28 evaluation.

The N = 139 split uses 111 + 28 = 139 exactly.

### Number of perturbations

The candidate calibration implementation uses:

    100 deterministic perturbations

per scenario/strength/condition setting.

This matches the perturbation count used by the inherited SAE stability
instrument while remaining a separate Arm-B calibration procedure.

### No cross-perturbation leakage

For every perturbation:

- Stage-A evaluation observations must remain untouched during C selection;
- statistics from other perturbations may not determine that perturbation's C;
- independent-validation seeds may never participate;
- biological data may never participate.

### Calibration status

The architecture above is frozen before calibration execution.

Calibration may still compare R1, R2 and R3 and may select final numerical
P/S/I/G definitions and thresholds.

The target-N meaning, Stage-A/Stage-B separation, 80/20 internal split,
without-replacement outer sampling and 100-perturbation count may not be altered
after calibration seeds are opened without declaring the calibration block
consumed and moving to a fresh untouched seed block.

---

# Probe model

## 14. Model class

Frozen:

- logistic regression;
- L1 penalty;
- intercept enabled;
- 1,280 input features.

Candidate regularization grid:

\[
C \in
\{
10^{-4},
3\times10^{-4},
10^{-3},
3\times10^{-3},
10^{-2},
3\times10^{-2},
10^{-1},
3\times10^{-1},
1
\}
\]

Solver, iteration cap, tolerance and deterministic behavior must be frozen
before independent validation.

---

# Regularization selection

## 15. Candidate rules

### R1 — maximum internal-CV AUROC

Choose C with the highest mean internal cross-validated AUROC.

Risk:

May favor unnecessarily dense models.

### R2 — one-standard-error sparse rule

Find the best mean internal-CV AUROC, then choose the smallest C whose score is
within one standard error of the best.

This is the preferred starting rule.

### R3 — discrimination-constrained sparsity

Among models within a frozen discrimination tolerance of the best score, choose
the sparsest.

R3 introduces an additional tunable tolerance and should only be adopted if R2
fails calibration.

No rule may use biological or independent-validation outcomes.

---

### Frozen Stage-A internal-CV mechanics

R1 and R2 use the same internal cross-validation construction.

This cross-validation occurs **only inside the Stage-A internal-training
portion**.

The untouched Stage-A internal-evaluation portion may not enter:

- fold construction;
- C selection;
- mean CV AUROC;
- standard-error calculation;
- tie-breaking.

The frozen CV construction is:

    StratifiedKFold(
        n_splits = 5,
        shuffle = True,
        deterministic seed = perturbation-derived CV seed
    )

Every candidate C must be evaluated on exactly the same five folds within a
given perturbation.

The CV seed must be derived deterministically from the perturbation seed using
a dedicated seed stream distinct from:

- target-N subsampling;
- Stage-A train/evaluation splitting;
- synthetic-data generation.

### Fold-level AUROC

For candidate C and fold f:

1. fit the frozen L1 logistic model on four CV folds;
2. compute AUROC on the held-out fold only;
3. record one fold-level held-out AUROC.

Training AUROC is prohibited.

For each C:

    mean_C =
        arithmetic mean of the 5 held-out fold AUROCs

and:

    sd_C =
        sample standard deviation of the 5 held-out fold AUROCs
        using denominator 4

The standard error is:

    se_C = sd_C / sqrt(5)

No pooled out-of-fold AUROC may replace the arithmetic mean of the five
fold-level AUROCs for R1/R2 selection.

### Frozen R1 definition

R1 selects the C with the largest:

    mean_C

If multiple C values have exactly equal mean_C values, select the smallest C.

Thus R1 ties favor stronger L1 regularization.

### Frozen R2 one-standard-error definition

R2 first identifies C_best using the frozen R1 definition.

Define:

    best_mean = mean_C_best

and:

    best_se = se_C_best

The one-standard-error admissibility boundary is:

    one_se_floor = best_mean - best_se

A candidate C is admissible if:

    mean_C >= one_se_floor

R2 selects the **smallest C** among all admissible candidates.

Because smaller C corresponds to stronger L1 regularization, this is the frozen
sparse one-standard-error rule.

The standard error used to construct the boundary is always:

    se_C_best

It is not:

- the candidate C's own standard error;
- the fold-level standard deviation itself;
- a confidence-interval half-width;
- a pooled standard error across C values;
- uncertainty from the Stage-A held-out evaluation set.

### Numerical handling and ties

Candidate C values are evaluated in ascending order:

    1e-4,
    3e-4,
    1e-3,
    3e-3,
    1e-2,
    3e-2,
    1e-1,
    3e-1,
    1

Full floating-point AUROC values are retained.

No rounding may occur before:

- identifying C_best;
- calculating one_se_floor;
- testing admissibility.

Exact ties are resolved toward the smallest C.

No additional numerical epsilon or tolerance may be introduced into the
one-standard-error comparison unless a solver pathology is demonstrated during
calibration and documented before independent validation.

### Stage-A sample sizes entering internal CV

The five-fold CV operates only on the Stage-A internal-training portion.

Nominal class counts are:

- target N = 100:
  - 80 per class enter internal CV;
- target N = 120:
  - 96 per class enter internal CV;
- target N = 139:
  - 111 per class enter internal CV.

Fold sizes need not be identical because 96 and 111 are not divisible by 5.

No observations may be dropped, duplicated or weighted to equalize fold sizes.

### Stage-A held-out evaluation after C selection

After R1, R2 or R3 selects C using only the Stage-A internal-training portion:

1. refit the selected-C model on the complete Stage-A internal-training set;
2. evaluate it once on the untouched Stage-A internal-evaluation set;
3. record that AUROC as the perturbation-level predictive statistic.

This held-out AUROC is the candidate input to P.

The five internal-CV AUROCs used for C selection may not substitute for the
Stage-A held-out AUROC used by P.

### R2 calibration failure mode

R2 is the preferred starting regularization rule.

Calibration must explicitly test whether R2 collapses stable sparse positive
controls to near-zero or otherwise non-informative coefficient solutions.

Such behavior constitutes a candidate-rule calibration failure.

It may not be repaired by:

- changing the one-standard-error formula;
- changing the number of CV folds;
- changing the Stage-A split fraction;
- choosing a larger C post hoc for selected scenarios.

Any replacement of R2 by R1 or R3 must be made as a rule-level calibration
decision and frozen before independent validation.

---

# Candidate statistics

## 16. Prediction

Primary candidate:

- held-out AUROC.

Training AUROC is prohibited as a stability gate.

Candidate aggregate:

- median held-out AUROC across perturbations.

## 17. Sparsity

Primary candidate:

- number of non-zero coefficients.

Candidate aggregate:

- median number of non-zero coefficients across perturbations.

No arbitrary coefficient-magnitude cutoff should be introduced unless solver
numerical behavior requires one.

## 18. Coefficient identity stability

Candidate statistic:

- pairwise Jaccard similarity of selected non-zero feature sets.

Candidate aggregate:

- median pairwise Jaccard across perturbations.

## 19. Sign stability

For selected coordinates, quantify whether the same coordinate recurs with the
same coefficient sign.

Candidate summaries include:

- signed recurrence;
- median signed recurrence;
- fraction of nominated coordinates exceeding a frozen signed-recurrence
  threshold.

The final definition must be fixed during calibration.


---

## 20. Intended joint rule

The intended structure is conjunctive:

PROBE STABLE = P AND S AND I AND G

where:

- P = predictive-discrimination gate;
- S = sparsity gate;
- I = coefficient-identity gate;
- G = sign-stability gate.

No compensatory weighted score is planned.

High prediction cannot rescue failed sparsity or stability.

---

# Calibration / validation firewall

## 21. Seed separation

Calibration seeds:

1000-1099

These may be used for:

- generator debugging;
- comparing perturbation schemes;
- comparing regularization rules;
- inspecting metric distributions;
- choosing final statistics;
- selecting thresholds.

Independent validation seeds:

2000-2099

These remain untouched until:

- the full instrument is frozen;
- thresholds are written into PROTOCOL.md;
- validation acceptance criteria are written;
- implementation is finalized.

The validation block may be executed only once for a frozen instrument.

If validation fails, seeds 2000-2099 are considered consumed.

The next untouched block becomes:

3000-3099

Further revisions consume successive untouched blocks:

4000-4099
5000-5099
and so on.


---

## 22. Independent-validation requirements

Before validation is run, numerical acceptance criteria must be frozen.

At minimum, the instrument must demonstrate that it:

1. rarely calls S0 null data stable sparse;
2. reliably recognizes sufficiently strong S1 sparse signals;
3. loses coordinate-identity stability in highly interchangeable S3 cases;
4. rejects S4 and S5 dense signals as stable sparse even when predictive;
5. remains reasonably robust to moderate S6 nuisance correlation;
6. rejects S7 shortcut-driven predictive instability.

---

# Biological firewall

## 23. Prohibited until synthetic validation succeeds

Do not:

- embed fresh toxin sequences at layers 1, 9, 24, 30 or 33;
- inspect fresh biological ESM representations;
- inspect fresh InterPLM SAE activations;
- compute fresh biological discrimination;
- fit biological sparse probes;
- tune C using toxin-associated results;
- alter thresholds using biological observations;
- embed confirmatory sequences.

---

## 24. Implementation order

Frozen order:

1. implement deterministic synthetic generators;
2. unit-test planted-signal recovery under an easy sparse case;
3. implement probe fitting and internal C selection;
4. implement perturbation metrics;
5. run calibration seeds 1000-1099 only;
6. choose and freeze the complete probe instrument;
7. write thresholds and validation acceptance criteria into PROTOCOL.md;
8. commit and push the frozen pre-validation state;
9. run validation seeds 2000-2099 exactly once;
10. if validation succeeds, freeze the biological Experiment 04 protocol;
11. only then inspect fresh biological activations.

---

## 25. Current freeze boundary

Frozen here:

- N = 139 positives + 139 negatives;
- p = 1,280;
- S0-S7 scenario families;
- sparse, correlated, distributed, nuisance and shortcut controls;
- candidate N = 100/120/139 perturbation geometry;
- L1 logistic model class;
- C grid;
- candidate R1/R2/R3 selection rules;
- candidate metric families;
- conjunctive P AND S AND I AND G structure;
- calibration seeds 1000-1099;
- first validation seeds 2000-2099;
- consumed-validation rule;
- implementation order;
- biological firewall.

Not yet frozen:

- exact synthetic generator implementation;
- signal scaling needed for discrimination matching;
- primary perturbation construction;
- final C-selection rule;
- final predictive statistic and threshold;
- final sparsity threshold;
- final identity-stability definition and threshold;
- final sign-stability definition and threshold;
- independent-validation numerical acceptance criteria.
