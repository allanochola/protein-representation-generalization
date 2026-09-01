# Experiment 04 — S1-S5 Generator Diagnostics

## Status

**PASSED — DIAGNOSTIC-ONLY GENERATOR VERIFICATION**

These diagnostics verify synthetic-generator arithmetic and structural behavior
only.

They do not calibrate the sparse-probe instrument.

No probe was fit. No AUROC was computed. No threshold was selected. No
calibration seed or independent-validation seed was used. No biological
activation was computed.

Generator source under test:

- commit: `953b244`
- file: `experiments/04-depth-and-basis/synthetic_generators.py`

Methodological tau freeze:

- commit: `64d6887`

---

## 1. Diagnostic firewall

Reserved diagnostic block:

- `900001-900100`

Calibration block remained untouched:

- `1000-1099`

Independent-validation block remained untouched:

- `2000-2099`

Diagnostic seeds used in the executed checks:

- D2 large-N score-SD: `900001`, `900002`, `900003`
- D3 S3 population-score rho check:
  - rho 0.70: `900010-900019`
  - rho 0.90: `900020-900029`
  - rho 0.99: `900030-900039`
- D4/D5 biological-sized structural checks:
  - S0: `900050`
  - S1: `900051`
  - S2: `900052`
  - S3: `900053`
  - S4: `900054`
  - S5: `900055`
- additional S3 actual-generator rho-isolation check: `900060`

These seeds are diagnostic-only and may never be reused for threshold
calibration or independent validation.

---

## 2. D1 — tau-to-b arithmetic

**PASS**

For every frozen master-tau value, the internally derived coefficient
magnitudes reconstructed the target population score SD:

- S1/S2/S3: `b = tau / sqrt(5)`
- S4: `b = tau / sqrt(128)`
- S5: `b = tau / sqrt(1280)`

No dataset generation was required for this check.

---

## 3. D2 — large-N population score-SD geometry

**PASS**

Diagnostic sample size:

- `N = 200,000`

Tested tau values:

- `0.223606797749979`
- `1.118033988749895`
- `3.354101966249685`

Tested seeds:

- `900001`
- `900002`
- `900003`

All empirical score SDs were within the frozen 1% implementation sanity bound.

Observed relative-error range:

- minimum: approximately `0.0014%`
- maximum: approximately `0.2194%`

Representative results:

| Scenario | Seed | tau | Empirical SD | Relative error |
|---|---:|---:|---:|---:|
| S1/S2 | 900001 | 0.223607 | 0.223786 | 0.0800% |
| S4 | 900001 | 0.223607 | 0.223349 | 0.1154% |
| S5 | 900001 | 0.223607 | 0.223696 | 0.0401% |
| S1/S2 | 900002 | 1.118034 | 1.117513 | 0.0466% |
| S4 | 900002 | 1.118034 | 1.115581 | 0.2194% |
| S5 | 900002 | 1.118034 | 1.118018 | 0.0014% |
| S1/S2 | 900003 | 3.354102 | 3.354153 | 0.0015% |
| S4 | 900003 | 3.354102 | 3.348667 | 0.1620% |
| S5 | 900003 | 3.354102 | 3.348216 | 0.1755% |

The tau parameterization therefore behaves as intended at population scale.

---

## 4. D3 — S3 population-score rho check

**PASS**

At fixed tau, independent diagnostic seeds produced effectively invariant
population-score SD across the three frozen rho values.

Observed summaries:

| rho | Mean SD | Minimum | Maximum |
|---:|---:|---:|---:|
| 0.70 | 1.117326 | 1.113993 | 1.119152 |
| 0.90 | 1.117601 | 1.114306 | 1.121029 |
| 0.99 | 1.118553 | 1.115634 | 1.121660 |

Relative span of rho-group mean SDs:

- `0.0010978197691953106`
- approximately `0.11%`

This is within the diagnostic sanity bound.

---

## 5. D4/D5 — actual-generator structural checks

**PASS**

At biological-matched `N = 278`, one diagnostic dataset was generated for each
scenario S0-S5.

Every dataset had:

- `X.shape = (278, 1280)`
- 139 positives
- 139 negatives

For S1-S5:

