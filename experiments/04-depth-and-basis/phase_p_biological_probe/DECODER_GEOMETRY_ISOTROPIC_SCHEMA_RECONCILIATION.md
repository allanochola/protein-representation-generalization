# Decoder Geometry Isotropic Schema Reconciliation

Status: **FROZEN PRE-REPAIR / FAILED PRE-SUMMARY EXECUTION**

## Context

The authorized final decoder-geometry aggregation was executed once from
repository commit:

`f51564878d418762ca21e38ec4b0819297f28381`

using final aggregation driver SHA-256:

`f2a60e932ce5647000899789a36efd14bdb8fe3ad2fbfe532af0ba016c40aeeb`

under final aggregation specification SHA-256:

`54e4110acd3d38148e553d1cdb766fd8130bbb91355edd698678e4c159e69d55`

The execution terminated before final result construction with:

`RuntimeError: Geometry payload schema mismatch.`

No final aggregation output was written.

No bootstrap result was written.

No population summary or final comparison artifact was produced.

The confirmatory universe remained untouched.

## Failure localization

Read-only diagnostics established that the failure is a serialization-interface
mismatch in the historical isotropic records.

All 1,000 isotropic records use one uniform flattened serialization.

Each record contains the following relevant top-level fields:

- `status`
- `omp_status`
- `rank_deficient`
- `rank_deficiency_step`
- `exact_reconstruction_step`
- `r_by_k`
- `rank_by_k`
- `condition_by_k`
- `raw_weight_status`
- `topk_mass`
- `n_eff`
- `vector_index`
- `child_stream_identifier`
- `engine_sha256`
- `spec_sha256`

The final aggregation loader instead expects each isotropic record to expose
top-level `omp` and `raw_weight` dictionaries.

Neither field exists in the historical isotropic serialization.

## Population-wide audit

The reconciliation audit established:

- isotropic records inspected structurally: 1,000 / 1,000
- isotropic indices: exactly 0 through 999
- unique flattened schema signatures: 1
- records with top-level `omp`: 0
- records with top-level `raw_weight`: 0
- records with nested `geometry`: 0
- records with every required flattened source field: 1,000
- records with complete 10-point frozen K grid: 1,000
- overall status `complete`: 1,000
- OMP status `complete`: 1,000
- raw-weight status `complete`: 1,000
- rank deficient: 0
- field-identity mismatches under the candidate mapping: 0

All 1,000 records report geometry engine SHA-256:

`8289d96a11ee3f5506edf298bf0290f58414454737156c98737f4522642915ab`

All 1,000 records report geometry specification SHA-256:

`205d13b20ef5bf9325794274b531f46c9ffa7fa7cc77a7e8bdd0a8be05edce69`

## Frozen lossless compatibility mapping

The only permitted compatibility mapping is deterministic regrouping of
already-persisted fields.

### OMP object

- `omp.status <- omp_status`
- `omp.rank_deficient <- rank_deficient`
- `omp.rank_deficiency_step <- rank_deficiency_step`
- `omp.exact_reconstruction_step <- exact_reconstruction_step`
- `omp.r_by_k <- r_by_k`
- `omp.rank_by_k <- rank_by_k`
- `omp.condition_by_k <- condition_by_k`

### Raw-weight object

- `raw_weight.status <- raw_weight_status`
- `raw_weight.topk_mass <- topk_mass`
- `raw_weight.n_eff <- n_eff`

The mapping performs no numerical transformation.

It performs no rounding.

It performs no recomputation.

It consumes no seeds.

It does not rerun OMP.

It does not regenerate isotropic vectors.

It does not alter historical private isotropic records.

## Repair classification

This is classified as a **serialization-interface compatibility defect**.

It is not evidence of:

- corrupted isotropic geometry;
- missing scientific quantities;
- failed OMP reconstruction;
- failed raw-weight analysis;
- seed inconsistency;
- population incompleteness;
- a scientific-result discrepancy.

The scientific quantities required by the frozen final aggregation
(`R(k)`, top-k mass, and `N_eff`) are already present in every historical
isotropic record.

## Permitted repair boundary

A repair may modify only the isotropic record-loading compatibility path in
the final aggregation driver.

The repair may:

1. recognize the exact historical flattened isotropic schema;
2. construct the expected in-memory `omp` and `raw_weight` dictionaries
   using the frozen mapping above;
3. pass that reconstructed in-memory object through the existing final
   aggregation validation path.

The repair must not:

- modify biological population records;
- modify canonical permutation-null records;
- modify C-matched records;
- modify historical isotropic archive bytes;
- alter any persisted scientific value;
- recalculate geometry;
- alter K-grid semantics;
- alter bootstrap seeds;
- alter bootstrap stream assignments;
- alter bootstrap replicate count;
- alter population denominators;
- alter headline metrics;
- alter comparison authority;
- introduce p-values;
- introduce PASS/FAIL thresholds;
- access confirmatory data.

## Execution policy

The failed aggregation driver is reclosed before compatibility repair.

The compatibility repair must be:

1. implemented while hard-disabled;
2. audited against all 1,000 historical isotropic records;
3. shown to preserve every mapped field exactly;
4. committed before authorization;
5. authorized separately by the minimum execution-gate change.

Only after those conditions are satisfied may the final aggregation be
executed again.

That later execution is classified as a repair-controlled rerun following
a pre-summary serialization failure, not as an adaptive scientific rerun.
