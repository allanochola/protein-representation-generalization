# Disabled resolvability implementation 001

Formal Gate B. This commit implements the frozen statistical specification;
it authorizes no production simulation, surface or benchmark.

## Phases

- Validation runner: both allocations, V1 and V2 budgets from the frozen settings,
  plus V3 boundary fixtures. Results are archived whether numerical validation
  passes or fails. Integrity exceptions retain checkpoints and require inspection.
- Surface runner: independent authorization; the validation runner must be closed.
  Before loading design or generating anything, verify every validation archive
  file against committed bytes and hashes; reaggregate archived replicate records;
  require all V1/V2 cells and all V3 fixtures to pass.
- Benchmark runner: separately disabled, fabricated group sizes and fabricated
  scores only. It reads no real geometry. It discards inference results and
  reports timing plus explicitly illustrative serial-runtime extrapolations.

The benchmark must be audited and archived before authorizing expensive validation.
No automatic resource-driven reduction in budgets or change in statistical method.

## Numerical conventions and synthetic audit

Calibration is the smallest observed score attaining weighted CDF >=19/20.
A fast cumulative calculation locates the crossing; exact rational group weights
resolve near-boundary roundoff. All ties at a selected score have the same call;
classification uses strict greater-than. Bootstrap groups carry multiplicities,
all their records, both arms and mixed labels together. Both thresholds are refit
inside every bootstrap draw.

Positive-score means use Python statistics.NormalDist inverse CDF. NumPy PCG64
provides independent per-outer generation and bootstrap streams under the frozen
hash-token rule. All bootstrap multiplicities are drawn before computational
batching. Chunk order or batch size does not change the specified stream.

Boundary fixtures have identical scores across arms. Perfect separation uses
negative=0, positive=1. Tied negatives use negative=0 and positive=0/1 alternating
in stable record order. Adjacent-score fixtures give all negative records distinct
scores by stable identifier order and positive scores=2. The observed calibration
threshold and midpoint to the next calibration score must induce the same
CALIBRATION calls. An evaluation score could lie in that gap: identical calibration
calls do not imply identical evaluation calls. The midpoint never replaces the
frozen observed threshold. Report the gap explicitly.

The audit uses synthetic records only and tests exact rational quantiles, ties,
refitting, group multiplicity, identical-arm cancellation, zero-support failures,
insertion-order stability, batch invariance, disjoint phase streams and the V1/V2/V3
acceptance firewall. It does not load archived biological geometry or estimate
real-geometry power/coverage.

## Checkpoints and publication

Production writes 100-outer-replicate checkpoint chunks outside the repository,
bound to phase, execution HEAD, runner, implementation/settings and validation
identity. No retry is automatic. Explicit --resume accepts only a matching complete
checkpoint ledger. Partial or orphan chunks stop rather than silently recompute.
Thus an interruption within an unpublished chunk needs an explicit recovery ruling.
Atomic publication uses a temporary directory on the archive filesystem.

Published archives include per-replicate summaries, summary tables, checkpoint
ledger and non-circular provenance. No empirical model or protected performance
inputs are allowed. Disabled source hash identities are preserved; separate
authorization/closure may change only the gate and self-description, verified
through normalized AST hashes.

Operational groups are not certified independent families. Favorable conditional
precision does not settle overlap or historical family-separation limitations.
