# Experiment 04 Decoder-Geometry Final Aggregation Specification

Status: **FROZEN BEFORE FINAL GEOMETRY RESULT INSPECTION**

This document is the final governing specification for aggregation and
comparison of the Experiment 04 decoder-geometry follow-up.

It is prospective with respect to final biological, canonical-null,
C-matched-null, and isotropic geometry comparison. At the time this
specification is frozen, no new final aggregation has been executed and
no private geometry payload has been opened for the final comparison.

---

## 1. Authority and precedence

This specification supersedes
`DECODER_GEOMETRY_AGGREGATION_SPEC.md`
for final decoder-geometry aggregation and comparison.

Where this document conflicts with the historical aggregation specification,
this document governs.

Where this document is silent, provisions of the historical aggregation
specification remain in force unless they conflict with the upstream
decoder-geometry recovery specification or the C-matched reconciliation.

The historical aggregation specification is preserved unchanged as provenance
of the pre-C-matched analysis plan.

Upstream authorities:

- `DECODER_GEOMETRY_BETA_RECOVERY_SPEC.md`
  SHA-256:
  `205d13b20ef5bf9325794274b531f46c9ffa7fa7cc77a7e8bdd0a8be05edce69`

- `DECODER_GEOMETRY_AGGREGATION_SPEC.md`
  SHA-256:
  `59f3b9f27c51dbf46092e4ff276acfe5cca4f5aa3fb7c7d94791a5337b8e55d2`

- `DECODER_GEOMETRY_CMATCHED_RECONCILIATION.md`
  SHA-256:
  `2993ce95285b54f6e0c5992298a0ca56bd183bce25b076c3563818a1c8126d4f`

- historical aggregation driver,
  `decoder_geometry_aggregation.py`
  restored to hard-disabled SHA-256:
  `d71787762271c29add94ccf0907da57bdb59e4c651017301fd638a85dcb23a51`

The obsolete historical aggregation driver MUST NOT be executed.

A new final aggregation driver must cite this specification by exact SHA-256
and must be frozen hard-disabled before any authorization to execute.

---

## 2. Scientific status and scope

This is a post hoc Experiment 04 decoder-geometry follow-up.

It gates nothing in Experiment 05.

It does not access the confirmatory universe.

It does not establish:

- causal toxin mechanisms;
- unique toxin specificity;
- cross-family toxin generalization;
- mechanistic decomposition;
- a unique causal explanation for Experiment 03 SAE instability.

All inferential language remains descriptive.

No p-values or PASS/FAIL thresholds are permitted.

---

## 3. Populations

Four populations enter final aggregation.

### 3.1 Biological

Layer-18, N=139 biological Stage-B probe directions.

Expected population size:

`100`

Expected exact-zero beta count:

`0 / 100`

Directional-geometry denominator:

`n = 100`

### 3.2 Canonical permutation null

Layer-18, N=139 canonical permutation-null Stage-B probe directions generated
under the complete frozen Phase-P procedure, including the original
model-selection behavior.

Expected population size:

`100`

Previously established exact-zero beta count:

`37 / 100`

Directional-geometry denominator:

`n = 63`

The 37 exact-zero beta directions remain a separate structural population
outcome. They MUST NOT be assigned fabricated R(k), top-k mass, N_eff, or any
other directional geometry value.

### 3.3 C-matched permutation null

Post hoc secondary marginal selected-C-distribution-matched permutation
control specified by the upstream recovery contract.

Expected population size:

`100`

Previously established exact-zero beta count:

`0 / 100`

Directional-geometry denominator:

`n = 100`

The ordinal mapping between biological and C-matched null perturbations is
bookkeeping only. It does NOT create a paired biological-vs-C-matched design.

### 3.4 Isotropic reference

Frozen isotropic decoder-geometry reference.

Expected population size:

`1000`

Directional-geometry denominator:

`n = 1000`

This is a geometric reference, not a biological label null.

---

## 4. Primary and secondary comparison hierarchy

### 4.1 Primary comparison

The primary scientific comparison remains:

**biological vs canonical permutation null**

This hierarchy is retained because the canonical permutation null preserves
the complete frozen Phase-P randomized-label procedure, including realized
model-selection behavior and the possibility of an exactly zero Stage-B
direction.

