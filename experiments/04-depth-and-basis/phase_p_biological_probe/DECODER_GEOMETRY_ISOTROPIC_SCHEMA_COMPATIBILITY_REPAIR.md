# Decoder Geometry Isotropic Schema Compatibility Repair

Status: **FROZEN HARD-DISABLED / PRE-AUTHORIZATION**

Parent reconciliation commit:

`ab053bafa24a45d15b481140fc3e485f6fb0b9e0`

Reconciliation note SHA-256:

`b5c15fe37427fd34d668778d6bffa2fae1c9aa36a7b3e726a5b08e9267e1268a`

Pre-repair hard-disabled final aggregation driver SHA-256:

`eaa6e45845438e5ffc4f55fa7502ce4954c2343dfb7d3fff24912bdbb062c303`

Repaired hard-disabled final aggregation driver SHA-256:

`e5c60d4b5e8fb3ba929e51b4940af76be78524e734e4dc85b05835d7c82e438c`

## Scope

This repair addresses only the isotropic serialization-interface defect
documented in `DECODER_GEOMETRY_ISOTROPIC_SCHEMA_RECONCILIATION.md`.

Historical isotropic private records remain immutable.

No biological, canonical permutation-null, C-matched, or confirmatory record
is modified.

No geometry is recomputed.

No random seed is consumed.

No aggregation or bootstrap is executed during repair validation.

## Compatibility behavior

For an isotropic record already containing dictionary-valued `omp` and
`raw_weight` fields, the loader preserves those objects.

For the exact historical flattened serialization, where both fields are
absent, the loader constructs an in-memory copy and adds:

### `omp`

- `status <- omp_status`
- `rank_deficient <- rank_deficient`
- `rank_deficiency_step <- rank_deficiency_step`
- `exact_reconstruction_step <- exact_reconstruction_step`
- `r_by_k <- r_by_k`
- `rank_by_k <- rank_by_k`
- `condition_by_k <- condition_by_k`

### `raw_weight`

- `status <- raw_weight_status`
- `topk_mass <- topk_mass`
- `n_eff <- n_eff`

If exactly one of `omp` or `raw_weight` exists, the loader rejects the
serialization as ambiguous.

If a flattened source field is missing, the loader rejects the record.

The normalized in-memory record is passed through the pre-existing
`validate_eligible_geometry` validator.

The normalized record is then retained by isotropic discovery so that the
existing downstream `geometry_from_isotropic_record` function can consume
the expected nested schema.

## Full-population repair audit

The hard-disabled repaired loader was exercised over the exact historical
isotropic population:

- records: 1,000
- indices: exactly 0 through 999
- unchanged validator accepted: 1,000 / 1,000
- downstream geometry extraction accepted: 1,000 / 1,000
- mapped scientific-field mismatches: 0
- geometry engine SHA-256: `8289d96a11ee3f5506edf298bf0290f58414454737156c98737f4522642915ab`
- geometry specification SHA-256: `205d13b20ef5bf9325794274b531f46c9ffa7fa7cc77a7e8bdd0a8be05edce69`

No population summary, comparison, bootstrap, p-value, or PASS/FAIL verdict
was computed.

No final aggregation output exists.

The confirmatory universe remained untouched.

## Authorization boundary

The repaired driver remains hard-disabled.

A later authorization may change only:

`ENABLE_AGGREGATION = False`

to:

`ENABLE_AGGREGATION = True`

after this hard-disabled repair commit is authenticated.

No additional scientific or compatibility change is permitted in that
authorization commit.