- metadata retained `tau`;
- metadata retained the internally derived `b`;
- recorded `b` matched the frozen tau-to-b mapping;
- `noise_scale = 1.0`.

No predictive model or discrimination statistic was computed.

---

## 6. Additional S3 actual-generator rho-isolation check

**PASS**

Diagnostic seed:

- `900060`

Fixed tau:

- `1.118033988749895`

Actual S3 datasets were generated at:

- rho = 0.70
- rho = 0.90
- rho = 0.99

At fixed seed and tau:

- labels were identical across all three rho values;
- every dataset contained exactly 139 positives and 139 negatives;
- tau metadata was identical;
- internally derived b was identical.

Observed mean within-block correlations were:

| rho | Mean observed within-block correlation |
|---:|---:|
| 0.70 | 0.6964 |
| 0.90 | 0.8991 |
| 0.99 | 0.9900 |

Thus rho changed the observed proxy geometry in the intended direction while
leaving the label-generating signal fixed.

---

## 7. Diagnostic verdict

**S1-S5 generator diagnostics: PASS**

The executed diagnostics support the following implementation claims:

1. tau is converted to internal coefficient magnitude using the frozen
   scenario-specific geometry;
2. population score SD tracks tau;
3. S3 rho changes observed-coordinate interchangeability without changing
   generative strength;
4. all non-null generators retain logistic `noise_scale = 1.0`;
5. actual generated datasets preserve exact 139/139 class balance;
6. S1-S5 generator metadata preserves both public tau and internally derived b.

These results validate generator implementation only.

They do not validate:

- sparse-probe regularization selection;
- sparsity gates;
- coefficient-identity gates;
- sign-stability gates;
- predictive-discrimination gates;
- joint sparse-probe PASS/FAIL thresholds.

Those remain calibration-stage questions and must use calibration seeds
`1000-1099` only after the full S0-S7 generator environment is frozen.

---

## 8. Next step

Define and implement S6 and S7 under the same frozen tau convention before any
probe calibration is executed.


---

## 9. S6-S7 generator diagnostics

### Status

**PASS — S6/S7 DIAGNOSTIC-ONLY GENERATOR VERIFICATION**

Frozen diagnostic script:

- commit: `32a800b`
- file: `experiments/04-depth-and-basis/diagnose_s6_s7.py`

Generator source under test:

- S6 implementation commit: `0f7b027`
- S7 implementation commit: `2f064c2`

No probe was fit.

No AUROC was computed.

No threshold or regularization setting was selected.

Calibration seeds `1000-1099` remained untouched.

Independent-validation seeds `2000-2099` remained untouched.

No biological activation was computed.

### Newly consumed diagnostic seeds

S6:

- large-N geometry: `900061`, `900062`, `900063`
- actual-generator rho-isolation: `900064`

S7:

- large-N geometry: `900071`, `900072`, `900073`
- actual-generator structure: `900074`

These seeds are now consumed permanently for diagnostic use and may never be
reused for calibration or independent validation.

---

## 10. S6 diagnostic results

### S6-D1 — large-N geometry

**PASS**

Diagnostic sample size:

- `N = 200,000`

Tested tau values:

- `0.223606797749979`
- `1.118033988749895`
- `3.354101966249685`

Tested rho values:

- `0.30`
- `0.60`
- `0.90`

Across seeds `900061-900063`:

- empirical score SD remained within the frozen 1% tau sanity bound;
- nuisance variance remained approximately 1.0;
- mean signal-to-own-nuisance correlation tracked rho directly;
- representative cross-block nuisance correlations remained near zero.

Observed ranges included:

- nuisance variance: approximately `0.998762` to `1.000181`;
- mean own-block correlation:
  - rho 0.30: approximately `0.299540` to `0.300245`;
  - rho 0.60: approximately `0.599532` to `0.600155`;
  - rho 0.90: approximately `0.899828` to `0.900030`;
- maximum representative cross-block absolute correlation:
  approximately `0.003112` to `0.004987`.

These results support the frozen S6 construction:

    nuisance = rho * signal + sqrt(1 - rho^2) * epsilon

with unit nuisance variance and simple Pearson correlation equal to rho.

