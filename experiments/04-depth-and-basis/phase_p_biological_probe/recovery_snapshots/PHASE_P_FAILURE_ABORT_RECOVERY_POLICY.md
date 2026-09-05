# Experiment 04 Phase P — Failure, Abort, and Recovery Policy

Status: FROZEN BEFORE BIOLOGICAL AUTHORIZATION

Scientific branch:
`exp04-depth-and-basis`

Frozen scientific HEAD:
`3e52262358914de0089e72491ce413d3c91e0a99`

Recovery branch:
`recovery/exp04-phase-p-checkpoints`

## 1. Scientific immutability

The scientific branch must remain at the frozen scientific HEAD during
biological Phase P execution.

Checkpoint persistence must not require commits, branch switches, resets,
or output staging in the scientific worktree.

No frozen scientific mechanics may be modified to repair, accelerate,
simplify, or otherwise adapt an in-progress biological execution.

## 2. Pre-first-protected-fit failures

Before the first protected biological fit begins, infrastructure failures
may be repaired and execution may be retried only if:

1. the scientific HEAD is unchanged;
2. the production runner hash remains the frozen authorized hash;
3. no protected biological fit has begun;
4. no protected seed namespace has been consumed;
5. the production output state is audited before retry.

Such a retry is not a biological rerun because protected execution has not
yet begun.

## 3. Point of no return

Once the first protected biological fit begins, the biological execution
identity is consumed.

From that point onward:

- no fresh biological rerun is permitted;
- no new seed namespace is permitted;
- no deletion-and-restart of production output is permitted;
- every continuation must be treated as a resume of the same execution.

## 4. Durable completion boundary

A scientific row counts as completed only after the frozen production runner
has appended the complete row, flushed the file handle, and successfully
fsync'd it.

Rows that are present on resume must pass the runner's strict structural and
scientific semantic validation before their atomic keys count as completed.

Existing valid rows must never be rerun or repaired.

## 5. Execution manifest

`execution_manifest.json` is create-once provenance.

On resume, its canonical bytes must exactly equal the manifest that the
frozen runner would construct from the authorized immutable inputs.

Any manifest mismatch is a hard STOP.

No provenance adaptation or reconstruction is permitted.

## 6. Recovery snapshot contents

A remote recovery snapshot may contain only the exact durable production
artifacts required for resume, plus recovery metadata.

The expected durable scientific artifact set is:

- `execution_manifest.json`
- the main Phase P per-perturbation CSV
- the permutation-null Phase P per-perturbation CSV

A snapshot may legitimately omit a CSV that has not yet been created at the
checkpointed execution stage.

Recovery metadata must record at minimum:

- scientific branch;
- scientific HEAD;
- production runner SHA-256;
- snapshot sequence identifier;
- snapshot creation time;
- exact included artifact filenames;
- SHA-256 of every included artifact;
- row count of each included CSV;
- whether the main census is complete;
- whether the null census has begun;
- whether the null census is complete.

Recovery metadata is not scientific output and must never alter the durable
production artifacts.

## 7. Snapshot publication

Recovery snapshots must be published only on the dedicated recovery branch.

Recovery history is append-only.

No force push, reset, history rewrite, or replacement of an earlier remote
snapshot is permitted.

Before publishing a new snapshot:

1. verify the scientific branch and HEAD;
2. verify the frozen production runner hash;
3. copy only already-durable production artifacts;
4. hash the copied bytes;
5. record row counts and execution stage;
6. commit the snapshot on the recovery branch;
7. push it;
8. verify the remote recovery HEAD;
9. verify the remote scientific HEAD remains frozen.

If remote checkpoint publication fails, do not modify scientific outputs to
make publication succeed.

## 8. Recovery after interruption or Kaggle reset

After protected execution has begun, a new environment must never start a
fresh biological run.

Recovery must:

1. recover the exact frozen scientific HEAD;
2. verify the frozen production runner SHA-256;
3. retrieve the latest valid recovery snapshot;
4. verify recovery-branch ancestry and snapshot metadata;
5. verify SHA-256 for every included artifact;
6. verify expected artifact filenames;
7. verify CSV row counts against metadata;
8. restore the exact artifact bytes into the production output directory;
9. allow the frozen runner itself to perform strict manifest and persisted-row
   validation;
10. continue only missing atomic keys.

If any provenance, hash, schema, semantic, ancestry, or row-count check fails,
STOP.

Do not infer, regenerate, repair, truncate, merge, or manually reconstruct
protected scientific rows.

## 9. Partial trailing writes

The frozen runner defines completed rows by successful persisted-row
validation.

If interruption leaves a malformed or structurally incomplete persisted CSV,
that state is not automatically repairable.

STOP and inspect the exact bytes and frozen runner semantics.

Do not truncate or rewrite the file merely because the last row appears
partial unless a separately frozen recovery procedure explicitly establishes
that operation as scientifically neutral.

## 10. Checkpoint loss

If local state is lost after protected execution begins, restore only from the
latest remotely verified recovery snapshot.

Any scientifically completed work after that remote snapshot but lost before
the next successful snapshot may be recomputed only as missing atomic keys of
the same frozen execution identity.

This does not create a new biological run or new seed namespace.

## 11. Corrupt or inconsistent recovery snapshot

If a recovery snapshot is corrupt, incomplete relative to its own metadata,
has unexpected files, fails hash verification, has invalid ancestry, or
conflicts with the frozen scientific state:

STOP.

Do not repair the snapshot by inference.

Use the most recent earlier snapshot that independently passes every frozen
recovery validation rule.

## 12. Completed-state re-entry

Once the exact main and null censuses are complete, re-entry must be a
validation-only resume.

The frozen runner must recognize every expected atomic key as already
completed and must not refit existing rows.

Completed-state re-entry is expected to preserve the durable scientific
artifacts byte-for-byte.

## 13. Interpretation boundary

Checkpointing, recovery, and completed-state validation must not inspect
scientific results for the purpose of changing execution mechanics,
hyperparameters, thresholds, representations, seed handling, stopping rules,
or analysis plans.

Operational recovery may inspect artifact existence, hashes, schemas, row
counts, keys, and frozen semantic-validity conditions only.

## 14. Abort conditions

Biological execution must hard STOP on any of the following:

- scientific HEAD mismatch;
- production runner SHA-256 mismatch;
- manifest mismatch;
- invalid recovery ancestry;
- recovery artifact hash mismatch;
- unexpected production artifact;
- invalid persisted-row schema;
- invalid persisted-row scientific semantics;
- duplicate atomic key;
- unexpected atomic key;
- protected seed namespace inconsistency;
- inability to establish whether a prior protected execution has begun;
- uncertainty about whether the requested action constitutes a fresh rerun.

When uncertain, preserve existing durable bytes and STOP.

## 15. Authorization boundary

Freezing this policy does not authorize biological Phase P.

Biological execution may begin only after a separate final pre-authorization
audit explicitly confirms the frozen scientific state, frozen runner hash,
closed-to-open authorization change, immutable inputs, production output
state, protected namespaces, and operational recovery readiness.
