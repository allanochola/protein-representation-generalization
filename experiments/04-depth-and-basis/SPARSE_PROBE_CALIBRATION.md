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

## 10. S6 — Sparse signal plus correlated nuisance

Purpose:

Test robustness to biological-like covariance.

Specification:

- retain the 5 planted S1 signal coordinates;
- add 100 nuisance coordinates;
- nuisance coordinates have no direct coefficient;
- nuisance coordinates correlate with signal coordinates.

Correlation ladder:

- rho = 0.30
- rho = 0.60
- rho = 0.90

Required behavior:

Moderate nuisance correlation should not destroy recognition of a genuine
stable sparse signal.

Extreme-correlation degradation is acceptable if quantified.

---

## 11. S7 — Predictive shortcut / unstable signal

Purpose:

Test whether discovery-set shortcuts can generate high discrimination without
stable coefficients.

Specification:

- introduce a small set of shortcut coordinates associated with class;
- make shortcut-label association heterogeneous across predefined sample groups;
- perturbation subsets alter group composition;
- no globally invariant sparse coefficient vector generates the label.

Required behavior:

- some fits may be strongly predictive;
- coefficient identity and/or sign stability should fail;
- the joint sparse-stability gate should reject the case.

---

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

## 13. Candidate discovery sizes

Inherited from Arm A:

- N = 100 per class
- N = 120 per class
- N = 139 per class

For N < 139:

- select N positives and N negatives without replacement;
- sampling determined by frozen perturbation seeds.

For N = 139, instability must still be induced using one frozen method chosen
during calibration.

Candidate methods:

1. stratified subsampling;
2. stratified bootstrap;
3. repeated stratified K-fold training partitions.

Only one primary perturbation construction will enter biological analysis.

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
