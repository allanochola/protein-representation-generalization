# Experiment 04 follow-up — decoder geometry and beta-recovery specification

**Status:** FROZEN BEFORE BETA RECOVERY OR DECODER-RECONSTRUCTION ANALYSIS

## 1. Purpose

This is a post hoc explanatory follow-up to the closed Experiment 04 discovery
analysis. It does not alter the Experiment 04 verdict, open the confirmatory
universe, or authorize any new biological hypothesis test.

The follow-up asks:

> How compactly can the supervised layer-18 probe directions recovered from
> Experiment 04 be represented using directions from the exact frozen InterPLM
> layer-18 SAE decoder, and how concentrated are those directions over the raw
> decoder columns?

This analysis gates nothing in Experiment 05.

The analysis is descriptive and explanatory. It has no hypothesis-test
PASS/FAIL threshold and does not modify any previously frozen Experiment 04
decision rule.

## 2. Confirmatory firewall

No confirmatory-universe protein, representation, label, output, statistic, or
artifact may be opened or used.

The analysis is restricted to:

- the already-consumed Experiment 04 discovery universe;
- the already-frozen Experiment 04 permutation-null paths;
- persisted artifacts required to verify those paths;
- the exact frozen public InterPLM SAE artifact; and
- execution-environment provenance required for deterministic replay auditing.

No confirmatory data are authorized at any stage.

## 3. Frozen SAE artifact

The decoder is exactly the Experiment 03 frozen SAE:

- repository: `Elana/InterPLM-esm2-650m`
- revision: `5121c4c7f3ad0b5fbe0f3b9a457969192bb9912f`
- file: `layer_18/ae_normalized.pt`
- SHA-256:
  `bf0dfb992321cf4d1ce80fced0db0256f5c7a1f9fdd8a7fe4834e786c1f6472a`
- decoder tensor: `decoder.weight`
- frozen shape: `1280 x 10240`

The exact decoder was verified before this specification was frozen.

Observed decoder geometry:

- strict/default numerical rank: 1280
- relative rank at 1e-3: 1280
- relative rank at 1e-4: 1280
- relative rank at 1e-6: 1280
- entropy effective rank: 548.421320551186
- 99% spectral-energy dimension: 1203
- 99.9% spectral-energy dimension: 1268
- exact zero-norm decoder atoms: 9
- usable nonzero atoms: 10231

Because the decoder spans the complete 1280-dimensional ambient space,
ordinary decoder-span projection is mathematically vacuous and will not be
used as a scientific statistic.

## 4. Two frozen decoder representations

Two distinct decoder representations are used for two distinct questions.

### 4.1 Raw decoder: `D_raw`

`D_raw` is the exact checkpoint tensor `decoder.weight`, shape
`1280 x 10240`, converted to float64 without column normalization.

It is used only for the raw decoder-weight/concentration analysis defined
below.

The nine zero-norm columns remain present in `D_raw` and therefore contribute
exactly zero weight.

### 4.2 Unit-direction decoder: `D_unit`

For sparse directional reconstruction:

1. identify and exclude exactly the nine zero-norm decoder columns;
2. preserve each surviving atom's original checkpoint decoder-column index;
3. L2-normalize each remaining decoder column independently;
4. represent all resulting values as float64;
5. do not alter or overwrite the original checkpoint.

The resulting directional dictionary contains exactly 10,231 unit-norm atoms.

`D_unit` is used only for sparse directional reconstruction.

No analysis code may substitute `D_raw` for `D_unit` or vice versa.

### 4.3 Decoder bias

The SAE decoder bias is not used when reconstructing beta.

A supervised probe coefficient beta is a linear functional/direction on
activation space rather than an activation-space point. Decoder bias
contributes an affine constant to activation reconstruction and cannot
participate in representing the orientation of beta itself.

## 5. Probe population

Only the protocol-designated Experiment 04 layer-18 / N=139 paths are eligible.

The two canonical populations are:

- 100 biological perturbations:
  `1000001` through `1000100`;
- 100 permutation-null perturbations:
  `1100001` through `1100100`.

No perturbation may be selected, nominated, removed, replaced, or reordered
based on recovered coefficient geometry.

The primary coefficient for each perturbation is the Stage-B coefficient
vector from the full target-N fit.

The stability-refit coefficient may be used for replay verification or an
explicitly labeled secondary sensitivity analysis only.

