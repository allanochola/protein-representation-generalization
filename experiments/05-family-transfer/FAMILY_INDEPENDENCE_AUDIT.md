# Family-Independence and Leakage Audit

**State:** Phase-0 audit plan. The `L`, assignment-coverage, and
family-concentration thresholds and the primary biological-family definition
are frozen; the executable A1 implementation and annotation-release pin remain
to be frozen.

## Principle

A sequence-identity cluster is one edge type, not a complete biological-family
definition. Evaluation claims must name the relationships actually excluded.

## Candidate relationship graph

Each protein is a node. Candidate edges should be constructed independently of
model performance from the following evidence layers:

1. sequence similarity at prespecified identity, coverage, and sensitivity;
2. remote-homology evidence from profile/profile or profile/sequence methods;
3. shared Pfam domain families and, where justified, clans;
4. curated toxin family or functional-family annotations;
5. defensible higher-order functional-neighborhood links.

Connected components under the frozen edge rule become indivisible allocation
units. Edge provenance and the rule that generated every edge must be retained.

## Frozen primary definition

The earlier D1-D4 ladder is superseded for the primary A1 fork. A1 uses the
clan-first, family-fallback, per-protein connected-component definition frozen
in `GATE_A_SPLIT_AND_ORDER.md`.

Alternative definitions are not computed beside the primary census. Doing so
would create a result-dependent menu for a later amendment. If the frozen
definition is invalidated by concentration or missingness, its result remains
recorded and any successor requires a prospective amendment before execution.

## Leakage tests before partition freeze

- exact sequence and accession overlap;
- component overlap across partitions;
- positive/negative collision within components;
- shared clan-first/family-fallback components across protected and
  development partitions;
- remote-homology bridges under the frozen rule;
- duplicated source records or isoforms split across partitions;
- feature construction using corpus statistics from protected sequences;
- taxonomy, length, or annotation-source imbalance capable of acting as a
  trivial shortcut.

Taxonomy and length imbalance should be measured for audit, not automatically
matched away. Any matching changes the target population and must be justified
before partitioning.

## Allocation constraint

Partition allocation occurs at the frozen connected-component level and should
be deterministic from a committed seed. No component may be split to satisfy
protein-count targets.

If the strictest scientifically defensible graph collapses the universe into
too few independent units, Gate A fails. The response is not to silently drop
edge types.

## Frozen blocking-power threshold

Define `L` among assigned discovery positives as the fraction that have at
least one same-component positive neighbour whose removal distinguishes family
blocking from an unblocked split. Positives in assigned singleton families do
not contribute to the numerator because blocking cannot change their
training-neighbour status. `UNASSIGNED` positives are excluded from both the
numerator and denominator and are governed by a separate missing-family gate.

The threshold is frozen before the census:

`L_min = 0.25`

Derivation uses only the public Experiment 04 discovery AUROCs. The largest
available raw-ESM versus 21-D-baseline contrast was approximately
`0.965 - 0.587 = 0.378`. Even if every family-supported positive lost the full
available contrast under blocking, an AUROC drop of 0.05 would require
`L >= 0.05 / 0.378 = 0.132`. Under a more plausible half-collapse, it would
require `L >= 0.264`. The frozen 0.25 threshold represents that partial-collapse
regime without adapting to the observed census.

`L` is necessary but not sufficient. The second frozen condition is:

`largest discovery-positive family share <= 0.15`

The frozen missing-family condition is:

`UNASSIGNED discovery-positive share <= 0.10`

The census must report `L`, its assigned-positive denominator, assigned count
and fraction, largest-component share, assigned-singleton fraction, and
unassigned count/share regardless of the gate outcome. Assigned fraction is a
first-class routing output rather than a descriptive footnote: `L` is
conditional on assignment, so identical values of `L` at materially different
coverage do not support the same blocking claim. Every outcome record must say
that the frozen `L_min` derivation assumed broad positive-set coverage and is
being applied only to the reported assigned subpopulation. Connected-component
structure is validated before `L` is interpreted.

- If `L >= 0.25` and the largest-family condition passes, the blocking stage is
  eligible, subject to all other Phase-0 gates.
- If `L < 0.25`, the blocking stage is classified as near-vacuous and is not
  run. Experiment 05 may proceed directly to its preregistered confirmatory
  test only if the comparator and resolvability instruments pass and all other
  gates authorize the spend.
- If the largest-family condition fails, Gate A does not pass merely because
  `L` is large. The concentration problem must be closed or the design must be
  redesigned before protected computation.
- If unassigned share exceeds 0.10, A1 returns `INCONCLUSIVE`; the architecture
  fork remains unread and a prospectively frozen secondary grouping source is
  required.

If Stage 1 is authorized, `UNASSIGNED` discovery positives are dropped from
Stage 1 rather than represented as singleton blocks or one pooled block. They
participate in neither Stage-1 model fitting nor Stage-1 evaluation. This
avoids asserting either independence or relatedness where the frozen annotation
provides neither. The resulting Stage-1 claim is explicitly limited to assigned
discovery positives, and its reported result must include the assigned fraction.

The complete routing table, A1/A2 firewall, chaining audit, and execution
discipline are frozen in `GATE_A_SPLIT_AND_ORDER.md`.
