# Experiment 04 Decoder-Geometry Main Population Recovery Specification

Status: **FROZEN BEFORE RECOVERY EXECUTION**

This document governs deterministic recovery of the previously completed
biological and canonical-permutation-null decoder-geometry population for the
Experiment 04 post hoc decoder-geometry follow-up.

This is a recovery operation only.

It does not authorize a new scientific analysis, a new model fit, a new beta
recovery, a new decoder geometry method, a new seed namespace, a confirmatory
analysis, or any downstream population comparison.

---

## 1. Why recovery is required

The original biological + canonical-null decoder-geometry population completed
successfully under the frozen population driver.

The public completion provenance records:

- total rows accounted for: `200 / 200`;
- eligible geometry analyses completed: `163 / 163`;
- exact-zero beta rows explicitly retained as geometry-ineligible: `37 / 37`;
- biological rows completed: `100 / 100`;
- canonical-null nonzero rows completed: `63 / 63`;
- canonical-null exact-zero rows retained explicitly: `37 / 37`.

The original private completion manifest had SHA-256:

`a5246082517ca1270a75f48288df9cb03d21d5c6393f3f2daaeb41229a4a0257`

The private per-direction records existed and were byte-verified against that
manifest at the time of original completion.

No population-level geometry summary, biological-vs-null comparison,
biological-vs-isotropic comparison, bootstrap interval, p-value, PASS/FAIL
verdict, or confirmatory analysis had been computed when that provenance was
frozen.

The original frozen driver wrote records only to its supplied local
`output_dir`. Public provenance and source audit found no durable external
archive/upload mechanism for that original output.

The current Kaggle filesystem no longer contains that population.

Therefore deterministic reconstruction is required solely to restore the
already-completed direction-level artifact needed by the frozen downstream
aggregation contract.

---

## 2. Historical execution identities

Original population-driver lifecycle:

- hard-disabled commit:
  `610ae7299b0087a120289467f74ce08bc5694989`
- hard-disabled driver SHA-256:
  `b9d789fe73ddf12138c36544dc4d79760469f6b62c04587da90da009f0b566b5`
- authorization commit:
  `dadb8f0c65bce0b5966ac4c14b34c80874cf1ff7`
- authorized driver SHA-256:
  `e3c172d9abfe304b785506a773fa5abaa8be306e6172122d52f81c35a89f35f8`
- post-execution closure commit:
  `4408eb77a8d56133aed7d5b50c9273a62a277982`
- provenance commit:
  `e9f3d3ba9855e259b9e366f2eb1430c7e9df9835`
- completion-note SHA-256:
  `3a138c6ecd696352d24d1dc322b91b275089831bae2ac047e7d8c016fbad2aa7`

Original population completion-manifest SHA-256:

`a5246082517ca1270a75f48288df9cb03d21d5c6393f3f2daaeb41229a4a0257`

---

## 3. Frozen upstream numerical artifacts

Recovery MUST use exactly:

### 3.1 Pass-2 beta artifact

SHA-256:

`934b69de6765fb96f5dfe43460544cd7d06ad2bc0557029c6f66daeb18fd3580`

Expected contents:

- `biological_ids`: shape `(100,)`
- `biological_beta`: shape `(100, 1280)`
- `null_ids`: shape `(100,)`
- `null_beta`: shape `(100, 1280)`

Expected zero census:

- biological exact-zero beta: `0 / 100`
- canonical null exact-zero beta: `37 / 100`
- canonical null nonzero beta: `63 / 100`

Associated Pass-2 report SHA-256:

`b1905cb7ad9140f9f85f3c7cd621b1ace5dece645e63b0a8c1317ff643de10ed`

Pass-2 closure commit:

`41a62e5869ba4597d41bb873c5fe0d86c3b0a0f6`

No beta fitting or beta regeneration is permitted in recovery.

### 3.2 Decoder-geometry engine

Exact frozen engine SHA-256:

