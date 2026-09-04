# Experiment 04 — S7 step-4b implementation-failure record

## Frozen classification

Namespace `920001-920100` is **CONSUMED / CLOSED**.

S7-v2 is **NOT EVALUATED**.

Reuse of `920001-920100` is forbidden.

## Protected attempt

The protected attempt was archived and remote-frozen at commit:

`8b7805ccfe7c721325d3ed5d6a52c4d23956efe8`

The run entered `run_one_perturbation()` and `select_C_R2()`.

`select_C_R2()` calls `fit_probe_or_fail()` during frozen Stage-A
cross-validation. `fit_probe_or_fail()` executes `model.fit(X, y)`.

The failure occurred only later when `select_C_R2()` attempted to
construct `R2Result(...)`.

Therefore at least one protected probe fit occurred before failure and
the namespace-consumption boundary was crossed.

## Root cause

The dedicated runner's `R2Result` omitted the inherited constructor-
providing decorator:

    @dataclass(frozen=True)

The current and inherited classes have the same eight annotated fields.
The current class has no explicit `__init__`, while the inherited class
constructs successfully.

Behavioral audit confirmed:

- inherited `R2Result`: PASS
- current `R2Result`: FAIL with
  `TypeError: R2Result() takes no arguments`

This is classified as a **pure extraction / implementation defect**.

## Systematic audit

Every class shared between the dedicated S7 runner and inherited
architecture runner was checked structurally.

Shared classes:

- `CalibrationContractError`
- `CalibrationFitFailure`
- `R2Result`
- `ScenarioCell`

`R2Result` is the only remaining structural/behavioral constructor defect.

`ScenarioCell` now matches and constructs successfully.

The generator's `SyntheticDataset` already has
`@dataclass(frozen=True)`, constructs successfully, and preserves frozen
behavior.

No third class-constructor extraction defect was found.

## Scientific status

No complete perturbation row, acceptance-cell result, or 9-of-9 candidate
verdict was produced.

Therefore this failure provides no scientific evidence for or against
S7-v2.

No generator amendment or scientific parameter change is authorized.

The frozen S7-v2 generator and frozen S7 step-4b scientific contract carry
forward unchanged.

## Successor namespace

The successor protected namespace is:

**`930001-930100` — ASSIGNED / UNOPENED**

It becomes consumed at its first protected probe fit.

## Firewall

- `910001-910100`: CONSUMED / CLOSED
- `920001-920100`: CONSUMED / CLOSED
- `930001-930100`: ASSIGNED / UNOPENED
- `4000-4099`: UNOPENED
- `2000-2099`: SEALED
- gamma: NONE
- S7-v2: NOT EVALUATED
