# Candidate 2 production checkpoint contract 001

State: prospective operational specification only. This commit authorizes no
production validation, surface execution, or production checkpoint upload.
Implement and audit this contract while all execution gates remain disabled.
A separate authorization must name validation execution and its checkpoint
uploads. The surface remains separately gated.

## Scientific invariants

Candidate 2 remains the frozen paired hierarchical bootstrap: unchanged random
streams, occurrence-level draws, endpoint equality non-rejection, 999 bootstrap
replicates, allocation, estimands and acceptance bands. Complete both 10,000-slot
V1 cells, all six 2,500-slot V2 cells and both V3 fixture sets. No early stopping
based on results, no replacement seeds, no interval adjustment and no best-cell
selection. Session stops are operational only. Preserve all 35,000 outer slots.
Validation results stay withheld until complete independent audit and archival.
The resolvability surface cannot be generated or read until all V1/V2/V3 pass
and separate surface authorization is committed.

## Stable execution identity

The checkpoint binds candidate, phase, authorization HEAD, runner, implementation
snapshot and settings hashes, and the pinned Python/NumPy environment. Storage
commits never change the experiment branch. Keep the same experiment authorization
HEAD through all validation sessions. An amended implementation cannot silently
resume an existing execution. Checkpoint files must be restored into a temporary
directory on the destination filesystem and verified before atomic publication.

## Bounded sessions and checkpoint handshakes

Retain the production 100-outer-slot checkpoint cadence and original slot order.
At every committed chunk boundary, finish and fsync the chunk and atomically
publish its ledger, then PAUSE the worker. The controller exports that exact
ledger and all its referenced chunks. The worker may not begin the next chunk
until the controller verifies the remote commit through an independent fetch.
This handshake prevents copying a moving ledger. V3/final publication also needs
an explicit durable handoff; completing computation does not imply archival.

Each launch records freshly user-reported remaining session minutes and a chosen
wall-time budget, capped at 120 minutes. Reserve at least 30 minutes of the reported
allowance for export and shutdown. Before starting a chunk, require enough budget
for 1.25 times the largest of the slower-fixture median chunk estimate and all
observed completed-chunk durations in this execution. Stop cleanly at a chunk
boundary when insufficient. No hard kill of a running chunk is planned. These
estimates are admission rules, not guarantees of completion before platform kill.
The prior session's 11h20m is stale. CPU quota is not displayed; no unlimited-quota
assumption or guaranteed number of sessions is permitted.

## Durable append-only storage

Use the existing exp05-candidate2-checkpoint-storage branch. Preserve its probes
and controlled-reset artifacts. Production storage contract adoption requires the
separate production upload authorization. Namespace:
production/candidate2/validation/<execution_identity>/.
Store immutable chunks by content hash and numbered immutable export manifests;
each manifest contains the complete ledger, member hashes, execution binding,
previous export identity, completed slot ranges and environment. No summary of
coverage, rejection, width, power or simulated scores is printed during progress.
Retaining raw checkpoint bytes for resume is permitted by the future upload scope;
reading them for interim scientific decisions is not.

Use ordinary fast-forward pushes with expected-parent verification. A fresh fetch
must reproduce the export manifest and all referenced chunk hashes before receipt
and worker acknowledgement. No force pushes, branch resets, overwritten chunks,
automatic inference retry or silent collision resolution. A failed export leaves
the worker paused and local state intact. Export-only recovery may upload existing
verified bytes without running inference. Remote branch movement requires
inspection; never rerun slots to repair a Git failure.

## Restore and failure paths

Restore only from an explicitly pinned, independently fetched export. Verify the
entire member set, hashes, binding, slot continuity, uniqueness, cell budgets and
ledger before importing scientific execution code or computing a slot. Explicit
resume skips completed slots. Corrupt, missing, orphan, overlapping or foreign
chunks stop before work. A local partial file or a session killed mid-chunk needs
a recorded recovery decision; this contract does not authorize recomputing lost
or partly completed inference. The export boundary defines demonstrated durable
progress; work after it is not presumed recoverable.

## Required synthetic implementation audit

Test actual production scheduling with fabricated geometry: worker pause/ack,
no next chunk before verified export, stop at budget boundary, export-only retry,
restore/skip, foreign execution rejection, corrupt/missing/orphan/duplicate chunks,
remote-parent movement and stable publication. Use actual inference for a small
fixture with test-only small chunk sizes; assert production default remains 100.
Compare resumed outputs and final RNG states against uninterrupted reference.
These audits must not load production geometry or validation results.

## Evidence and limits

The archived controlled reset test used real synthetic inference, a genuine
user-attested session reset, remote restoration and exact comparison of twelve
outputs and RNG states. It tested a dedicated fixture, not the production phase
runtime. It does not establish survival of a kill mid-write, automatic periodic
backup, storage availability, or production-scale runtime. This contract's
implementation and synthetic audit remain necessary before authorization.
