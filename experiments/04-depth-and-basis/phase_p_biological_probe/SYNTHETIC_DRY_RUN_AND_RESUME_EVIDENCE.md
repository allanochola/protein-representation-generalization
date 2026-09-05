# Experiment 04 — Phase-P Synthetic Dry-Run and Resume Evidence

Date archived: 2026-09-05

## Frozen production state before archival

- Branch: `exp04-depth-and-basis`
- Scientific parent HEAD: `78b7fc4528b4ef4b9dc772bd3679c4140f181ea7`
- Production runner: `experiments/04-depth-and-basis/phase_p_biological_probe/run_phase_p_biological_probe.py`
- Production runner SHA-256: `93940e890541ea437aa51c9bc3085e704d6a1ed04b3318937b14c0a7d988f3c2`
- Production Phase-P output directory: absent
- Biological probing: CLOSED
- Protected main perturbation IDs `1000001–1000100`: UNCONSUMED
- Protected permutation-null IDs `1100001–1100100`: UNCONSUMED
- Baseline generator: not executed during these tests

## Synthetic dry-run scope

The synthetic dry run exercised the actual frozen Phase-P downstream mechanics while replacing the biological attachment boundary with deterministic synthetic inputs and using a separate synthetic seed namespace.

The final passing scratch runner SHA-256 was:

`1ed372d889c7bd597320069c5b85a0c0586ff3f5207dfe11668d04e7a95832a0`

The dry run retained the frozen scientific R2 mechanics:

- 5-fold shuffled stratified cross-validation
- frozen 9-value C grid
- 45 Stage-A CV fits plus the frozen 46-child Stage-A seed contract
- actual Phase-P wrapper wiring
- actual Phase-P orchestration
- manifest creation and validation
- atomic per-row CSV persistence
- exact census verification
- completed-run no-op re-entry

The synthetic census was intentionally small:

- 2 synthetic main perturbations
- 1 target-N value
- 7 representations
- 14 total main rows
- 1 permutation-null row

## Uninterrupted synthetic run

The uninterrupted restored-mechanics dry run completed successfully.

Artifact hashes:

- `execution_manifest.json`: `4756787ad68145f4e94b77e49709ad05f756f1e4c65a00edb46d5f2cdd6a563f`
- `main_per_perturbation.csv`: `fa577802b52a295d3abb544b16cd4e12981a1ab4d31a77765e720aaea661cc81`
- `permutation_null_per_perturbation.csv`: `4377471e54cdd15efa97dbd8cb6726612f160ff74afa8dcb68c8ef62daec3ecc`

Census:

- main rows: 14 / 14
- null rows: 1 / 1

A completed-state re-entry returned successfully and left all three artifacts byte-identical.

## Forced interruption and resume

The exact same passing scratch source was launched again from a fresh synthetic output directory.

The process was forcibly terminated after exactly 5 durable main rows had been observed.

Partial durable state at interruption:

- manifest SHA-256: `4756787ad68145f4e94b77e49709ad05f756f1e4c65a00edb46d5f2cdd6a563f`
- main rows: 5
- null rows: 0
- partial main CSV SHA-256: `3fde8e8ee64aeb7b2ebe941df0b80894063b1e40dc4291faec050efb4de49abd`
- interrupted process return code: `-15`

The exact same scratch source was then resumed without changing source, manifest, seed namespace, or synthetic inputs.

The resumed computation completed:

- main rows: 14 / 14
- null rows: 1 / 1

Final resumed artifact hashes were:

- `execution_manifest.json`: `4756787ad68145f4e94b77e49709ad05f756f1e4c65a00edb46d5f2cdd6a563f`
- `main_per_perturbation.csv`: `fa577802b52a295d3abb544b16cd4e12981a1ab4d31a77765e720aaea661cc81`
- `permutation_null_per_perturbation.csv`: `4377471e54cdd15efa97dbd8cb6726612f160ff74afa8dcb68c8ef62daec3ecc`

These hashes were byte-for-byte identical to the uninterrupted run.

A further completed-state re-entry was also a byte no-op.

## Interpretation

This synthetic test supports the infrastructure claim that completed Phase-P checkpoint rows survive a mid-main-sweep interruption and that resuming from the durable checkpoint can reconstruct the same final artifacts as an uninterrupted computation.

It does **not** consume or test the protected biological experiment and does not establish any biological result.

The production Phase-P biological execution remained closed throughout these tests.
