# Experiment 03 — biological SAE stability-sweep specification

**Status:** PRE-MODEL / FROZEN BEFORE FIRST EXPERIMENT-03 ESM OR SAE ACTIVATION

## 1. Purpose

Stage 1 asks whether the frozen discovery partition contains a reproducible,
compact set of SAE features associated with toxin-positive versus burned
family-aware negative proteins.

This stage is discovery only.

It may nominate a stable feature set for later confirmatory evaluation, but
it may not inspect or use any confirmatory representation statistic.

## 2. Model

### Protein language model

Frozen PLM:

`esm2_t33_650M_UR50D`

Frozen representation layer:

`18`

Layer 18 is selected before biological activation inspection as the nearest
available InterPLM 650M SAE layer to the previously used mid-model
representation regime.

No sweep over ESM layers is permitted.

### Sparse autoencoder

Frozen SAE source:

`Elana/InterPLM-esm2-650m`

Frozen SAE layer:

`layer_18`

Frozen weight variant:

`ae_normalized.pt`

Expected ESM input dimension:

`1280`

Expected SAE feature dimension:

`10240`

No sweep over SAE layers, SAE sizes, normalized versus unnormalized weights,
or alternative SAE checkpoints is permitted.

## 3. Model provenance gate

Before any Experiment-03 biological activation is computed, the implementation
must record:

- resolved ESM checkpoint identifier;
- InterPLM package/source revision;
- resolved Hugging Face revision for `Elana/InterPLM-esm2-650m`;
- SHA-256 of the downloaded `layer_18/ae_normalized.pt`;
- Python version;
- PyTorch version;
- transformers / fair-esm version as applicable;
- InterPLM version or Git commit;
- CUDA version;
- device name.

The resolved external revision and file hash are provenance records, not
model-selection variables.

If the downloaded model cannot be uniquely hashed or its architecture does
not match 1280 input dimensions and 10240 SAE features, model contact stops.

## 4. Discovery membership

The biological sweep uses only the already frozen realized discovery sets in:

`stage1_model_blind/realized_partition/`

Primary discovery set:

- 139 toxin-positive proteins;
- 139 permanently burned family-aware negatives.

Nested descriptive subsets:

- N=100 per class;
- N=120 per class;
- N=139 per class.

The memberships and hashes already frozen in
`realized_partition_snapshot.json` are authoritative.

No replacement, supplementation, or rebalancing is allowed after activation
inspection.

## 5. Confirmatory firewall

The following remain completely inaccessible during Stage 1 feature
nomination and stability analysis:

- 161 confirmatory V2-B positive clusters;
- 3,541 confirmatory family-aware negatives.

They may not be:

- embedded;
- passed through the SAE;
- scored on nominated features;
- used for threshold selection;
- used for sign selection;
- used for pooling choice;
- used for feature-set size selection;
- used for debugging numerical output;
- used to decide whether Stage 1 succeeded.

Only identifiers needed to verify exclusion are permitted before the
confirmatory stage.

## 6. Sequence eligibility

Every discovery sequence must satisfy the frozen ESM compatibility rule:

`1 <= biological sequence length <= 1022`

No truncation is permitted.

A sequence that exceeds the limit, cannot be recovered exactly, contains an
unresolved identifier, or differs from the frozen discovery membership causes
a hard stop before feature scoring.

## 7. Residue handling

ESM and SAE representations are computed at residue resolution.

Only positions corresponding to biological amino-acid residues are included.

The following are excluded:

- BOS / CLS;
- EOS;
- padding;
- any framework-specific special token.

No sliding windows are permitted because all Stage-1 discovery sequences
satisfy the <=1022-residue eligibility rule.

## 8. Protein-level SAE representation

Let:

`a[p, r, j]`

be the normalized SAE activation for protein p, biological residue r, and
latent j.

For each protein p and latent j, define the frozen protein-level score:

`z[p, j] = max_r a[p, r, j]`

