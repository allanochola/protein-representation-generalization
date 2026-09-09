# Decoder Geometry Pass-1 Restoration Completion

Status: **COMPLETE / BYTE-IDENTICAL RESTORATION / GATE RECLOSED**

The previously accepted decoder-geometry Pass-1 verification artifact was
deterministically restored under the frozen artifact-restoration contract.

## Restoration result

- canonical biological perturbations: 100 / 100 verified
- canonical permutation-null perturbations: 100 / 100 verified
- total: 200 / 200 verified
- mismatches/exceptions: 0

The restored report SHA-256 is:

`f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

This is exactly equal to the SHA-256 of the historical accepted Pass-1
verification report. Therefore the restoration reproduced the historical
artifact byte-for-byte.

No alternate Pass-1 report identity or Pass-2 compatibility exception is
required.

## Frozen restoration authority

- restoration specification SHA-256:
  `5a348031eb510de736a1e22db4d3f03478fc3ee3c81793c93b25e7064be28bd2`
- authorized restoration driver SHA-256:
  `211eaf7982ea8641c90b8c7dba4fec51fd06e3b4837309ed826b30ba2e7f1f17`
- authorization commit:
  `207e74988b21fe8ba0f9064b01c68f98f150e69e`

The restoration replay was executed in a fresh child Python process with:

- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`

The restored report itself records those thread values.

## Durable private persistence

The byte-identical restored report was copied to a dedicated private Kaggle
dataset:

`ocholla/exp04-pass1-restoration-private`

Remote redownload verification confirmed:

- report SHA-256:
  `f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`
- private storage manifest SHA-256:
  `f0805b78bf2d39059e1e400d9746d5966c4b88f2be56b9554d7534095e64441c`

The private report itself is not committed to the public repository.

## Scientific boundary

This operation restored a previously accepted verification artifact only.

It did not:

- inspect Stage-B coefficient values;
- alter the frozen replay contract;
- compute decoder geometry;
- perform biological/null/isotropic/C-matched comparisons;
- bootstrap any population statistic;
- execute Pass-2;
- execute main-population geometry recovery;
- execute final aggregation;
- access the confirmatory universe.

The Pass-1 restoration execution gate is reclosed as part of this completion
state and must not be rerun.
