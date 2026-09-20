# Gate A2-C joint family-geometry specification 001

Status: frozen specification and disabled implementation. Execution requires a
separate authorization commit. No family geometry was used to choose these rules.

## Scope and firewall

Use only the immutable joint A2-SS archive at
978b9be0df7c909c18d606774074b692090a0cec: 278 discovery records and
3,702 confirmatory records. All identifiers retain their universe namespace.
Every input must match its original Git blob and recorded SHA-256 before use.
No network, sequence retrieval, scanner, feature extraction, model fitting,
prediction, performance metric or Gate C simulation is permitted in this phase.

Confirmatory family geometry is acknowledged information about test difficulty.
It is opened for provenance/disjointness checking and later simulator inputs,
not for representation, comparator or threshold selection. Outcomes remain sealed.

## Equivalence classes

Retain every joint sequence cluster exactly as archived. For every accepted Pfam
hit, strip only the accession version suffix, map to its clan when nonempty, and
otherwise retain that Pfam family accession. A family absent from the pinned
Pfam mapping is an integrity error, not an unassigned protein. A protein with
no accepted hit has no Pfam relationships but retains its sequence cluster.
Use all accepted domains, without selecting a best domain. Duplicate domain hits
do not multiply membership. Distinct proteins sharing a clan/family token or a
sequence cluster are related. Take full transitive closure of both sources over
all 3,980 records, retaining mixed labels and universes. Never split or drop a
component to restore disjointness. Component ID is SHA-256 of LF-joined sorted
namespaced member identifiers, without a final LF.

## Reports and exact denominators

Assignments identify each record's joint component, class, universe, and Pfam
tokens. Component membership is exported in full for Gate C; no independent-unit
claim is made solely from the count of operational groups.

Report component intersections separately for all discovery, discovery positives,
discovery negatives, all confirmatory, confirmatory positives, and confirmatory
negatives. For each population report record count, number of joint components
bearing at least one member, full intersection-size distribution, largest
intersection count/share, singleton intersection count, and Pfam assignment
coverage. The concentration denominator is the number of records in that
population. In particular 3,541 negatives are not treated as 3,541 independent
threshold-setting units. Components are computed jointly before intersections;
paths through another population can join its members.

Report three separate disjointness checks: whether confirmatory positives occupy
distinct joint components; whether any share a component with discovery positives;
and whether any share a component with any discovery record. Report exact duplicate
sequence relationships across universes from the frozen mapping's sequence hashes.
Report these as fresh operational checks, not proof of historical filter failure.

Cross-label Pfam counts refer to unordered distinct-protein pairs sharing a Pfam
clan/family token. Report pair-token incidences and unique pairs separately, for
discovery-only, confirmatory-only and cross-universe pairs. These are direct Pfam
relationships, not sequence-search hits or evidence of mislabeling. The same pair
sharing multiple tokens counts once in unique pairs. Archive the Pfam token
membership table so counts are independently reconstructible. Do not compute or
interpret toxin mechanism, potency or hazard from these relationships.

Historical annotation_status remains a historical claim. Preserve the already
committed historical_annotation_claims.tsv with its hash and original path in
provenance; do not use it to assign current families or claim that annotation
status itself proves family disjointness. No historical annotation is rewritten.

## Result handling

Integrity failure produces no published geometry archive and requires the usual
disable/repair/audit/separate-authorization sequence. Scientifically inconvenient
geometry is retained unchanged. This phase has no new numerical eligibility gate
and does not authorize population filtering, resampling, threshold changes, model
changes, confirmatory evaluation or Gate C. Overlap or concentration findings must
be recorded and interpreted against the North Star before subsequent authorization.

## Execution and archival

Use a same-filesystem staging directory and refuse existing output. Output is
assignments.tsv, components.tsv, pfam_memberships.tsv, summary.json and
geometry_provenance.json. Provenance binds input hashes, this definition, runner
hash, Git HEAD and non-circular derived-output hashes. Execute, independently audit,
commit/push, and close in separate steps. No geometry is printed by the runner.
