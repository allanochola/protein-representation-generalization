# Decoder-Geometry C-Matched Null Reconciliation

**Status:** FROZEN BEFORE POPULATION-LEVEL GEOMETRY INSPECTION

## Purpose

This note documents a pre-result implementation reconciliation in the
Experiment 04 decoder-geometry follow-up.

The original frozen decoder-geometry and beta-recovery specification requires
a secondary marginal C-distribution-matched permutation control.

The later decoder-geometry aggregation specification and the first frozen
aggregation driver omitted that already-specified secondary arm.

The omission was identified after the aggregation driver had been authorized
but before that driver was executed and before any private biological,
canonical-null, or isotropic population-level geometry result was opened.

No decoder-geometry result informed this reconciliation.

## Frozen provenance

At the time this omission was identified:

- branch: `exp04-depth-and-basis`
- authorized-but-unexecuted repository HEAD:
  `c5fbd686a2987f97902226816c96cb58b9700200`
- original decoder-geometry / beta-recovery specification SHA-256:
  `205d13b20ef5bf9325794274b531f46c9ffa7fa7cc77a7e8bdd0a8be05edce69`
- aggregation specification SHA-256:
  `59f3b9f27c51dbf46092e4ff276acfe5cca4f5aa3fb7c7d94791a5337b8e55d2`
- authorized aggregation driver SHA-256:
  `4e653fd71a44b07e9b6e43180b753eb14ae2caca9bf73bdc73b394068bb67283`

The existing aggregation authorization commit is retained as provenance.

It is not rewritten or removed.

## Original frozen requirement

Section 11 of the original decoder-geometry / beta-recovery specification
defines a secondary marginal C-distribution-matched permutation control.

For null perturbation ordinal i, the frozen procedure requires:

1. reproduce the exact frozen null target-N pool and frozen permuted labels;
2. do not rerun Stage-A selection for the secondary fit;
3. impose the persisted selected C from biological perturbation ordinal i;
4. reuse the already-consumed canonical null Stage-B seed for null
   perturbation ordinal i;
5. otherwise retain the frozen Phase-P Stage-B solver semantics;
6. capture convergence warnings, failures, and exceptions;
7. do not retry, replace, rematch, or alter solver settings;
8. exclude failed/nonconverged secondary fits only from the secondary
   direction-based geometry comparison while reporting their counts;
9. report the C-matched comparison separately from the canonical
   biological-versus-null comparison.

The ordinal mapping supplies marginal C-distribution matching only.

It is not a paired biological-versus-null design.

## Reconciliation finding

The later aggregation specification froze population summaries for:

- biological eligible directions;
- canonical permutation-null eligible directions;
- the frozen isotropic reference.

It did not carry forward the already-frozen Section-11 C-matched null arm.

The corresponding authorized aggregation implementation therefore cannot yet
be used as the complete decoder-geometry population analysis.

## Required prospective correction

Because no population-level decoder-geometry result had been opened when the
omission was discovered, the correction remains prospective.

Before final population-level aggregation:

1. implement the frozen Section-11 C-matched null replay procedure;
2. freeze that implementation while hard-disabled;
3. authorize it separately;
4. execute the C-matched secondary fits and direction-level geometry under the
   frozen original rules;
5. preserve all convergence accounting and realized denominators;
6. recover the already-completed frozen isotropic archive;
7. reconcile the aggregation implementation so it reports:
   - biological versus canonical permutation null as the primary comparison;
   - biological versus isotropic as the geometric reference;
   - biological versus marginal C-distribution-matched permutation null as the
     separately labeled secondary regularization-comparability analysis;
8. freeze and authorize the reconciled aggregation implementation before any
   population-level geometry result is inspected.

## Scientific boundary

This reconciliation:

- does not change any observed Experiment 04 result;
- does not alter the original decoder-geometry scientific question;
- does not add a new post-result analysis;
- does not consume a new seed namespace;
- does not authorize confirmatory-universe access;
- does not introduce p-values or PASS/FAIL thresholds;
- does not alter the canonical permutation-null population;
- does not convert the C-matched arm into a paired design;
- does not alter Experiment 05.

The decoder-geometry follow-up remains post hoc, descriptive, and
non-confirmatory.

## Results-unopened state at freeze

At the time this note is frozen:

- aggregation execution: NOT STARTED;
- biological population-level geometry: UNOPENED;
- canonical-null population-level geometry: UNOPENED;
- isotropic population-level payload: UNOPENED for this aggregation;
- C-matched secondary fits: NOT RUN;
- population bootstrap: NOT RUN;
- confirmatory universe: UNTOUCHED.
