# Experiment 04 — Arm B Phase-P Orchestration and Output Contract

Status: **DRAFT — prospective, pre-biological-execution**

This document specifies the experiment-level orchestration, persistence,
checkpointing, and descriptive aggregation required to execute the already
frozen Arm-B Phase-P per-perturbation mechanics.

It does **not** modify the scientific mechanics already frozen in
`run_phase_p_biological_probe.py`.

No biological Phase-P execution is authorized by this document alone.

---

## 1. Purpose

The frozen biological runner already encodes the per-perturbation mechanics:

### Main biological path

`21 -> 22 -> 23 -> 24 -> 25 -> 26 -> 27`

### Permutation-null path

`21 -> 28 -> 22 -> 23 -> 24 -> 25 -> 26 -> 27`

followed by exact stream-21 + stream-28 replay and exact stream-26
membership replay validation.

The remaining implementation task is experiment-level orchestration and
lossless persistence of those frozen mechanics.

This contract must not alter:

- seed derivation;
- target-N selection;
- Stage-A splitting;
- shared five-fold CV;
- one-SE C selection;
- L1 + liblinear probe construction;
- Stage-B refit;
- stability subsampling;
- stability refit;
- support definition;
- permutation-null ordering;
- null replay;
- representation matrices;
- biological labels;
- baseline representation;
- frozen layer set;
- frozen target-N values;
- frozen C grid;
- any previously frozen scientific threshold or interpretation boundary.

The exact inherited C grid is:

`1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0`

No intermediate C value, alternate logarithmic grid, or post-hoc extension is
permitted.

---

## 2. Execution remains closed during implementation

Until a later explicit execution authorization:

`ENABLE_PHASE_P_BIOLOGICAL_PROBING = False`

must remain literal `False`.

The existing terminal `PhasePContractError` inside
`run_enabled_phase_p()` must also remain in force while orchestration is
implemented and audited.

Implementation and static audit must occur without:

- loading a Phase-E matrix;
- loading biological probing labels;
- instantiating a protected `SeedSequence`;
- instantiating a protected RNG;
- consuming any identifier in `1000001..1000100`;
- consuming any identifier in `1100001..1100100`;
- fitting a biological or null probe;
- computing biological/null AUROC;
- computing biological/null support or stability statistics.

---

## 3. Frozen representations

The main biological sweep must report all frozen representations.

Raw ESM layers:

1. layer 1
2. layer 9
3. layer 18
4. layer 24
5. layer 30
6. layer 33

and the frozen 21-dimensional baseline.

No scaling, normalization, PCA, dimensionality reduction, feature selection,
or representation-dependent preprocessing may be introduced.

Representation identity must not enter the seed entropy.

Therefore target memberships, Stage-A splits, folds, and other frozen
randomization identities remain paired across representations.

---

## 4. Main biological perturbation census

Authorized biological perturbation identifiers are exactly:

`1000001..1000100`

inclusive.

Frozen target-N values are exactly:

`100, 120, 139`

per class.

For every biological perturbation identifier and target-N, the same frozen
perturbation identity must be evaluated across every frozen representation.

Expected main design:

- 100 perturbation identifiers;
- 3 target-N values;
- 7 representations.

Therefore the expected representation-level main result census is:

`100 * 3 * 7 = 2100`

rows.

The orchestration layer must not silently omit a failed row or replace it
with a rerun using another seed.

---

## 5. Descriptive permutation-null census

The permutation null is frozen to:

- raw ESM layer 18 only;
- target-N = 139 only;
- perturbation identifiers `1100001..1100100`;
- exactly 100 null perturbations;
- label-position permutation only;
- exact frozen downstream mechanics;
- exact frozen replay checks.

Expected null result census:

`100`

rows.

The null is descriptive/exploratory.

It creates no new gate and may not be extended post hoc to another layer,
target-N, representation, baseline, null construction, seed namespace, or
threshold.

---

## 6. Representation ordering

The canonical representation order for persistence must be:

1. `esm_layer_1`
2. `esm_layer_9`
3. `esm_layer_18`
4. `esm_layer_24`
5. `esm_layer_30`
6. `esm_layer_33`
7. `baseline_21d`

The ordering is a persistence convention only.

It must not affect seed derivation or scientific mechanics.

---

## 7. Atomic unit of main persistence

The atomic main result row is one:

`(biological_perturbation_id, target_n, representation)`

combination.

Each completed row must preserve sufficient information to reconstruct the
frozen per-perturbation outcome without refitting.

At minimum each main row must contain:

- perturbation identifier;
- target-N;
- representation identifier;
- selected C;
- best C;
- best CV mean AUROC;
- best CV standard error;
- one-SE floor;
- all nine CV mean AUROCs;
- all nine CV standard errors;
- Stage-A evaluation AUROC;
- Stage-B support size `K_t_full`;
- stability-refit support size `K_t_stab`;
- exact stability-refit unsigned support;
- exact stability-refit signed support represented as `(coordinate, sign)`;
- stability membership SHA-256.

The exact inherited support convention is coefficient non-zero by exact
floating-point comparison:

`beta != 0.0`

