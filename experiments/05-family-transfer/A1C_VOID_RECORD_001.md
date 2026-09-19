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


---

## Appendix A — root-cause correction (appended; original text above unchanged)

The root-cause section above is accurate but incomplete. It identifies a gap in
a synthetic test. The primary cause was broader: at the time of the failure,
**no behavioral audit of the split runners existed in the repository.**

### What was actually in the tree

`audit_gate_a1_split.py` was 13 lines. It parsed both runners, asserted two
authorization strings by literal match, and checked a short token list for
phase separation. It never imported either runner, never called `census()`,
and never referenced clan resolution. `audit_gate_a1.py` targeted the
superseded combined runner, not the split successors.

The synthetic census battery — multidomain closure, the L denominator, the
concentration ceiling, the family-without-clan fallback — was executed in an
ad-hoc session cell during the split implementation. It was never committed.
It ran once, against code that subsequently changed, and left no artifact.

### Why this matters more than the missing case

The stub printed a PASS line on every run. That line was read, across several
authorization steps, as evidence of coverage it did not provide. A green
result from a test that asserts almost nothing is worse than no test, because
it suppresses the question of whether coverage exists.

The stub had also gone stale: its line 7 asserted `SCAN_AUTHORIZED = True`,
which became false when A1-S was correctly closed after its archived
execution. The script could not have passed in the repository state it was
committed to guard.

### Corrected root cause

1. **Primary.** No committed behavioral audit covered the split runners. The
   only thing that could have caught the clan-resolution defect before
   execution did not exist in the tree.
2. **Secondary.** The uncommitted synthetic test that did exercise grouping
   used a family absent from the clans mapping, which triggers the dictionary
   default. Real Pfam encodes a no-clan family as present with an empty clan
   value, so the default never fired.
3. **Contributing.** The committed stub emitted a PASS line, which was read as
   coverage, and contained a literal assertion that had become false.

### Remediation

`audit_gate_a1_split.py` was replaced with a behavioral preauthorization audit
(commit 5c9bffc2266d9eb552fa8fd0df4cfcec35483cab, 253 lines). It imports both
runners, and asserts: unique boolean gate states with both phases never
simultaneously authorized; phase-separation tokens in both directions;
subprocess use in A1-C restricted to `git ls-files`; the eight committed
archive SHA-256 values and their tracked status; the 278-row / 139-139
discovery gate through A1-S's own function; rejection of all four
`Pfam.version` field mutations; the loader's exclusion of empty clan values;
census semantics including clan mapping, transitive closure, both no-clan
encodings, and zero-hit retention; the empty-identifier backstop; routing
precedence and denominators at the frozen boundaries; and the banned-column
firewall.

That audit is to be re-run before every A1-S or A1-C authorization.

### Standing lesson

A test that is not in the repository is not a test. A passing line from a
script that asserts little is a liability, because it answers the coverage
question falsely. Gate states in audits are asserted structurally — unique
boolean assignment, mutual exclusion — rather than pinned to a literal value
that goes stale the moment the gate legitimately moves.

### Scope unchanged

This appendix corrects the causal record only. It does not alter the
classification (repairable implementation failure), the disposition (census
output void, never committed), or the re-authorization requirements. No
scientific value from the void run was read or recorded at any point, and the
confirmatory universe remains sealed.
