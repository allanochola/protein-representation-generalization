# A1-C void record 001 — grouping-rule implementation failure

## Classification
Repairable implementation failure. The frozen grouping rule was not changed.
The implementation failed to apply it. The census result is VOID.

## What happened
A1-C was authorized at commit ab82118a5b0e72f208f5535bddaf014215277487 and
executed once. Its output was audited before any commit. The audit found that
proteins whose accepted Pfam families carry no clan were grouped under the
empty string rather than under the frozen family-accession fallback.

## Evidence (recorded pre-commit, from the uncommitted output)
- Pfam 37.0 families with no clan in the archived Pfam-A.clans.tsv: 12167 of 21979.
- Rows in assignments.tsv containing an empty group token: 6.
- Of those rows, proteins carrying at least one no-clan family: 6.
- Rows using a family-accession fallback: 0.

The fallback path never executed.

## Root cause
The implementation resolved clans with a dictionary default keyed on family
absence. In Pfam-A.clans.tsv a family without a clan is PRESENT with an empty
clan value, so the default never fired and the empty string propagated as a
group identifier. Every no-clan family would therefore share one meaningless
group, and any component computed over that grouping is not the frozen grouping.

## Why the preauthorization audit did not catch it
The synthetic census test used a family absent from the clans mapping, which
exercises the dictionary default. It did not test a family present with an
empty clan value, which is how real Pfam encodes the no-clan case.

## Disposition
- The census output was NEVER committed and has been discarded.
- No L value, route, component count, or component size was read or recorded.
- A1-C is re-disabled by this commit.
- A1-S remains closed. The A1-S archive is unmodified.
- The confirmatory universe was not accessed at any point.

## Required before re-authorization
1. Repair the clan resolution so an empty clan value is treated as absent and
   the frozen family-accession fallback applies.
2. Extend the preauthorization audit with a family PRESENT in the mapping with
   an empty clan value, asserting the family-accession fallback.
3. Assert that no emitted group identifier is empty.
4. Re-run the full split preauthorization audit.
5. Re-authorize A1-C in an isolated commit and re-execute.
