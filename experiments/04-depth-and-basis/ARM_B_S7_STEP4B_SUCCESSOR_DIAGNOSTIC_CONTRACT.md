# Experiment 04 — Arm B S7 step-4b successor diagnostic contract

## 1. Purpose

This contract governs a successor protected execution after
`920001-920100` was consumed by an implementation defect before S7-v2
received a complete scientific evaluation.

This is an **implementation-recovery contract**, not a scientific redesign.

## 2. Successor namespace

The successor protected namespace is:

**`930001-930100`**

At contract freeze it is:

**ASSIGNED / UNOPENED**

The entire namespace becomes permanently consumed at the first protected
probe fit.

No automatic retry is authorized after that boundary.

## 3. Prior namespace

`920001-920100` is permanently CONSUMED / CLOSED.

It must never be reused.

The reason is recorded in:

`S7_STEP4B_IMPLEMENTATION_FAILURE_920001_920100.md`

## 4. Scientific carry-forward

The previously frozen S7 step-4b scientific contract remains authoritative
and is incorporated here unchanged.

In particular, this recovery does not alter:

- S7-v2 generator or parameters;
- MASTER_TAU;
- target N values;
- 100 perturbations per cell;
- Stage-A split;
- five-fold R2 CV;
- C grid;
- one-SE C-selection rule;
- solver configuration;
- full-target-N refit;
- independent 80% stability subsampling;
- seed-stream architecture apart from the new protected namespace;
- unsigned or signed support definitions;
- Jaccard definitions;
- pairwise median aggregation;
- K_stab >= 3 resolution rule;
- >=71/100 resolution requirement;
- planted-coordinate recurrence R >= 71;
- min(n_plus, n_minus) >= 8;
- strict G_stat < I_stat;
- acceptance tau indices {6,7,8};
- all-three-limbs cell rule;
- 9-of-9 candidate acceptance rule.

No gamma is selected.

## 5. Generator

The S7-v2 generator must remain byte-for-byte unchanged.

The prior protected failure produced no S7-v2 candidate evidence and
therefore supplies no scientific basis for generator amendment.

## 6. Authorized implementation repair

The only currently demonstrated remaining runner defect is that
`R2Result` lacks the inherited:

    @dataclass(frozen=True)

The authorized repair is exactly restoration of that inherited decorator.

No fields, annotations, function bodies, thresholds, seed rules, solver
parameters, generator parameters, acceptance rules, or scientific constants
may change in that repair.

## 7. Required pre-opening verification

Before `930001-930100` may be opened:

1. restore only `@dataclass(frozen=True)` on `R2Result`;
2. verify the repair diff is exactly the authorized semantic restoration;
3. compare every shared runner class against the inherited source;
4. behaviorally instantiate inherited dataclasses and their runner copies;
5. confirm `ScenarioCell` constructor behavior;
6. confirm `R2Result` constructor behavior;
7. confirm `SyntheticDataset` constructor and frozen behavior;
8. confirm runner and generator imports;
9. perform only non-protected runtime checks;
10. confirm no protected fit or protected SeedSequence occurred;
11. commit and remote-verify the repaired disabled runner;
12. separately enable protected successor execution;
13. commit and remote-verify that enablement.

Only after all gates pass may `930001-930100` be opened.

## 8. Execution sequence

After enablement is remote-verified:

1. invoke the frozen successor diagnostic exactly once;
2. do not automatically retry;
3. archive outputs and provenance before scientific interpretation;
4. commit the archive;
5. push;
6. live-remote verify;
7. only then inspect the frozen aggregate result;
8. mechanically apply the existing 9-of-9 decision rule.

## 9. Failure semantics

Process launch alone does not consume `930001-930100`.

If failure occurs before the first protected fit, determine namespace status
by read-only failure-point audit.

Once the first protected fit occurs, `930001-930100` is permanently
CONSUMED / CLOSED regardless of later interruption or implementation error.

Any subsequent execution would require another prospectively frozen
namespace.

## 10. Scientific rejection

If a complete successor S7-v2 evaluation fails the existing preregistered
9-of-9 criterion, the candidate is scientifically rejected.

No same-namespace rescue, tuning, threshold change, generator adjustment, or
favorable variant selection is permitted.

## 11. Firewall at freeze

- `910001-910100`: CONSUMED / CLOSED
- `920001-920100`: CONSUMED / CLOSED
- `930001-930100`: ASSIGNED / UNOPENED
- `4000-4099`: UNOPENED
- `2000-2099`: SEALED
- gamma: NONE
- S7-v2: NOT EVALUATED
- protected fits under `930001-930100`: NONE
