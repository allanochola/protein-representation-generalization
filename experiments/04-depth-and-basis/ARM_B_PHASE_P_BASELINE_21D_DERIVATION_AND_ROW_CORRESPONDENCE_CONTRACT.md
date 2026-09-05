# Arm B Phase-P baseline_21d derivation and row-correspondence contract

## Status

Prospective pre-execution contract.

This document freezes the construction, row identity, provenance, and
pre-orchestration validation requirements for the 21-dimensional sequence
baseline used by Experiment 04 Arm B Phase P.

At the time this contract is frozen:

- the biological Phase-P execution gate remains closed;
- the six raw ESM Phase-E matrices already exist and are frozen;
- no `baseline_21d` matrix has yet been generated;
- no biological predictive metric has been computed;
- no Phase-P protected seed has been consumed.

The baseline artifact must be derived only after this contract is committed.

## Authoritative row-order source

The sole authoritative row-order source is:

`experiments/03-toxin-representation/stage1_model_contact/discovery_extraction/discovery_matrix_rows.tsv`

SHA-256:

`ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e`

Required schema:

1. `matrix_row`
2. `class_name`
3. `identifier`
4. `retrieved_length`
5. `sequence_sha256`

Required row count: exactly 278.

`matrix_row` must equal exactly `0, 1, ..., 277` in file order.

The Phase-E local copy:

`experiments/04-depth-and-basis/phase_e_extraction/output/phase_e_matrix_rows.tsv`

must remain byte-identical to the authoritative matrix-row manifest and
therefore has the same SHA-256:

`ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e`

The Exp03 manifest remains authoritative even though the Phase-E copy is
byte-identical.

## Biological label authority

The biological label vector `y` must be derived directly and only from
`class_name` in the authoritative matrix-row manifest, in manifest row order.

Frozen mapping:

- `negative` -> 0
- `positive` -> 1

Required class census:

- 139 negative
- 139 positive
- 278 total

No realized-partition TSV, FASTA header, extraction file, or independent join
may define `y`.

If a realized-partition source is inspected as a cross-check, disagreement
with the authoritative manifest is an immediate STOP.

## Independent row-correspondence source

Row identity must not be validated from labels alone.

The frozen FASTA source is:

`experiments/03-toxin-representation/stage1_model_blind/precontact_gate/discovery_sequences.fasta`

SHA-256:

`ef17a1231bafc86255bf8ba57aaa64fe7f81c39677fb8d0553fa2d94ca2fb358`

The frozen precontact sequence manifest is:

`experiments/03-toxin-representation/stage1_model_blind/precontact_gate/discovery_sequence_manifest.tsv`

SHA-256:

`7ac8d253d06ab86b67f2f3d42d7b5ad0c770360a2d4959dc8d325bed00b9ce09`

The FASTA contains exactly 278 records.

Every FASTA header must parse exactly as:

`class_name|identifier`

For every row `i` from 0 through 277, all of the following must agree before
orchestration:

- FASTA record `i` class;
- FASTA record `i` identifier;
- authoritative manifest row `i` identifier;
- precontact sequence-manifest row `i` identifier;
- FASTA sequence length;
- authoritative manifest `retrieved_length`;
- precontact manifest `retrieved_length`;
- SHA-256 of the exact FASTA sequence;
- authoritative manifest `sequence_sha256`;
- precontact manifest `sequence_sha256`.

Any discrepancy is an immediate STOP before Phase-P orchestration.

`sequence_sha256`, not `class_name`, is the independent anti-permutation
identity check.

## baseline_21d feature definition

The baseline has shape exactly:

`(278, 21)`

Frozen column order:

- column 0: full sequence length
- columns 1-20: canonical amino-acid fractions in this exact order:

`ACDEFGHIKLMNPQRSTVWY`

Explicitly:

1. `fraction_A`
2. `fraction_C`
3. `fraction_D`
4. `fraction_E`
5. `fraction_F`
6. `fraction_G`
7. `fraction_H`
8. `fraction_I`
9. `fraction_K`
10. `fraction_L`
11. `fraction_M`
12. `fraction_N`
13. `fraction_P`
14. `fraction_Q`
15. `fraction_R`
16. `fraction_S`
17. `fraction_T`
18. `fraction_V`
19. `fraction_W`
20. `fraction_Y`

For a sequence `s` of full length `L`:

`fraction_AA = count(AA in s) / L`

The denominator is always the full sequence length.

The 20 canonical fractions must not be renormalized to sum to one.

Noncanonical residues remain part of the full-length denominator and do not
receive additional baseline columns.

No scaling, standardization, centering, normalization, PCA, imputation, or
other transformation is permitted during baseline construction.

## Frozen descriptive noncanonical behavior

`Q6RX08` is required to occur exactly once at matrix row 212.

Frozen facts:

- full sequence length: 842
- noncanonical residues: exactly one `X`
- sum of the 20 canonical fractions:
  `0.998812351543943`
- rounded to four decimal places:
  `0.9988`

