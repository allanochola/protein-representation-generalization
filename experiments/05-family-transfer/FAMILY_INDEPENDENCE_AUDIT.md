# Family-Independence and Leakage Audit

**State:** candidate audit plan. The `L` and family-concentration thresholds
are frozen; the biological-family definition is not yet frozen.

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

## Candidate definitions to census

The census should compare a small prespecified ladder rather than search for a
definition that improves performance:

- **D1:** sequence clusters only;
- **D2:** sequence clusters plus curated functional-family links;
- **D3:** D2 plus Pfam family/clan links;
- **D4:** D3 plus a prespecified remote-homology method.

For each definition report positive and negative component counts, component
size concentration, singleton share, cross-label components, and the largest
component share. Do not report model performance.

The final definition should be the least restrictive one that supports the
claim being made while closing known leakage routes. It must not be selected
to maximize usable sample size without accounting for biological leakage.

## Leakage tests before partition freeze

- exact sequence and accession overlap;
- component overlap across partitions;
- positive/negative collision within components;
- shared Pfam families/clans across protected and development partitions;
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

Define `L` as the fraction of discovery positives that have at least one
same-family positive neighbour whose removal distinguishes family blocking from
an unblocked split. Positives in singleton families do not contribute to `L`
because blocking cannot change their training-neighbour status.

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

The census must report `L`, largest-family share, and singleton fraction
regardless of the gate outcome.

- If `L >= 0.25` and the largest-family condition passes, the blocking stage is
  eligible, subject to all other Phase-0 gates.
- If `L < 0.25`, the blocking stage is classified as near-vacuous and is not
  run. Experiment 05 may proceed directly to its preregistered confirmatory
  test only if the comparator and resolvability instruments pass and all other
  gates authorize the spend.
- If the largest-family condition fails, Gate A does not pass merely because
  `L` is large. The concentration problem must be closed or the design must be
  redesigned before protected computation.
