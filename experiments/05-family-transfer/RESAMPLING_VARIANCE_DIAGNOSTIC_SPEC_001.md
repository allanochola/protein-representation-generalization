# Synthetic resampling variance diagnostic 001

Status: specification frozen; implementation absent; execution unauthorized.

## Question and scope

Does adding independent within-group resampling add a variance term already represented in the empirical distribution of group means, when the target is the superpopulation mean of paired group differences observed through finite records?

This is an analytically tractable surrogate, not a revalidation of either rejected candidate and not Candidate 3. It isolates a possible resampling mechanism. It does not implement threshold calibration, the TPR ratio, the positive lattice or the actual allocation geometry. A result here cannot establish the cause of conservatism in the production estimand. No inference about power, scientific resolvability, or biological validity is allowed.

## Prior exposure

Candidate 1 and Candidate 2 remain rejected. Candidate 2 had V1 rates 0.0204 and 0.0205 and six V2 coverages from 0.9708 to 0.9780; these results were seen before this diagnostic was specified. Candidate 1 endpoint-tie and width diagnostics were also exposed. This diagnostic is outcome-informed exploratory methodology. It cannot be described as an independent confirmation or used to alter prior acceptance rules. Shared code and methods do not establish an independent replication of a causal explanation.

## Fixed fixtures and estimand

Use G=24 independent groups. Two size vectors are used in the stated order: 24 groups of size 4; then [1,2,4,8] repeated six times. Cross each with rho in [0,0.5,0.9], giving six fixtures. These fabricated sizes are not fitted to any archived geometry.

For each outer dataset generate independent standard-normal U_g, E_gi and Z_gi. Define D_gi=sqrt(rho)*U_g+sqrt(1-rho)*E_gi. Define paired comparator scores C_gi=Z_gi and ESM scores S_gi=Z_gi+D_gi. These are synthetic continuous scores, not probabilities or classification outcomes. Both arms always use identical group and record resampling indices. Compute the statistic from D directly to avoid cancellation; assert the paired-arm representation agrees to floating-point tolerance on synthetic audit fixtures.

The estimator is T=(1/G)*sum_g mean_i(D_gi), targeting E[T]=0 over fresh independently generated groups and their finite records. Conditional on the fixed size vector its sampling variance is

V_true=rho/G + (1-rho)*sum_g(1/n_g)/G^2.

No Bernoulli outcomes are generated. Every observation in a group shares its U_g. The oracle-Gaussian interval is a diagnostic control only and is not proposed as an interval for the production TPR estimand.

## Two fixed resampling schemes

For every outer dataset, draw G group indices with replacement per bootstrap replicate. Scheme A uses the observed mean difference for each selected group. Scheme B uses the same outer group indices, then draws n_g records with replacement within each selected occurrence, independently between repeated occurrences. Each selected group occurrence carries weight 1/G regardless of its size. Paired arms use the same inner indices. Singleton inner resampling is deterministic.

Let m_g be observed group means, mbar their average, and v_g the within-group population-form empirical variance with divisor n_g. The exact conditional variances of the resampled statistic are

V_A=sum_g((m_g-mbar)^2)/G^2,
V_added=sum_g(v_g/n_g)/G^2,
V_B=V_A+V_added.

Derive these expressions by the law of total variance in the implementation notes before execution. They are known-answer checks, not assumed evidence about the production candidates. Scheme B necessarily adds a nonnegative conditional term here; whether that causes excess total variance relative to the target is evaluated against V_true. This does not imply within-group resampling is always wrong: a different target or design may require it.

## Frozen budget and randomness

Exactly 1,000 outer datasets per fixture, 199 bootstrap replicates per outer dataset for each scheme: 6,000 datasets and 2,388,000 scalar bootstrap statistics total. No budget extension, adaptive stopping, seed search, fixture replacement or result-responsive optimization.

Use NumPy Generator(PCG64(SeedSequence([20260928, fixture_index, outer_index, stream_id]))). Fixture order is size-vector order then rho order. Stream 0 draws U, then E and Z group by group in ascending group order. Stream 1 draws each replicate's G outer group indices. Stream 2 draws inner record indices in replicate, occurrence order, including singleton calls. Freeze exact draw order in implementation and test batch/order invariance before authorization. Python 3.12.13 and NumPy 2.0.2 are pinned.

## Reports and fixed conventions

Per fixture report empirical outer variance of T (ddof=1), V_true, Monte Carlo standard error sqrt(2/(999))*V_true for the normal-theory outer sample variance, mean exact conditional V_A, V_added and V_B, their ratios to V_true, and bootstrap sample-variance estimates (ddof=1) versus exact conditional values. Report Monte Carlo discrepancy distributions rather than demanding per-dataset equality of sampled and exact variances.

For transparency report null rejection, coverage, interval width and failure count for percentile intervals of A/B and the oracle interval T +/- NormalDist().inv_cdf(0.975)*sqrt(V_true). Percentile endpoints use NumPy linear quantiles at .025 and .975; endpoint equality covers and does not reject. Monte Carlo standard errors accompany coverage/rejection proportions. These exploratory reports have no Gate B acceptance standing. Neither A nor B is a candidate-selection competition.

Archive fixture definitions, seed identifiers, per-outer statistics and summaries with non-circular hashes. Do not archive or read real protein inputs. Optional outputs are prohibited: no production power/width surface, no candidate recommendations based on winning intervals, no protected data.

## Integrity and sequencing

Synthetic audit before authorization must test the exact variance identities by exhaustive enumeration on tiny fixtures, pairing, independent occurrence-level draws, singleton behavior, deterministic stream indexing, serialization and closed-gate refusal. Compare exact enumeration to the analytic formulas at absolute tolerance 1e-12. Any integrity failure stops execution and preserves evidence; do not silently substitute a formula or fixture.

Next steps are disabled implementation and audit, then isolated authorization, one bounded execution, independent archive audit and closure. This freeze authorizes none of those executions. Runtime feasibility must be assessed before authorization; runtime pressure cannot change statistical budgets silently.

Both original candidates and their archives remain unchanged. Original V1/V2/V3 bands remain binding. Any subsequent diagnostic for threshold/calibration or any Candidate 3 specification requires a separate prospective record acknowledging all prior exposures. All confirmatory outcomes remain sealed.
