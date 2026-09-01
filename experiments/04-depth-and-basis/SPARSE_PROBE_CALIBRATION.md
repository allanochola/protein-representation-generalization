# Experiment 04 — Sparse-Probe Synthetic Calibration Design

## Status

**PRE-BIOLOGICAL / SYNTHETIC INSTRUMENT DEVELOPMENT**

This document freezes the synthetic environment used to design and independently
validate the Experiment 04 supervised sparse-probe stability instrument.

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

The synthetic suite should span approximately:

- AUROC ~0.50
- AUROC ~0.60
- AUROC ~0.70
- AUROC ~0.80
- AUROC >=0.90

Dense and sparse scenarios must overlap in predictive discrimination.

Otherwise AUROC alone could trivially identify the scenario family.

---

# Perturbation geometry

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
