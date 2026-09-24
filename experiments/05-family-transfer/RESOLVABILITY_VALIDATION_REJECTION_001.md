# Resolvability validation rejection 001

Status: the frozen percentile-bootstrap instrument is rejected for resolvability
surface use. This records a valid archived validation outcome; the run is not voided.

## Evidence

| Allocation | V1 rejections / replicates | Rate | Required band | Result |
|---|---:|---:|---|---|
| Dominant to calibration | 270 / 10,000 | 0.0270 | [0.030, 0.070] | Reject |
| Dominant to evaluation | 291 / 10,000 | 0.0291 | [0.030, 0.070] | Reject |

All six V2 cells pass: coverage ranges from 0.9608 to 0.9688, within [0.93,0.97].
All three V3 fixtures pass in each allocation. There are zero recorded inference
failures among the 35,000 validation outer replicates. The surface has not run.

The accompanying record independently reconstructs V1/V2 counts from committed
replicate intervals and verifies archive hashes and recorded V3 acceptance. It
performs no new simulations and does not rerun boundary fixtures.

## Interpretation

The observed null rejection rates fall below the frozen acceptance band.
Higher coverage and lower rejection are consistent with conservative behavior
under the tested regimes. They do not establish the cause, prove that width
alone explains it, exclude an implementation defect, or establish invariance to
allocation. No cause is asserted in this record.

Neither proximity to a bound nor Monte Carlo uncertainty changes the frozen
acceptance rule. No rounding, seed retries, extension of this run's replicate
budget, or altered acceptance band is authorized to seek a passing result.

Low rejection at the zero-effect null does not validate a claim that the effect
exceeds +0.10. Lower power of a conservative method and bias in a simulated power
estimate are distinct concepts; neither is adjudicated without the blocked surface.
No conclusion about power at +0.10 or ESM-2 transfer follows from this rejection.

## Ruling and prospective work

Preserve the archived result, settings and code unchanged. Validation and surface
authorizations remain closed. No routine interval adjustment, new method,
resimulation or surface execution is authorized by this record.

The parent RESOLVABILITY_PLAN lists possible interval-method classes, while the
later RESOLVABILITY_STATISTICAL_SPEC_001 froze one method without competition.
An alternative therefore requires an explicit prospective amendment: record the
observed failure, methodological rationale, fresh validation streams, and a
bounded candidate/selection process. It must not become an undeclared search
until a method passes. A code repair requires evidence of an implementation
defect and the prescribed failure-classification process; this record establishes
no such defect.

Read-only analysis of existing validation evidence may inform diagnosis but cannot
change this rejection. Confirmatory outcomes remain sealed. The North Star remains
testing incremental unfamiliar-protein detection at controlled false-alarm rate;
this failed instrument validation has not answered that biological question.
