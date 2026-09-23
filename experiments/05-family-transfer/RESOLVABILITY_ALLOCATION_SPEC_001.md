# Formal Gate B: resolvability allocation specification 001

Status: prospective operational allocation rule; execution disabled.
This metadata-only instrument precedes statistical simulator specification.
It does not run V1-V3, estimate power, certify independence or authorize scoring.

## Population and operational unit

Use the immutable joint sequence partition from A2-SS. Its identifiers are hashes
of full joint member sets; retain those identifiers when restricting to the
3,702 confirmatory records (161 positive, 3,541 negative). All confirmatory
members of each joint sequence cluster remain together, including mixed labels.
No Pfam/clan edges are added. These are operational groups, not certified
independent biological families or effective sample sizes.

Discovery records are not assigned to calibration or evaluation. Their presence
in a joint group is recorded as discovery overlap. No overlapping group is
removed, renamed, split or declared independent of development.

## Two fixed diagnostic scenarios

Define the dominant group as the confirmatory-negative-bearing group with the
largest negative intersection count; break ties by ascending stable cluster ID.
The previously reported 469 negatives describe this intersection, not full group
membership. Its mixed-label confirmatory members travel together.

- dominant_to_calibration: place that entire confirmatory group in calibration.
- dominant_to_evaluation: place that entire confirmatory group in evaluation.

For each scenario independently, order all remaining negative-bearing groups by
descending confirmatory negative count, then ascending stable cluster ID. Assign
next to the side currently holding fewer negative records; ties go to calibration.
This aims to balance negative record counts around 50:50; it does not guarantee
balance of records, groups, classes or independence. There is no seed or search.

After that pass, put every positive-only group in evaluation. Calibration positives
arise only from mixed-label groups placed in calibration. They are unavailable
for evaluation and must not be used for fitting, selection or threshold estimation.
Calibration thresholds will use calibration negatives only. The numerical threshold
rule and paired interval method remain to be frozen with the simulator specification.

## Reports and deterministic identities

Archive per-record assignments for both scenarios, per-group allocations and
label counts, and summaries by side/class. Report record counts, bearing-group
counts, intersection-size distributions, largest intersection shares, singleton
intersections, mixed-group counts, and overlap with discovery. Empty-population
shares are null. Check all records appear exactly once in each scenario and no
group crosses sides. Report missing-label support as a diagnostic condition;
never repair an allocation by trying another rule.

Both scenarios must be reported. Neither may be selected after simulation for
favorable performance. They are a prespecified placement-sensitivity pair, not
an exhaustive set of realistic allocations. The later statistical specification
must define how they inform conclusions before any resolvability surface access.

## Scientific boundaries

Formal Gate B targets >=80% power at DeltaTPR=+0.10 and median interval half-width
<=0.10 under the inherited validation requirements. This instrument does not
calculate or adjudicate those targets. It does not estimate a 5% FPR threshold
or derive quantile resolution before the threshold and weighting rules are frozen.

A favorable future precision diagnostic cannot clear exact-sequence holdout
overlap or verify historical family separation. Confirmatory performance remains
sealed. No model, embedding, SAE, predictions, scores or outcomes are read.

## Execution discipline

Freeze this specification and runner while disabled. Authorize through a separate
AST-verified gate-only commit and remote verification. Execute once, independently
audit outputs, commit/push the archive, then close authorization. An existing
archive blocks reruns. This authorization never extends to a simulator.
