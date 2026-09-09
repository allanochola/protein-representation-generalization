# Decoder-Geometry C-Matched Null Recovery — Execution Completion

Status: **COMPLETE AND HARD-DISABLED**

This note records execution provenance for the secondary marginal
C-distribution-matched permutation-control coefficient recovery specified
prospectively for the Experiment 04 decoder-geometry follow-up.

## Authorization identity

- Authorization commit:
  `a32c2970eaab5d75ba5ab5cde510495541431a29`
- Authorized driver SHA-256:
  `57e693f52f8bbcf813da52131861a24488f1539a7e7321a6c3babc90a1e63bc0`
- Frozen hard-disabled driver SHA-256:
  `6cbb1937347256973272e6235e1711e24544942657dc758fecdf6f810cbf1946`

The authorization changed only the hard execution gate from `False` to
`True`. After successful execution, the driver was returned byte-for-byte
to the previously frozen hard-disabled source.

## Execution accounting

- Expected secondary fits: **100**
- Accounted secondary fits: **100**
- Converged fits: **100**
- Fit/convergence exclusions: **0**
- Valid recovered coefficient vectors: **100**
- Coefficient width: **1,280**

The secondary construction reused the frozen null perturbation mechanics
and existing null Stage-B seed stream. Stage-A model selection was not
rerun and no new seed namespace was introduced.

## Private artifact identities

The execution products remain private and are not committed to this
repository.

- Recovery report SHA-256:
  `bcc20a34612c9f9c81e546cb6fc74ae6fc2fd81c21b9094ba924a6f36143a45c`
- Recovered-beta artifact SHA-256:
  `a1ac55f9810a0f100e3b9cb4805acbdf5c63a9667980f8229d6478b44be7268c`

No coefficient values, selected-C values, reconstructed label vectors, or
per-row label hashes are published in this note.

## Scientific boundary

This execution recovered coefficients for the prospectively reconciled
secondary marginal C-distribution-matched permutation control only.

At completion:

- decoder geometry had **not** been computed for these recovered vectors;
- existing biological geometry had **not** been opened for comparison;
- existing canonical-null geometry had **not** been opened for comparison;
- isotropic geometry had **not** been opened for comparison;
- no population aggregation had been executed;
- no bootstrap comparison had been executed;
- no p-value, PASS/FAIL decision, or scientific verdict had been computed;
- the confirmatory universe remained untouched.

The C-matched construction is a **secondary marginal control**, not a
paired biological-versus-null design. It does not replace or modify the
canonical Experiment 04 permutation-null population.

The next permitted step is a separately frozen decoder-geometry
population procedure for the successfully recovered C-matched
coefficient vectors. Final population comparison remains prohibited until
that procedure and the reconciled aggregation procedure are separately
frozen and authorized.
