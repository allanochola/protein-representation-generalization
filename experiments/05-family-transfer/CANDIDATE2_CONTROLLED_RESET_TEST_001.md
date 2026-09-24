# Candidate 2 controlled reset test 001

Scope: 12 actual synthetic outer inferences, 999 hierarchical bootstrap replicates
each, fabricated dominant-calibration fixture (3696 records, 276 calibration
and 435 evaluation groups). Stream phase controlled_reset_001, allocation token
synthetic_reset_001, b=.60 rho=.30 r=.50 delta=.10; indices 0 through 11.
No production geometry or empirical confirmatory model outcomes are read.

First session: compute indices 0-5 once, save complete inference outputs and both
final per-outer RNG states, export to the dedicated storage branch and independently
fetch/hash-verify. Stop. Preserve the exact authorization commit and dependencies.
Second session: recover that checkpoint, refuse a same-session continuation,
compute ONLY indices 6-11, and compare all 12 outputs and RNG states against a
separately computed uninterrupted synthetic reference at the same stream indices.
The reference is explicitly authorized test duplication, not a validation retry.
No scientific inference values are printed or used for method decisions.

Test-only checkpoint cadence is six slots. Production cadence remains 100 and
production source is unchanged. This dedicated fixture tests core inference plus
remote checkpoint recovery; it is not an end-to-end production runtime test.
Previous stub tests cover production ledger scheduling and corruption checks.
The second-half wrapper must reject corrupt data, wrong implementation/execution
identity and completed-slot recomputation before continuation.

A working-directory session marker must be absent after the reported genuine
Kaggle reset, and the user must attest a new session. Marker absence alone does
not prove a reset. Do not delete it to bypass the guard. The reset test gate stays
open across the authorized two-session test and is closed after final archival.
All production validation/surface gates remain closed throughout.

This establishes controlled-stop recovery only. It does not establish survival
of a session kill mid-write, recovery of unuploaded work, automatic periodic
backup, guaranteed storage availability, or production-scale performance.

An earlier session had a user-reported 11 hours 20 minutes remaining; a Kaggle
reset has since been reported. Current remaining allowance is unverified.
CPU quota: not displayed. No production runtime budget is inferred from this.

Durable destination: exp05-candidate2-checkpoint-storage branch of this repository,
reset_tests/candidate2_reset_001/. Preserve existing probes and append the test
contract/checkpoint. Ordinary fast-forward pushes only. Production checkpoint
uploads are not authorized. Stop on failure; no automatic inference retry.
