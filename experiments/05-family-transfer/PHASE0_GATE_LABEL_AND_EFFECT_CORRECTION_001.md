# Phase-0 gate-label and effect-target correction 001

Status: correction before simulator implementation or execution.
Authority: PRE_PROTOCOL.md and RESOLVABILITY_PLAN.md, pinned in the companion JSON.

## Formal labels and historical artifact names

| Formal gate | Function | Historical labels in this work |
|---|---|---|
| A | Independence / family geometry | A1, A2 |
| B | Resolvability | Recent Gate C simulator/scope discussion |
| C | Comparator | GATE_B_FIXED_COMPARATOR_AMENDMENT_001.md and related comparator work |
| D | Provenance | Supports instruments across phases |
| E | Firewall | Continuously binding |

The naming mismatch does not retroactively certify that a formal gate passed.
Existing files, commits and archives are retained. New simulator artifacts
should use resolvability in their names and explicitly identify formal Gate B.
The operational order remains comparator scope, A1, comparator build/freeze,
A2, then simulator validation and resolvability surface.

## Frozen scientific target and validation requirements

The minimum scientifically interesting incremental effect is +0.10.
Required power is >=0.80 at DeltaTPR=+0.10 and median interval half-width <=0.10.
The grid includes 0, +0.05, +0.10, +0.15 and +0.20. The +0.05 value is not
the Experiment 05 scientific target. Earlier pessimistic assertions about
resolving +0.05 do not establish infeasibility at +0.10.

V1: at least 10,000 null replicates with family clustering on the public
161-positive/3,541-negative geometry; type-I error in [0.030, 0.070] at alpha .05.
V2: nominal 95% interval coverage in [0.93, 0.97] at at least three nonzero effects.
V3: defined, recorded handling of perfect separation and an operating-point
threshold between adjacent negative scores, without silently clipping results.
All three must pass before any resolvability surface is viewed. Failures follow
the inherited implementation/scientific-failure classification.

## Partition and remaining prospective choices

Development, calibration and protected evaluation have different roles.
Thresholds are estimated only from calibration families and transferred unchanged
to evaluation families. Their negative-family counts must be audited separately.
556 negative-bearing sequence clusters does not imply 278 independent families
per side. Group sizes, mixed labels, overlap and grouping assumptions matter.

Before implementation, specify the primary weighting estimand, operational
groupings, deterministic allocation rule and realistic allocation set, threshold
rule and ties, paired interval method with calibration refitting, dependence
regimes, seeds, Monte Carlo budgets, and scenario-level and aggregate reporting.
Do not infer measured independence or an effective sample size from a grouping.
No numerical choice absent from the inherited protocol is frozen by this correction.

## Closure and scope

If no realistic allocation clears both primary targets, the inherited plan
closes Experiment 05 unresolved before ESM extraction. The tested allocation
set must be frozen prospectively and its scientific scope stated; failure on
an arbitrary narrow set cannot establish universal impossibility.

This remains an unchanged-universe feasibility diagnostic. Neither a favorable
result nor this naming correction clears exact negative-sequence holdout overlap
or verifies historical family separation. Confirmatory outcomes remain sealed.