## 6. Nature of beta recovery

The full Stage-B coefficient vectors were not serialized in the canonical
Experiment 04 per-perturbation output.

They may therefore be recovered only by deterministic replay of the already
frozen Phase-P runner and seed derivation.

This is artifact recovery for a new post hoc derived analysis. It must not be
represented as recovery of originally committed coefficient magnitudes or
Stage-B support identities.

No recovered beta may enter the decoder-geometry analysis unless the complete
verification-only pass succeeds for all 200 canonical perturbations.

## 7. Execution-environment provenance

Before any replay fit:

1. read the original Phase-P execution-environment provenance from the frozen
   Experiment 04 execution manifest;
2. record the current replay environment;
3. compare the two before fitting.

At minimum record, where available:

- Python version;
- NumPy version;
- SciPy version;
- scikit-learn version;
- BLAS/LAPACK implementation and configuration;
- operating platform;
- architecture;
- `OMP_NUM_THREADS`;
- `OPENBLAS_NUM_THREADS`;
- `MKL_NUM_THREADS`.

Any unavailable field is recorded explicitly as unavailable rather than
inferred.

For both canonical replay passes, set before fitting:

- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`

The Stage-B coefficient SHA-256 identity gate defined below is conditioned on
this single-threaded execution contract.

An environment difference does not authorize changing the replay contract.

If replay verification fails, the environment comparison may be used to
diagnose possible numerical or version drift, but the failed invariant remains
a failed invariant.

No verification requirement may be weakened because the environments differ.

## 8. Mandatory replay verification

Recovery proceeds in two separate passes.

### 8.1 Pass 1 — verification only

Replay all 200 canonical perturbations under the frozen Phase-P procedure and
the single-threaded execution contract in Section 7.

During this pass, coefficient vectors may exist transiently in memory because
the frozen fitting procedure requires them, but no Stage-B or stability
coefficient vector may be retained as an analysis artifact, serialized,
exported, or passed to decoder-geometry analysis.

For every perturbation, compare replay against the corresponding committed
Experiment 04 row.

Require agreement for every applicable persisted invariant:

- perturbation identifier;
- target N = 139;
- representation = `esm_layer_18`;
- `stage_a_eval_auroc`;
- selected C;
- `K_t_full`;
- `K_t_stab`;
- stability membership SHA-256;
- canonical stability unsigned support;
- canonical stability signed support.

For permutation-null rows, also require the frozen replay-membership
verification fields to reproduce according to the existing Phase-P contract.

Pass 1 must continue through all 200 rows even if one or more rows fail.

It must return the complete mismatch set.

### 8.2 Transient Stage-B coefficient identity

For each Pass-1 Stage-B coefficient:

1. convert the coefficient vector to contiguous little-endian float64;
2. require shape exactly `(1280,)`;
3. hash the resulting raw byte sequence using SHA-256;
4. retain only:
   - perturbation identifier;
   - coefficient SHA-256;
   - verification metadata.

The Pass-1 coefficient vector itself must not be retained after its hash has
been produced.

This hash is a recovery-integrity artifact, not an originally committed
Experiment 04 artifact.

### 8.3 Pass-1 acceptance rule

Coefficient recovery is authorized only if Pass 1 returns:

`200 / 200 canonical perturbations verified`.

If one or more rows fail:

1. retain no beta vectors;
2. report the complete mismatch set;
3. do not perform any biological-versus-null decoder-geometry comparison;
4. do not weaken, substitute, or remove a failed verification condition.

### 8.4 Pass 2 — coefficient recovery

Only after Pass 1 returns 200/200 may the same 200 canonical paths be replayed
again under the same single-threaded execution contract.

Pass 2 retains the Stage-B coefficient vectors required for the frozen derived
analysis.

Each Pass-2 row must again reproduce the complete persisted verification
bundle.

Each Stage-B coefficient must also reproduce exactly the SHA-256 recorded from
its transient Pass-1 coefficient.

The required coefficient-hash result is:

`200 / 200 Pass-1 versus Pass-2 Stage-B coefficient hashes identical`.

If any Pass-2 persisted invariant or coefficient hash differs, recovery fails
closed and no decoder-geometry population comparison is produced.

The final report must state both:

- Pass-1 persisted-invariant verification result; and
- Pass-1 versus Pass-2 coefficient-hash agreement result.

`K_t_full` is only a Stage-B support-cardinality check.

The original canonical Experiment 04 output did not persist Stage-B support
coordinates, signs, or coefficient magnitudes. This limitation must be stated
in every report of this follow-up.

## 9. Degenerate beta rule

Before normalization, test every accepted Stage-B beta for exact zero norm.

If

`||beta||_2 == 0`

then:

- do not normalize it;
- exclude it from all direction-based reconstruction and concentration
  statistics;
- count it;
- report the count separately for each population and realized C;
- do not replace it with another perturbation.

A zero-beta row is not a replay-verification failure if all replay invariants
reproduce correctly.

All analysis denominators must state the resulting number of nonzero beta
vectors explicitly.

## 10. Canonical procedure null and regularization comparability

The canonical biological and permutation-null populations were produced by
the same frozen model-selection and fitting procedure, but they need not
realize the same selected C.

They must therefore not be described as "identically fitted."

They are:

> recovered under the identical frozen procedure, with realized regularization
> allowed to differ.

For both populations, report alongside the geometry results:

- full selected-C distribution;
- full `K_t_full` distribution;
- zero-beta count;
- nonzero-beta count.

Differences in realized C and Stage-B support size are an explicit potential
comparability limitation for the canonical biological-versus-null geometry
comparison.

## 11. Secondary marginal C-distribution-matched permutation control

A secondary control is frozen before coefficient recovery to examine the
effect of realized regularization.

Map perturbations by ordinal index:

- biological `1000001` -> null `1100001`;
- biological `1000002` -> null `1100002`;
- ...
- biological `1000100` -> null `1100100`.

This index mapping is arbitrary bookkeeping.

It does not assert that an individual biological perturbation corresponds
scientifically or statistically to the null perturbation with the same ordinal
index.

Its sole purpose is to transfer the complete realized biological selected-C
multiset onto the 100 null fits.

Therefore this arm provides marginal C-distribution matching only.

It must not be interpreted as a paired biological-versus-null design.

For secondary null fit i:

1. reproduce the exact frozen null target-N pool and frozen permuted labels for
   null perturbation i;
2. do not rerun Stage-A model selection to select C for the secondary fit;
3. set C exactly equal to the persisted selected C of biological perturbation
   i under the arbitrary ordinal mapping above;
4. fit a Stage-B full-target-N null probe using the frozen null Stage-B seed
   for null perturbation i and otherwise unchanged Phase-P solver semantics.

This produces a new post hoc `C-matched null beta`.

It is not a canonical Experiment 04 null coefficient and must never be
represented as one.

Because C is intentionally changed relative to the original canonical null
fit, canonical null `K_t_full` is not an expected checksum for the C-matched
fit.

### 11.1 Convergence rule

For every secondary C-matched null fit:

- capture convergence warnings;
- capture fit exceptions;
- record whether the fit reached the frozen solver's convergence criterion
  within the unchanged `max_iter` and `tol` settings.

A fit producing a convergence warning, convergence failure, or fitting
exception is excluded from the secondary geometry comparison.

Such rows are:

- counted;
- reported by imposed C;
- not retried with altered C, solver, `max_iter`, tolerance, or initialization;
- not replaced.

The valid secondary denominator must be stated explicitly.

### 11.2 Seed hygiene

The secondary arm consumes no new seed namespace.

It deterministically re-derives and reuses the already-consumed canonical null
Stage-B seed path for each null perturbation.

No new biological, null, validation, or confirmatory seed range is authorized.

No C matching, rematching, caliper, support-size matching, or pairing rule may
be changed after decoder-geometry results are inspected.

The C-matched comparison is secondary and must be reported separately from the
canonical-procedure comparison.

## 12. Co-primary analysis A — sparse decoder-direction reconstruction

For every eligible nonzero beta:

1. convert beta to float64;
2. normalize beta to unit L2 norm;
3. reconstruct it using `D_unit`;
4. use the deterministic orthogonal matching pursuit procedure below.

### 12.1 Frozen OMP algorithm

Initialize:

- selected support = empty;
- fitted vector = zero;
- residual = normalized beta.

For steps `s = 1, ..., 512`:

1. compute float64 correlations between every unselected atom in `D_unit`
   and the current residual;
2. select the atom having maximum absolute correlation;
3. if multiple atoms have exactly equal maximum absolute correlation, select
   the atom having the smallest original checkpoint decoder-column index;
4. append that atom to the support;
5. refit all selected coefficients jointly by float64 least squares;
6. recompute the fitted vector and residual from that joint least-squares
   solution.

Least-squares refitting uses:

`numpy.linalg.lstsq(A, beta, rcond=1e-12)`

where A contains the currently selected unit decoder atoms.

No coefficient-sign restriction is imposed.

No lasso penalty, shrinkage, or post-selection regularization is applied.

### 12.2 Rank and conditioning audit

At every OMP step, not only frozen reporting-grid points, record or check:

- nominal selected support size s;
- effective rank returned by `numpy.linalg.lstsq`;
- 2-norm condition number of A.

The effective rank must equal s.

If effective rank `< s` at any step:

1. declare the row `rank_deficient`;
2. record the first deficient step as `rank_deficiency_step`;
3. halt OMP for that row immediately;
4. report no R value for that step or any larger step.

OMP must not continue after rank deficiency because later atom choices would
be based on a residual obtained from a truncated least-squares solution.

At frozen grid points reached before any deficiency, also report:

- R(k);
- effective rank;
- condition number.

Condition number is descriptive when full rank is preserved.

It is not itself an exclusion criterion.

### 12.3 Numerical invariants

All decoder matrices, beta vectors, correlations, least-squares inputs,
coefficients, fitted vectors, residuals, singular-value diagnostics, condition
numbers, and reconstruction statistics are computed in float64.

If normalized-beta residual L2 norm becomes `<= 1e-12`, numerical exact
reconstruction is declared and all later frozen-grid reconstruction values are
set to 1.0.

If maximum absolute unselected-atom correlation becomes `<= 1e-12` while
residual L2 norm remains `> 1e-12`, the reconstruction implementation fails
closed and no population comparison is produced.

At each valid recorded k:

`R_beta(k) = 1 - ||beta - beta_hat_k||_2^2 / ||beta||_2^2`.

Because beta has unit norm, the denominator equals 1.

Require R(k) to lie within:

`[-1e-12, 1 + 1e-12]`.

Values marginally outside `[0,1]` but inside this numerical tolerance may be
clipped to `[0,1]` for reporting.

Values outside the tolerance are an analysis failure.

### 12.4 Monotonicity invariant

For every row having valid reconstruction values at consecutive frozen grid
points:

`R(k_next) >= R(k_previous) - 1e-12`.

A decrease exceeding `1e-12` is an implementation/numerical failure, not a
scientific result.

If this invariant fails for any row, no population comparison is produced.

### 12.5 Frozen reconstruction grid

The frozen sparsity grid is:

`k = {1, 2, 4, 8, 16, 32, 64, 128, 256, 512}`.

Report the complete valid reconstruction curve.

For each beta also report:

- first frozen-grid k attaining R >= 0.50, if attained;
- first frozen-grid k attaining R >= 0.80, if attained;
- first frozen-grid k attaining R >= 0.90, if attained.

Failure to attain a threshold by k=512 is reported as `>512`, not extrapolated.

A row halted for rank deficiency before a threshold becomes unavailable for
that threshold rather than being classified as `>512`.

## 13. Co-primary analysis B — raw decoder-weight concentration

For every same eligible nonzero beta:

1. convert beta to float64;
2. normalize beta to unit L2 norm;
3. use the exact unnormalized checkpoint decoder `D_raw`;
4. compute:

`w = D_raw.T @ beta`.

This statistic is not an SAE encoder activation.

It measures alignment of the supervised direction with the exact raw frozen
decoder columns while retaining their checkpoint column scales.

The nine exact zero decoder columns remain present and contribute zero.

Define:

`p_j = |w_j| / sum_l |w_l|`.

If the denominator is numerically zero at `<= 1e-15`, the row is reported as
undefined for this statistic, counted, and not replaced.

### 13.1 Top-k absolute-weight mass

Using the same frozen grid:

`k = {1, 2, 4, 8, 16, 32, 64, 128, 256, 512}`,

define top-k mass as the fraction of total absolute raw decoder weight
contained in the k largest values of `|w_j|`.

Ties at a top-k boundary are ordered by smaller original checkpoint
decoder-column index.

Report the complete top-k mass curve.

### 13.2 Entropy effective count

For all `p_j > 0`, compute Shannon entropy:

`H = -sum_j p_j log(p_j)`

using the natural logarithm.

Define:

`N_eff = exp(H)`.

Report `N_eff` for every eligible beta and its population distribution.

This statistic is parameterization-dependent because it uses the exact raw
checkpoint decoder-column scales.

It must therefore be described as raw-decoder directional
weight/concentration, not as realized SAE feature activation or causal feature
contribution.

## 14. Frozen population summaries and headline quantities

No grid point may be selected after beta recovery as the preferred result.

### 14.1 Designated headline k

The designated headline sparsity/concentration level is:

`k = 32`.

This choice is frozen before beta recovery because the motivating Experiment
03 question concerned whether toxin-related information could be represented
by a compact sparse feature set.

Thirty-two decoder directions remains compact relative to both the
1,280-dimensional ESM representation and the 10,231 usable decoder
directions, while avoiding a headline criterion restricted to only a handful
of atoms.

The choice of k=32 is not based on any recovered beta geometry.

### 14.2 Headline quantities

For each population, the prespecified headline summaries are:

1. median OMP reconstruction `R(32)`;
2. median raw-decoder top-32 absolute-weight mass;
3. median raw-decoder entropy effective count `N_eff`.

If R(32) is unavailable for one or more rows because of prespecified rank
deficiency, report the valid denominator and rank-deficiency count explicitly.

No unavailable row is replaced.

### 14.3 Full-curve summaries

At every frozen grid k, separately for each population, report:

- median R(k);
- 95% bootstrap percentile interval for median R(k);
- valid denominator;
- rank-deficiency/unavailable count;
- median selected-matrix condition number among valid rows;

and for raw decoder-weight concentration:

- median top-k absolute-weight mass;
- 95% bootstrap percentile interval for that median;
- valid denominator.

For `N_eff`, report:

- median;
- 95% bootstrap percentile interval for the median;
- valid denominator.

### 14.4 Frozen bootstrap procedure

The resampling unit is the perturbation/beta row.

Decoder atoms, ESM coordinates, proteins within a perturbation, and curve
points are never bootstrap units.

For each population and each reported statistic:

- use 10,000 bootstrap replicates;
- sample eligible perturbation rows with replacement;
- preserve the original population sample size in every replicate;
- compute the population median in each replicate;
- report the 2.5th and 97.5th percentiles of the bootstrap-median
  distribution.

Use NumPy `Generator(PCG64)` with frozen bootstrap seed:

`2026090801`.

Biological, canonical-null, C-matched-null, and isotropic-reference bootstrap
calculations must use deterministic child RNG streams derived from this frozen
root seed and identified in the analysis output.

### 14.5 Inferential status

This follow-up is descriptive.

No null-hypothesis significance test is run.

No p-value is calculated.

No multiplicity-adjusted inferential procedure is applied.

No difference between biological and null curves receives a thresholded
PASS/FAIL interpretation.

Population differences may be reported descriptively using the prespecified
summaries and intervals, subject to the regularization and pooling limitations
in this specification.

## 15. Pre-recovery isotropic geometric reference

An isotropic reference must be computed before any Experiment 04 beta replay.

It uses only:

- the frozen decoder;
- the frozen reconstruction/concentration implementation;
- a seeded random-number generator.

It accesses no biological beta, biological label, permutation label,
Experiment 04 model coefficient, or confirmatory artifact.

### 15.1 Frozen isotropic population and execution-size rule

The isotropic reference population size is selected operationally from:

`N_iso in {500, 1000}`.

The choice is determined before any Experiment 04 beta replay and before any
isotropic geometry result is inspected.

#### Timing calibration

Before the full isotropic run:

1. execute exactly five isotropic vectors through the frozen OMP engine;
2. use isotropic vector indices 0 through 4;
3. record wall-clock OMP time separately for each vector;
4. compute the median wall-clock seconds per vector;
5. define:

   `projected_1000_hours =
       median_seconds_per_vector * 1000 / 3600`.

Freeze the operational rule:

- if `projected_1000_hours <= 8.0`, set `N_iso = 1000`;
- otherwise set `N_iso = 500`.

No other isotropic population size is permitted.

The timing decision depends only on wall-clock execution cost.

No R(k), decoder-weight concentration, N_eff, selected atoms, condition
numbers, or other geometry result from the five timing vectors may be
inspected or used when selecting N_iso.

The five timing vectors are not treated as separately sampled observations.
They are regenerated from their frozen vector-index streams during the final
isotropic analysis and therefore belong to the final reference population in
the ordinary way.

#### Independently derivable random streams

Use root:

`SeedSequence(2026090802)`.

Each isotropic vector has its own deterministic child random stream derived
from the root SeedSequence and its integer vector index.

Vector i must therefore be reproducible independently of:

- execution order;
- previous vectors;
- checkpoint history;
- session interruption; or
- worker scheduling.

The implementation must not depend on advancing one shared sequential
`Generator` state across the isotropic population.

For each index `i = 0, ..., N_iso - 1`:

1. deterministically derive the child SeedSequence associated with index i
   from root `SeedSequence(2026090802)`;
2. instantiate `Generator(PCG64(child_seed_i))`;
3. generate exactly 1,280 independent standard-normal float64 coordinates;
4. normalize the vector to unit L2 norm;
5. apply exactly the frozen OMP reconstruction implementation using `D_unit`;
6. apply exactly the frozen raw decoder-weight/concentration implementation
   using `D_raw`.

The mapping from integer vector index to child stream must be explicit in the
analysis implementation and covered by its pre-run audit.

The isotropic vectors are geometric references, not simulated biological/null
fits.

### 15.2 Resumability and checkpoint boundary

The isotropic run is checkpointable per vector index.

Each completed vector may write only the minimal derived analysis state needed
to resume without recomputing already completed indices, including:

- vector index;
- deterministic child-stream identifier;
- valid R(k) values;
- rank-deficiency status and halt step, if any;
- condition-number diagnostics at frozen grid points;
- top-k raw-weight mass values;
- N_eff;
- implementation/provenance identifiers required for integrity checking.

The underlying random vector itself need not be retained because it is exactly
re-derivable from its vector index and frozen SeedSequence contract.

Partial checkpoints must be written to the same private Kaggle Dataset
checkpoint boundary used for protected Phase-P execution artifacts.

They must not be written to, staged in, or committed to the public Git
repository.

The implementation must resolve that already-existing private checkpoint
destination from the frozen Phase-P checkpoint configuration rather than
creating a new public destination or seed namespace.

Partial isotropic checkpoints are execution-recovery artifacts only.

They are not frozen scientific outputs and must not be summarized,
interpreted, compared with biological/null results, or published while the
isotropic population is incomplete.

The isotropic reference becomes a frozen analysis artifact only after:

1. every required index `0 ... N_iso-1` has completed or received its
   prespecified terminal status;
2. checkpoint integrity has been audited;
3. the complete population summaries required below have been generated; and
4. the final aggregate isotropic output has been written.

### 15.3 Frozen isotropic outputs

Before any beta replay, persist:

- median R(k) for every frozen k;
- 95% bootstrap percentile interval for median R(k);
- valid denominator and any rank-deficiency count at every k;
- median selected-matrix condition number at every k;
- median top-k raw absolute-weight mass at every frozen k;
- 95% bootstrap percentile interval for those medians;
- median `N_eff`;
- 95% bootstrap percentile interval for median `N_eff`;
- headline R(32);
- headline top-32 mass.

The isotropic bootstrap uses random-direction rows as the resampling unit and
the frozen bootstrap procedure in Section 14.

The isotropic results must be frozen before Experiment 04 beta recovery.

They may not be used to change:

- the OMP algorithm;
- numerical tolerances;
- k grid;
- headline k;
- raw-weight definition;
- bootstrap procedure; or
- biological/null comparison plan.

The isotropic population is a descriptive geometric reference only.

It is not the primary permutation null and does not generate p-values.

### 15.4 Isotropic implementation sanity check

For a roughly incoherent dictionary in a 1,280-dimensional ambient space, a
simple scale heuristic is:

`R(k) ~= k / 1280`.

At the frozen headline k=32:

`32 / 1280 = 0.025`.

This heuristic is evaluated only after N_iso has already been fixed by the
timing-only rule in Section 15.1.

It is an implementation sanity heuristic only.

It is not:

- an acceptance threshold;
- an expected scientific result;
- an inferential null;
- a population-size selection criterion; or
- a target to which the implementation may be tuned.

A grossly inconsistent result, such as R(32) on the order of 0.4, must trigger
implementation review before any Experiment 04 beta replay.

No analysis rule may be altered merely to force agreement with the heuristic.

## 16. Primary and secondary comparisons

### 16.1 Primary comparison

The primary descriptive comparison is:

- eligible biological Stage-B directions; versus
- eligible canonical permutation-null Stage-B directions.

Both were recovered under the identical frozen Phase-P procedure, while
realized selected C and support size are explicitly allowed to differ and must
be reported.

Both co-primary analysis families are reported:

1. OMP sparse decoder-direction reconstruction;
2. raw-decoder directional weight/concentration.

The designated headline quantities are those frozen in Section 14.

No single biological or null perturbation is nominated as representative.

### 16.2 Secondary regularization-control comparison

The prespecified secondary comparison is:

- biological Stage-B directions; versus
- the marginal C-distribution-matched permutation-null directions defined in
  Section 11.

This is not a paired-effect analysis.

The ordinal index mapping has no biological or statistical correspondence
interpretation.

Its purpose is only to reproduce the marginal biological selected-C
distribution in the secondary null fits.

Rows excluded under the frozen convergence rule are counted and reported, and
the valid secondary denominator is stated explicitly.

### 16.3 Isotropic reference

The frozen isotropic results are shown only as a geometric reference for
interpreting whether a reported level of reconstruction or raw decoder
concentration is ordinary relative to generic ambient directions.

They are not substituted for the canonical permutation-null comparison.

Because `N_iso` is either 500 or 1,000 while each canonical biological/null
population contains at most 100 rows, the isotropic bootstrap intervals will
generally be narrower partly or largely because of sample size.

That narrower interval must not be interpreted as evidence that the isotropic
population is scientifically stronger, more valid, or more meaningfully
determined than the biological/null populations.

## 17. Interpretation boundary

This analysis can distinguish patterns consistent with:

- compact alignment with SAE decoder directions;
- distributed accessibility requiring many SAE decoder directions;
- concentrated versus diffuse alignment with the exact raw decoder columns.

Because the decoder is full-rank, it cannot support a claim that the
supervised direction lies outside the decoder span.

Conversely, a low reconstruction k, high top-k raw-weight concentration, or
low effective decoder-weight count does not establish that the SAE encoder
actually activates those features on toxin proteins.

The SAE encoder has its own learned affine/nonlinear mapping, schematically:

`z = ReLU(W_enc x + b_enc)`.

Neither sparse representation of beta by decoder directions nor

`D_raw.T @ beta`

is equivalent to observing SAE encoder activations on biological examples.

Accordingly, this analysis cannot by itself justify a claim that identified
decoder directions constitute realized toxin features or are suitable
function-based screening features.

The analysis also does not establish:

- a causal toxin mechanism;
- unique toxin specificity;
- mechanistic decomposition;
- cross-family toxin generalization;
- a unique cause of the Experiment 03 SAE stability failure.

The canonical biological-versus-null comparison may also reflect differences
in realized regularization and support size. The secondary C-distribution
control reduces one aspect of that comparability problem but does not convert
the analysis into a causal decomposition of why the populations differ.

Pooling remains an explicit limitation: the supervised Experiment 04 probe
operates on protein-level pooled ESM representations, whereas the SAE was
trained/applied at residue resolution.

## 18. Execution ordering

The required order is:

1. freeze and commit this specification;
2. implement the OMP and raw-weight analysis engine;
3. audit the implementation against this specification;
4. run the five-vector timing-only calibration;
5. freeze `N_iso` mechanically as 500 or 1,000 using Section 15.1;
6. run the complete checkpointed isotropic geometric reference;
7. audit completeness and freeze the aggregate isotropic output;
8. review the isotropic output only for implementation failures or gross
   violations of the frozen sanity heuristic;
9. do not alter the scientific analysis specification based on the isotropic
   outcome;
10. implement the environment/replay-verification program;
11. audit that program before biological/null replay;
12. pin replay BLAS/OpenMP thread counts to one and capture environment
    provenance;
13. run verification-only Pass 1 over all 200 canonical paths;
14. report the complete Pass-1 verification result;
15. proceed only if Pass 1 returns 200/200;
16. run coefficient-recovery Pass 2;
17. require and report 200/200 Pass-1 versus Pass-2 Stage-B coefficient-hash
    agreement;
18. only after complete canonical recovery, run the frozen canonical
    biological-versus-null decoder-geometry analysis;
19. run the prespecified secondary marginal C-distribution-matched null
    analysis under the frozen convergence rule;
20. report all results as a post hoc Experiment 04 explanatory follow-up.

No confirmatory data are authorized at any stage.
