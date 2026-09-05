# Experiment 04 — Arm B Phase-P Numerical-Conditioning Execution Authorization

## Status

PROSPECTIVE EXECUTION AUTHORIZATION.

This document authorizes a later, separate execution step for the already
frozen Arm-B Phase-P numerical-conditioning dry run. It does not itself
enable or execute the runner.

## Frozen implementation

The authorized implementation is exactly:

- runner: `experiments/04-depth-and-basis/phase_p_biological_probe/run_phase_p_numerical_conditioning_dry_run.py`
- runner SHA-256: `809aec1e712a040ecb4e6415f9eba7bedd9ced13022f6d33246adddbafe31340`
- hard-disabled freeze commit: `1adc75511d2e480c04bf767516de6a779d5d4fd2`

No other implementation is authorized by this document.

## Authorized execution

A later execution step may enable and execute the frozen numerical-
conditioning census exactly as already specified and amended:

- six frozen Phase-E raw ESM matrices;
- layers 1, 9, 18, 24, 30, and 33;
- fit sizes 128, 153, 154, 160, 177, 178, 192, 200, 222, 240, and 278;
- nine frozen C values;
- engineering solver states 0 through 4;
- exactly 2,970 attempted fits if no immediate integrity STOP occurs;
- deterministic row permutation `(137 * j) % 278`;
- artificial labels `i % 2`;
- exact frozen L1 + liblinear solver mechanics.

## Purpose

The sole authorized question is numerical conditioning:

> Can the frozen L1 + liblinear probe fit the actual Phase-E numerical
> matrices across the frozen engineering grid without ConvergenceWarning,
> fitting exception, or nonfinite fitted parameters?

This is an engineering dry run. It is not biological evidence.

## Immediate integrity STOP

Execution must STOP before the numerical census if an immediate integrity
condition occurs, including provenance/hash mismatch, wrong matrix
shape/dtype/finiteness, output collision, or frozen grid/count mismatch.

No numerical result from a partially entered or invalid experiment may be
interpreted as the conditioning result.

## Deferred fit-local STOP

If no immediate integrity STOP occurs, all 2,970 conditions are attempted.

The following are fit-local failures:

- `ConvergenceWarning`;
- fitting exception;
- nonfinite coefficient;
- nonfinite intercept.

Fit-local failures are recorded rather than causing an early census abort.

After the complete census:

- PASS requires zero fit-local failures;
- one or more fit-local failures produces the prospectively frozen final STOP.

## PASS consequence

PASS means only that no numerical-conditioning failure was observed over the
frozen 2,970-fit engineering census.

PASS does not establish biological predictiveness, biological validity,
generalization, mechanistic interpretation, SAE-basis misalignment, or toxin
specificity.

PASS does not itself authorize biological probing.

Any subsequent biological-probe execution requires its own already-applicable
frozen protocol gates and a separate explicit execution boundary.

## STOP consequence

A numerical-conditioning STOP is recorded as observed.

No automatic numerical repair is authorized.

In particular, after observing a STOP this authorization does not permit
changing C values, solver, tolerance, max_iter, scaling, normalization,
representation, layer set, fit sizes, artificial labels, row permutation,
engineering states, or failure criteria and rerunning as though the change
were part of this frozen census.

Any proposed remedy requires a new prospective amendment made after the
observed conditioning result is archived, with the original STOP preserved.

## Biological-label firewall

This execution must not load, inspect, reconstruct, validate, compare, or
otherwise use biological class labels.

Artificial labels are engineering-only and carry no biological meaning.

No AUROC or other predictive-performance metric is authorized.

## Seed firewall

The conditioning execution is RNG-free apart from the already-frozen
deterministic liblinear engineering `random_state` values 0 through 4.

It must not instantiate NumPy RNG or SeedSequence.

It must not materialize or consume protected biological or permutation-null
seed namespaces, including 1000001–1000100 and 1100001–1100100.

## Result handling

The complete conditioning diagnostic output must be preserved exactly as
produced.

The observed PASS or STOP must be reported without threshold changes,
selective reruns, omitted failed conditions, or post-hoc reinterpretation.

The conditioning result must be archived before any later decision about
biological-probe execution.

## Current boundary

At the time this authorization is drafted:

- the conditioning runner remains hard-disabled;
- zero conditioning fits have been executed;
- no Phase-E matrix has been opened by the authorization step;
- no biological label has been loaded;
- no protected biological/null seed has been consumed;
- biological probing remains closed.
