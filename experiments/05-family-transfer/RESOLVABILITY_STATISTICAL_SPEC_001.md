# Formal Gate B statistical specification 001

Status: frozen assumptions for a disabled simulator to be implemented next.
No simulation is implemented or authorized by this specification.

## 1. Scope and geometry

Use both archived allocations unchanged. Preserve their actual group membership,
label composition and discovery-overlap flags. Calibration positives remain
unused. Evaluation uses its retained positives and negatives. Never substitute
161 evaluation positives when the allocation retains 155 or 154.

Groups are operational sequence-cluster intersections, not established independent
biological families. The model below ASSUMES independence across groups. This is
a conditional feasibility analysis, not evidence that the assumption is true.
Within-group synthetic records are exchangeable; exact duplicate sequences are
not forced to have identical synthetic scores. Discovery is not re-fit or simulated.
Training overlap, memorization, parameter-estimation uncertainty and dependence
between different operational groups are not modeled. No favorable result clears
these limitations or the unverified historical family-separation criterion.

## 2. Primary and secondary estimands

Primary sensitivity and FPR average each bearing group's within-label fraction,
then average equally across label-bearing evaluation groups. For calibration
negatives, each bearing group gets equal total weight and its negative records
share that weight equally. Mixed groups contribute separately to each label.

The population target is the difference between arms' marginal positive
exceedance probabilities at each arm's population 95th-negative percentile.
This is the ideal population-calibrated DeltaTPR. The finite-sample estimator
uses independently estimated calibration thresholds; bootstrap intervals must
include that calibration uncertainty. Finite-calibration bias is measured against
the ideal target and is not silently redefined as a different truth.

Secondary sensitivity and FPR are record-weighted at the SAME primary-calibrated
thresholds. They do not answer a separately protein-calibrated 5% FPR question,
never replace the primary decision, and must be labelled accordingly.

## 3. Threshold, ties and inference target

For each arm independently, threshold is the smallest observed calibration-negative
score whose primary-weighted empirical CDF is at least 0.95. Call a record positive
only when score > threshold. Aggregate equal scores before selecting the quantile.
No interpolation, randomized ties, evaluation recalibration or forced realized 5%
FPR is allowed. The calibration tail is at most 5%; evaluation FPR is measured,
not constrained to equal 5%. Empty calibration support yields an explicit failure.

Report calibration CDF jump at the selected threshold (attainable resolution),
threshold value, realized calibration FPR, evaluation FPR and transfer error.
For the continuous null-negative generator, the population threshold is
z = Phi^{-1}(0.95). Record threshold error relative to z.

## 4. Paired synthetic score generator

No biological model is loaded. Use group IDs and labels only.
For every operational group g draw a standard bivariate normal G_g; for every
record i draw an independent standard bivariate normal E_i. Each pair represents
(comparator, ESM), with correlation r. All G and E draws are mutually independent
except these declared correlations. Use the same G_g across both labels of a
mixed group. For arm m:

    score_i,m = mu_label,m + sqrt(rho)*G_g,m + sqrt(1-rho)*E_i,m

Negative means are zero in both arms. Positive means are
mu_comparator = z + Phi^{-1}(b), mu_ESM = z + Phi^{-1}(b + delta).
Thus marginal population TPRs at z are b and b+delta and true DeltaTPR is delta.
Every grid combination has 0 < b < b+delta < 1, except delta=0 equality of TPRs.
These are LATENT score correlations, not asserted binary-outcome correlations.
Report realized paired positive discordance descriptively within simulations.
Group size and class do not alter the marginal score distribution.

Surface grids: b in {0.30,0.60}; rho in {0,0.30,0.80}; r in {0.25,0.75};
delta in {0,0.05,0.10,0.15,0.20}; both archived allocations. This is 120 cells.
Do not select a regime because it matches a desired power verdict.

## 5. Interval and bootstrap pairing

Use a single prespecified method: paired group percentile bootstrap with 999
replicates per outer simulated dataset. No interval-method competition is run.
Independently resample calibration negative-bearing groups and evaluation groups,
with replacement, retaining their original number of groups in each partition.
The evaluation sampling frame includes ALL groups bearing any evaluation label.
Within each draw retain all records, both arms and labels of the sampled group.
Do not resample proteins within groups. A duplicated group is a duplicated unit;
its within-label mean enters once per selection. This preserves mixed-label and
cross-arm dependence while allowing random label-bearing counts in replicates.

Refit both calibration thresholds for every bootstrap draw, transfer them to the
resampled evaluation data, and calculate paired DeltaTPR. Quantiles of bootstrap
DeltaTPR use linear interpolation at index (n-1)*p, p=.025 and .975. No clipping,
studentization, continuity correction or post-hoc interval switch is permitted.