The previously observed `37 / 100` exact-zero canonical-null directions do
not change the primary comparison.

### 4.2 Secondary geometric reference

The secondary geometric-reference comparison is:

**biological vs isotropic**

This asks whether the biological supervised directions have unusual decoder
compactness relative to generic directions in the 1280-dimensional
representation space.

### 4.3 Secondary regularization-distribution sensitivity control

The secondary regularization-sensitivity comparison is:

**biological vs C-matched permutation null**

The C-matched control deliberately imposes the realized biological selected-C
multiset on randomized-label Stage-B fits. It therefore conditions away one
aspect of the complete canonical randomized-label procedure and answers a
narrower sensitivity question.

It is not a replacement for the canonical null and MUST NOT be promoted to
primary based on result magnitude.

### 4.4 Additional descriptive diagnostics

The following are retained for symmetric diagnostic completeness:

- canonical null minus isotropic;
- canonical null minus C-matched null;
- C-matched null minus isotropic.

These are descriptive diagnostics only.

---

## 5. Frozen metrics

The headline directional metric is:

**median R(32)**

Companion metrics are:

- median top-32 raw decoder-weight mass;
- median N_eff.

The previously frozen complete OMP k-grid remains:

`1, 2, 4, 8, 16, 32, 64, 128, 256, 512`

Threshold-grid and numerical/rank diagnostics remain as specified upstream.

No metric may be added, removed, replaced, transformed, or promoted after
result inspection begins.

---

## 6. Bootstrap uncertainty

Bootstrap root seed:

`2026090801`

Number of replicates:

`10000`

Generator construction:

`numpy.random.Generator(numpy.random.PCG64(...))`

Each named stream uses:

`numpy.random.SeedSequence(2026090801, spawn_key=(stream_id,))`

Bootstrap intervals are descriptive percentile intervals only.

### 6.1 Single-population median

For each population/metric:

1. resample n observations with replacement from that population;
2. compute the median;
3. repeat 10,000 times;
4. report the 2.5th and 97.5th percentiles.

### 6.2 Difference of independent population medians

For each comparison/metric:

1. independently resample each population with replacement at its own observed
   directional-geometry denominator;
2. compute each bootstrap median;
3. subtract in the frozen comparison order;
4. repeat 10,000 times;
5. report the 2.5th and 97.5th percentiles.

No paired bootstrap is permitted for biological vs C-matched null.

No BCa interval, studentized interval, permutation p-value, or alternative
resampling scheme may be substituted after results are opened.

---

## 7. Frozen bootstrap stream map

Historical stream IDs `0–17` are preserved exactly and may not be renumbered,
renamed, or repurposed.

C-matched extensions occupy IDs `18–29` only.

| ID | Stream name |
|---:|---|
| 0 | `bio_r32_median` |
| 1 | `null_r32_median` |
| 2 | `iso_r32_median` |
| 3 | `bio_top32_median` |
| 4 | `null_top32_median` |
| 5 | `iso_top32_median` |
| 6 | `bio_neff_median` |
| 7 | `null_neff_median` |
| 8 | `iso_neff_median` |
| 9 | `bio_minus_null_r32` |
| 10 | `bio_minus_iso_r32` |
| 11 | `null_minus_iso_r32` |
| 12 | `bio_minus_null_top32` |
| 13 | `bio_minus_iso_top32` |
| 14 | `null_minus_iso_top32` |
| 15 | `bio_minus_null_neff` |
| 16 | `bio_minus_iso_neff` |
| 17 | `null_minus_iso_neff` |
| 18 | `cmatched_r32_median` |
| 19 | `cmatched_top32_median` |
| 20 | `cmatched_neff_median` |
| 21 | `bio_minus_cmatched_r32` |
| 22 | `bio_minus_cmatched_top32` |
| 23 | `bio_minus_cmatched_neff` |
| 24 | `null_minus_cmatched_r32` |
| 25 | `null_minus_cmatched_top32` |
| 26 | `null_minus_cmatched_neff` |
| 27 | `cmatched_minus_iso_r32` |
| 28 | `cmatched_minus_iso_top32` |
| 29 | `cmatched_minus_iso_neff` |

The subtraction order encoded in the stream name is authoritative.

