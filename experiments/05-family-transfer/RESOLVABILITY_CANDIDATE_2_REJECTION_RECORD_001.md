# Candidate 2 instrument rejection record 001

Candidate 2 (paired hierarchical bootstrap) is rejected under its frozen validation rules. Both V1 cells and all six V2 cells failed. Existing archives and acceptance rules remain unchanged. No surface computation or Candidate 3 authorization is granted by this record.

## Verified evidence

All 35,000 outer replicates were independently checked for exact schedule membership and agreement with the final checkpoint. Per-replicate endpoint decisions, summary arithmetic, acceptance flags, output hashes and non-circular provenance were independently reproduced. Recorded V3 fixture invariants were checked; synthetic inference was not rerun. Zero inference failures were recorded.

| Allocation | Validation | Effect | Observed rate | Acceptance band | Result |
|---|---|---:|---:|---|---|
| dominant_to_calibration | V1 | 0 | 0.0204 | [0.030, 0.070] | FAIL |
| dominant_to_calibration | V2 | 0.05 | 0.9740 | [0.930, 0.970] | FAIL |
| dominant_to_calibration | V2 | 0.1 | 0.9780 | [0.930, 0.970] | FAIL |
| dominant_to_calibration | V2 | 0.2 | 0.9744 | [0.930, 0.970] | FAIL |
| dominant_to_evaluation | V1 | 0 | 0.0205 | [0.030, 0.070] | FAIL |
| dominant_to_evaluation | V2 | 0.05 | 0.9748 | [0.930, 0.970] | FAIL |
| dominant_to_evaluation | V2 | 0.1 | 0.9708 | [0.930, 0.970] | FAIL |
| dominant_to_evaluation | V2 | 0.2 | 0.9776 | [0.930, 0.970] | FAIL |

## Interpretation and limits

Candidate 2 has too few null rejections and coverage above the permitted range under the tested regimes. This is conservative behavior under these regimes, not a finding that the biological hypothesis failed or that the scientific effect is unresolvable.

The conservative direction is shared with the previously rejected Candidate 1. Candidate 1 used a paired family bootstrap with nested calibration refit; Candidate 2 added occurrence-level within-group resampling. They are related methods with shared code and assumptions, not independent implementations that identify the cause of conservatism. This comparison uses already exposed historical results; this cell independently rechecks Candidate 2 only.

Passing the recorded V3 invariants and recording zero inference failures do not exclude other implementation, generating-process or estimand mismatches. Neither placement comparison identifies the dominant negative group as the cause. Operational group counts and concentration are not effective sample sizes. Two rejected methods do not show that all bootstrap methods would fail.

## Standing decision and exposure

Both candidates remain rejected. Their intervals, endpoint conventions, seeds and replicate budgets will not be adjusted or rerun to seek acceptance. Endpoint equality remains non-rejection. The frozen two-sided validation bands remain binding.

The Candidate 2 rejection rates and coverage rates in this record have been exposed. A later specification must acknowledge that exposure. Rejection of these validation instruments does not establish lack of power. No resolvability surface was read or authorized here. Holdout sequence overlap and unverified historical reference-family separation retain their prior status; this record supplies no admissibility clearance.

Before any Candidate 3 implementation, a separately frozen, bounded synthetic-only diagnostic may examine whether the generating process, estimand and resampling scheme represent the same sources of variation, including whether within-family resampling adds uncertainty outside the intended target. This record does not implement or authorize that diagnostic. Any later model requires a statistical justification, not a desired interval width. The existing candidate-order rule is not changed.

## Execution and provenance

The final wrapper printed a stale 34,700-slot counter after archive publication. The independent audit verifies all 35,000 slots using checkpoint 405 and archive 406; the stale display does not change archived data.

- Authorized execution HEAD: `fb9e4a807d0444bed4f782909fad8b7f8cdc0c15`
- Audited archive commit: `fb0c5978276e814cf4dfe2c6be141f9dc3d58e6b`
- Closed experiment HEAD: `00315530e753143ae416ae3dac838450daba9d1c`
- Closed storage HEAD: `dd8a6f74e9fb05f8dc557e1a489f11b7bf5805cc`
- Archive export: 406; manifest SHA-256: `967f106e778447a1fd528d1a6ccd3f9bc70f72dadfc99f02de6bb376ff569736`
- Final checkpoint: 405; manifest SHA-256: `f18654f1e43de8a3c9111a33fd918d7daa3fb5982b83aa8d8ce74be1ed9564ec`
- Validation provenance SHA-256: `c4c5f2570c3e9b7ed01b28a2669ea72441af4315b91a078be3de16eb8594557e`
- Validation summary SHA-256: `192e5262ba3c06fa012c0a81a5e0eff44a5cd677d168c1c05862399cb1268e4a`
- Settings SHA-256: `7c4b62718b748282d3a1d777d4fa8bf57009d4beedf0ca9322500ec6698902c1`
- Confirmatory outcomes accessed by this operation: NO
- New simulation performed: NO
