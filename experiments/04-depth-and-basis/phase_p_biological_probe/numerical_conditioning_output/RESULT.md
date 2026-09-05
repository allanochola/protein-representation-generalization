# Experiment 04 — Arm B Phase-P Numerical-Conditioning Result

## Status

**PASS — COMPLETE AND CLOSED.**

This document archives the single prospectively authorized numerical-conditioning execution for the frozen Arm B L1 + liblinear probe.

This is an engineering result only. It is not biological evidence and does not report predictive performance.

## Frozen execution boundary

- Authorization freeze commit: `e4aba777a0628cfbd163d4cb8b75584c71197fe3`
- Frozen execution-authorization SHA-256: `3e5bff11db738b584088ab3b9bff0afdd7baf44e5d070b2468f439fe9a4fadab`
- Canonical hard-disabled runner SHA-256: `809aec1e712a040ecb4e6415f9eba7bedd9ced13022f6d33246adddbafe31340`
- Enabled execution-state runner SHA-256: `fcb364ad3a35ab9620bc8e0b16b94d5380fc28d452a20afd281f9a92d1f65e59`
- Diagnostic CSV SHA-256: `111e6bffda11f81c8a4346b5ae10dac2e79a156fe862ee761918d0f8926b91b7`

The enabled runner differed from the canonical frozen runner only by the mechanical execution-state change:

`EXECUTION_ENABLED = False` -> `EXECUTION_ENABLED = True`

No scientific or numerical mechanics were changed.

## Frozen census

The authorized census contained exactly 2,970 attempted fits:

- layers: 1, 9, 18, 24, 30, 33;
- fit sizes: 128, 153, 154, 160, 177, 178, 192, 200, 222, 240, 278;
- C grid: 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0;
- engineering solver states: 0, 1, 2, 3, 4.

Exact arithmetic:

`6 layers x 11 fit sizes x 9 C values x 5 engineering states = 2,970 fits`.

The artificial labels and deterministic row permutation were those frozen in the conditioning specification/amendments and execution authorization.

## Observed result

Exactly 2,970 diagnostic rows were produced.

Prospectively frozen fit-local failure census:

- fit not completed: **0**
- ConvergenceWarning: **0**
- coefficient not finite/True: **0**
- intercept not finite/True: **0**
- recorded exception_type: **0**
- any fit-local numerical failure: **0**
- n_iter populated: **2,970 / 2,970**

Therefore the prospectively frozen verdict is:

**PASS — all 2,970 frozen engineering fits completed without an observed fit-local numerical failure.**

## Interpretation boundary

This PASS establishes only that the frozen L1 + liblinear probe fit the actual Phase-E numerical matrices across the frozen engineering grid without an observed:

- ConvergenceWarning;
- fitting exception;
- nonfinite fitted coefficient;
- nonfinite fitted intercept.

It does **not** establish:

- biological predictiveness;
- toxin specificity;
- biological validity;
- generalization;
- mechanistic interpretation;
- SAE-basis misalignment;
- distributed accessibility;
- superiority to a biological baseline.

No AUROC or other predictive metric was computed in this conditioning census.

## Result-audit artifact note

Two post-execution read-only audit attempts initially reported apparent C-grid mismatches.

These were **audit-code errors, not experiment failures and not runner deviations**.

The incorrect audit expectation used square-root-of-ten-style intermediate C values such as `0.000316227766...`, whereas frozen Amendment 1 and the frozen runner both specify the exact 1-3-10-style grid:

`1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0`.

A subsequent read-only source/spec diagnostic established:

- runner `C_GRID` exactly equals the frozen Amendment-1 grid;
- the same C value is passed directly to `LogisticRegression(C=float(C), ...)`;
- the same C value is written to the diagnostic CSV;
- the executed CSV contains exactly that frozen grid.

No conditioning fit was rerun and no output was modified while resolving the audit artifact.

## Closure

The conditioning execution occurred exactly once.

After archiving this result, the runner was restored to its canonical hard-disabled state.

No automatic numerical repair was needed or performed.

Biological probing remained closed throughout this conditioning result audit and archive step.

Protected biological/null seed namespaces were not consumed by this conditioning experiment.
