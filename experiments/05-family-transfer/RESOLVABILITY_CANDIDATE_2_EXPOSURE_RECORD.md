# Candidate 2 prior-exposure record

This record is frozen alongside Candidate 2, before its implementation or results.
The change is prospective with respect to Candidate 2; it is not blind to Candidate 1.
Git commits are atomic: this record and the specification share one commit.

## Evidence already seen

Candidate 1 failed V1 in both allocations: 270/10000 and 291/10000 null
rejections against [0.030,0.070]. All six V2 cells and all V3 fixtures passed.
Zero inference failures were recorded. Candidate 1 remains rejected.

The descriptive archive exposed validation median half-widths of approximately
0.121-0.132 at effects +0.05,+0.10,+0.20, including approximately 0.1294 at
+0.10, and these have been compared with the formal Gate B target <=0.10.
They are validation reports from a rejected method, not an authorized
resolvability surface or a scientific Gate B decision.

A comparison of mean null half-width with 1.96 times the empirical standard
deviation was described as approximately 4-5% excess width. This is a normal-
approximation comparison, not a validated estimate of excess interval width,
not a causal decomposition, and not a target for narrowing Candidate 2.

There were 65/10000 and 64/10000 intervals touching zero. Counting those as
rejections would give 335/10000 and 355/10000. This counterfactual arithmetic
has been seen. It does not justify changing the endpoint convention or prove
that it alone caused failure. The frozen non-rejection at equality remains.

Near-zero average bias and interval-center displacement, approximately matching
marginal threshold standard deviations, and width/threshold-uncertainty
correlations have also been seen. They do not certify the nested procedure or
exclude an implementation defect. No alternative interval was computed.

## Consequences

Candidate 2 is not targeted to a 5% width reduction or to a passing endpoint
count. Its rationale is a declared two-level sampling interpretation. It may
produce wider intervals or fail the same validation. No improvement is promised.
No observed Candidate 1 result is used as a numerical correction or calibration
constant. No empirical confirmatory outcomes or resolvability surface were seen.
