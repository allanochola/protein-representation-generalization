# Resolvability validation diagnostic 001

Status: descriptive analysis of the existing rejected validation instrument.
Candidate 1 remains rejected. This record authorizes no replacement or execution.

## Scope and evidence

All eight committed validation cells are analyzed, preserving the frozen V1/V2
classification and verifying original archive bytes. No simulator is imported;
no synthetic scores or bootstrap samples are regenerated. No surface is read.
Existing archives, settings, runners, and rejection record are unchanged.

The companion JSON reports point-estimate bias and spread, interval width,
interval-center displacement from the estimate, signed endpoint distances,
coverage misses in each tail, and exact endpoint contact with the true effect.
For V1 the true effect is zero. Contact uses exact stored numeric equality;
no tolerance, rounding or revised acceptance decision is introduced.

It also reports calibration thresholds across outer datasets, deviations from
the frozen theoretical negative 95th percentile, archived within-replicate
bootstrap threshold standard deviations, empirical calibration CDF jumps,
calibration/evaluation FPR, and paired-arm threshold correlation. Exploratory
correlations of width with threshold uncertainty are descriptive only.

These are post-validation diagnostics, not prospectively registered tests or
criteria for selecting a replacement. Correlation does not establish a cause.
Endpoint contact, asymmetry and bias can describe the failure but cannot alone
identify its mechanism. Monte Carlo uncertainty does not waive rejection.
Archived bootstrap draws are unavailable here: no alternative interval can be
reconstructed from these summaries, and none is calculated.

## Frozen ruling remains binding

Both V1 cells failed; all six V2 cells and the V3 fixtures passed. Candidate 1
is not adjusted, rerun, or extended to seek acceptance. Power/surface results
remain NOT_EVALUATED_VALIDATION_FAILED. No claim about resolving +0.10 follows.
A replacement requires a prospective methodological amendment with a bounded
process and fresh validation streams. These diagnostics prescribe no narrower
interval target and authorize no method selection.

Holdout sequence overlap and unverified historical reference-family separation
remain unresolved by this simulation work. Confirmatory outcomes remain sealed.

## Descriptive results

- dominant_to_calibration, V1, effect 0.00: bias 0.0001716129; median half-width 0.13466747; interval above truth 137; below truth 133; endpoint touches truth 65.
- dominant_to_calibration, V2, effect 0.05: bias 0.0011483871; median half-width 0.13199165; interval above truth 40; below truth 38; endpoint touches truth 0.
- dominant_to_calibration, V2, effect 0.10: bias 0.00052129032; median half-width 0.12936924; interval above truth 43; below truth 41; endpoint touches truth 0.
- dominant_to_calibration, V2, effect 0.20: bias -0.00070451613; median half-width 0.12160467; interval above truth 37; below truth 51; endpoint touches truth 0.
- dominant_to_evaluation, V1, effect 0.00: bias 5.974026e-05; median half-width 0.13368089; interval above truth 135; below truth 156; endpoint touches truth 64.
- dominant_to_evaluation, V2, effect 0.05: bias -7.012987e-05; median half-width 0.13165503; interval above truth 41; below truth 43; endpoint touches truth 0.
- dominant_to_evaluation, V2, effect 0.10: bias -0.0005974026; median half-width 0.12933606; interval above truth 39; below truth 47; endpoint touches truth 0.
- dominant_to_evaluation, V2, effect 0.20: bias -0.00032467532; median half-width 0.12095694; interval above truth 46; below truth 52; endpoint touches truth 0.
