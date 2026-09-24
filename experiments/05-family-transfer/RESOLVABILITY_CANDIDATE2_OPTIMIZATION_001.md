# Candidate 2 optimization 001

Status: disabled implementation optimization. No method, draw, budget, endpoint,
acceptance, allocation or random-stream change. Production validation has not run.

Profile evidence: archive e9167f9a35254b80605ecd8881682abf389c6bca exposed repeated
small-array construction in evaluate_draw. Replace per-stratum numpy.full arrays
with one count matrix, repeat of occurrence IDs, and repeat of positive/negative
flags. Keep record order and dtypes identical. draw_hierarchy and every other
core definition are AST-identical to the preserved reference. No RNG calls move.

The original core and implementation snapshot are retained byte-for-byte.
The active implementation snapshot is updated while all gates are false, with
new hashes and this record. Previous timing and profiling archives continue to
refer to the old snapshot; they are not rewritten or claimed to time this version.

The equivalence audit uses fabricated singleton, unequal-sized and mixed-label
strata, tied scores and identical arms. It compares sampled indices, constructed
arrays, every evaluated rate/threshold, complete intervals/output dictionaries,
and final RNG state exactly, including floating-point bit representation.
It also checks matching missing-label failures and different inference batches.
These finite tests support the narrowly scoped rewrite, not equivalence for every
possible input. No runtime improvement is claimed before a new authorized benchmark.

Existing Candidate 2 synthetic audits run again while disabled. No scientific
validation, surface, production geometry, protected outcome or rebenchmark is
executed by this installation. A durable production checkpoint destination is
still not configured. Old profiling snapshot pins intentionally remain historical.
