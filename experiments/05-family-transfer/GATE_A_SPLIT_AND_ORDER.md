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
5. assigned-positive count and fraction;
6. unassigned-positive count and fraction;
7. `L`, as defined in `FAMILY_INDEPENDENCE_AUDIT.md`, with its explicit
   assigned-positive denominator.

A1 has zero confirmatory contact. It alone determines the architecture fork.
The fork therefore cannot depend on confirmatory family geometry.

## A2 — confirmatory family geometry

A2 is a separately authorized metadata opening. It may report only the family
counts and component-size distributions required by the resolvability
simulator for the 161 confirmatory positives and 3,541 confirmatory negatives,
plus discovery-to-confirmatory family relationships under the same frozen
definition and code path.

If A1 uses a fresh annotation snapshot, A2 must also re-evaluate whether the
161 positives remain family-disjoint and whether the negative universe remains
family-aware under that snapshot. “161 family-disjoint positives” is then a
claim to test, not an inherited premise. A2 must report attrition and
cross-partition bridges before Gate C receives any geometry.

A2 is not outcome access, but it is not information-theoretically blind.
Confirmatory family geometry provides weak information about confirmatory
difficulty. That leakage is necessary for Gate B resolvability and must be
declared in the authorization and completion record.

A2 cannot influence the A1 architecture fork, family definition, Layer-24
selection, comparator choice, estimand, or scientific thresholds.

## Frozen run order

`B scope -> A1 -> B build/freeze -> A2 authorization -> C validation -> C surface`

- Comparator B is a fresh discovery-only model build, not an audit of the
  historical 0.9494 model. Its scope is frozen before A1; its family-grouped
  construction follows A1 and must be frozen before A2.
- A2 is ineligible until A1 has been executed, audited, and committed and one
  fresh comparator has been fully frozen.
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
| any | any | `INCONCLUSIVE` if unassigned share exceeds 0.10; secondary grouping source required before the fork may be read |

The third row is not a PASS or scientific FAIL. A dominant component makes the
blocking variance uninterpretable. Any replacement family definition or
modified blocking scheme must be written and frozen before a new A1 execution;
the observed first-run structure must remain permanently recorded.

The unassigned rule is evaluated before the other rows. If it binds, neither
`L` nor family concentration may select an architecture route.

## Family-definition requirements

Before A1 execution, one definition must be frozen with all of the following:

- computable from sequence plus frozen annotation only;
- no model, SAE, seed, fit, or performance contact;
- byte-identical family-construction function for A1 and A2;
- an equivalence-class output with transitive membership;
- explicit handling of missing and multiple annotations;
- canonical component serialization independent of row order;
- a chaining audit performed before `L` is interpreted.

The frozen grouping rule is:

1. assign each protein directly from its own domain annotations;
2. use Pfam clan identity wherever its Pfam family belongs to a clan;
3. otherwise use the Pfam family identity;
4. do not aggregate annotations across MMseqs2 cluster members;
5. proteins with no assignable Pfam family are `UNASSIGNED`, not singleton
   families;
6. form connected components over proteins sharing at least one resulting
   clan-or-family identifier;
7. canonicalize every component and identifier list by lexical byte order.

The same pure construction function is used byte-identically by A1 and A2.
Its annotation inputs must pin both a UniProt release and a Pfam release,
including the Pfam family-to-clan mapping.

`L` is calculated among assigned discovery positives only:

`L = assigned positives with >=1 same-component neighbour / assigned positives`

The unassigned share uses all discovery positives as its denominator. A1 must
report assigned count/fraction, unassigned count/share, and the denominator
used for `L` as first-class routing outputs. Unassigned proteins are excluded
from both the numerator and denominator of `L`. Every A1 outcome record must
state that `L` is conditional on annotation assignment and therefore does not
describe the family structure of unassigned positives.

If the two-stage route is selected, `UNASSIGNED` discovery positives are
excluded from Stage 1 entirely: they enter neither family-blocked fitting nor
Stage-1 evaluation. They are not treated as singleton blocks, because missing
annotation does not establish independence, and they are not pooled into one
block, because missing annotation does not establish relatedness. The Stage-1
estimand and gate therefore apply to the annotation-assigned discovery-positive
subpopulation. The assigned fraction must accompany every Stage-1 result.

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

Clan-first grouping is not relaxed to family-only grouping if the 0.15
concentration rule fails. Such failure means this discovery set cannot support
the intended structural-family-blocked stage under the frozen definition; it
does not license a weaker biological-independence claim.

The two safeguards address distinct problems. Direct per-protein annotation,
rather than aggregation across MMseqs2 cluster members, removes the inherited
cluster-mediated chaining mechanism. Clan-first grouping is separately frozen
as the conservative biological holdout rule: it prevents closely related Pfam
families in the same clan from appearing independent. Both choices were made
before the census and neither may be relaxed in response to the observed `L`
or component concentration.