---

## 8. Structural population accounting

Before directional summaries are inspected, report:

- biological total and exact-zero beta count;
- canonical-null total and exact-zero beta count;
- C-matched-null total and exact-zero beta count;
- isotropic total;
- eligible directional-geometry denominators for all four populations.

Expected structural accounting before aggregation:

- biological: `0 / 100` exact-zero beta;
- canonical null: `37 / 100` exact-zero beta;
- C-matched null: `0 / 100` exact-zero beta;
- isotropic: `1000` complete geometry directions.

Any mismatch stops interpretation.

---

## 9. Final inspection order

After all integrity checks succeed, inspect results in this exact order:

1. structural population accounting;
2. biological median R(32);
3. canonical-null-eligible median R(32);
4. primary biological-minus-canonical-null R(32) bootstrap interval;
5. isotropic median R(32);
6. biological-minus-isotropic R(32) bootstrap interval;
7. C-matched-null median R(32);
8. secondary biological-minus-C-matched R(32) bootstrap interval;
9. canonical-null-minus-C-matched R(32) descriptive bootstrap interval;
10. C-matched-minus-isotropic R(32) descriptive bootstrap interval;
11. top-32 raw-weight-mass population summaries and pairwise comparisons in
    the same comparison hierarchy;
12. N_eff population summaries and pairwise comparisons in the same comparison
    hierarchy;
13. full frozen R(k) grid;
14. threshold-grid diagnostics;
15. rank and numerical diagnostics;
16. integrated descriptive interpretation under the frozen interpretation map.

No method, comparator, denominator, metric, exclusion rule, bootstrap stream,
or reporting hierarchy may be changed after item 2 is observed.

---

## 10. Integrity requirements

The final driver must verify, before summarization:

- exact expected population counts;
- exact expected zero-direction counts;
- exact IDs where applicable;
- exact engine/spec/provenance identities;
- exact completion-manifest identities for private geometry populations;
- exactly one geometry record per expected eligible direction;
- no duplicate IDs;
- finite values;
- frozen-grid completeness;
- R(k) monotonicity;
- top-k-mass monotonicity;
- rank-deficiency counts;
- exact-reconstruction counts;
- missing frozen-grid-value counts;
- consistency of all private-record hashes with their completion manifests.

Any unexpected integrity violation stops interpretation.

---

## 11. Storage-only isotropic deviation

The isotropic geometry population was persisted across the historical private
checkpoint dataset and a private overflow dataset for indices 951–999.

This is a storage-only deviation from the original same-dataset checkpoint
plan.

It does not change vector generation, RNG identity, decoder identity, OMP
semantics, population membership, or final aggregation.

The final report must document this deviation before scientific
interpretation.

---

## 12. Interpretation map

The final analysis asks whether the biological supervised probe directions are
represented unusually compactly in the frozen SAE decoder dictionary.

Interpretive possibilities remain descriptive:

- biological substantially more compact than isotropic:
  decoder vocabulary unusually aligned with the biological supervised signal;

- biological not more compact than isotropic:
  full-span accessibility without unusually compact SAE dictionary alignment;

- intermediate result:
  distributed or partial alignment.

Canonical-null and C-matched-null controls refine this interpretation but do
not establish causal mechanism.

The C-matched analysis is explicitly secondary.

---

## 13. Prohibited actions before final-driver freeze

Before the replacement final aggregation driver is itself frozen
hard-disabled:

- do not mount or open private geometry payloads for scientific inspection;
- do not compute R(32) summaries;
- do not compute top-32 mass summaries;
- do not compute N_eff summaries;
- do not run bootstrap;
- do not compare populations;
- do not access confirmatory data;
- do not alter the bootstrap map;
- do not alter the primary/secondary hierarchy.

---

## 14. Required next step

After this specification is committed and pushed:

1. construct a NEW final aggregation driver;
2. bind it to this specification's exact SHA-256;
3. hard-disable it by default;
4. audit it without private-result inspection;
5. freeze and push it;
6. only then create a separate one-line authorization commit;
7. recover exact private populations;
8. perform one final integrity-gated aggregation run;
9. inspect results strictly in Section 9 order.

The obsolete historical aggregation driver remains permanently hard-disabled.
