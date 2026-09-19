# Gate A2 intake void record 001

**Classification:** Repairable implementation failure

**Authorization commit:** `f82dc048dd29538b1562fe718eb8d8c8dc0ca295`
**Authorization variable:** `A2_INTAKE_AUTHORIZED`

## Failure

The first authorized Gate A2-I execution terminated with:

```text
A2_INTAKE_SCHEMA_MISMATCH: missing accession column
```

The runner read the protected membership header before rejecting
the schema. Confirmatory metadata access has therefore begun.

- `confirmatory_metadata_accessed: true`
- `confirmatory_outcomes_accessed: false`
- intake archive produced: no
- confirmatory sequences accessed: no
- family geometry computed: no
- Gate A2-S executed: no
- Gate A2-C executed: no
- Gate C executed: no

## Integrity classification

This is a repairable implementation failure. The frozen header-alias
contract did not recognize the protected membership schema. It is
not a scientific gate result.

A2-I is re-disabled before further protected inspection. The only
permitted diagnostic is a first-line header read of the two already
contacted membership TSV files. No data row, sequence, score,
prediction, grouping, geometry, or outcome may be inspected.

Any schema repair must be committed while A2-I remains disabled.
A2-I requires a separate authorization commit before rerunning.