`8289d96a11ee3f5506edf298bf0290f58414454737156c98737f4522642915ab`

Recovery MUST use the exact frozen public engine implementation.

No OMP method, tolerance, k-grid, rank rule, tie rule, decoder normalization,
raw-weight definition, threshold definition, or N_eff definition may change.

### 3.3 SAE checkpoint

Exact checkpoint SHA-256:

`bf0dfb992321cf4d1ce80fced0db0256f5c7a1f9fdd8a7fe4834e786c1f6472a`

The checkpoint must be hash-verified before deserialization.

---

## 4. Population identities

Biological perturbation IDs:

`1000001 ... 1000100`

Canonical-null perturbation IDs:

`1100001 ... 1100100`

Expected structural accounting:

- biological total: `100`
- biological eligible nonzero: `100`
- biological exact-zero: `0`
- canonical-null total: `100`
- canonical-null eligible nonzero: `63`
- canonical-null exact-zero: `37`
- total accounted: `200`
- total eligible geometry directions: `163`
- total explicit zero-beta ineligible rows: `37`

Any mismatch is a hard recovery failure.

---

## 5. Exact-zero semantics

Recovery must preserve the frozen zero semantics.

A beta is geometry-ineligible if and only if the frozen engine's
`normalize_direction(beta)` returns `None`, corresponding to exact L2 norm
zero under the engine's frozen implementation.

Every exact-zero canonical-null row must be persisted explicitly with:

- `eligibility = "ineligible_zero_beta"`
- `analysis_status = "not_run_zero_beta"`
- `geometry = null`

No zero direction may be normalized, imputed, assigned `R(k)=0`, assigned
top-k mass, assigned N_eff, silently dropped, or replaced.

---

## 6. Eligible-direction recovery

For every nonzero beta direction:

1. load the exact persisted beta vector;
2. call the exact frozen decoder-geometry engine;
3. compute geometry exactly once;
4. require top-level geometry status `"complete"`;
5. persist the same outer population-record schema used by the original
   population driver.

Recovery does not authorize any alternative geometry implementation.

No new random-number generator is required or permitted for geometry
reconstruction.

---

## 7. Recovery output schema

The recovered population must contain exactly:

- `100` biological records;
- `100` canonical-null records;
- one completion manifest.

The per-direction outer record schema must remain identical to the original
population driver:

Eligible row:

- population
- perturbation_id
- eligibility = `"eligible_nonzero_beta"`
- coefficient_sha256
- analysis_status = `"complete"`
- geometry = exact frozen engine result

Zero row:

- population
- perturbation_id
- eligibility = `"ineligible_zero_beta"`
- coefficient_sha256
- analysis_status = `"not_run_zero_beta"`
- geometry = `null`

No population summary may be added to per-direction records.

---

## 8. Historical identity test

After recovery, first compute the SHA-256 of the recovered
`completion_manifest.json`.

Primary recovery identity target:

`a5246082517ca1270a75f48288df9cb03d21d5c6393f3f2daaeb41229a4a0257`

### 8.1 Exact match

If the recovered completion manifest SHA equals the historical target, record:

`RECOVERY_IDENTITY = EXACT_MANIFEST_MATCH`

This is the strongest recovery outcome.

### 8.2 Manifest mismatch

If the recovered completion-manifest SHA does not equal the historical target:

1. STOP before downstream aggregation;
2. do not alter the driver or regenerate opportunistically;
3. preserve the recovered candidate privately;
4. perform a recovery-identity diagnostic limited to deterministic
   provenance/serialization/path differences and record hashes;
5. do not inspect scientific geometry summaries during diagnosis.

A manifest mismatch MUST NOT be silently accepted.

---

## 9. Record-level identity and invariants

For every recovered record:

