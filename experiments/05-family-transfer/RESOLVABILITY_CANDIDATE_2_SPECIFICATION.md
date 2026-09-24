# Candidate 2: paired hierarchical bootstrap with nested calibration

Status: prospectively frozen specification only. No implementation, simulation,
benchmark, validation or surface execution is authorized by this commit.
Formal gate: B (resolvability). Candidate 1 remains archived and rejected.
The accompanying exposure record must be read first.

## 1. Rationale, target and limits

Select the hierarchical-bootstrap option listed in RESOLVABILITY_PLAN, with
within-group protein sampling explicitly part of the diagnostic target.
This is a separately named sampling procedure, not an adjusted Candidate 1
interval. It retains percentile endpoints but adds paired within-group record
resampling; Candidate 1 code and archives are not overwritten.

The target is a hypothetical superpopulation: draw an operational group, then
exchangeable proteins within that group's label stratum. Primary rates weight
label-bearing groups equally, then proteins equally within the label stratum.
Condition on observed per-group label counts and on the archived allocations.
This is NOT uncertainty solely about the fixed finite accession census.
There is no evidence that these operational groups are independent biological
families or that the observed proteins are a random sample. These are stated
working assumptions, not findings. No favorable simulation clears admissibility.

Retain the inherited Gaussian random-effects DGP, primary population estimand,
fixed geometry, thresholds, effect grid, dependency regimes and scientific targets.
That DGP already makes records conditionally exchangeable given group effects.
This amendment makes the two-level superpopulation interpretation explicit.
Mixed-label groups share their outer group draw and latent group effects;
conditional record draws are independent across distinct label strata.

Hierarchical resampling can compound uncertainty already represented by group
resampling, particularly for small strata. Singleton strata cannot estimate
within-group heterogeneity. All retained evaluation positive strata here are
singletons: their inner resampling adds no variation. Additional variation mainly
enters through negatives, including calibration. Narrower intervals are neither
expected by specification nor an acceptance objective. Validation tests adequacy;
it does not establish that the assumed sampling model describes real proteins.

Methodological background: Saravanan, Berman and Sober (2020), Application of
the hierarchical bootstrap to multi-level data in neuroscience,
https://pmc.ncbi.nlm.nih.gov/articles/PMC7906290/ . This motivates sequential
resampling at nested levels, not a guarantee for this paired threshold estimand.

## 2. Exact estimator and threshold convention

Use the unchanged two archived allocations and all their retained records.
Calibration positives are unused. The point estimator is identical to Candidate 1.
For each arm, calibration negative groups have equal mass and each group's
negative records share its mass equally. Threshold = smallest observed score
whose weighted CDF is >=0.95. Tied scores aggregate; prediction is score > threshold.
No interpolation between calibration scores or randomized threshold ties.
Primary evaluation rates average within-label group rates equally. Secondary
record-weighted rates use the same primary-calibrated thresholds.

The target delta is the difference between marginal positive exceedance
probabilities at the population negative 95th percentiles, as inherited.
Finite calibration thresholds remain estimated and uncertain.

## 3. Exact paired hierarchical resampling

For EACH outer dataset generate 999 independent bootstrap replicates.
For EACH bootstrap replicate:

1. Sample C calibration negative-bearing group IDs with replacement from the C
   observed IDs, uniformly. Sample E evaluation group IDs with replacement from
   ALL E evaluation groups, uniformly, independently of the calibration draw.
   A selected mixed evaluation group carries both labels. Do not draw arms or
   label-bearing evaluation group lists independently.
2. For EACH selected group occurrence and each relevant nonempty label stratum,
   sample n records with replacement from that group's n records of that label.
   Use one sampled index vector for BOTH model scores. Different occurrences
   of the same selected group get independent inner samples. Never reuse a
   single inner sample multiplied by the group's outer multiplicity.
3. Calibration resamples negatives only. In evaluation, sample positive then
   negative strata if present. Counts and labels per occurrence remain fixed.
   Singleton draws reproduce their record. Empty strata remain absent.
4. Refit both thresholds using resampled calibration groups and records. Give
   each group occurrence equal mass; its n resampled records each receive 1/n
   of that mass. Apply those thresholds unchanged to the resampled evaluation.
5. Within each arm and label, average each occurrence's within-label fraction,
   then equally average occurrences bearing that label. Compute paired delta
   from the two arms using the SAME group and inner-record samples. Secondary
   record-weighted rates count every resampled occurrence and record.

Compute the 95% interval from the 999 delta values using 0.025 and 0.975
quantiles with linear interpolation at index (999-1)*p. No clipping,
studentization, bias correction, normal-width adjustment, smoothing or jitter.

## 4. Endpoint and failure rules

Coverage includes equality at either endpoint. Reject a null delta0 only if
lower > delta0 OR upper < delta0. A boundary equal to the null does NOT reject.
Positive-effect detection requires lower > 0. These are unchanged from Candidate 1.
The point-estimate grids include 1/155 and 1/154, depending on allocation;
bootstrap label denominators and interpolated endpoints need not have that grid.
The rule applies to exact computed values; no equality tolerance or rounding.

A bootstrap replicate lacking an evaluation label makes that entire outer
inference undefined. Do not discard bad replicates, replace them, or resample
until both labels occur. Undefined outer inferences count as no coverage/no
rejection using the full requested denominator. Report their reasons; report
width conditional on defined intervals. Any inference failures bar a favorable
scientific precision conclusion. Integrity failures stop execution for the
existing implementation-failure classification process, not silent repair.