where the maximum is taken only over biological residue positions.

Thus every protein is represented by one 10,240-dimensional vector.

The max aggregation is fixed before biological activation inspection.

No alternative mean, median, top-q, sum, fraction-active, or attention-weighted
pooling is permitted in the primary analysis.

Rationale: toxin-associated functional signatures may be localized in
sequence; max pooling asks whether a feature is strongly present anywhere in
the protein.

## 9. Signed discovery score

For every SAE latent j:

`d[j] = mean_positive(z[:,j]) - mean_negative(z[:,j])`

Primary ranking score:

`abs(d[j])`

Signed feature identity is:

- `(j, +)` when `d[j] >= 0`;
- `(j, -)` when `d[j] < 0`.

Ties are broken by lower latent index.

No labels beyond discovery positive versus discovery negative are used.

## 10. Full-dataset nomination

On the complete N=139 discovery set:

1. compute `d[j]` for all 10,240 latents;
2. rank by descending `abs(d[j])`;
3. take the top five signed latent identities.

Frozen feature-set size:

`k = 5`

No k sweep is permitted.

The complete N=139 top-five set is the nominated biological discovery feature
set whose stability is evaluated.

## 11. Perturbation procedure

For each N in:

`{100, 120, 139}`

use exactly 100 perturbations.

The perturbation mechanism mirrors the independently validated synthetic
instrument.

For perturbation index b:

- sample floor(0.80 * N) positives without replacement;
- sample floor(0.80 * N) negatives without replacement;
- positive and negative sampling are independent;
- sampling uses NumPy `default_rng`;
- no confirmatory protein can enter a perturbation.

Frozen biological perturbation seed:

`20_000_000 + 100_000 * N + perturbation_index`

where:

`perturbation_index = 0,...,99`

The seed namespace is distinct from all synthetic calibration and validation
seed namespaces.

The realized discovery set is already class-balanced and target-length
matched. Perturbations are therefore not re-stratified.

Length-stratum counts for each perturbation must nevertheless be reported
descriptively to expose accidental composition drift.

No perturbation may be discarded or regenerated because of its result.

## 12. Perturbation feature sets

Within every perturbation:

1. compute the signed mean-difference score for every latent;
2. rank by descending absolute score;
3. select the top five signed latent identities.

The same tie-breaking rule is used as for the complete discovery set.

## 13. Frozen three-way stability instrument

The biological N=139 feature-set instrument is exactly the independently
validated synthetic instrument.

### 13.1 Pairwise Jaccard

For every pair of perturbation top-five signed feature sets A and B:

`J(A,B) = |A intersect B| / |A union B|`

Primary statistic:

`median_pairwise_jaccard`

Jaccard gate:

`median_pairwise_jaccard >= 0.60`

### 13.2 Full-set feature recurrence

For each of the five signed features nominated on the complete N=139 dataset,
compute:

`inclusion_frequency =
    number of perturbation top-five sets containing the signed feature / 100`

A nominated signed feature is recurrent when:

`inclusion_frequency >= 0.80`

Recurrence gate:

`at least 4 of the 5 full-dataset nominated signed features are recurrent`

### 13.3 Fixed-identity concentration

Let S5 be the five latent identities nominated on the complete N=139 dataset.

For perturbation b, let:

`d_b[j]`

be its signed mean-difference score.

Define:

`mass_b[j] = abs(d_b[j])`

and:

`concentration_b =
    sum_{j in S5} mass_b[j]
    /
    sum_{j=1..10240} mass_b[j]`

The identities in S5 are fixed from the complete discovery dataset and are
not reselected for the concentration numerator.

Primary statistic:

`median_fixed_top5_concentration`

Frozen concentration threshold:

`>= 0.35`

### 13.4 Final Stage-1 stability decision

The N=139 biological discovery feature set is declared STABLE only if ALL
three hold:

