# Experiment 04 Pass-1 Artifact Restoration Specification

Status: **FROZEN BEFORE PASS-1 RESTORATION REPLAY**

This document governs deterministic restoration of the lost accepted
Pass-1 verification report required by the decoder-geometry beta-recovery
pipeline.

This is restoration of a previously completed and accepted replay artifact.
It is not a new scientific analysis.

---

## 1. Historical state

The original Pass-1 replay completed successfully and produced an accepted
verification report with historical SHA-256:

`f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

That exact report is no longer available in current local storage or in the
inventoried durable private Kaggle datasets.

The historical Pass-1 driver remains recoverable exactly:

- hard-disabled SHA-256:
  `b73af5a62c99171eb99f37244ecc38df19fe19def3377b542bcbe2ec6753ef91`
- historical authorized SHA-256:
  `4279b8b064ccc53471a4d633707a60d4d0e453599e297b7d9972ba7fed3e30d1`

The historical report was accepted at:

- `200 / 200` rows verified;
- `0` mismatches;
- exact Stage-B coefficient hashes persisted for all `200` rows.

---

## 2. Frozen Pass-1 source identities

Restoration MUST use exactly:

- Phase-P runner SHA-256:
  `e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec`
- decoder-geometry recovery specification SHA-256:
  `205d13b20ef5bf9325794274b531f46c9ffa7fa7cc77a7e8bdd0a8be05edce69`
- decoder-geometry engine SHA-256:
  `8289d96a11ee3f5506edf298bf0290f58414454737156c98737f4522642915ab`

No source substitution or numerical-method change is permitted.

---

## 3. Frozen private historical inputs

Restoration MUST use the exact historical Phase-P triplet:

- `execution_manifest.json`
  SHA-256 `f5049a77f210b53e58ded918d8cbce9444444fd141df86f61a94dc8aa460e7ba`
- `main_per_perturbation.csv`
  SHA-256 `5ec2ce9810d344613b91117fe72e76d54306ba8ae2402a3e31ff327bfb93841c`
- `permutation_null_per_perturbation.csv`
  SHA-256 `2657f3f7a04b5ebe50a9e0514cefdf94d22b6d92a8695c8b957602d97348c6ae`

The three files must be verified by SHA-256 before replay.

---

## 4. Why historical report byte identity is not the restoration criterion

The historical Pass-1 report contains a `current_environment` payload.

That payload records, among other fields:

- Python version;
- NumPy version;
- SciPy version;
- scikit-learn version;
- platform;
- machine architecture;
- OMP thread environment;
- OpenBLAS thread environment;
- MKL thread environment;
- NumPy build/configuration output.

The historical Phase-P execution manifest does not contain the corresponding
original execution-environment values.

Therefore the exact historical report bytes cannot be reconstructed from the
persisted scientific inputs alone.

The historical report SHA

`f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

remains a provenance anchor identifying the originally accepted report, but
byte equality to that historical JSON is NOT required for restoration
acceptance.

A restored report MUST NOT be represented as the historical report.

---

## 5. Scientific restoration identity

The restored Pass-1 artifact is scientifically accepted only if ALL of the
following hold under the exact historical authorized Pass-1 program:

1. exact static source identities pass;
2. exact historical Phase-P triplet identities pass;
3. exactly `100` biological rows are replayed;
4. exactly `100` canonical permutation-null rows are replayed;
5. total replay census is exactly `200`;
6. persisted-row invariant verification succeeds for every row;
7. `verified_count == 200`;
8. `expected_count == 200`;
9. `mismatch_count == 0`;
10. every record has `verified == true`;
11. every record has `mismatches == []`;
12. every record has `exception == null`;
13. every replayed Stage-B coefficient SHA-256 equals the coefficient SHA
    produced by the historical accepted Pass-1 replay for the same population
    and perturbation ID, where that identity can be independently recovered
    from accepted downstream provenance.

If any condition fails, restoration fails closed.

No result substitution, tolerance widening, rerun-until-match behavior, row
dropping, or changed numerical contract is permitted.

---

## 6. Environment treatment

The current restoration environment must be recorded exactly as produced by
the frozen historical Pass-1 driver.

Environment differences do not authorize any change to:

- frozen inputs;
- perturbation identities;
- target N;
- selected C;
- solver;
- seed paths;
- replay semantics;
- coefficient hashing;
- persisted-row comparisons.

The restored report's environment block is restoration provenance only.

---

## 7. Output identity

The restored Pass-1 report must be written to a NEW private/local path.

Its new SHA-256 must be recorded separately as:

`RESTORED_PASS1_REPORT_SHA256`

It must never be labeled or substituted as the historical report SHA:

`f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

The restoration provenance must explicitly record both identities.

---

## 8. Relationship to historical Pass-2 contract

The historical Pass-2 driver expects the original Pass-1 report SHA:

`f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

Because restored Pass-1 JSON bytes may legitimately differ solely due to the
unrecoverable historical environment payload, the historical Pass-2 driver
must NOT be silently patched to accept an arbitrary new report.

Before Pass-2 restoration execution, a separate frozen compatibility rule or
restoration driver must:

1. authenticate the restored Pass-1 report by this specification;
2. verify its full scientific identity;
3. record the restored report SHA separately;
4. preserve the historical Pass-2 replay computation unchanged;
5. change only the provenance/report-authentication boundary required to admit
   the scientifically identical restored Pass-1 report.

That compatibility change must be frozen and audited before Pass-2 replay.

---

## 9. Scientific firewall

Pass-1 restoration does NOT authorize:

- decoder geometry;
- geometry aggregation;
- biological-vs-null comparison;
- isotropic comparison;
- C-matched comparison;
- bootstrap;
- p-values;
- scientific verdicts;
- confirmatory access.

The restored coefficient hashes are verification artifacts only.

No coefficient magnitudes, directions, support patterns, geometry values, or
population summaries may be inspected during restoration.

---

## 10. Replay rule

Pass-1 restoration may occur exactly once after a restoration execution
mechanism has been:

1. derived from the exact historical authorized Pass-1 source;
2. hard-disabled;
3. audited against this specification;
4. frozen publicly;
5. authorized by an explicit one-line execution gate.

On restoration failure, stop and diagnose identity/provenance only.

Do not modify the scientific replay contract and rerun opportunistically.

---

## 11. Required sequence after this specification

1. construct a hard-disabled Pass-1 restoration driver from the exact
   historical authorized computation;
2. add only restoration-spec binding and output-provenance safeguards;
3. deep-audit computational equivalence;
4. freeze and push;
5. authorize by one line;
6. replay exactly `200` canonical paths once;
7. verify `200 / 200`, zero mismatches, zero exceptions;
8. freeze restored report identity and provenance;
9. construct the narrow Pass-2 restored-report compatibility boundary;
10. only then restore Pass-2 beta artifact;
11. return to the already-authorized main-population geometry recovery.
