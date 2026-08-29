# Experiment 02 — implementation and pre-data design notes

## Status

Experiment 02 closed pre-data as underpowered, before any confirmatory M-CSA label pool was constructed, any ESM-2 embedding extracted, any probe fit, or any test split evaluated.

This file is the chronological audit of how that conclusion was reached, including three simulator implementations that were rejected before the final evidence was accepted. It exists because the closure changed direction twice, and the reasons matter more than the endpoint.

Every number in this file comes from synthetic data.

## Starting point

- Experiment 01 final commit: `3b50719c192365b202626ee42ca9e29e453bee9d`
- Experiment 01 verdict: `H_repr`
- Experiment 01 DOI: `10.5281/zenodo.22134890`

Branch: `exp02-catalytic-residues`. Protocol committed at `25207f8` before any simulation was written or run.

## Design, before any simulation

The protocol went through four review iterations before implementation. All predate every result below.

**Label policy.** Only manually curated M-CSA catalytic annotations admitted as confirmatory positives. Homology-transferred annotations excluded under all conditions, including as a power fallback — M-CSA states that its homologue file disregards residue conservation and function, and a transferred label is not independent of the reference entry it came from, which would contaminate a family holdout in a way sequence identity cannot detect.

**Operational negatives.** Unannotated residues in curated reference enzymes are benchmark negatives, not experimentally established non-catalytic residues. Negative subsampling removed entirely; imbalance handled in the probe loss so that evaluation prevalence is never an imposed quantity.

**Arms.** A, central amino-acid identity. B, local ±3 window. C, explicit homology transfer from the training pool. D, ESM-2 650M layer 17. Arm C was strengthened during review from best-global-hit transfer to best residue-level catalytic evidence across all qualifying hits, because the best global hit can align poorly through the catalytic site while a lower-scoring hit aligns through a conserved motif.

**Splits.** Approximately 20% of proteins reserved for the divergent test by whole-cluster assignment, the residual pool then split at protein level into random test and train, deliberately permitting train/random cluster overlap while guaranteeing zero divergent overlap.

**Decision quantities.** Advantage disjunctive — `CI_low(AP_D/AP_B) > 2.0` or `CI_low(AP_D − AP_B) > 10π` — with a signal floor of `AP_D ≥ 5π`. Retention `R = Δ_div / Δ_rand` with `CI_low(R) > 0.75`. `H_repr` required both.

### Specification error in the protocol, recorded not corrected

§11 defined the K2/K3 precision criterion on `log(ratio)` alone, while the advantage criterion had been disjunctive since the pre-simulation draft. Gating on one arm of a two-arm criterion is a specification error. It was caught during the precision analysis and is the reason the absolute arm was tested separately rather than assumed to share the ratio arm's precision. Since the experiment closed before any freeze, the error is recorded rather than corrected.

## Rejected implementation 1 — smoke test

2 outer simulations, 50 bootstrap replicates, clusters in {50, 100}, positives in {100, 300}. Verified the execution path only. Produced provisional `K2 = 100`, `K3 = 300`, and selected `R` over `R*`. Rejected as scientific output on the replicate counts alone. JSON deleted.

## Rejected implementation 2 — first validation run

25 outer simulations, 500 bootstrap replicates. Produced provisional `K2 = 50`, `K3 = 400`, detection 0.000 at true ratio 2.5 and 0.880 at 3.0, and selected `R` over `R*`. Rejected in full. Five defects:

1. **Impossible detection behaviour.** `P(CI_low > 2.0)` must increase monotonically with the true ratio. Under a lognormal approximation at the run's own half-widths the expected values were roughly 0.23 and 0.60. The implementation could not be used for any detection claim.
2. **Inadequate replication.** All pass rates moved in increments of 0.04, confirming 25 outer simulations — too few for probability estimation.
3. **`K2` was the grid minimum.** Increasing cluster count barely moved interval width anywhere in the grid, showing the generator treated clusters as arbitrary containers of residue-independent observations. `K2 = 50` was the smallest value tested, not a precision knee.
4. **The `R` versus `R*` comparison was not the preregistered test.** §9.3 specified synthetic rankings at varying prevalence with ranking quality held fixed. The implementation evaluated the algebraic identity `R* = R(1 − π_rand)/(1 − π_div)` instead — every reported figure matched that formula to machine precision. It confirmed an affine relationship that was never in doubt and could not detect AP's nonlinear prevalence dependence, which is the reason the check exists.
5. **Wrong precision summary.** The floor selector used median CI half-width where the protocol specified the mean.

The validation JSON was renamed `power_sim_validation_DIAGNOSTIC_INVALID.json` and then deleted. It was never accepted as a scientific output. Deleting it was a mistake — it was the evidence that defect 1 occurred — and the run is reconstructed here from session output rather than from a retained artifact.

## Correction 1 — cluster dependence

