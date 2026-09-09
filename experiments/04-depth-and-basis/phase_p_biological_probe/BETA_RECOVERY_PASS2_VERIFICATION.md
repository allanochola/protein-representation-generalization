# Experiment 04 — beta recovery Pass 2 verification

**State:** `BETA_RECOVERY_PASS2_VERIFIED_FROZEN_PASS2_HARD_DISABLED`

This note records provenance for the successful deterministic Stage-B beta
recovery required by the frozen decoder-geometry follow-up specification.

No recovered coefficient vector is contained in this file.

## Frozen authorization

- Authorized replay parent commit:
  `ff81228050efc43460328102aaabcabd8a7e096b`
- Authorized Pass-2 driver SHA-256:
  `2648c088c6dc3e8d250d6941e4a806b5e590a02a477997939b4d8059fe7b74ec`
- Accepted Pass-1 verification report SHA-256:
  `f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

## Pass-2 acceptance

The authorized replay returned:

- canonical perturbations expected: 200
- persisted verification bundles reproduced: 200 / 200
- Pass-1 versus Pass-2 Stage-B coefficient SHA-256 identities: 200 / 200
- serialized Stage-B coefficient vectors independently re-hashed successfully:
  200 / 200
- biological canonical rows: 100
- permutation-null canonical rows: 100
- failed rows: 0

Private Pass-2 verification report SHA-256:

`b1905cb7ad9140f9f85f3c7cd621b1ace5dece645e63b0a8c1317ff643de10ed`

Private recovered-beta artifact SHA-256:

`934b69de6765fb96f5dfe43460544cd7d06ad2bc0557029c6f66daeb18fd3580`

The private verification report and recovered coefficient artifact are not
committed to the public repository.

## Zero-beta accounting

The frozen exact-zero rule was applied after successful recovery:

- biological exact-zero beta: 0 / 100
- biological nonzero beta: 100 / 100
- canonical-null exact-zero beta: 37 / 100
- canonical-null nonzero beta: 63 / 100

Exact-zero beta rows remain part of population accounting but are ineligible
for direction-normalized decoder reconstruction or concentration statistics.

## Scientific boundary

This recovery does not change the closed Experiment 04 verdict.

The canonical Experiment 04 output originally persisted `K_t_full` only as a
Stage-B support-cardinality check. It did not persist Stage-B support
coordinates, signs, or coefficient magnitudes. The recovered vectors are
deterministic post hoc recovery artifacts for the frozen decoder-geometry
analysis.

No confirmatory-universe data were accessed.

No decoder geometry had been computed at the time this recovery state was
frozen.

In the same repository transition that adds this record, the Pass-2 execution
gate is returned to hard-disabled state.
