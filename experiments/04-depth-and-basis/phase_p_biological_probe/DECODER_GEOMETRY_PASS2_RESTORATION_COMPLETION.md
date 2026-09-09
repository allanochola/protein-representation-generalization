# Decoder Geometry Pass-2 Restoration Completion

Status: **COMPLETE / BYTE-IDENTICAL RESTORATION / GATE RECLOSED**

The previously accepted decoder-geometry Pass-2 artifacts were
deterministically restored under the frozen Pass-2 artifact-restoration
contract.

## Restoration result

The exact historical Pass-2 verification report was restored:

`b1905cb7ad9140f9f85f3c7cd621b1ace5dece645e63b0a8c1317ff643de10ed`

The exact historical Stage-B beta NPZ was restored:

`934b69de6765fb96f5dfe43460544cd7d06ad2bc0557029c6f66daeb18fd3580`

Both restored artifacts are byte-for-byte identical to their historical
accepted identities.

Pass-2 replay accounting:

- canonical biological perturbations: 100
- canonical permutation-null perturbations: 100
- total persisted bundles verified: 200 / 200
- Pass-1 versus Pass-2 coefficient hashes identical: 200 / 200
- failed records: 0

Artifact-integrity census:

- biological exact-zero beta rows: 0
- biological nonzero beta rows: 100
- canonical-null exact-zero beta rows: 37
- canonical-null nonzero beta rows: 63

No beta coefficient magnitudes or directions were inspected during
restoration.

## Frozen restoration authority

- restoration specification SHA-256:
  `90781279f38dce61c2367374c08b9fe180a13eaa70a54784e6844f127d23b17d`
- historical authorized Pass-2 SHA-256:
  `2648c088c6dc3e8d250d6941e4a806b5e590a02a477997939b4d8059fe7b74ec`
- restoration authorization commit:
  `7b78c5c51a800824b48faa2652b7b7389d48ab8d`

The replay was executed in a fresh Python child process with:

- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`

## Durable private persistence

The restored private artifacts were archived in:

`ocholla/exp04-pass2-restoration-private`

Fresh remote redownload verification confirmed:

- Pass-2 report SHA-256:
  `b1905cb7ad9140f9f85f3c7cd621b1ace5dece645e63b0a8c1317ff643de10ed`
- beta NPZ SHA-256:
  `934b69de6765fb96f5dfe43460544cd7d06ad2bc0557029c6f66daeb18fd3580`
- private storage manifest SHA-256:
  `ec7bd023c2fb46bd9f89b99368ab22d8a38ad3a11e59ad4e7e1abc785c02c411`

The private Pass-2 report and beta NPZ are not committed publicly.

## Scientific boundary

This operation restored previously accepted artifacts only.

It did not:

- inspect beta coefficient values;
- inspect beta directions;
- alter the frozen Pass-2 replay computation;
- compute decoder geometry;
- compare biological, canonical-null, isotropic, or C-matched geometry;
- bootstrap population statistics;
- execute final aggregation;
- access the confirmatory universe.

The Pass-2 execution gate is reclosed as part of this completion state.

The recovered beta artifact is now eligible for the already-frozen
main-population geometry recovery workflow.
