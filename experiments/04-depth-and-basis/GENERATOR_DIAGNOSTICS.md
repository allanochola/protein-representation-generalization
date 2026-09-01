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
