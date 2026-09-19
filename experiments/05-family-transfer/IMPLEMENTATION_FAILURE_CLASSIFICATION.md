# Implementation-Failure Classification

**Status:** frozen before Phase-0 instrument execution.

The classification boundary is determined only by prespecified integrity
invariants. Surprisingness, direction, or convenience of an observed number is
never evidence of an implementation defect.

## 1. Repairable implementation failure

One or more internal integrity invariants fail, including but not limited to:

- impossible rank or dimension;
- required monotonicity failure;
- out-of-bound probability, rate, count, or index;
- census totals inconsistent with the frozen manifest;
- replay, content, or code-hash mismatch;
- missing or duplicated required cells;
- failure to terminate with the result type required by a frozen fixture.

Required action:

1. disable the affected gate;
2. classify the run as void;
3. commit the repair alone, without changing scientific thresholds or rules;
4. re-authorize execution explicitly;
5. rerun from the last uncontaminated state.

The void output cannot support or oppose a scientific conclusion.

## 2. `NO_GROSS_IMPLEMENTATION_FAILURE`

Every frozen integrity invariant holds, but the result contradicts a
prospectively recorded expectation or heuristic.

Required action:

1. classify the run `NO_GROSS_IMPLEMENTATION_FAILURE`;
2. record the contradiction and its magnitude;
3. change no analysis rule, threshold, or interpretation in response;
4. apply the frozen scientific decision rule exactly as written.

## 3. Scientific gate failure

A correctly functioning instrument produces a result that fails a frozen
scientific gate.

Required action: close the affected branch or stage under the frozen rule. A
scientific failure is not a software defect and is not repaired.

## Founding precedent

The founding precedent is the Experiment 04 isotropic reconstruction result:

`R(32) = 0.241` observed versus `0.025` prospectively expected.

The `0.025` expectation was Allan Ochola's heuristic. The relevant integrity
invariants held, so the miss was not reclassified as a computational defect.
Freezing the heuristic before execution made the contradiction auditable
rather than convenient. Experiment 05 generalizes that precedent: invariant
failure can void a run; surprise cannot.