The generator was modified to introduce genuine cluster-level dependence through two synthetic heterogeneity terms:

    CLUSTER_PREVALENCE_SIGMA = 0.75
    CLUSTER_DIFFICULTY_SIGMA = 0.60

These are diagnostic modelling assumptions, not empirical measurements of M-CSA.

Clumping self-test at the expected divergent operating point — 170 clusters, 700 positives — returned 124 positive-bearing clusters (fraction 0.729), mean 5.645 positives per positive-bearing cluster, maximum 51 in one cluster. Positives are genuinely concentrated rather than scattered.

## Cluster-count grid

With cluster dependence present, cluster count became strongly relevant. Mean 95% CI half-width on `log(ratio)`, against the frozen ceiling `log(1.5) = 0.4055`:

| clusters | 400 positives | 700 positives |
|---:|---:|---:|
| 20 | 0.934 | 1.006 |
| 30 | 0.805 | 0.840 |
| 40 | 0.809 | 0.797 |
| 50 | 0.707 | 0.764 |
| 75 | 0.684 | 0.656 |
| 100 | 0.647 | 0.644 |
| 150 | 0.589 | 0.535 |
| 200 | 0.556 | 0.493 |
| 300 | 0.512 | 0.449 |
| 400 | 0.488 | 0.426 |
| 600 | 0.499 | 0.396 |

Only 700 positives at 600 clusters cleared the ceiling. No cell at 400 positives passed at any cluster count, so `K3 = 400` from the rejected run did not survive. The expected operating point of roughly 170 clusters and 700 positives interpolates near 0.51–0.53.

The curve flattens and reverses between 400 and 600 clusters at 400 positives. At that density there is well under one positive per cluster, so most resampled clusters contribute nothing. The binding quantity is closer to the count of positive-bearing clusters than to raw cluster count.

Medians tracked means closely — best medians 0.494 and 0.387 — so the conclusion is not an artifact of the summary statistic.

## Absolute advantage arm

Tested separately because the advantage criterion was already disjunctive before any simulation, so testing the second arm changed no decision rule.

At 170 clusters, 700 positives, π = 0.01, synthetic `AP_B = 0.05`, `AP_D = 0.10`, true Δ = 0.05, using 100 outer and 1,000 bootstrap replicates: mean observed Δ = 0.0499, mean half-width 0.0409, median 0.0398, `P(CI_low(Δ) > 0.10) = 0.0`.

The zero was arithmetic, not a precision result — the simulated true Δ was half the decision threshold and clears it essentially never by construction. The finding was that the absolute interval is an order of magnitude narrower than the ratio interval, so the absolute disjunct can remain estimable where the ratio disjunct is not. Derived from the half-width, the absolute arm detects a true advantage of roughly 16π at 80%.

## Retention, first attempt

A naïve implementation was computationally prohibitive: every bootstrap replicate concatenated residue arrays and recomputed four average-precision values. A 300 × 1,000 run was stopped after roughly four hours without a result.

**This is the same failure mode as Experiment 01's eight-hour bootstrap hang, and it was fixed the same way.** Both came from per-replicate array materialization; both were resolved by resampling over precomputed structure. A failure mode that has now appeared twice in this repository is a repo-level lesson, not an incident.

The optimized version uses cluster multiplicities as residue sample weights, which preserves whole-cluster resampling without materializing duplicated arrays.

At equal 170/700 support with heterogeneity active and true R ∈ {0.75, 0.85, 0.90}, the optimized diagnostic returned mean log-R half-widths of 0.580, 0.640 and 0.607, `P(CI_low > 0.75) = 0.0` throughout, and valid fraction 1.0. A focused confirmation at true R = 0.90 with 100 outer and 500 bootstrap replicates reproduced it: mean median R = 0.897, half-width 0.614, mean `CI_low` 0.483, detection 0.000.

**A closure was drafted on this evidence. It was wrong, and two further defects were found before it was committed.**

## Correction 2 — arm pairing

`generate_scores` drew fresh residue noise and cluster-difficulty latents on every call, so arms B and D within a split were statistically independent. In reality they are strongly positively correlated: a resample that draws easy clusters raises both APs together. Since `Var(Δ) = Var(AP_D) + Var(AP_B) − 2·Cov`, zeroing the covariance inflates the variance of every difference-based statistic — the exact quantities the closure rested on.

Fixed by drawing residue noise and cluster-difficulty once per split and sharing them across arms, so the arms differ only in signal strength. Committed at `438f746`.

Effect at equal support with heterogeneity switched off: log-R half-width fell from 0.614 to 0.207, roughly a 9× reduction in variance.

## Correction 3 — AP pinning

The maximally favorable run (`b152af3`) reported a half-width of 0.207 and detection of 0.06 at true R = 0.90. Those two numbers are inconsistent: the half-width implies roughly 0.41 analytically. The gap was 6.6× in standard-deviation terms.