No tolerance, coefficient-magnitude cutoff, top-k rule, or approximate-zero
rule may replace that convention.

`I_stat` and `G_stat` are **not** per-perturbation row fields. They are
cell-level aggregates across the complete 100-perturbation set and are
computed only from the persisted stability-refit supports under the frozen
definitions in §15 below.

Where an inherited statistic has a more exact frozen definition elsewhere,
that definition controls.

This document must not redefine a previously frozen statistic.

---

## 8. Paired baseline comparison

The baseline is evaluated under the same biological perturbation identity,
target-N membership, Stage-A split identity, CV identity, and stability
identity as each raw-ESM representation.

Any ESM-minus-baseline quantity must be derived only after both paired rows
have been successfully persisted.

For each:

`(biological_perturbation_id, target_n, raw ESM layer)`

the paired Stage-A quantity is:

`delta_stage_a_auroc = raw_esm_stage_a_auroc - baseline_stage_a_auroc`

No unpaired replacement, nearest available baseline row, or cross-seed
comparison is permitted.

---

## 9. Atomic unit of null persistence

The atomic null result row is one:

`permutation_null_perturbation_id`

at frozen layer 18 and target-N 139.

At minimum each null row must preserve:

- null perturbation identifier;
- representation identifier = `esm_layer_18`;
- target-N = 139;
- selected C;
- best C;
- best CV mean AUROC;
- best CV standard error;
- one-SE floor;
- all nine CV mean AUROCs;
- all nine CV standard errors;
- Stage-A evaluation AUROC;
- Stage-B support size `K_t_full`;
- stability-refit support size `K_t_stab`;
- exact stability-refit unsigned support;
- exact stability-refit signed support represented as `(coordinate, sign)`;
- original stability membership SHA-256;
- replay stability membership SHA-256;
- exact replay success indicator.

As in the main sweep, null `I_stat` and `G_stat` are not per-perturbation
fields. If reported, they are derived only after all 100 frozen null
perturbations are complete, using the same inherited support and Jaccard
definitions.

The exact row-level permuted-label equality check remains mandatory inside
the frozen mechanics and may not be replaced by a weaker aggregate check.

---

## 10. Raw fitted objects are not result artifacts

Persisted result files must not serialize sklearn model objects.

Persisted experiment results should contain frozen scalar/vector diagnostics
and hashes needed for interpretation/audit, not executable estimator state.

Coefficient vectors may be used in-memory to compute already-frozen support
statistics.

No new coefficient-derived statistic may be introduced during execution.

---

## 11. Output files

The biological execution must use a new output directory that is absent
before first execution.

The implementation must use exclusive creation semantics for the output
directory or an equivalent collision STOP.

The prospective output set is:

### `main_per_perturbation.csv`

Exactly 2100 data rows after a complete main sweep.

### `permutation_null_per_perturbation.csv`

Exactly 100 data rows after a complete null sweep.

### `execution_manifest.json`

Machine-readable execution provenance including at minimum:

- execution-start frozen HEAD;
- runner SHA-256;
- relevant frozen contract/document SHA-256 values;
- Phase-E matrix SHA-256 values;
- authoritative row-manifest SHA-256;
- biological-label source SHA-256;
- baseline source SHA-256;
- exact representation order;
- exact main perturbation range;
- exact null perturbation range;
- exact target-N values;
- exact C grid;
- execution state.

### `RESULT.md`

Written only after the frozen execution and result audit have established
the factual observed outcome.

`RESULT.md` must distinguish factual observations from scientific
interpretation.

---

## 12. Checkpointing and crash recovery

Checkpointing exists only to preserve completed frozen work.

It must never change the frozen perturbation, representation, target-N,
seed, fit, or statistic.

After every completed atomic result row:

1. write the complete row;
2. flush the file;
3. force buffered file content to stable storage where supported.

A resumed execution may skip an atomic row only when the persisted row
uniquely matches the exact frozen key expected at that position.

Resume must STOP on:

- duplicate keys;
- malformed rows;
- unexpected keys;
- representation-order disagreement;
- target-N disagreement;
- perturbation-ID disagreement;
- provenance disagreement;
- output schema disagreement.

Resume must not:

- regenerate a completed row;
- selectively rerun an unfavorable row;
- change a seed;
- change C;
- change solver mechanics;
- drop a failure;
- substitute another representation;
- repair a scientific result.

Crash recovery is computational recovery, not experimental adaptation.

---

## 13. Failure semantics

### Immediate integrity STOP

Execution must stop immediately on evidence that the frozen experiment is
not being run, including:

- provenance/hash mismatch;
- matrix shape/dtype/finiteness failure;
- biological-label integrity failure;
- baseline integrity failure;
- wrong representation set/order;
- wrong perturbation range;
- wrong target-N set;
- wrong C grid;
- wrong output schema;
- output collision inconsistent with valid resume;
- replay failure;
- impossible or duplicated result key.

### Fit/computation failure

A frozen fitting failure, convergence failure, nonfinite fitted parameter,
invalid AUROC condition, or other already-defined scientific-mechanics
failure must be preserved as an observed failure.

