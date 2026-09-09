# Decoder Geometry Main-Population Recovery Completion

Status: **COMPLETE / HISTORICAL MANIFEST MATCH / DURABLY ARCHIVED / GATE RECLOSED**

The historical decoder-geometry main-population outputs were recovered
under the frozen main-population recovery contract.

## Recovery result

The exact historical completion manifest was recovered:

`a5246082517ca1270a75f48288df9cb03d21d5c6393f3f2daaeb41229a4a0257`

Canonical accounting:

- biological records: 100
- permutation-null records: 100
- total records: 200
- eligible nonzero-beta geometry records: 163
- explicit zero-beta ineligible records: 37
- biological eligible: 100
- biological zero-beta: 0
- permutation-null eligible: 63
- permutation-null zero-beta: 37

The historical accepted population state was reproduced without rerunning
the completed recovery after acceptance.

## Frozen authority

- main-population recovery specification SHA-256:
  `4be794967fae51df8f514873a4255ec5ebb0d1fff3be018358a550a3db30cb9e`
- authorized recovery-driver SHA-256:
  `2a4a27b353cccaa542f8d2b26191e14b59d79fe88e0ad4e6acc69e8590ee5742`
- execution parent commit:
  `f55bf29600fcb7d7441421ee019a57aab3418512`

## Durable private persistence

The recovered population outputs were archived in the private Kaggle dataset:

`ocholla/exp04-main-population-geometry-private`

An initial archive version omitted the `per_direction/` directory because
the installed Kaggle CLI defaulted to directory mode `skip`.

This was repaired by creating a new dataset version using directory mode
`zip`, without rerunning geometry or modifying any scientific artifact.

Fresh remote redownload verification confirmed:

- historical completion manifest SHA-256:
  `a5246082517ca1270a75f48288df9cb03d21d5c6393f3f2daaeb41229a4a0257`
- private storage manifest SHA-256:
  `7373a9987060003313b6988831642efd2ce2fd455fc7a7c256da62495163766e`
- all 200 per-direction records were present and byte-identical to the
  recovered local records.

The private per-direction geometry records are not committed publicly.

## Scientific boundary

This operation recovered and archived previously completed direction-level
geometry only.

It did not:

- rerun beta recovery;
- rerun the accepted main-population recovery after completion;
- alter the frozen geometry engine;
- inspect beta coefficient values;
- compute new population summaries;
- compare biological and permutation-null geometry;
- compare isotropic geometry;
- compare C-matched geometry;
- run bootstrap inference;
- execute the final aggregation;
- access the confirmatory universe.

The main-population recovery execution gate is reclosed as part of this
completion state.

The recovered private records are now eligible for the already-frozen final
aggregation workflow.