An outer replicate with undefined bootstrap estimates is recorded as failed;
do not discard invalid bootstrap draws to manufacture an interval. Report reasons
and counts. Coverage/rejection indicators use the total requested outer budget;
failed outer replicates contribute no successful coverage or rejection. Width
summaries are conditional on defined intervals and accompanied by failure counts.
Any power/width conclusion with failed intervals is explicitly inconclusive;
this does not change the inherited rule that failure rate itself is a report,
not a new numerical simulator-acceptance threshold.

## 6. Known-answer validation and firewall

Before any surface generation or access, validate BOTH actual allocations with
b=.60, rho=.30 and r=.50. These are fixed instrument-validation assumptions,
not empirically estimated or asserted typical biological conditions.

V1: 10,000 outer datasets per allocation at delta=0. For a defined 95% interval,
reject the null if zero is strictly outside it. Two-sided empirical type-I error
must lie in [.030,.070] in EACH allocation.

V2: 2,500 outer datasets for EACH allocation at EACH delta in {.05,.10,.20}.
Coverage includes endpoint equality and must lie in [.93,.97] in every cell.
Also record estimate bias, interval width and failures.

V3 deterministic fixtures, using both allocations:
- Perfect separation: all negative scores=0 and all positive scores=1 in both
  arms. Threshold=0, FPR=0, both TPRs=1, DeltaTPR=0; a degenerate interval is valid.
- Adjacent negative scores: assign distinct scores in stable identifier order.
  Record the selected observed threshold, its next distinct score and the open
  gap between them; all thresholds inside that gap induce the same strict-tail
  calls. Never silently substitute interpolated threshold values.
- Tied negatives: all negative scores=0, with identical deterministic positive
  score fixtures across arms. Report defined ties and achieved FPR=0.
Record expected results and exact fixture algorithms in the disabled code/audit
before authorization; do not use real model scores to construct a fixture.

All V1-V3 must pass before the surface can be generated. Separate validation and
surface runners, archives and authorization gates enforce this order structurally.
A valid method failing calibration is rejected; it is not relabelled a scientific
resolvability failure. Repairs and prospective statistical amendments follow the
inherited failure-classification rules. No automatic retries or seed searches.

## 7. Surface budget, reports and decision rule

After separately archived passing validation and separate authorization, generate
1,000 outer datasets in each of the 120 surface cells. Use 999 nested bootstrap
replicates. This entails 35,000 validation outer datasets and 120,000 surface
outer datasets (154,845,000 nested bootstrap replicates, excluding fixtures).
Budget is material: implement chunking/checkpoints and benchmark synthetic-only
computational fixtures before authorization. A resource problem does not license
silently reducing replicate counts, skipping cells or changing methods.

For each cell report rejection probability, positive-effect power (lower interval
bound >0), coverage, estimate bias, median interval half-width, failures, paired
positive discordance, calibration quantile resolution, threshold variation,
evaluation-FPR distribution and error relative to .05, and DeltaTPR error relative
to its ideal target. Report primary and descriptive secondary weighting distinctly.
Report Monte Carlo standard errors for indicator rates using the requested budget.
Include the separate calibration/evaluation bearing-group and record counts.

At delta=.10, a cell clears the inherited targets if power >=.80 and median
half-width <=.10, with inference failures reported as inconclusive rather than
an optimistic pass. An allocation is robustly adequate within this grid only if
all twelve baseline/dependence combinations clear both targets. If some clear and
some do not, report regime-dependent feasibility, not a universal verdict. Neither
allocation may be selected for favorable results; report both and their sensitivity.

If no tested allocation clears the targets across the prespecified regimes,
report no robustly adequate allocation within this diagnostic set. These two
allocations are NOT an exhaustive proof about every realistic allocation. A
formal experiment-closure ruling must respect that limit and unresolved
admissibility; no favorable surface result authorizes confirmatory computation.

## 8. Reproducibility

Pin implementation dependencies before authorization. Use NumPy PCG64, seeded
independently per outer dataset and purpose by SHA256 of the canonical compact
JSON token list in the machine specification. Encode numerical grid tokens as
fixed strings with two decimal places, integer indices as integers, UTF-8, no
spaces. Interpret the first 16 digest bytes as an unsigned big-endian integer.
Purpose separates generation and bootstrap streams. No SeedSequence or global
RNG state. Chunk order must not change outputs. Validation and surface phase
names differ; no random draws are reused between them.

Archive settings, source hashes, input identities, per-replicate summaries and
provenance before interpreting reports. Store no empirical protein-model outcomes.
