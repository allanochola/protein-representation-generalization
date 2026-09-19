# Gate A Split, Firewall, and Execution Order

**Status:** structural rules frozen before A1 implementation or execution.

Gate A is divided because discovery family structure and confirmatory family
geometry have different firewall status.

## A1 — discovery-only family structure

A1 may access only the frozen 139 discovery-positive identities, their
discovery sequences, and prospectively frozen discovery annotation artifacts.
It reports:

1. number of family components;
2. full component-size distribution;
3. largest-family share;
4. singleton fraction;
5. `L`, as defined in `FAMILY_INDEPENDENCE_AUDIT.md`.

A1 has zero confirmatory contact. It alone determines the architecture fork.
The fork therefore cannot depend on confirmatory family geometry.

## A2 — confirmatory family geometry

A2 is a separately authorized metadata opening. It may report only the family
counts and component-size distributions required by the resolvability
simulator for the 161 confirmatory positives and 3,541 confirmatory negatives,
plus discovery-to-confirmatory family relationships under the same frozen
definition and code path.

A2 is not outcome access, but it is not information-theoretically blind.
Confirmatory family geometry provides weak information about confirmatory
difficulty. That leakage is necessary for Gate B resolvability and must be
declared in the authorization and completion record.

A2 cannot influence the A1 architecture fork, family definition, Layer-24
selection, comparator choice, estimand, or scientific thresholds.

## Frozen run order

`A1 -> B in parallel/independently -> A2 authorization -> C validation -> C surface`

- Comparator provenance audit B may begin alongside A1 because it is
  archaeology on Experiment 03 artifacts and does not require A1 or A2.
- A2 is ineligible until A1 has been executed, audited, and committed.
- Gate C cannot be executed before A2 because its clustered geometry is an A2
  output.
- The C resolvability surface remains unread until its three known-answer
  validations pass.

## Frozen A1 routing table

| `L` | Largest discovery-positive family share | Route |
|---:|---:|---|
| `>=0.25` | `<=0.15` | Two-stage: discovery-only family-blocked Stage 1, then confirmatory Stage 2 only under the frozen Stage-1 gate |
| `<0.25` | `<=0.15` | Skip Stage 1 as near-vacuous; direct preregistered confirmatory test, conditional on Gate C and all remaining gates |
| any | `>0.15` | Neither route; prospective amendment required before A1 may be rerun |

The third row is not a PASS or scientific FAIL. A dominant component makes the
blocking variance uninterpretable. Any replacement family definition or
modified blocking scheme must be written and frozen before a new A1 execution;
the observed first-run structure must remain permanently recorded.

## Family-definition requirements

Before A1 execution, one definition must be frozen with all of the following:

- computable from sequence plus frozen annotation only;
- no model, SAE, seed, fit, or performance contact;
- byte-identical family-construction function for A1 and A2;
- an equivalence-class output with transitive membership;
- explicit handling of missing and multiple annotations;
- canonical component serialization independent of row order;
- a chaining audit performed before `L` is interpreted.

Connected-component structure is reported before `L`. The largest-family
constraint is first a definition-validity test and only second a blocking-power
test.

## A1 execution discipline

A1 is deterministic, seedless, model-free, and expected to be cheap. Execution,
audit, and commit are separate steps; run-and-archive-in-one-cell is not used.

Pre-execution checks must establish:

- successful `ast.parse` of every A1 Python source;
- no import of model, ESM, SAE, or probe modules;
- no `SeedSequence` or other RNG construction;
- no model fit or score computation;
- no reachable confirmatory input path;
- output-schema rejection of any column containing, case-insensitively,
  `auroc`, `tpr`, `fpr`, `score`, or `threshold`.

The run emits a provenance JSON patterned on Phase E containing input SHA-256
values, family-definition identifier and hash, code hash, output hashes, and
the literal field `"confirmatory_accessed": false`.

The family definition and outputs are hashed together. Results cannot be
detached from the definition that produced them.
