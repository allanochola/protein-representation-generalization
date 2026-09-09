# Experiment 04 Pass-2 Artifact Restoration Specification

Status: **FROZEN BEFORE PASS-2 RESTORATION AUTHORIZATION**

This document governs deterministic restoration of the previously completed
decoder-geometry Pass-2 beta artifact and its verification report.

This is artifact restoration only. It is not a new scientific analysis.

## 1. Historical Pass-2 program

The exact historical Pass-2 driver is:

- hard-disabled SHA-256:
  `da3c90d860e6af9efd2ba39a7dd346dee9710650c05ee94bb122a2df1317d90a`
- authorized SHA-256:
  `2648c088c6dc3e8d250d6941e4a806b5e590a02a477997939b4d8059fe7b74ec`
- historical authorization commit:
  `ff81228050efc43460328102aaabcabd8a7e096b`
- historical closure commit:
  `41a62e5869ba4597d41bb873c5fe0d86c3b0a0f6`

Restoration MUST use this exact historical program.

The only permitted source change for restoration authorization is:

`ENABLE_PASS2 = False`

to:

`ENABLE_PASS2 = True`

No other source modification is permitted.

## 2. Exact Pass-1 authentication artifact

The required Pass-1 report SHA-256 is:

`f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

The lost historical Pass-1 report was deterministically restored byte-for-byte.
Therefore the restored artifact satisfies the historical Pass-2 authentication
contract without any compatibility exception or altered acceptance rule.

Pass-1 restoration closure:

`b61f82bec204cb90703bbc4af1607eb88c463dfa`

Durable private archive:

`ocholla/exp04-pass1-restoration-private`

Private storage manifest SHA-256:

`f0805b78bf2d39059e1e400d9746d5966c4b88f2be56b9554d7534095e64441c`

## 3. Frozen scientific source identities

The historical Pass-2 program must continue to authenticate:

- Pass-1 driver SHA-256:
  `b73af5a62c99171eb99f37244ecc38df19fe19def3377b542bcbe2ec6753ef91`
- Phase-P runner SHA-256:
  `e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec`
- decoder-geometry beta-recovery specification SHA-256:
  `205d13b20ef5bf9325794274b531f46c9ffa7fa7cc77a7e8bdd0a8be05edce69`
- decoder-geometry analysis engine SHA-256:
  `8289d96a11ee3f5506edf298bf0290f58414454737156c98737f4522642915ab`

No source substitution is permitted.

## 4. Exact historical Phase-P inputs

Pass-2 restoration MUST use the exact historical private input triplet:

- `execution_manifest.json`
  SHA-256 `f5049a77f210b53e58ded918d8cbce9444444fd141df86f61a94dc8aa460e7ba`
- `main_per_perturbation.csv`
  SHA-256 `5ec2ce9810d344613b91117fe72e76d54306ba8ae2402a3e31ff327bfb93841c`
- `permutation_null_per_perturbation.csv`
  SHA-256 `2657f3f7a04b5ebe50a9e0514cefdf94d22b6d92a8695c8b957602d97348c6ae`

All identities must be verified before replay.

## 5. Historical Pass-2 CLI contract

The exact historical Pass-2 program requires:

- `--phase-p-private-dir`
- `--pass1-report`
- `--output-json`
- `--output-npz`

Restoration must bind the first two arguments to the exact historical inputs and
byte-identical restored Pass-1 report.

The output arguments must point to a fresh private/local restoration directory.

Existing Pass-2 outputs must never be overwritten or reused.

## 6. Replay population

The canonical replay population remains:

- biological perturbations: 100
- biological IDs: 1000001 through 1000100
- canonical permutation-null perturbations: 100
- null IDs: 1100001 through 1100100
- total replay paths: 200

No row may be dropped, substituted, retried selectively, or replaced.

## 7. Numerical execution contract

Pass-2 restoration must execute in a fresh Python child process with these
environment variables set before interpreter startup:

- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`

The frozen numerical computation, solver semantics, seed paths, selected-C
semantics, Stage-B fitting semantics, coefficient serialization, and hashing
must remain unchanged.

## 8. Historical restoration targets

The previously accepted historical Pass-2 output identities are:

Pass-2 verification report SHA-256:

`b1905cb7ad9140f9f85f3c7cd621b1ace5dece645e63b0a8c1317ff643de10ed`

Stage-B beta NPZ SHA-256:

`934b69de6765fb96f5dfe43460544cd7d06ad2bc0557029c6f66daeb18fd3580`

These are restoration targets.

A successful restoration requires exact byte equality to both historical
SHA-256 identities.

Failure of either identity check fails closed.

No automatic retry is permitted.

## 9. Required beta artifact structure

The historical accepted beta artifact had exactly four arrays:

- `biological_beta`
- `biological_ids`
- `null_beta`
- `null_ids`

Required shapes:

- `biological_ids`: `(100,)`
- `biological_beta`: `(100, 1280)`
- `null_ids`: `(100,)`
- `null_beta`: `(100, 1280)`

All beta arrays must remain finite `float64`.

The historical exact-zero census was:

- biological zero beta: 0
- biological nonzero beta: 100
- canonical-null zero beta: 37
- canonical-null nonzero beta: 63

This census is an artifact-integrity expectation, not a new scientific result.

No beta coefficient magnitudes or directions may be printed or inspected
during restoration.

## 10. Restoration acceptance rule

Pass-2 restoration succeeds only if all of the following hold:

1. exact historical Pass-2 source identities pass;
2. exact Pass-1 report SHA passes;
3. exact Phase-P private input identities pass;
4. exactly 200 canonical replay paths are processed;
5. all persisted Pass-1 coefficient hashes are authenticated;
6. no replay mismatch or exception occurs;
7. Pass-2 report SHA equals:
   `b1905cb7ad9140f9f85f3c7cd621b1ace5dece645e63b0a8c1317ff643de10ed`
8. beta NPZ SHA equals:
   `934b69de6765fb96f5dfe43460544cd7d06ad2bc0557029c6f66daeb18fd3580`
9. beta artifact keys, shapes, dtypes, finiteness and zero census match the
   historical accepted artifact.

If any condition fails, stop.

Do not modify the computation and rerun.

## 11. Durable storage

After successful exact restoration, both private Pass-2 artifacts must be
placed in dedicated durable private storage and independently redownloaded and
SHA-verified before the local ephemeral copies are relied upon downstream.

The beta NPZ and private Pass-2 report must not be committed to the public
repository.

## 12. Scientific firewall

Pass-2 restoration does NOT authorize:

- decoder-geometry computation;
- inspection of beta coefficient values;
- biological-vs-null geometry comparison;
- isotropic comparison;
- C-matched comparison;
- population aggregation;
- bootstrap;
- p-values;
- scientific verdicts;
- confirmatory-universe access.

Pass-2 exists here only to restore the previously accepted coefficient
artifact required by the already-frozen geometry-recovery workflow.

## 13. Required sequence

After this specification is frozen:

1. authorize the exact historical Pass-2 driver by one line only;
2. verify the authorized SHA exactly;
3. bind the four historical CLI arguments;
4. verify fresh output paths;
5. launch one fresh single-thread child process;
6. execute the canonical 200-path Pass-2 replay exactly once;
7. verify historical report SHA exactly;
8. verify historical beta NPZ SHA exactly;
9. verify artifact structure without printing coefficients;
10. durably archive both private artifacts;
11. independently redownload and verify them;
12. re-close Pass-2 to exact historical disabled bytes;
13. freeze public restoration-completion provenance;
14. return to the already-authorized main-population geometry recovery.

No geometry result is opened during this sequence.