1. median pairwise Jaccard >= 0.60;
2. at least 4 of 5 nominated signed features recur in >=80% of perturbations;
3. median fixed-top5 concentration >= 0.35.

This is a three-way AND.

No component may be dropped or replaced after biological results are visible.

## 14. Role of N=100 and N=120

N=100 and N=120 are descriptive stability-support analyses only.

For each, report:

- top-five signed feature set;
- median pairwise Jaccard;
- recurrence frequencies;
- number of recurrent nominated features;
- median fixed-top5 concentration;
- overlap with the N=139 nominated set;
- length-stratum composition across perturbations.

The primary Stage-1 decision is made only at N=139.

No plateau threshold is introduced.

N=100 or N=120 cannot rescue a failed N=139 gate.

## 15. Single-feature statistics

For continuity with the synthetic calibration work, report descriptively:

- modal top-1 signed latent;
- modal top-1 frequency;
- pairwise top-1 agreement.

However, the previously proposed single-feature verdict gate remained
formally uncalibrated.

Therefore:

- no single-feature PASS/FAIL verdict is permitted;
- no post-model top-1 threshold may be introduced;
- a visually dominant single latent cannot replace the frozen k=5 decision
  rule.

## 16. Length-exhaustion limitation

The N=139 discovery-positive pool exhausts the available `>150` discovery
stratum.

This is a frozen geometry limitation.

Therefore:

- N=139 long-protein membership is not a resampling-stability test of the
  source universe;
- perturbation stability is conditional on the frozen realized N=139 pool;
- per-length-stratum feature behavior must be reported descriptively;
- high stability in `>150` proteins must not be interpreted as independent
  evidence that alternative long-protein discovery memberships would nominate
  the same feature set.

No confirmatory positive may be borrowed to increase long-stratum variation.

## 17. Required pre-confirmatory outputs

Before any confirmatory protein is embedded, save and commit:

1. model provenance JSON;
2. discovery sequence-manifest TSV with identifiers, lengths, and SHA-256
   sequence hashes;
3. discovery protein-level SAE matrix metadata and matrix SHA-256;
4. complete N=139 signed latent-score table;
5. nominated top-five signed feature set;
6. perturbation membership manifest / deterministic seeds;
7. perturbation stability summary;
8. N=100 / N=120 / N=139 descriptive comparison;
9. Stage-1 decision JSON;
10. a human-readable Stage-1 result note.

Large activation matrices need not be committed to Git, but their exact path,
shape, dtype, generation configuration, and SHA-256 must be recorded.

## 18. Hard stop conditions

Stage 1 stops without confirmatory access if any of the following occurs:

- discovery membership cannot be reconstructed exactly;
- a frozen sequence cannot be recovered exactly;
- sequence length is outside 1–1022;
- model or SAE provenance cannot be pinned;
- SAE dimensionality is not 10,240;
- ESM layer is not 18;
- normalized SAE weights cannot be loaded;
- special-token masking cannot be verified;
- any confirmatory sequence is accidentally embedded or scored;
- numerical failure produces NaN/Inf in protein-level scores;
- the N=139 discovery feature set fails any component of the frozen three-way
  stability gate.

No failed gate may be repaired by changing:

- ESM layer;
- SAE checkpoint;
- pooling;
- k;
- Jaccard threshold;
- recurrence threshold;
- concentration threshold;
- perturbation fraction;
- perturbation count;
- discovery membership.

## 19. First-model-contact boundary

The following are not considered Experiment-03 biological model contact:

- downloading package metadata;
- resolving external model revisions;
- downloading model weights;
- hashing model weights;
- checking architecture dimensions without passing biological sequences.

The first Experiment-03 biological model contact occurs when a frozen
discovery protein sequence is passed through ESM-2.

That action is permitted only after:

1. this specification is committed;
2. the model-provenance gate is implemented;
3. the frozen discovery sequence manifest is reconstructed and verified;
4. the confirmatory firewall is verified.
