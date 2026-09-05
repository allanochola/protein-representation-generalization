# Arm B Phase-P Numerical-Conditioning Dry-Run Amendment

## Status

**PROSPECTIVE ENGINEERING AMENDMENT — NOT EXECUTION AUTHORIZATION**

This amendment supersedes only the clauses identified below in the frozen
`ARM_B_PHASE_P_NUMERICAL_CONDITIONING_DRY_RUN_SPEC.md`.

All original firewalls and restrictions not explicitly changed here remain
fully in force.

Writing or freezing this amendment does not authorize matrix loading,
conditioning execution, or biological Phase-P probing.

## 1. Reason

Read-only inspection of the frozen production runner established that the
278-row-only test does not cover the smaller fitting regimes used by Phase P.

The smallest production probe fit contains 128 rows for 1,280 raw-ESM
features.

The same inspection established that production LogisticRegression freezes:

- penalty = l1
- solver = liblinear
- fit_intercept = True
- max_iter = 10000
- tol = 1e-6
- integer random_state

The conditioning test must therefore exercise production-relevant fit sizes
and these exact numerical solver mechanics.

## 2. Superseded fit-size scope

The original 278-row-only scope is superseded.

Frozen unique conditioning fit sizes are:

`128, 153, 154, 160, 177, 178, 192, 200, 222, 240, 278`

These arise prospectively from the frozen production regimes:

- N=100: CV 128; Stage-A final/stability 160; Stage-B 200.
- N=120: CV 153 or 154; Stage-A final/stability 192; Stage-B 240.
- N=139: CV 177 or 178; Stage-A final/stability 222; Stage-B 278.

No fit size may be added or removed after conditioning results are observed.

## 3. Frozen conditioning grid

The amended dry run covers every combination of:

- layers: 1, 9, 18, 24, 30, 33;
- the eleven frozen fit sizes above;
- C values: 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0;
- engineering solver states: 0, 1, 2, 3, 4.

Exact authorized fit count:

`6 * 11 * 9 * 5 = 2970`

## 4. Artificial-label firewall

The original artificial-label rule remains unchanged:

`y_dry[i] = i mod 2`

Biological labels must not be loaded, reconstructed, inspected, or compared
with these artificial labels.

The firewall is structural. The conditioning test must not check empirical
agreement between artificial and biological labels.

## 5. Deterministic subset rule

For smaller fit sizes define the fixed row-position permutation:

`p[j] = (137 * j) mod 278`

for j = 0,...,277.

Because gcd(137,278)=1, every row position occurs exactly once.

For fit size m, use exactly the first m positions:

`p[0:m]`

in that order.

No biological metadata and no RNG may influence subset membership.

Artificial labels remain the global row-parity labels of the selected rows.

Odd fit sizes may have artificial class counts differing by one.

## 6. Exact production solver mechanics

Every conditioning fit must use LogisticRegression with exactly:

- penalty="l1"
- solver="liblinear"
- C=float(C)
- fit_intercept=True
- max_iter=10000
- tol=1e-6
- random_state=int(engineering_solver_state)

No scaling, normalization, PCA, whitening, centering, clipping, imputation,
feature filtering, or dimensionality transformation is permitted.

## 7. Engineering solver-state clarification

The fixed integers 0,1,2,3,4 are engineering-only liblinear solver states.

They are not Experiment-04 perturbation seeds and are not SeedSequence
entropy.

The conditioning implementation must not instantiate np.random.SeedSequence
or np.random.default_rng.

These five integers may be used only as LogisticRegression random_state.

Therefore the original seedless/RNG-free clause is clarified to forbid
Experiment-04 stochastic addressing and NumPy RNG construction while
permitting these prospectively frozen solver-state integers.

## 8. Permitted outputs

For each of exactly 2970 fits record only:

- layer;
- fit size;
- C;
- engineering solver state;
- fit completed or failed;
- ConvergenceWarning yes/no;
- finite coefficients yes/no;
- finite intercept yes/no;
- iteration count if exposed;
- exception class/message if fitting fails.

No predictive metric, C selection, support statistic, coefficient
interpretation, layer ranking, or biological comparison is permitted.

## 9. STOP rule

STOP if any authorized fit produces:

- ConvergenceWarning;
- fitting exception;
- non-finite coefficient;
- non-finite intercept;
- provenance/hash mismatch;
- matrix shape/dtype/finiteness failure;
- total fit count other than exactly 2970.

A STOP does not authorize dropping a condition, changing max_iter or tol,
adding scaling, changing solver or penalty, changing subsets or labels, or
rerunning until a passing result appears.

Any response to STOP requires a separate prospective amendment.

## 10. Meaning of PASS

A complete PASS means only that the frozen production solver configuration
completed this prospectively defined conditioning census without an observed
convergence warning, fitting exception, or non-finite fitted parameter.

PASS does not prove convergence for every possible future random_state.

PASS is not biological evidence and does not itself authorize Phase-P
biological execution.

## 11. Protected state and execution boundary

This amendment does not consume or redefine:

- main biological namespace 1000001-1000100;
- permutation-null namespace 1100001-1100100;
- later candidate null namespaces;
- 4000-4099;
- 2000-2099.

Biological probing remains CLOSED.

After this amendment is independently audited and frozen, a hard-disabled
conditioning implementation may be written and independently audited.

Execution still requires a separate prospective enablement step.

No Phase-E matrix may be opened by this conditioning experiment before those
boundaries are satisfied.