The cause was in `generate_scores`, which binary-searched the signal shift to hit the target AP in *every* synthetic dataset. That pinned realized AP and removed the across-dataset variation that outer replication exists to measure, so `detection_probability` was not a power estimate. The same artifact had deflated the earlier retention run's reported 0.000.

Fixed by calibrating the shift once against a large reference dataset and holding it fixed across outer replicates, letting realized AP vary as it would in a real dataset. Committed at `550bcda`.

`retention_favorable.json` at `b152af3` is retained as an AP-pinned diagnostic. Its 0.06 detection figure is superseded for inference and is preserved only because it documents how the pinning problem was found.

## Calibrated instrument

After both corrections, the simulator was checked against the quantity that matters: across-replicate standard deviation of `log R̂` versus mean bootstrap sigma. Under AP pinning that ratio was 6.6. Maximally favorable configuration, fixed shift, equal 170/700 support, zero heterogeneity, 100 outer and 300 bootstrap replicates (`7d4c310`):

| target R | realized R | sd(log R̂) | bootstrap σ | ratio | detection | analytic |
|---:|---:|---:|---:|---:|---:|---:|
| 0.85 | 0.836 | 0.113 | 0.107 | 1.05 | 0.19 | 0.22 |
| 0.90 | 0.889 | 0.123 | 0.105 | 1.17 | 0.37 | 0.41 |
| 0.95 | 0.962 | 0.097 | 0.106 | 0.91 | 0.70 | 0.61 |
| 1.00 | 1.009 | 0.105 | 0.105 | 1.00 | 0.81 | 0.78 |

Detection is monotone and tracks the analytic expectation. Calibration holds to within 17% at worst. The 0.95 row overshoots because its realized R was 0.962 rather than 0.950 — the condition was measured at a slightly easier true value than its label. The point estimator sits within 0.007 of realized R throughout.

This retired the drafted closure. Under favorable assumptions the design detects retention at 81% when retention is complete.

## Planned support — the decisive run

The favorable configuration was favorable on three counts at once: zero heterogeneity, shared latents, and equal 170/700 support in both splits. The planned random test is smaller than the divergent test, and `R` divides by `Δ_rand`, so the random split's size bears directly on the statistic.

Configuration verified before launch on all eight parameters: both sigmas live at 0.75 and 0.60, random support 100 clusters / 420 positives, divergent support 170 clusters / 700 positives, calibration ratio exposed in the output. 100 outer, 300 bootstrap replicates (`686fda2`, `06e4f06`, `8d92e7f`).

| true R | half-width | mean CI_low | detection | calibration ratio |
|---:|---:|---:|---:|---:|
| 0.95 | 0.4112 | 0.636 | 0.18 | 0.967 |
| 1.00 | 0.4118 | 0.688 | 0.29 | 0.928 |

Calibration ratios of 0.93 and 0.97 confirm the bootstrap is measuring real sampling variability, so the detection figures mean what they say.

Adding heterogeneity and the real random split doubled the half-width from 0.207 to 0.412 and cut detection at complete retention from 0.81 to 0.29.

## Closure

At planned support, the calibrated simulator detects complete true retention only 29% of the time. The mean point estimate remains centered near the target, the bootstrap remains calibrated against across-dataset variability, and every retention bootstrap replicate is valid. The failure is therefore precision under the planned support and heterogeneity assumptions.

At the observed mean log-R half-width of approximately 0.412, the preregistered lower-bound requirement is demanding enough that point estimates substantially above complete retention would often be needed before `CI_low(R) > 0.75` clears. This is a diagnostic consequence of the observed interval width, not a separately simulated biological regime, and it is not used as the stopping rule.

The 0.207 → 0.412 increase in half-width combines cluster heterogeneity and unequal random/divergent support. Their separate contributions were not identified. The present evidence therefore closes the **planned configuration**, not every possible reallocation or future catalytic-residue design.

Experiment 02 therefore closes: **NO VERDICT — UNDERPOWERED, PRE-DATA.**

No confirmatory M-CSA dataset was constructed. No ESM-2 embeddings were extracted. No probe was fit. No random-test or divergent-test result was inspected. No threshold was relaxed after the precision analysis. No homology-transferred labels were introduced to rescue power. No layer sweep, model-size sweep, EC holdout, CATH holdout, or alternative model was added.

## What this record is for

The closure changed direction twice. It was drafted on the unpaired, AP-pinned simulator; retired when both defects were found; and reinstated on a simulator that passes its own calibration check. The final conclusion happens to match the first one, which makes it easy to present as though the intermediate work was wasted. It was not — the first version of this conclusion was not supported by its own evidence, and only the corrections make the final one worth anything.

The transferable lesson: a feasibility simulator is an instrument and needs its own validity check. The calibration ratio in the table above — across-replicate variability against bootstrap width — is the check that should have run first, before any grid, floor, or detection number was reported.
