# Candidate 2 checkpoint implementation 001

Disabled implementation of the production recovery contract. No validation,
production checkpoint upload or surface execution is authorized by this commit.
The source changes only phase scheduling, transport and recovery. The statistical
core, random streams, inference method and 100-slot production cadence are unchanged.

The existing validation runner refuses execution without a controller. The new
session runner has a separate disabled upload gate and also requires the validation
gate to be authorized. Its behavior is bound by the implementation snapshot's
normalized runner hash. Both future gate changes must be separately recorded;
the final authorization HEAD remains constant throughout the execution.

The controller pauses synchronously for every ledger export, independent fetch and
hash acknowledgement before admitting another chunk. Restoration checks the exact
prefix of chunks, slot indices, binding and member hashes before loading geometry.
Final archives are exported after V3 and publication, with values withheld.

The storage branch must first have an explicitly adopted production contract with
production_checkpoint_upload_authorized true and production_execution_head equal
to the final experiment authorization HEAD. This implementation does not adopt it.
Production namespace is content-addressed by the unchanged runtime execution binding.

Future launch arguments require a fresh remaining-minutes report, budget-minutes
at most 120, and exact storage-parent commit. Cross-session recovery uses a pinned
restore-export number; local continuation uses resume-local and must exactly match
the latest remote checkpoint. Export-only cannot compute inference and requires a
retained timing receipt matching the checkpoint. Transport directories and failed
local Git commits are retained, with no automatic retry. A failure after remote
push but before fetch must be inspected and reconciled before further action.

The synthetic audit runs the actual phase scheduler on fabricated geometry with a
test-only two-slot chunk. Actual inference uses 999 bootstrap replicates. It checks
bounded stop, restored skipping, exact outputs and final RNG states, failure to
advance without acknowledgement, export-only handling, and corrupt/missing/orphan/
duplicate/foreign input rejection. Local bare Git repositories exercise actual
push/fetch bytes and remote-parent movement without GitHub uploads. This complements
the separate genuine-session reset test; it is not a production run or a promise
of survival under process kill during inference, write, or publication.

Session-budget admission uses 25% headroom over the maximum benchmark chunk estimate
and recorded completed-chunk time. Thirty minutes is reserved from the freshly
reported allowance. Platform quotas remain unverified. No hard completion guarantee
is made, and a partial chunk still requires a recorded recovery decision.
