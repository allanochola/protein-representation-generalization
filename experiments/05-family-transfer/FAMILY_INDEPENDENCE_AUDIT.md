# Family-Independence and Leakage Audit

**State:** candidate audit plan; the family definition is not yet frozen.

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
