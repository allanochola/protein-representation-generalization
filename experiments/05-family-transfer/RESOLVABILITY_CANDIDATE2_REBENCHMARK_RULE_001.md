# Candidate 2 rebenchmark and execution-planning rule 001

Freeze before rebenchmarking. The optimized core and statistical settings stay
unchanged. Use the original two fabricated fixtures, four timing repeats each,
999 bootstraps per outer dataset. No production geometry is loaded. Profile
instrumentation is absent. Report each fixture separately; these fixtures do not
isolate the causal effects of group and record count.

Validation serial planning time = 35000 times the slower fixture median runtime.
Reserve 25% additional time for variability, checkpointing and archival. Surface
planning time uses 120000 outer datasets and the same margin. These are planning
estimates, not guarantees. The runner is serial; available CPUs do not imply
parallel execution.

If the headroom-adjusted validation estimate fits a verified remaining session
allowance, a single-session plan may be considered. Otherwise use a multi-session
plan. Without a verified allowance the single-session route remains undetermined.
Durable checkpoint backup is required for EITHER route and is not configured by
this cell. Before multi-session production, demonstrate interrupted/restored
execution using actual synthetic inference, not just stub outer rows, preserving
output and RNG identity. No real confirmatory outcomes may be used for this test.

No further optimization is triggered solely by disappointing timing. No changes
to the method, RNG order, budgets, endpoint convention or validation acceptance
criteria are authorized. This cell does not authorize validation or surface use.

The original benchmark/profile archives remain immutable. The new runner and
output directory are separate. Sequence: freeze, isolated gate authorization,
one execution, independent schema/provenance/timing-arithmetic audit, archival,
then gate closure. On failure stop without automatic retry.