- verify exact expected perturbation ID;
- verify unique population/ID membership;
- verify coefficient SHA-256 derived from exact beta bytes;
- verify eligible/zero classification;
- verify analysis status;
- verify geometry completeness for eligible rows;
- verify geometry absent for zero rows;
- verify finite numerical payloads;
- verify frozen k-grid structure;
- verify no unexpected rank/status schema;
- hash every record;
- include exact record SHA in the recovered completion manifest.

Recovery must produce exactly `200` record identities.

---

## 10. Scientific firewall during recovery

Until recovery identity is accepted and the population is privately persisted:

Do NOT compute or inspect:

- biological median R(32);
- canonical-null median R(32);
- biological-minus-null R(32);
- any top-k mass population summary;
- any N_eff population summary;
- any threshold population summary;
- any full-grid population summary;
- any biological-vs-isotropic comparison;
- any biological-vs-C-matched comparison;
- any bootstrap interval;
- any p-value;
- any PASS/FAIL verdict;
- any confirmatory result.

Individual geometry payloads may exist as deterministic recovery outputs, but
must not be opened for population-level scientific interpretation during the
recovery phase.

---

## 11. Durable private persistence requirement

Successful recovery MUST be durably persisted before downstream aggregation.

The recovery output must be stored in a new private Kaggle dataset dedicated
to the recovered biological + canonical-null geometry population.

The private storage bundle must include:

- `completion_manifest.json`;
- all `200` per-direction records, directly or in an archive whose byte
  contents are independently verifiable;
- `private_storage_manifest.json`.

The storage manifest must record:

- recovered completion-manifest SHA;
- record count;
- record archive/file SHA(s);
- governing recovery-spec SHA;
- recovery-driver SHA;
- engine SHA;
- beta artifact SHA;
- SAE checkpoint SHA;
- storage-only provenance.

The recovery output must be re-downloaded or otherwise independently verified
after upload before aggregation is allowed.

---

## 12. Recovery driver requirements

A new recovery driver must be created.

It must:

- be hard-disabled by default;
- bind to this recovery specification by exact SHA-256;
- bind to all frozen upstream artifact SHA-256 values;
- reuse original population-record semantics;
- refuse pre-existing output;
- refuse confirmatory paths;
- perform no population summary or comparison;
- write only deterministic recovered direction records and completion
  provenance;
- be audited and frozen before authorization;
- be authorized by exactly one gate change;
- be returned to the exact hard-disabled bytes after recovery completion.

The historical population driver remains preserved unchanged.

---

## 13. Relationship to final aggregation

The already-frozen final aggregation authority remains unchanged:

Final aggregation specification SHA-256:

`54e4110acd3d38148e553d1cdb766fd8130bbb91355edd698678e4c159e69d55`

Currently authorized final aggregation-driver SHA-256:

`f2a60e932ce5647000899789a36efd14bdb8fe3ad2fbfe532af0ba016c40aeeb`

The final aggregation driver MUST NOT be executed until:

1. recovery succeeds;
2. recovery identity is accepted;
3. the recovered population is durably persisted;
4. the recovery driver is re-closed;
5. recovery completion provenance is frozen;
6. a final input preflight verifies all four populations.

---

## 14. Interpretation status

Recovery success establishes only restoration of the previously completed
direction-level biological + canonical-null geometry artifact.

It does not establish:

- compact SAE alignment;
- biological-vs-null separation;
- biological-vs-isotropic separation;
- biological-vs-C-matched separation;
- mechanistic decomposition;
- toxin-specific causal structure;
- cross-family generalization;
- confirmatory evidence.

Those remain questions for the separately frozen final aggregation procedure.

---

## 15. Required next action

After this specification is frozen:

1. build a NEW hard-disabled recovery driver;
2. deep-audit it against this specification;
3. freeze and push it;
4. authorize by one gate change;
5. recover the 200 direction-level records once;
6. test exact historical identity;
7. durably persist the recovered population privately;
8. verify the private archive independently;
9. re-close the recovery driver;
10. freeze recovery completion provenance;
11. only then return to final aggregation.
