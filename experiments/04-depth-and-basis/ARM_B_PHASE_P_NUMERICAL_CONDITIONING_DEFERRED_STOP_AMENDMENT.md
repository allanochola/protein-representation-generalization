# Arm B Phase-P Numerical-Conditioning Deferred-STOP Amendment

## Status

**PROSPECTIVE ENGINEERING AMENDMENT — NOT EXECUTION AUTHORIZATION**

This amendment modifies only the STOP timing of the frozen numerical-
conditioning dry run.

It is prospective: no numerical-conditioning fit has yet been executed.

All clauses of the original conditioning specification and first amendment
remain in force except where this amendment explicitly supersedes their
fail-fast STOP timing.

Writing, auditing, or freezing this amendment does not authorize execution.

## 1. Reason

The purpose of the conditioning dry run is to characterize whether the
already-frozen L1/liblinear probe is numerically operational over the
complete prospectively frozen conditioning grid.

Aborting after the first fit-local numerical failure would reveal only one
point on that grid and would leave the remaining prospectively authorized
conditions unobserved.

The diagnostic is therefore amended to distinguish fit-local numerical
failures from experiment-integrity failures.

## 2. Complete-census rule

Once all pre-load provenance and integrity checks have passed and the
conditioning census begins, every one of the exactly 2970 prospectively
authorized fit conditions must be attempted.

A fit-local numerical failure must be recorded for that fit and must not
terminate the remaining authorized census.

The runner must therefore attempt all combinations of the already-frozen:

- six Phase-E layers;
- eleven fit sizes;
- nine C values;
- five engineering solver states.

No new condition may be added during execution.

## 3. Deferred-STOP conditions

The following are fit-local numerical failures and are deferred until the
complete authorized census has been attempted:

- ConvergenceWarning;
- fitting exception;
- non-finite fitted coefficient;
- non-finite fitted intercept.

For each affected fit, the runner must record the permitted diagnostics
already frozen by the first amendment.

After all 2970 authorized fit conditions have been attempted, the overall
conditioning verdict is STOP if one or more fit-local numerical failures
were observed.

A deferred STOP remains a STOP. It does not convert a failing fit into a
passing fit and does not authorize adaptation.

## 4. Immediate-STOP conditions

Experiment-integrity failures remain immediate STOP conditions.

These include:

- specification SHA mismatch;
- amendment SHA mismatch;
- row-manifest SHA mismatch;
- Phase-E matrix SHA mismatch;
- unexpected matrix shape;
- unexpected matrix dtype;
- non-finite matrix input;
- frozen grid or fit-count definition mismatch;
- output-path collision that would overwrite or mix prior results;
- any condition showing that the executed census is no longer the frozen
  conditioning experiment.

An immediate integrity STOP terminates execution because subsequent rows
would no longer constitute the preregistered diagnostic.

## 5. Output completeness

If no immediate integrity STOP occurs, the output table must contain exactly
2970 fit-result rows, one for every prospectively authorized condition.

Every row must identify:

- layer;
- fit size;
- C;
- engineering solver state;
- fit completed yes/no;
- ConvergenceWarning yes/no;
- coefficient finite yes/no when available;
- intercept finite yes/no when available;
- n_iter when exposed and available;
- exception class/message when fitting fails.

The output must not contain predictive-performance quantities, support
statistics, biological outcomes, or adaptive selections.

## 6. Overall verdict

If all 2970 fit conditions are attempted and no fit-local numerical failure
is observed, the engineering verdict is PASS under the interpretation
already frozen by the first amendment.

If all 2970 fit conditions are attempted and one or more fit-local numerical
failures are observed, the engineering verdict is STOP.

The complete table may be used only to describe the numerical failure
surface and to inform whether a separate prospective engineering amendment
should be proposed.

It does not itself authorize any repair.

## 7. No automatic repair interpretation

No observed failure pattern prospectively authorizes a particular remedy.

In particular, failures concentrated at a C value, fit size, layer, or
engineering solver state do not automatically authorize:

- increasing max_iter;
- weakening tol;
- scaling or normalization;
- removing a C value;
- removing a fit size;
- removing a layer;
- removing an engineering solver state;
- changing solver;
- changing penalty;
- changing subset construction;
- changing artificial labels.

Any such response requires a separate prospective amendment after the
conditioning result is frozen.

## 8. Interpretation firewall

The complete failure surface is an engineering diagnostic only.

It must not be interpreted as toxin prediction, biological generalization,
mechanistic evidence, feature importance, layer quality, or evidence for
or against SAE-basis misalignment.

Biological probing remains CLOSED.

## 9. Implementation boundary

After this amendment is independently audited and frozen, the hard-disabled
conditioning runner may be written.

That implementation must encode:

- immediate STOP for integrity failures;
- per-fit recording and continuation for fit-local numerical failures;
- exactly 2970 attempted conditions absent an immediate integrity STOP;
- final PASS only when zero fit-local numerical failures occurred;
- final STOP when one or more fit-local numerical failures occurred.

The runner must then be independently audited and frozen while execution
remains hard-disabled.

A separate prospective enablement step is still required before any
conditioning fit may execute.
