# Decoder-Geometry Aggregation and Comparison Specification

## Status and scope

This is a post hoc Experiment 04 analysis specification.

It is frozen **after direction-level geometry generation completed but before
the private biological or canonical-null geometry payloads were opened for
population-level analysis**.

This analysis gates nothing in Experiment 05.

No confirmatory-universe data may be accessed.

## Frozen upstream identities

- decoder-geometry engine SHA-256:
  `8289d96a11ee3f5506edf298bf0290f58414454737156c98737f4522642915ab`
- original decoder-geometry / beta-recovery specification SHA-256:
  `205d13b20ef5bf9325794274b531f46c9ffa7fa7cc77a7e8bdd0a8be05edce69`
- completed population manifest SHA-256:
  `a5246082517ca1270a75f48288df9cb03d21d5c6393f3f2daaeb41229a4a0257`
- public population-completion provenance note SHA-256:
  `3a138c6ecd696352d24d1dc322b91b275089831bae2ac047e7d8c016fbad2aa7`
- closed population execution driver SHA-256:
  `b9d789fe73ddf12138c36544dc4d79760469f6b62c04587da90da009f0b566b5`

The completed private population contains:

- 100 biological Stage-B beta directions;
- 100 canonical label-permutation-null Stage-B beta records;
- 100 / 100 biological directions geometry-eligible;
- 63 / 100 canonical-null directions geometry-eligible;
- 37 / 100 canonical-null directions exact-zero and explicitly
  geometry-ineligible.

A previously completed isotropic reference contains exactly 1,000 frozen
isotropic directions.

## Scientific question

The downstream analysis asks:

> Are the biological supervised directions unusually compact or unusually
> aligned with the frozen SAE decoder geometry, relative to canonical
> label-permutation directions and to ordinary isotropic directions?

The analysis is descriptive and post hoc.

It does not establish causal mechanism, toxin specificity, mechanistic
decomposition, or cross-family generalization.

## Population handling

### Biological

All 100 biological records must be present.

All 100 must have:

- `eligibility = eligible_nonzero_beta`;
- `analysis_status = complete`;
- geometry status `complete`.

No biological row may be silently excluded.

### Canonical permutation null

All 100 canonical-null records must remain in population accounting.

Exactly:

- 63 must be `eligible_nonzero_beta`;
- 37 must be `ineligible_zero_beta`.

The 37 exact-zero beta directions are a separate structural outcome.

They MUST NOT be assigned:

- reconstruction score zero;
- reconstruction score one;
- raw-weight concentration zero;
- raw-weight concentration one;
- artificial threshold values;
- artificial N_eff.

They are excluded only from quantities mathematically requiring a nonzero
direction.

Therefore:

- canonical-null zero-beta frequency is reported as **37 / 100**;
- geometry-distribution summaries use the **63 eligible null directions**;
- the denominator 63 must be printed next to every canonical-null
  geometry summary.

No analysis may silently describe the 63 eligible null directions as
"100 null directions".

### Isotropic reference

The isotropic population is the already-completed frozen set of exactly
1,000 directions.

No timing rerun is permitted.

No isotropic direction is regenerated merely to alter or replace the frozen
reference.

## Frozen geometric quantities

For every eligible direction, use the already-generated frozen engine output
only.

No geometry is recomputed.

### OMP reconstruction

For:

`k = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512`

extract:

`geometry["omp"]["r_by_k"][str(k)]`

The headline reconstruction quantity is:

**R(32)**.

R(k) remains descriptive reconstruction fraction under the frozen OMP
procedure.

### OMP threshold quantities

Also retain descriptively:

- `threshold_k_50`
- `threshold_k_80`
- `threshold_k_90`

No numeric interpolation between grid values is allowed.

The literal `">512"` remains a categorical value and must not be converted to
513 or another invented number.

### Raw-weight concentration

For every k in the same frozen grid, extract:

`geometry["raw_weight"]["topk_mass"][str(k)]`

The headline raw-weight concentration quantity is:

**top-32 absolute decoder-weight mass**.

Also retain:

`geometry["raw_weight"]["n_eff"]`

as the effective-number-of-atoms concentration descriptor.

No new concentration metric may be introduced after results are opened.

## Integrity requirements

Before computing any population statistic:

1. verify the completed population-manifest SHA-256;
2. verify all 200 per-record SHA-256 values against that manifest;
3. require exactly 200 unique population records;
4. require exactly 100 biological IDs 1000001--1000100;
5. require exactly 100 canonical-null IDs 1100001--1100100;
6. require biological eligible / zero counts 100 / 0;
7. require canonical-null eligible / zero counts 63 / 37;
8. for every eligible record require geometry status `complete`;
9. require every R(k) value to be finite and in [0,1];
10. require every top-k mass value to be finite and in [0,1];
11. require R(k) nondecreasing over the frozen k-grid within the frozen
    numerical tolerance;
12. require top-k mass nondecreasing over the frozen k-grid;
13. verify the frozen 1,000-vector isotropic archive before using it.

Any integrity failure stops analysis.

It does not authorize repair, exclusion, replacement, or tuning.

## Population summaries

For each of:

- biological eligible directions, n=100;
- canonical-null eligible directions, n=63;
- isotropic directions, n=1000;

report for every frozen k:

- n;
- mean R(k);
- median R(k);
- 2.5th percentile R(k);
- 97.5th percentile R(k);
- mean top-k mass;
- median top-k mass;
- 2.5th percentile top-k mass;
- 97.5th percentile top-k mass.

For N_eff report:

- n;
- mean;
- median;
- 2.5th percentile;
- 97.5th percentile.

Headline descriptive values are:

1. median R(32);
2. median top-32 mass;
3. median N_eff.

The full frozen k-grid must still be retained in the output.

## Primary comparisons

The primary scientific comparison is:

**biological versus canonical permutation null**.

Because the canonical null contains 37 exact-zero beta directions, the
directional geometry comparison is necessarily:

- 100 biological eligible directions;
- 63 canonical-null eligible directions.

The zero-null frequency 37 / 100 is reported separately and must accompany
this comparison.

For each headline quantity compute:

- biological median;
- canonical-null eligible median;
- difference:
  biological median minus canonical-null eligible median.

No p-value is computed.

No thresholded PASS/FAIL verdict is computed.

## Isotropic geometric reference

The secondary geometric-reference comparison is:

**biological versus frozen isotropic reference**.

For each headline quantity compute:

- biological median;
- isotropic median;
- difference:
  biological median minus isotropic median.

Direction of interpretation is metric-specific:

- larger R(32) = more compact reconstruction at k=32;
- larger top-32 mass = more decoder-weight concentration;
- smaller N_eff = more decoder-weight concentration.

Therefore N_eff must not be interpreted using the sign convention for R(32).

The isotropic population is a geometric reference, not a biological
significance null.

## Canonical-null versus isotropic context

Also report canonical-null-eligible versus isotropic median differences for
the same headline quantities as descriptive context.

This is not a separate hypothesis test.

## Bootstrap uncertainty

Bootstrap root seed:

`2026090801`

Number of replicates:

`10000`

Generator:

`numpy.random.Generator(numpy.random.PCG64(...))`

Bootstrap estimates are descriptive percentile intervals only.

For a single-population median:

1. sample n observations with replacement from that population;
2. compute the median;
3. repeat 10,000 times;
4. report the 2.5th and 97.5th percentiles.

For a difference of independent population medians:

1. independently resample each population with replacement at its observed n;
2. compute each bootstrap median;
3. subtract in the frozen order;
4. repeat 10,000 times;
5. report the 2.5th and 97.5th percentiles.

Population sizes remain:

- biological = 100;
- canonical-null eligible = 63;
- isotropic = 1000.

The 37 exact-zero null directions are NOT injected into directional bootstrap
samples with fabricated geometry values.

They remain reported separately as 37 / 100.

Bootstrap RNG streams must be deterministically separated by comparison and
metric from the frozen root seed. The implementation driver must define the
exact deterministic child-stream mapping before analysis is authorized.

No BCa interval, studentized interval, permutation p-value, or alternative
resampling method may be substituted after results are opened.

## Threshold-grid summaries

For each eligible population, summarize the empirical proportions whose
frozen threshold category is:

- reached by k <= 32;
- reached by k <= 64;
- reached by k <= 128;
- reached by k <= 256;
- reached by k <= 512;
- `>512`.

Do this separately for threshold 0.50, 0.80, and 0.90.

If a frozen engine record is rank-deficient and a threshold is unavailable,
retain it explicitly as unavailable rather than coercing it into `>512`.

These summaries are secondary descriptive diagnostics.

## Rank / numerical-integrity diagnostics

Report, by population:

- geometry status counts;
- OMP status counts;
- rank-deficient count;
- exact-reconstruction count;
- missing frozen-grid value count;
- R(k) monotonicity violation count;
- top-k-mass monotonicity violation count.

Any unexpected integrity violation stops interpretation.

## Result order

After successful integrity verification, results are inspected in this order:

1. structural population accounting;
2. headline biological R(32);
3. headline canonical-null-eligible R(32);
4. headline isotropic R(32);
5. biological-minus-null R(32) bootstrap interval;
6. biological-minus-isotropic R(32) bootstrap interval;
7. top-32 raw-weight mass comparisons;
8. N_eff comparisons;
9. full frozen k-grid;
10. threshold-grid diagnostics;
11. rank/numerical diagnostics.

No method, comparator, metric, or exclusion rule may be changed after item 2
is observed.

## Interpretation map

Possible descriptive patterns include:

### Biological more compact than null and isotropic

If biological directions show materially higher R(32), higher top-32 mass,
and/or lower N_eff than both reference populations, that is consistent with
the SAE decoder vocabulary being unusually aligned with the supervised
biological signal despite the earlier SAE feature-stability failure.

It does not establish a mechanistic decomposition.

### Biological similar to isotropic

If biological geometry resembles the isotropic reference, the decoder may span
the supervised directions without organizing them into unusually compact SAE
coordinates.

This would support a distributed / basis-misalignment interpretation more than
a compact-feature interpretation.

### Biological intermediate

If biological geometry is more compact than isotropic but still requires many
atoms, the appropriate interpretation is partial or distributed alignment.

### Canonical null complications

The exact-zero canonical-null frequency is itself informative about the sparse
probe under permuted labels but must not be conflated with decoder geometry.

The zero-beta phenomenon cannot be used to manufacture stronger geometric
separation.

## Statistical boundary

This follow-up remains:

- post hoc;
- discovery-only;
- descriptive;
- non-confirmatory.

No p-values are required.

No PASS/FAIL scientific gate is defined.

No Experiment 05 decision depends on this result.

## Prohibited claims

This analysis cannot establish:

- causal toxin mechanism;
- toxin-specific decoder atoms;
- unique causal explanation of Experiment 03;
- cross-family toxin generalization;
- confirmatory signed-support stability;
- that a particular atom is a biological mechanism;
- that decoder span membership is meaningful by itself.

The decoder is full rank in the 1,280-dimensional representation space, so the
scientifically meaningful object here is compact reconstruction / concentration,
not mere span inclusion.