### S6-D2 — actual-generator rho isolation

**PASS**

Diagnostic seed:

- `900064`

Fixed tau:

- `1.118033988749895`

Observed actual-generator summaries:

| rho | Mean own-block corr | Nuisance variance | Background mean | Background variance | Max background corr |
|---:|---:|---:|---:|---:|---:|
| 0.30 | 0.3047 | 1.0088 | 0.0009 | 0.9978 | 0.1116 |
| 0.60 | 0.6049 | 1.0158 | 0.0009 | 0.9978 | 0.1116 |
| 0.90 | 0.9019 | 1.0253 | 0.0009 | 0.9978 | 0.1116 |

At fixed seed and tau, changing rho left exactly unchanged:

- the five true signal coordinates;
- the reconstructed noiseless score;
- the background coordinates;
- the final 139/139 labels.

Only nuisance indices `5-104` changed with rho.

Thus S6 successfully isolates nuisance covariance from generative difficulty.

---

## 11. S7 diagnostic results

### S7-D1 — large-N geometry

**PASS**

Diagnostic sample size:

- `N = 200,000`

Tested tau values:

- `0.223606797749979`
- `1.118033988749895`
- `3.354101966249685`

Tested seeds:

- `900071`
- `900072`
- `900073`

Observed shortcut geometry:

- proxy variance remained approximately 1.0;
- same-orientation correlations remained approximately `+0.95`;
- opposite-orientation correlations remained approximately `-0.95`;
- empirical score SD tracked tau within the frozen implementation sanity bound.

Observed ranges:

- proxy variance: `0.996543` to `1.003567`;
- same-orientation correlation: `0.949702` to `0.950260`;
- opposite-orientation correlation: `-0.950214` to `-0.949755`.

These results support the frozen signed-interchangeable proxy construction.

### S7-D2 — actual-generator structure

**PASS**

Diagnostic seed:

- `900074`

Fixed tau:

- `1.118033988749895`

Observed:

- same-orientation correlation = `0.9530`;
- opposite-orientation correlation = `-0.9551`;
- background mean = `-0.0011`;
- background variance = `1.0022`;
- maximum sampled background-background absolute correlation = `0.0722`;
- maximum sampled latent-z/background absolute correlation = `0.1194`.

The independently reconstructed latent score and frozen label-noise stream
reproduced the generated labels exactly.

The returned observed-space beta remained identically zero, consistent with the
frozen non-identifiable observed-basis interpretation.

Thus S7 successfully implements one latent predictive direction represented by
a globally active mixed-orientation interchangeable proxy block.

---

## 12. Combined S0-S7 generator verdict

**PASS — FULL SYNTHETIC GENERATOR ENVIRONMENT IMPLEMENTED AND
DIAGNOSTICALLY VERIFIED**

The diagnostic evidence now supports the implementation of scenarios S0-S7 at
the generator level.

This verdict is strictly limited to synthetic-generator construction.

It does **not** validate:

- L1 regularization selection;
- predictive-discrimination threshold P;
- sparsity threshold S;
- coefficient-identity stability threshold I;
- sign-stability threshold G;
- the conjunctive `P AND S AND I AND G` probe decision rule;
- S1/S6 common-tau robustness;
- S1/S7 common-tau operating-window separation.

Those are calibration-stage questions.

Calibration seeds `1000-1099` remain completely unobserved.

Independent-validation seeds `2000-2099` remain completely unobserved.

No Experiment-04 biological activation has been computed.

---

## 13. Next boundary

The synthetic generator environment is now frozen and diagnostically verified.

The next methodological phase is sparse-probe **calibration** using calibration
seeds `1000-1099`.

Before any calibration seed is executed:

1. the calibration runner itself must be written;
2. its perturbation construction must be frozen;
3. candidate C-selection rules R1/R2/R3 must be implemented exactly as specified;
4. predictive, sparsity, identity and sign-stability statistics must be
   implemented without final numerical thresholds being chosen from validation;
5. the complete calibration script must be statically inspected and committed;
6. only then may seeds `1000-1099` be opened.

Validation seeds `2000-2099` remain sealed until the complete probe instrument
and numerical acceptance criteria have been frozen from calibration.
