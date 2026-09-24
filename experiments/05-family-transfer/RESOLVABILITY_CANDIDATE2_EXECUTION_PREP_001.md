# Candidate 2 execution preparation 001

Scope: synthetic runtime profiling and checkpoint plumbing only. Candidate 2's
statistical definition, source modules, validation budgets and acceptance criteria
remain unchanged. All benchmark/validation/surface phase gates remain closed.
This separate prep runner requires its own isolated authorization.

Profile one fabricated dataset per inherited benchmark geometry, with 999 nested
bootstraps, using a distinct execution_prep_profile stream namespace. Save only
function call counts, self/cumulative times and fixture dimensions. Discard scores,
estimates, intervals and all scientific metrics. Profiling adds overhead;
function cumulative times overlap. No causal performance attribution is prespecified.

Exercise the committed runtime's checkpoint/publication machinery in temporary
roots with stub inference rows: 101 slots, interruption after 100 durable slots,
hash-manifest ZIP export, restore in a different root, explicit resume. Require
all final archive bytes to match an uninterrupted fixture and only slot 100
(zero-based) to execute after restore. Require corrupted chunks and changed
execution identity to fail before work. Core outer inference and boundary outputs
are stubbed for this plumbing fixture, not tested statistically. No real geometry
is loaded. The temporary export is synthetic evidence, not a production backup.

This test does not demonstrate an actual Kaggle restart or a remote export service.
Before long validation, establish a durable export destination and retain the exact
authorization commit and dependency versions. No background auto-push of live or
partial production checkpoints is implemented or authorized here.

Sequence: freeze this record, disabled runner and source snapshot; separately
flip only the prep gate; run once; audit and archive; close the prep gate.
No optimization or production simulation is authorized by this record.