It must not trigger an automatic solver/scaling/C/seed/representation repair.

No failed perturbation may be silently omitted.

Any later remedy would require a new prospective amendment after the
original result has been archived.

---

## 14. Main/null sequencing

The main biological sweep is the primary Phase-P experiment.

The permutation null is descriptive and must not alter the main sweep.

Canonical execution order:

1. validate all frozen provenance and input integrity;
2. establish output directory / execution manifest;
3. execute and persist the complete main biological sweep;
4. verify the complete 2100-row main census;
5. execute and persist the frozen 100-row permutation-null sweep;
6. verify the complete 100-row null census;
7. close files;
8. perform a separate read-only result audit;
9. archive factual result;
10. only then interpret.

No main result may be used to alter the null mechanics.

No null result may be used to alter the main mechanics.

---

## 15. Aggregation boundary

Per-perturbation rows are the authoritative primary result records.

Any summary table must be deterministically derived from those records.

For each complete 100-perturbation `(target_n, representation)` cell, define
the frozen stability-refit unsigned support for perturbation `t` as:

`A_t = {j : beta_t,j != 0.0}`

and define the corresponding signed support as:

`B_t = {(j, sign(beta_t,j)) : beta_t,j != 0.0}`

For two perturbations `t` and `u`, the inherited unsigned pairwise Jaccard is:

`J_I(t,u) = |A_t intersection A_u| / |A_t union A_u|`

when the union is non-empty.

The inherited empty-set convention is:

`Jaccard(empty, empty) = 0`

The inherited signed pairwise Jaccard is:

`J_G(t,u) = |B_t intersection B_u| / |B_t union B_u|`

when the union is non-empty, with the same empty-set convention.

A coordinate with opposite fitted signs in two perturbations contributes to
the signed union but not the signed intersection.

Across exactly 100 perturbations there are:

`choose(100, 2) = 4,950`

unordered perturbation pairs.

The inherited aggregate definitions are:

`I_stat = median of J_I(t,u) over all 4,950 unordered pairs`

and:

`G_stat = median of J_G(t,u) over all 4,950 unordered pairs`

No alternative pairwise metric, empty-set convention, coefficient-zero
threshold, or aggregation statistic is authorized.

Because the stronger S7-v2 signed-instability calibration criterion failed,
no calibration-derived `gamma_I`, `gamma_G`, `R >= 71`, `M >= 8`, or other
calibration acceptance threshold becomes a biological Phase-P gate.

`I_stat` and `G_stat`, if reported on biological or permutation-null data,
are therefore descriptive/calibration-limited quantities only.

At minimum the eventual descriptive main summary may report, for each
`(target_n, representation)`:

- number of completed perturbations;
- Stage-A AUROC distribution summaries;
- selected-C distribution;
- `K_t_full` distribution summaries;
- `K_t_stab` distribution summaries;
- descriptive `I_stat`;
- descriptive `G_stat`.

For raw ESM representations it may additionally report paired
ESM-minus-baseline Stage-A AUROC summaries.

The permutation-null summary may report the corresponding frozen layer-18,
N=139 descriptive distributions and descriptive `I_stat` / `G_stat`.

No new significance threshold, pass threshold, biological gate, null gate,
multiple-comparison rule, or post-hoc layer-selection rule may be introduced
by aggregation.

All six raw ESM layers must be reported.

---

## 16. Interpretation boundary

Phase-P Arm B remains:

**exploratory / descriptive / calibration-limited**

because the stronger S7-v2 signed-instability calibration criterion failed.

A biological result may support language such as:

- information is linearly accessible in the raw representation;
- accessibility varies with depth;
- the observed pattern is consistent with a representation-basis gap;
- the observed pattern is consistent with SAE-basis misalignment or
  distributed accessibility.

It does not by itself establish:

- a causal toxin mechanism;
- unique toxin specificity;
- mechanistic decomposition;
- cross-family generalization;
- that SAE failure has one proven causal explanation.

The permutation null is descriptive only and creates no confirmatory gate.

---

## 17. No automatic execution after implementation

Freezing and auditing the orchestration implementation does not itself
authorize biological execution.

A separate explicit biological-execution authorization must verify at least:

- exact frozen repository HEAD;
- clean worktree/index;
- exact runner SHA;
- exact orchestration/output-contract SHA;
- exact input hashes;
- output absence/collision state;
- main namespace still unconsumed;
- null namespace still unconsumed;
- hard-disable still intact immediately before authorized enablement.

Only after that separate authorization may biological execution be opened.

---

## 18. Current state at this draft

At drafting time:

- numerical conditioning: COMPLETE / PASS / ARCHIVED / CLOSED;
- biological per-perturbation mechanics: FROZEN;
- permutation-null per-perturbation mechanics: FROZEN;
- main biological seed namespace: AUTHORIZED / UNCONSUMED;
- permutation-null seed namespace: AUTHORIZED / UNCONSUMED;
- biological execution: CLOSED;
- outer orchestration/persistence: NOT YET IMPLEMENTED;
- experiment-level aggregation: NOT YET IMPLEMENTED.

This document is prospective and must be audited before freeze.
