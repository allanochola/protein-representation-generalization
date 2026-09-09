# Decoder Geometry Final Aggregation Completion

Status: **COMPLETE / POST HOC DESCRIPTIVE / CLOSED**

## Final artifact identity

Final aggregation artifact SHA-256:

`f9aae6b158e2d533b461c49b190be5c8a2201bec93109faeb6ccd9351afee8be`

Artifact size:

`33068` bytes

Durable private archive:

`ocholla/exp04-final-decoder-geometry-aggregation-private`

Private storage manifest SHA-256:

`74d5c20cdd946cc361f108f397085ef908aaae7cb16758427fc48cb861ce68d4`

The private Kaggle dataset was positively verified as private and was
independently redownloaded. The final aggregation artifact and storage
manifest were verified byte-identical to the local archived copies.

## Governing identities

Final aggregation specification SHA-256:

`54e4110acd3d38148e553d1cdb766fd8130bbb91355edd698678e4c159e69d55`

Authorized repaired aggregation driver SHA-256:

`1511449a535c7ad00c1c81638999ab66950c84dc52f0178898ad38e7dde01a1c`

Isotropic schema reconciliation note SHA-256:

`b5c15fe37427fd34d668778d6bffa2fae1c9aa36a7b3e726a5b08e9267e1268a`

Isotropic compatibility repair note SHA-256:

`aacd935ebd5728c7f20d00edcd0b3cfee5673bb5f7e66d8380dd4a1599ee9f53`

## Serialization-interface repair history

The first authorized final aggregation attempt terminated before final
summary construction because the historical isotropic checkpoints used a
uniform flattened serialization while the aggregation loader expected nested
`omp` and `raw_weight` dictionaries.

No final result artifact existed after that failed attempt.

The defect was diagnosed structurally before rerunning the aggregation.

The historical isotropic archive contained all required scientific values.
A deterministic in-memory compatibility mapping was frozen:

### OMP

- `status <- omp_status`
- `rank_deficient <- rank_deficient`
- `rank_deficiency_step <- rank_deficiency_step`
- `exact_reconstruction_step <- exact_reconstruction_step`
- `r_by_k <- r_by_k`
- `rank_by_k <- rank_by_k`
- `condition_by_k <- condition_by_k`

### Raw weight

- `status <- raw_weight_status`
- `topk_mass <- topk_mass`
- `n_eff <- n_eff`

The hard-disabled repaired loader was audited on all 1,000 isotropic records:

- loader acceptance: 1,000 / 1,000;
- unchanged geometry validator acceptance: 1,000 / 1,000;
- downstream extraction acceptance: 1,000 / 1,000;
- mapped scientific-field mismatches: 0.

The repair involved no numerical transformation, no geometry recomputation,
no new seed consumption, and no modification of historical isotropic archive
bytes.

The repaired driver was then authorized separately by changing only the hard
execution gate.

## Final population accounting

- biological: 100 total, 100 geometry-eligible, 0 zero-beta;
- canonical permutation null: 100 total, 63 geometry-eligible, 37 zero-beta;
- C-matched permutation null: 100 total, 100 geometry-eligible, 0 zero-beta;
- isotropic geometric reference: 1,000.

The canonical permutation null remains the protocol-designated primary
comparison.

The C-matched null remains a secondary marginal realized-C-distribution
control.

The isotropic population remains a geometric reference.

## Bootstrap contract

- root seed: `2026090801`;
- bootstrap replicates: `10000`;
- bootstrap streams: 30.

No p-values were computed.

No PASS/FAIL verdict was computed.

## Headline decoder-geometry results

At `k = 32`, median OMP reconstruction fraction was:

- biological: `0.2568045461`;
- canonical eligible null: `0.2566901081`;
- C-matched null: `0.2432864945`;
- isotropic: `0.2412492356`.

Descriptive median differences:

- biological minus canonical eligible null:
  `+0.0001144379`;

- biological minus C-matched null:
  `+0.0135180515`,
  bootstrap interval
  `[+0.0100490271, +0.0155969950]`;

- biological minus isotropic:
  `+0.0155553105`,
  bootstrap interval
  `[+0.0129991655, +0.0161949639]`.

Median top-32 raw decoder-weight mass:

- biological: `0.0286990090`;
- C-matched null: `0.0261725974`;
- isotropic: `0.0254392044`.

Median effective decoder-weight support (`N_eff`):

- biological: `6373.6714`;
- C-matched null: `6393.9102`;
- isotropic: `6451.5808`.

## Reconstruction scale

For all 100 biological probe directions:

- 50% reconstruction required more than 64 atoms and was reached by 128;
- 80% reconstruction required more than 128 atoms and was reached by 256;
- 90% reconstruction required more than 256 atoms and was reached by 512.

No geometry-eligible biological, canonical-null, C-matched, or isotropic
direction was rank deficient over the frozen grid.

## Scientific interpretation

The bounded descriptive interpretation is:

**Toxin-related information is strongly linearly accessible in raw ESM-2
representations but only weakly concentrated in the tested SAE decoder
basis. Biological supervised directions show modest preferential decoder
alignment relative to the C-matched permutation control and isotropic
directions, while remaining highly distributed across the SAE dictionary.**

This supports a picture of:

**linear accessibility with weak decoder-basis concentration rather than
compact sparse decomposition.**

The result does not establish:

- a causal toxin mechanism;
- unique toxin specificity;
- toxin neurons;
- uniquely interpretable toxin features;
- cross-family toxin generalization;
- that the SAE fails to span the biological direction;
- that SAE basis choice uniquely explains the Experiment 03 failure;
- a confirmatory statistical verdict.

## Canonical-null qualification

The canonical eligible-null median `R(32)` is nearly identical to the
biological median.

This result is retained transparently.

Because 37 of 100 canonical-null probes are exact zero-beta cases, those cases
do not possess a coefficient direction and therefore cannot enter the
direction-geometry comparison. The 63-member canonical eligible subset is
therefore selection-conditioned on having a nonzero sparse probe.

The separately frozen C-matched control provides complementary descriptive
evidence without replacing the canonical null as the protocol-designated
primary comparison.

## Relation to Experiments 03 and 04

Experiment 03 found that the frozen SAE instrument did not recover a compact,
stable feature set under its preregistered stability criteria.

Experiment 04 established that toxin-related information was nevertheless
strongly linearly accessible in raw ESM-2 representations.

This decoder-geometry follow-up shows that those supervised biological
directions have modest preferential alignment with the tested SAE decoder
basis, but the alignment remains distributed rather than compact.

## Closure

The final aggregation artifact is durably archived and byte-verified.

The private archive was positively verified as private.

The repaired aggregation driver is restored to its exact hard-disabled state
at closure.

No confirmatory data were accessed.

No further Experiment 04 decoder-geometry computation is authorized by this
closure.

Any additional scientific question belongs in a new experiment.
