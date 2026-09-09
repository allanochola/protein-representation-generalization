# Decoder-Geometry Population Completion Provenance

## Status

The post hoc Experiment 04 decoder-geometry population execution completed
successfully and the execution gate has been returned to its hard-disabled
state.

This document records execution provenance and structural completion only.

**No biological/null/isotropic population-level geometry summaries had been
computed or inspected when this record was frozen.**

## Execution identity

- Hard-disabled population driver commit:
  `610ae7299b0087a120289467f74ce08bc5694989`
- Hard-disabled driver SHA-256:
  `b9d789fe73ddf12138c36544dc4d79760469f6b62c04587da90da009f0b566b5`
- Authorization commit:
  `dadb8f0c65bce0b5966ac4c14b34c80874cf1ff7`
- Authorized driver SHA-256:
  `e3c172d9abfe304b785506a773fa5abaa8be306e6172122d52f81c35a89f35f8`
- Post-execution closure commit:
  `4408eb77a8d56133aed7d5b50c9273a62a277982`
- Closed driver SHA-256:
  `b9d789fe73ddf12138c36544dc4d79760469f6b62c04587da90da009f0b566b5`

The authorization commit changed only the execution gate from
`ENABLE_GEOMETRY = False` to `ENABLE_GEOMETRY = True`.

After successful population completion, the closure commit changed only that
gate back from `True` to `False`.

## Private completion artifact

The private completion manifest is not committed to the public repository.

- Completion manifest SHA-256:
  `a5246082517ca1270a75f48288df9cb03d21d5c6393f3f2daaeb41229a4a0257`
- Completion state:
  `DECODER_GEOMETRY_POPULATION_COMPLETE`
- Structural acceptance:
  `True`

Population accounting:

- total rows accounted for: **200 / 200**
- eligible geometry analyses completed: **163 / 163**
- exact-zero beta rows explicitly geometry-ineligible: **37 / 37**
- biological rows completed: **100 / 100**
- biological exact-zero beta rows: **0**
- canonical permutation-null nonzero rows completed: **63 / 63**
- canonical permutation-null exact-zero beta rows: **37 / 37**

The 37 exact-zero null directions were retained explicitly as
`ineligible_zero_beta`; they were not normalized, analyzed, or silently
discarded.

## Scientific boundary at completion

At the time this provenance record was frozen:

- no population geometry summary had been computed;
- no biological-vs-null comparison had been computed;
- no comparison against the isotropic reference had been computed;
- no bootstrap interval had been computed;
- no p-value or significance test had been computed;
- no scientific PASS/FAIL verdict had been computed;
- no confirmatory-universe data had been accessed.

The private per-direction records existed and their byte identities had been
verified against the completion manifest, but their geometry payloads had not
been opened for population-level analysis.

## Interpretation boundary

Completion of this execution establishes only that the frozen decoder-geometry
instrument successfully produced the preregistered biological and canonical
permutation-null direction-level outputs under the frozen population-accounting
contract.

It does **not** by itself establish:

- compact SAE alignment;
- biological-vs-null separation;
- biological-vs-isotropic separation;
- mechanistic decomposition;
- toxin-specific causal structure;
- cross-family generalization;
- a confirmatory result.

Those questions require the separately frozen downstream aggregation and
comparison procedure.
