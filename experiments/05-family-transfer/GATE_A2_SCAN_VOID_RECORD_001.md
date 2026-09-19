# Gate A2-SS void record 001

Status: voided. A2-SS re-disabled pending repair.

## What happened

The single authorized execution at `6cf5c64463f3e3de916ae7e543050821527efde6` raised
`Joint identifier mapping does not reproduce the frozen hash` inside
`build_joint` and exited 1. No archive directory was created, no
scanner ran, no tracked file was mutated.

## Scope of the defect

The joint FASTA assertion passed first: the derivation reproduced
`bbfa145c...` at 1,472,280 bytes over 3,980 namespaced records. Only
the identifier-mapping serialization differs from the artifact frozen
at `3eb736a5173ae0a41d5d319b40e5665adb4f0e86`. The defect is in the mapping writer, not in the
joint input itself.

## Ruling

The expected mapping hash is not edited. The writer is repaired to
match the frozen serialization, re-audited while disabled, and
reauthorized in a separate commit.

## State at void

- confirmatory metadata accessed: YES (A2 phase, expected)
- confirmatory sequences accessed: YES (A2-SR, committed)
- confirmatory outcomes accessed: NO
- Pfam scan performed: NO
- MMseqs2 clustering performed: NO
- family geometry computed: NO
