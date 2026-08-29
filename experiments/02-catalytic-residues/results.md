# Results — Experiment 02: catalytic-residue representation generalization

## Outcome

**NO VERDICT — UNDERPOWERED, PRE-DATA.**

Experiment 02 stopped before any confirmatory biological label or result was inspected. Pre-data synthetic precision analysis showed that the planned sample size could not estimate the preregistered retention quantity precisely enough to support the `H_repr` decision rule.

## Basis

`H_repr` required both an advantage over the local comparator on the divergent split and retention of that advantage:

    R = Δ_div / Δ_rand,   with   CI_low(R) > 0.75

At the planned support — 170 clusters and 700 positives divergent, 100 clusters and 420 positives random, with cluster-level heterogeneity active:

| true R | detection | half-width | calibration ratio |
|---:|---:|---:|---:|
| 0.95 | 0.18 | 0.411 | 0.967 |
| 1.00 | 0.29 | 0.412 | 0.928 |

Even at complete retention the criterion fires less than a third of the time. At the observed mean interval width, point estimates substantially above 1 would often be needed before the lower confidence bound clears 0.75; this is a diagnostic consequence of the interval width, not an additional simulated operating point.

The calibration ratios confirm the bootstrap measures real across-dataset variability, so these detection figures are trustworthy. The estimator is well centered and every bootstrap replicate was valid; the limitation is precision alone.

The absolute advantage arm was adequately precise at the same support and is not what closed the experiment.

## Instrument history

The closure was drafted once on a defective simulator, retired when two defects were found, and reinstated on a corrected one. Uncorrelated arms inflated the variance of every difference statistic; AP pinning deflated detection roughly sevenfold. Both are documented in `IMPLEMENTATION_NOTES.md`. The final result rests on a simulator whose bootstrap width matches across-dataset variability to within 8%.

## Scope

**The experimental design is closed. The biological hypothesis is not.**

Nothing here shows that catalytic-residue information in ESM-2 fails to generalize across sequence families. It shows that this design, at the expected curated M-CSA support, cannot distinguish its own hypotheses with adequate precision.

No confirmatory M-CSA label pool was built, no ESM-2 embeddings extracted, no probe fit, and no test split evaluated. No threshold was weakened after the precision analysis, and no homology-transferred labels were introduced to rescue power.

See `PROTOCOL.md`, `PRE_DATA_PRECISION.md`, `IMPLEMENTATION_NOTES.md`, and `results/power_sim/`.
