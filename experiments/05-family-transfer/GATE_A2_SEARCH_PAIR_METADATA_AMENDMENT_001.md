# A2 targeted search pair-metadata amendment 001

Status: frozen while disabled, before any targeted sequence search.

The 687 selected pairs, 687 negative queries, nine positive targets and both
canonical search FASTAs remain byte-identical in membership and sequence.
Only selected_pairs.tsv gains negative_length, positive_length and
shorter_sequence (negative, positive, equal). Lengths are computed from the
same hash-verified sequences submitted to search. Length asymmetry does not
establish alignment validity.

The command remains negative-query to positive-target, --cov-mode 1 -c 0.80.
Coverage applies to the positive target irrespective of which sequence is
shorter. Qualification after independent archival requires a returned
fident >= 0.30. All returned rows, including off-cluster and subthreshold
rows, are retained. Mere row presence is not the classification rule.

Execution provenance now states: absence of a qualifying hit means not
detected by this targeted diagnostic. It does not disprove an alignment or
establish what the historical filter would have done. Historical executable
identity and cleaned_precursor.fasta bytes have not been recovered from
inspected evidence; the target-database scope also differs.

The old snapshot remains preserved in Git history. Its SHA-256 is
52de732844f3b3f95db6ef4812c677793cfbecd96079dd6d8d5237566ff27ed5.
The revised snapshot records the new selected-pair hash and unchanged FASTA
hashes. This amendment authorizes no search, classification or model scoring.
