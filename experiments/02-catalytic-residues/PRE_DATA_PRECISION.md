# Pre-data precision analysis — Experiment 02

## Result

**Experiment 02 closed pre-data as underpowered.**

At the planned split support, and with a bootstrap confirmed calibrated against across-dataset variability, the preregistered retention requirement `CI_low(R) > 0.75` was reached with probability 0.29 even when true retention was complete. The design cannot adjudicate its own confirmatory hypothesis.

This is a closure of the experimental design, not of the biological hypothesis. Nothing here bears on whether catalytic-residue information in ESM-2 generalizes across sequence families.

## The question

Whether linearly accessible catalytic-residue information in ESM-2 650M layer 17 survives a 30%-identity family holdout beyond a ±3-residue local-sequence comparator.

`H_repr` required two things: an advantage over the local comparator on the divergent split, and retention of that advantage relative to in-distribution, `R = Δ_div / Δ_rand` with `CI_low(R) > 0.75`.

## Expected operating point

Public M-CSA counts — 1,003 hand-curated entries as of 12 August 2026 — suggested a divergent test of approximately 170 independent 30%-identity clusters, 700 curated catalytic positives, prevalence near 0.01, against a random test of roughly 100 clusters and 420 positives.

No Experiment 02 label pool was constructed to obtain these figures. They are order-of-magnitude estimates from published counts.

## Instrument validation

Feasibility diagnostics are only as good as the simulator producing them. Two defects were found and corrected before any result here was accepted; both are documented in `IMPLEMENTATION_NOTES.md`.

1. Arms B and D were generated with independent noise, zeroing a covariance that is strongly positive in reality and inflating the variance of every difference-based statistic. Across the subsequent pairing correction, the log-R half-width fell from 0.614 to 0.207. Those two runs also differed in cluster heterogeneity, so the full reduction cannot be attributed to pairing alone; the earlier 0.614 value is retained only as part of the simulator audit.
2. The score generator re-tuned its signal shift to hit target AP in every synthetic dataset, pinning realized AP and removing the across-dataset variation that outer replication measures. Reported detection was deflated roughly sevenfold.

After correction the simulator was validated on across-replicate standard deviation of `log R̂` against mean bootstrap sigma. That ratio was 6.6 under pinning. Post-correction it sits between 0.91 and 1.17 across four retention conditions, and detection tracks the analytic expectation monotonically:

| target R | detection | analytic | calibration ratio |
|---:|---:|---:|---:|
| 0.85 | 0.19 | 0.22 | 1.05 |
| 0.90 | 0.37 | 0.41 | 1.17 |
| 0.95 | 0.70 | 0.61 | 0.91 |
| 1.00 | 0.81 | 0.78 | 1.00 |

Equal 170/700 support, zero heterogeneity, shared latents — a deliberately favorable configuration establishing an upper bound, not an estimate.

## Ratio advantage arm

Frozen precision target: mean 95% CI half-width on `log(ratio)` no larger than `log(1.5) = 0.4055`.

With cluster-level prevalence and ranking-difficulty heterogeneity present, the expected operating point produced a half-width near 0.51–0.53. Only the extreme tested point of roughly 600 clusters at 700 positives cleared the ceiling. The ratio arm was underpowered at the planned split.

## Absolute advantage arm

The advantage criterion was disjunctive before any simulation: `CI_low(ratio) > 2.0` or `CI_low(Δ_div) > 10π`.

At 170 clusters and 700 positives with synthetic true Δ = 0.05, the absolute arm returned mean observed Δ = 0.0499 and half-width 0.0409 — an order of magnitude narrower than the ratio interval. Derived from that width, the absolute arm detects a true advantage of roughly 16π at 80%, corresponding at π = 0.01 to ESM near AP 0.20 against a local baseline near 0.05.

**The absolute advantage arm is adequately precise at the planned split.** It is not what closed the experiment.

## Retention at planned support

Both cluster-heterogeneity terms active at their assumed values, unequal support matching the planned design. 100 outer simulations, 300 whole-cluster bootstrap replicates.

| Quantity | true R = 0.95 | true R = 1.00 |
|---|---:|---:|
| Mean point R | 0.949 | 1.027 |
| Mean log-R half-width | 0.4112 | 0.4118 |
| Mean CI lower bound | 0.636 | 0.688 |
| `P(CI_low(R) > 0.75)` | 0.18 | 0.29 |
| Calibration ratio | 0.967 | 0.928 |
| Valid bootstrap fraction | 1.000 | 1.000 |

The estimator is centered — mean point R of 1.027 against a target of 1.00 — and every bootstrap replicate is valid. The failure is precision, not bias, denominator instability, or implementation degeneracy.

Adding heterogeneity and the real random split doubled the half-width from 0.207 to 0.412 and cut detection at complete retention from 0.81 to 0.29.

## What the planned-support result does and does not establish

At the observed mean log-R half-width of approximately 0.412, the retention criterion is extremely demanding. A point estimate must be well above 1 before its lower confidence bound reliably clears 0.75. This is another way of seeing why the planned configuration has low sensitivity even when true retention is complete.

These calculations are diagnostic extrapolations from the observed interval width, not additional simulated operating points, and they are not used as the stopping rule.

The planned-support result is sufficient to stop the **current allocation**: with approximately 100 random-test clusters / 420 positives and 170 divergent-test clusters / 700 positives, complete true retention is detected only 29% of the time.

The analysis does **not** establish that every alternative split allocation would fail. The 0.207 → 0.412 increase in half-width combines two changes — nonzero cluster heterogeneity and smaller random-test support — and those contributions were not decomposed. A future experiment could test whether reallocating support materially improves retention precision, but that would be a new design decision rather than a rescue of this planned configuration.

## Sensitivity and assumptions

The heterogeneity constants `CLUSTER_PREVALENCE_SIGMA = 0.75` and `CLUSTER_DIFFICULTY_SIGMA = 0.60` are diagnostic modelling assumptions, not measurements of M-CSA. The favorable configuration bounds the assumption in the generous direction: at zero heterogeneity and equal support, detection at complete retention is 0.81. The planned-support diagnostic assumes nonzero heterogeneity and unequal support, under which detection at complete retention is 0.29.

The 0.207 → 0.412 penalty combines heterogeneity and unequal support and has not been decomposed. That decomposition would inform what a future design requires — more independent families if heterogeneity dominates, a rebalanced split if support does. It does not change the stopping decision for the current planned allocation, whose calibrated detection at complete retention is only 0.29.

## Decision

`H_repr` requires both an advantage and a retained advantage under family shift. The advantage arm is estimable through its absolute disjunct. Retention is not estimable against its preregistered threshold at the expected sample size.

**Final pre-data outcome: NO VERDICT — UNDERPOWERED.**

The closure precedes construction of the confirmatory M-CSA label pool, ESM-2 embedding extraction, probe training, and evaluation of either test split. No decision threshold was weakened in response to the precision analysis.

## Scope

This is not evidence against representation generalization for catalytic residues, and not a finding that retention is inherently inestimable. The estimator is unbiased and the interval is honest. The threshold is unreachable at roughly 170 divergent clusters.

A future catalytic-residue experiment needs substantially more independent labelled families, or a different independently justified estimand, or both. Experiment 01 answered the analogous question because its divergent split held 2,209 clusters; the curated M-CSA pool offers roughly a thirteenth of that.