## 5. Validation, surface and complete reporting battery

Inherit all numerical settings from resolvability_statistical_spec_001.json.
V1: both allocations, b=.60, rho=.30, r=.50, delta=0; 10000 outer replicates
PER allocation. Null rejection acceptance [0.030,0.070], inclusive.
V2: same regime, delta=.05,.10,.20; 2500 outer replicates per cell.
Coverage acceptance [0.93,0.97], inclusive, EACH cell.
V3: perfect separation, adjacent calibration negative scores with a threshold
comparison inside the gap, and tied negative scores, BOTH allocations.
All fixtures must return defined recorded results. Preserve the frozen fixture
semantics; the adjacent-gap equivalence concerns calibration calls, not necessarily
evaluation calls. Complete every prespecified validation cell; no early stopping
based on a rate. Do not generate or read a surface until ALL V1/V2/V3 pass,
validation is independently audited, archived and closed, and surface execution
receives its own authorization.

Declare six reports: type-I error, coverage, power, interval width, failure rate,
and boundary behavior. Report Monte Carlo standard errors and denominators.
Validation reports type-I error, coverage, width, failure and boundary behavior.
Surface power is NOT_EVALUATED_VALIDATION_FAILED when validation fails; completeness
does not authorize accessing a blocked surface. Do not mine positive-rejection
rates from validation to substitute for the power surface.

After passing validation only: retain inherited 120-cell surface, 1000 outer
replicates per cell, both allocations, all baseline/dependence/effect regimes.
Target remains >=80% power at delta=+.10 and median half-width <=.10, with the
inherited across-regime aggregation. Report the same calibration quantile
resolution, threshold variability, transferred evaluation FPR uncertainty,
paired discordance, bias, secondary rates and concentration sensitivity.
No allocation or regime is selected because its power or width is favorable.

## 6. Fresh randomness and reproducible execution

Use NumPy 2.0.2 PCG64, Python 3.12.13. Canonical token-list JSON is compact
separators (comma, colon), ASCII encoding. SHA-256 first 16 bytes big-endian
integer seeds PCG64 directly. Tokens in order:
[root, candidate, phase, allocation, b, rho, r, delta, outer_index, purpose].
Root=20260924, candidate='hierarchical_v2'; b/rho/r/delta are fixed two-decimal
strings. Phase is validation_v1, validation_v2, boundary, surface or benchmark.
Purpose is generation or bootstrap. These streams are disjoint in naming from
Candidate 1. No seed search. Outer index is zero-based integer.
For boundary cells use b=.60,rho=.30,r=.50,delta=.00 and fixture index 0,1,2.

Within a bootstrap RNG stream, loop bootstrap replicate ascending. Draw the full
calibration group-index vector, then the full evaluation group-index vector,
using Generator.integers(0,G,size=G). Next process calibration occurrences in
sampled-vector order, then evaluation occurrences in sampled-vector order;
within evaluation visit positive then negative labels. Inner draws use
Generator.integers(0,n,size=n). Sort source group IDs and source record IDs by
ASCII bytes before indexing. Do not vectorize by merging occurrences unless
byte-identical draws and results are demonstrated. Output must be invariant to
batching, checkpoint boundaries, worker scheduling and input insertion order.
Retain the inherited score-generation algorithm; only its stream namespace changes.

Checkpoint and provenance bind candidate settings, implementation hashes,
execution HEAD, allocation inputs, environment, and replicate indices. Publish
on the same filesystem. No automatic retry, no unrecorded resume or budget increase.
Runtime timing uses synthetic fixtures only and needs separate authorization.

## 7. Selection and stopping

Candidate 1 is ineligible. Candidate 2 is the ONLY replacement specified here.
If Candidate 2 passes all validation, it is selected for its separately authorized
surface. A later candidate cannot displace it based on power or width, and an
unfavorable valid surface does not reopen method selection.
If Candidate 2 fails, its surface stays blocked. No Candidate 3 is implemented
or authorized here. At most one further candidate may be prospectively specified
under a new amendment, with exposure recorded and fresh streams; no third
replacement is permitted in this experiment. That later method must be completely
fixed before its own runs. Selection priority is fixed now: earliest eligible
candidate in order 2 then 3, never comparison of power or width. If both are ever
validated, 2 has priority. If all permitted methods fail, close the resolvability
attempt unresolved. A later amendment is adaptive, not retrospectively blind.

## 8. Implementation and synthetic audit obligations

Implement in new candidate-specific files with independent false authorization
gates for benchmark, validation and surface. Bind this specification and settings.
Do not rewrite Candidate 1 or its output archives. Reuse verified deterministic
utilities only with explicit source hashes; source reuse does not change identity.
Synthetic fixtures must test: paired score indices; mixed-label group conservation;
independent inner draws for repeated group occurrences; exact weights with unequal
stratum sizes; singleton and absent-label behavior; refitting thresholds inside
every replicate; observed-score/tie conventions; exact endpoint-null rules;
all V3 outcomes; malformed inputs; deterministic stream and batch/order invariance;
and rejection of surface access without committed passing Candidate 2 validation.
No production geometry or simulations are loaded by the synthetic audit.
Then: isolated authorization, validation once, independent audit, archive, closure.
