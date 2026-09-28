# Resampling variance diagnostic: routing addendum 001

Status: frozen before implementation or execution. Exploratory mechanism evidence about the specified Gaussian-mean surrogate only. This addendum supplements the original specification without rewriting it. Its machine-readable companion fixes classification constants; the original settings, fixture budget and seeds are unchanged.

## Integrity first

Any violated input, mathematical, pairing, seed, serialization or completeness invariant blocks all scientific routing. Preserve the failed evidence and classify the implementation failure. No partial-result routing, replacement fixtures or automatic retry. All six fixtures, both resampling schemes and the oracle control must be reported if integrity passes.

## Units, ratios and descriptive margin

The independent Monte Carlo unit is one outer dataset, not one inner bootstrap statistic. For each of 12 fixture-by-scheme combinations, define X_j as the exact conditional resampling variance divided by analytic V_true. Report R=mean(X_j) and SE=sample_sd(X_j,ddof=1)/sqrt(1000). The ratio denominator is analytic V_true, never an estimated empirical variance. Inner bootstrap sample variances remain numerical diagnostics, not extra independent observations.

Freeze a descriptive equivalence margin epsilon=0.10 around ratio 1. This means tolerating at most ten percent relative variance discrepancy, corresponding to a standard-deviation ratio between sqrt(0.90) and sqrt(1.10). It is a transparent practical tolerance for this exploratory surrogate, not an optimal or scientifically validated margin and not calibrated to either candidate's observed results. Report continuous ratios and intervals alongside labels; no post-result alternative margin analysis is authorized here.

Use R +/- z*SE, without clipping negative endpoints. This is a large-sample interval over 1000 independent outer datasets; simultaneous error control using it is approximate, not an exact finite-sample guarantee.

Variance flags are mutually exclusive within each combination:
- EQUIVALENT: the entire interval is inside inclusive [0.90,1.10].
- ABOVE: the lower endpoint is strictly greater than 1.10.
- BELOW: the upper endpoint is strictly less than 0.90.
- INCONCLUSIVE: all other configurations, including an interval spanning a margin boundary.

Empirical outer variance of T and its normal-theory Monte Carlo standard error remain a separate generating-process check under the original specification. They do not substitute for the analytic denominator and do not trigger routing labels.

## Calibration flags and simultaneous reporting

For each of six fixtures and three methods (A, B, oracle), use a Wilson score interval for coverage with denominator 1000. Let p=k/1000. The interval center is (p+z^2/(2n))/(1+z^2/n); half-width is z*sqrt(p*(1-p)/n+z^2/(4n^2))/(1+z^2/n).

Under this zero-truth, defined-interval diagnostic, null rejection is exactly the complement of coverage. Assert this per outer dataset, with endpoint equality covering and not rejecting. Derive the rejection interval by [1-U,1-L] rather than counting it as an independent test. A missing or undefined inference blocks calibration routing for that combination and is reported as INFERENCE_UNDEFINED; it is not treated as a non-rejection or silently removed. The stipulated finite Gaussian fixtures should produce defined results; any exception is retained for integrity review.

Coverage ABOVE_NOMINAL requires L>0.95 and means rejection BELOW_NOMINAL. Coverage BELOW_NOMINAL requires U<0.95 and means rejection ABOVE_NOMINAL. Otherwise label NO_DETECTED_DEVIATION. This label does not establish calibration equivalence. No calibration-equivalence margin is introduced.

Freeze one family of 44 intervals: 12 variance-ratio intervals, 18 coverage intervals and 14 prespecified cross-fixture contrasts below. Use family alpha=0.05 and z=NormalDist().inv_cdf(1-0.05/(2*44)) for every interval. This Bonferroni allocation is fixed even when a result is undefined; no alpha is recycled. Wilson and outer-normal intervals are approximate; Bonferroni does not make approximate marginal intervals exact. Do not expand the comparison family after viewing results.

## Cross-fixture contrasts

Fixture indices are size-vector order then rho order: balanced rho 0,0.5,0.9 followed by unequal rho 0,0.5,0.9. For each scheme, compare unequal minus balanced at each matched rho (three contrasts) and higher minus lower adjacent rho within each size vector (four contrasts). Thus there are seven contrasts per scheme, fourteen total. No pairwise contrasts beyond this list are authorized for routing.

For each contrast H=R_b-R_a use SE_H=sqrt(SE_a^2+SE_b^2), since outer streams are independently indexed by fixture. Use H +/- z*SE_H. Define MATERIAL_HETEROGENEITY only when the whole contrast interval is strictly above +0.10 or strictly below -0.10. State its sign, both fixtures, scheme and interval. At least one such contrast involving two fully completed fixtures is necessary to flag detected heterogeneity. Otherwise report NO_MATERIAL_HETEROGENEITY_DETECTED, not homogeneity. Different within-fixture significance labels alone cannot trigger this flag.

## Independent outcome-to-action flags

After integrity passes, variance, calibration and heterogeneity flags are evaluated independently and all reported. No precedence among these three dimensions suppresses another result.

- ABOVE variance supports excess conditional resampling variance relative to target sampling variance in that surrogate fixture. It permits a separately frozen investigation of whether the mechanism maps to production; it does not prescribe changing the production resampling unit.
- BELOW variance supports the opposite discrepancy, recorded separately.
- EQUIVALENT variance plus NO_DETECTED_DEVIATION in calibration means the proposed discrepancy was not demonstrated in that fixture; it does not clear production.
- EQUIVALENT variance plus directional calibration deviation shows that variance agreement does not establish interval calibration. A separate investigation of finite-sample interval construction may be specified.
- ABOVE variance plus over-coverage/under-rejection is compatible with the proposed conservative mechanism in the surrogate; it is not a causal diagnosis of production.
- Other joint directions are reported explicitly without forcing a single explanation.
- INCONCLUSIVE variance or undefined inference prevents a definitive variance-mechanism conclusion for that combination, regardless of other flags.
- Detected cross-fixture heterogeneity limits generalization across regimes. Absence of a detected contrast is not proof of regime invariance.

Permitted next actions are documentation, closure of this exploratory question, or a separately specified investigation. No flag chooses a candidate or modifies an existing gate.

## Silence and authorization clauses

This surrogate has no classification threshold, calibration quantile, attainable FPR grid or TPR lattice. It cannot address or rule out threshold discreteness. Null rejection here is not classifier false-positive rate. The discreteness hypothesis remains untested. Any investigation of it requires a separate freeze naming the target estimand, attainable operating-point grid, geometry source (fabricated or production), permitted inputs, outputs and budget before execution.

Candidate 1 and Candidate 2 remain rejected. Their archives, endpoint convention and original V1/V2/V3 rules are untouched. Candidate 3 requires its own specification and separate authorization. This diagnostic cannot authorize it, any surface, protected evaluation, or a band amendment.

Next: disabled implementation; synthetic audit against committed source; refusal exit code 2 with no diagnostic output directory; isolated enablement only after audit. No diagnostic execution is authorized by this addendum. Prior exposure is acknowledged in the original specification and rejection record; no claim of an outcome-naive methodology choice is made.
