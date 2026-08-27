# Results — Experiment 01: secondary-structure representation generalization

## Result

**Frozen verdict: H_repr.**

A linear probe on fixed layer-17 representations from ESM-2 650M retained essentially all of its Q3 secondary-structure performance when evaluation moved from the in-distribution random-protein test to proteins from 30%-identity clusters held out from training.

On the divergent test, ESM-2 exceeded the explicit ±3-residue local-sequence baseline by **15.50 percentage points**:

**Δ_ESM(divergent) = +0.1550, 95% cluster-bootstrap CI [+0.151, +0.159].**

The ESM probe's random-to-divergent degradation was only **0.29 percentage points**:

**G = +0.0029, 95% cluster-bootstrap CI [-0.003, +0.009].**

The preregistered `H_repr` region required Δ_ESM(divergent) ≥ 0.08 and G ≤ 0.10. Both conditions are satisfied comfortably.

## Confirmatory result table

| Representation | Test split | Q3 accuracy | Macro-F1 |
|---|---|---:|---:|
| ESM-2 layer 17 | Random / in-distribution | 0.765166 | 0.760551 |
| ESM-2 layer 17 | 30%-cluster-held-out / divergent | 0.762263 | 0.758054 |
| ±3 local sequence | Random / in-distribution | 0.607324 | 0.568646 |
| ±3 local sequence | 30%-cluster-held-out / divergent | 0.607224 | 0.568602 |

| Preregistered quantity | Estimate | 95% cluster-bootstrap CI | H_repr band |
|---|---:|---:|---:|
| Δ_ESM(divergent) | +0.155039 | [+0.151, +0.159] | ≥ +0.08 |
| G = Q3(ESM, random) − Q3(ESM, divergent) | +0.002903 | [-0.003, +0.009] | ≤ +0.10 |

## Interpretation

The result supports the preregistered representation-generalization hypothesis for this target.

The fixed ESM representation carries substantial linearly accessible Q3 secondary-structure information beyond the ±3 local-sequence context tested here. That advantage does not materially weaken when the probe is evaluated on proteins from sequence-identity clusters excluded from training.

The result is stronger than showing that ESM-2 predicts secondary structure well. The experiment specifically tests whether the apparent internal signal survives an explicit evolutionary-divergence control and whether it remains informative beyond an obvious local-sequence comparator. Both tests favor representation generalization.

The local baseline is essentially unchanged across the two tests (0.607324 random versus 0.607224 divergent), while ESM-2 is also nearly unchanged (0.765166 versus 0.762263). A large change in basic test-set difficulty therefore does not explain the retained ESM margin.

## Split audit

The canonical dataset contains **11,373 proteins, 11,043 30%-identity clusters, and 2,875,432 labeled residues**.

| Split | Proteins | Distinct clusters | Residues |
|---|---:|---:|---:|
| Train | 7,712 | 7,529 | 1,946,379 |
| Random / in-distribution test | 1,361 | 1,353 | 346,632 |
| Divergent test | 2,300 | 2,209 | 582,421 |

The per-split cluster counts sum naively to 11,091 because **48 clusters contain separate proteins assigned to both training and the in-distribution random test**:

`7,529 + 1,353 + 2,209 − 48 = 11,043`.

This is intentional. The random test is an in-distribution reference where homologous cluster membership may remain represented in training.

The load-bearing divergent split is clean: it shares **zero clusters** with training and **zero clusters** with the random test. There is also zero protein overlap between every pair of splits. The union of the three cluster sets is exactly the full set of 11,043 clusters.

## Bootstrap audit

Confidence intervals use 2,000 seed-0 bootstrap replicates with the sequence-identity cluster as the resampling unit.

The original implementation repeatedly materialized and concatenated residue-index arrays for every sampled cluster. This made the bootstrap computationally prohibitive despite predictions already being fixed.

After the primary point estimates had been saved, the implementation was replaced with an equivalent sufficient-statistic calculation using per-cluster residue counts and correct-prediction counts.

The statistical procedure did not change: cluster resampling, replacement scheme, random seed, sampled-cluster counts, residue-weighted statistic, replicate count, and percentile interval remained frozen.

Before the optimized implementation was used for the final intervals, equivalence was tested against the original computation. The paired Δ_ESM interval agreed to machine precision (maximum CI difference 2.1 × 10^-17). The G bootstrap produced exactly identical bootstrap replicates and exactly identical intervals.

The optimized 2,000-replicate bootstrap took **1.797 seconds total**: 0.698 seconds for Δ_ESM and 1.099 seconds for G.

The checkpointed final rerun reproduced the saved primary metrics and final confidence intervals. Because that rerun loaded the same trained probe checkpoints, it is not presented as an independent end-to-end retraining determinism test. Split determinism was tested separately by scrambling row order and arbitrary cluster labels and recovering identical biological split membership.

## Scope

This experiment establishes a narrower claim than general biological-function or biosecurity-feature generalization.

Secondary structure is a structural property, not a functional screening target. Linear probing establishes that information is accessible to a linear readout; it does not establish causal use by the model.

The result therefore motivates a higher-level biological generalization test before causal work such as activation patching or sparse-feature analysis.

It does not by itself establish a function-relevant screening feature.

## Conclusion

Experiment 01 lands in **H_repr** under the frozen decision bands.

For Q3 secondary structure, a fixed middle-layer ESM-2 representation preserves a large advantage over local sequence cues across a 30%-sequence-identity cluster holdout, with essentially no measurable degradation relative to the in-distribution reference.
