# A2 targeted-search semantics correction 001

Status: prospective correction and disabled diagnostic preparation. No search executed.

The pinned MMseqs2 source implements cov-mode 1 as target alignment coverage.
For the historical negative-query/positive-target command, -c 0.80 therefore
requires coverage of the positive target. Earlier descriptions of mode 1 as
shorter-sequence coverage in A1-M, Gate B and A2-SS records are superseded by this
interpretation. Numerical command arguments and immutable archives are unchanged.
Mode 5 is a sequence-length-ratio condition, not an equivalent alignment-coverage rule.

Historical 06b explicitly passed -e 1e-3 and --alignment-mode 3. The prior
statement that no explicit E-value was present is withdrawn. Other defaults
and search-database context remain relevant; this diagnostic is not a replay.

Cascaded cluster membership does not certify direct qualifying pairwise
alignments. The 475 representative-involving selected pairs are structural
relations only. Omission of --cluster-reassign alone does not prove the effective
setting; no claim about that run setting is required for this diagnostic.

Historical Pfam family disjointness was against non-divergent, non-burned
reference clusters, not mutual disjointness among the 161 confirmatory positives.
The 45 records and 49 current within-confirmatory family-sharing pairs do not
establish a historical criterion violation. Historical reference membership and
execution provenance have not been recovered from the inspected evidence.

The historical target was cleaned_precursor.fasta. This diagnostic uses committed
A2 recovered sequences and a nine-positive target database. Sequence preparation,
target scope, executable identity and remaining defaults prevent attribution of
any diagnostic hit to historical filter leakage without further evidence.

Retain all returned query,target,fident rows, including off-cluster hits. After
independent archival, classify selected pairs by returned fident >= 0.30.
No qualifying returned row means NO_QUALIFYING_ALIGNMENT_DETECTED_UNDER_DIAGNOSTIC;
a qualifying row means QUALIFYING_ALIGNMENT_DETECTED_UNDER_DIAGNOSTIC.
Malformed output or command failure is EXECUTION_OR_PROVENANCE_UNRESOLVED.
No universe edits, model loading, performance measurements or Gate C authorization.

Build identity, exact input hashes and arguments are in the companion snapshot.
Rebuilt binary hashes identify this session only. Search remains hard-disabled;
authorization requires a separate gate-only commit and remote verification.
