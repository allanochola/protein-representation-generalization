# Decoder-Geometry Beta Recovery — Pass 1 Verification

Status: **VERIFIED**

This record freezes the provenance-only outcome of deterministic beta-recovery
Pass 1 for the Experiment 04 decoder-geometry follow-up.

## Frozen identities

- Authorized replay commit:
  `2f15f34490854f83380c570dcda523ff4171ba79`
- Authorized replay driver SHA-256:
  `4279b8b064ccc53471a4d633707a60d4d0e453599e297b7d9972ba7fed3e30d1`
- Private Pass-1 verification report SHA-256:
  `f701d2d76f3363b28c420cdc0c4b8ae4c728039f024fab93d76531dbc97060b7`

## Acceptance result

- Canonical perturbations expected: 200
- Canonical perturbations verified: 200
- Biological perturbations: 100
- Canonical permutation-null perturbations: 100
- Replay mismatches: 0
- Replay exceptions: 0
- Stage-B coefficient hashes produced: 200

The accepted Pass-1 report persisted coefficient hashes and verification
metadata only. It did not persist Stage-B coefficient vectors.

## Boundary

Pass 1 was verification-only.

No decoder geometry was computed.
No confirmatory data were accessed.
Pass 2 was not executed by this verification step.

The private verification report itself is not committed to the public
repository.

After this record was created, the Pass-1 execution gate was returned to
hard-disabled state before any Pass-2 implementation or authorization.