The generated baseline must reproduce this behavior.

A construction that renormalizes canonical residues and therefore makes the
20 canonical fractions sum to 1.0 is invalid and must STOP.

## Baseline row derivation

Baseline row `i` must be generated only from FASTA record `i`, after the full
row-correspondence checks above pass.

For each row:

`baseline_21d[i, 0] = len(sequence_i)`

and, for each canonical amino acid in frozen order:

`baseline_21d[i, j] = sequence_i.count(AA_j) / len(sequence_i)`

Row sorting, accession joins, class grouping, positive-first reconstruction,
negative-first reconstruction, or any other reorder is prohibited.

## Derived baseline artifact

The generated baseline must be persisted as a dedicated derived input before
biological Phase-P execution.

Prospective path:

`experiments/04-depth-and-basis/phase_p_biological_probe/input/baseline_21d.npy`

The generation step must record and freeze:

- output path;
- exact SHA-256;
- shape;
- dtype;
- finite-value status;
- authoritative manifest SHA;
- FASTA SHA;
- precontact sequence-manifest SHA;
- feature order;
- row count;
- Q6RX08 descriptive check.

The baseline artifact must not be recomputed opportunistically inside the
biological execution path.

## Six frozen raw ESM inputs

The raw Phase-E matrices are fixed as:

- layer 1:
  `experiments/04-depth-and-basis/phase_e_extraction/output/raw_esm_layer_1.npy`
  SHA-256 `204b2d0901b805ce9221b8318883e29dfe2c9a2c1aa18f37b6fc831ef3b08c15`
- layer 9:
  `experiments/04-depth-and-basis/phase_e_extraction/output/raw_esm_layer_9.npy`
  SHA-256 `7eb08b17232cbf34c23ac8e246dbeb07bec2197904d4bb24e6717a93c1d03683`
- layer 18:
  `experiments/04-depth-and-basis/phase_e_extraction/output/raw_esm_layer_18.npy`
  SHA-256 `c4e408db0963a0cbb90996ebb59b5e83cd86a9120de1a968cd4b7d80f5fa440e`
- layer 24:
  `experiments/04-depth-and-basis/phase_e_extraction/output/raw_esm_layer_24.npy`
  SHA-256 `78c34e2c4419fb1ba850e383ab56b06b864412e65ba5046379983ff9e1190336`
- layer 30:
  `experiments/04-depth-and-basis/phase_e_extraction/output/raw_esm_layer_30.npy`
  SHA-256 `ebc98537034ea7946b4c634d4a0a3fff18f503428b3f182c79360a604159c98b`
- layer 33:
  `experiments/04-depth-and-basis/phase_e_extraction/output/raw_esm_layer_33.npy`
  SHA-256 `64e626858aa8e2a0a323af5121520f969f942679f8cbec4d27c7116bc8501f0d`

Each must remain exactly shape `(278, 1280)`, dtype `float32`, and finite.

Phase-E provenance:

`experiments/04-depth-and-basis/phase_e_extraction/output/PHASE_E_PROVENANCE.json`

SHA-256:

`655ea47a8300f1056656378238402cf12dc5a024b96c18117397bb804b02e6dd`

## Pre-orchestration attachment barrier

Before `run_phase_p_orchestration_from_loaded_inputs(...)` may be called,
the attachment layer must validate all of the following:

1. authoritative matrix-manifest SHA exact;
2. matrix manifest contains exactly 278 rows;
3. `matrix_row` is exactly 0 through 277;
4. `y` is derived only from manifest `class_name`;
5. `y` contains exactly 139 zeros and 139 ones;
6. frozen FASTA SHA exact;
7. frozen precontact sequence-manifest SHA exact;
8. all 278 FASTA headers parse exactly as `class_name|identifier`;
9. all 278 identifiers agree row-by-row;
10. all 278 retrieved lengths agree row-by-row;
11. all 278 sequence SHA-256 values agree row-by-row;
12. all six ESM matrix SHAs exact;
13. all six ESM matrices have shape `(278, 1280)`;
14. all six ESM matrices are `float32`;
15. all six ESM matrices are finite;
16. frozen `baseline_21d` SHA exact;
17. `baseline_21d` has shape `(278, 21)`;
18. `baseline_21d` is finite;
19. baseline feature order is exact;
20. Q6RX08 reproduces the frozen `0.9988` descriptive behavior;
21. baseline row identity remains tied to FASTA row identity;
22. label row identity remains tied to authoritative manifest row identity;
23. complete input provenance is assembled before orchestration.

Failure of any check is an immediate STOP.

No partial validation may be deferred until after orchestration begins.

## Execution separation

Baseline derivation, baseline validation, input attachment, and biological
orchestration are separate layers.

Freezing this contract does not authorize:

- baseline generation;
- baseline attachment;
- biological label materialization for execution;
- Phase-P execution;
- predictive metric computation;
- model fitting;
- protected-seed consumption.

Biological Phase P remains closed until a later explicit execution
authorization boundary.
