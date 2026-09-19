# Gate A2 sequence-recovery void record 001

**Classification:** Repairable implementation failure

**Authorization commit:** `ee2ec0bd2653b5a6ef5529b4358a7d646abfb1b3`

## Failure

The first authorized A2-SR execution completed network retrieval and
constructed its staged archive, but final publication failed with:

```text
OSError: [Errno 18] Invalid cross-device link
```

The runner created its temporary directory under `/tmp` and attempted
to rename it into the Git worktree on another filesystem. Python's
`Path.rename` cannot cross filesystem boundaries.

The temporary archive was deleted when the failed process exited.
No A2-SR output was committed or retained.

- `confirmatory_metadata_accessed: true`
- `confirmatory_sequence_accessed: true`
- `confirmatory_outcomes_accessed: false`
- sequence-recovery result: void
- Pfam scan performed: no
- MMseqs2 clustering performed: no
- family geometry computed: no

## Repair rule

Create the temporary staging directory under `OUTPUT.parent`, on the
same filesystem as the final archive. Preserve the atomic directory
rename and every retrieval, drift, hashing and output rule unchanged.

The failed retrieval result is void. It may not be interpreted.
