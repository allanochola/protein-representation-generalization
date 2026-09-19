# Gate A2 intake schema repair 001

**Status:** Frozen while A2-I is disabled.

## Cause

The first authorized intake was voided because the positive
membership TSV uses `cluster_rep` rather than one of the frozen
accession aliases. It also uses `representative_length` rather than
one of the frozen length aliases.

The negative schema already resolves through `accession` and
`length`.

## Narrow repair

- add `cluster_rep` to the identifier alias set;
- add `representative_length` to the length alias set;
- retain the original exactly-one-match rule;
- retain all banned-column and output-schema firewalls;
- do not copy `annotation_status` into the canonical intake output.

No data row, sequence, grouping, geometry, prediction, score, or
confirmatory outcome was inspected when choosing this repair.

The repair does not authorize execution. A2-I requires a separate
authorization commit.

- `confirmatory_metadata_accessed: true`
- `confirmatory_outcomes_accessed: false`
