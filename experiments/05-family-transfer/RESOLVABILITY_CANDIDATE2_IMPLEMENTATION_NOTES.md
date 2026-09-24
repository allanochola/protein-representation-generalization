# Candidate 2 disabled implementation

Implements RESOLVABILITY_CANDIDATE_2_SPECIFICATION.md without modifying Candidate 1.
Three separate gates protect synthetic timing, validation and surface execution.
All gates are false at this commit. Benchmarking needs separate authorization.

The point estimator, Gaussian generator, exact weighted-quantile helper, reporting
helpers and validation phase machinery are adapted from the pinned Candidate 1
sources listed in the implementation snapshot. Candidate 2 copies them into
separate modules; it does not import or mutate Candidate 1 production modules.
The new inference path draws groups, then paired records within each selected
occurrence and label stratum. An occurrence is never reduced to a multiplicity
before its independent inner draw. Thresholds are refit for every resample.

The implementation uses literal occurrence loops to preserve the specified RNG
ordering. Candidate 1 timing estimates do not predict its runtime. A separately
authorized synthetic benchmark is needed before sizing validation execution.

The synthetic audit uses fabricated geometry only. It checks interval endpoint
non-rejection, weighted thresholds against Fraction arithmetic, paired indices,
repeated-occurrence inner draws, explicit occurrence-weighted rates, nested refits,
missing-label failure, order/batch invariance, V3 and phase barriers. It does not
establish coverage, type-I calibration, power or scientific feasibility.

Validation archives raw inference indicators for audit, but its summary labels
power NOT_EVALUATED_VALIDATION_ONLY and omits positive-rejection-rate aggregation.
Candidate 2 surface verification accepts only its own committed passing validation
archive, bound to its implementation and settings. Candidate 1's archive cannot
unlock it. Checkpoints and outputs have candidate-specific paths.
