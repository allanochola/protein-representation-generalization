# Experiment 03 — biological SAE sweep pre-contact amendment

**Status:** PRE-MODEL / FROZEN BEFORE FIRST BIOLOGICAL ESM CONTACT

**Parent specification:** `STABILITY_SWEEP_SPEC.md` at commit `f90c892`.

This amendment closes implementation details identified after the parent
specification was committed but before any Experiment-03 biological sequence
was passed through ESM-2.

No biological ESM embedding, SAE activation, feature nomination, or
confirmatory representation statistic has been inspected.

## 1. Perturbation RNG instantiation

For every N in {100, 120, 139} and perturbation index b in {0,...,99},
instantiate a fresh RNG:

`rng = np.random.default_rng(20_000_000 + 100_000 * N + b)`

The positive and negative subsamples for that perturbation are drawn from that
fresh RNG instance.

The implementation must not seed once and advance one RNG across all 100
perturbations.

## 2. Concentration-definition equivalence

The biological fixed-identity concentration statistic is exactly the
independently validated synthetic statistic.

For perturbation b:

`d_b[j] = mean_positive(z[:,j]) - mean_negative(z[:,j])`

`mass_b[j] = abs(d_b[j])`

For S5 equal to the five latent identities nominated on the complete N=139
discovery dataset:

`C_b = sum_{j in S5} mass_b[j] / sum_{j=1..10240} mass_b[j]`

The numerator uses the same fixed five identities for every perturbation.

The denominator contains all 10,240 SAE latent score masses.

No alternative denominator is permitted.

## 3. Max-pooling and frozen length matching

The realized N=139 discovery classes are jointly length-stratum matched.

For BOTH positives and negatives the frozen counts are:

- <30: 9
- 30-75: 22
- 76-150: 29
- >150: 79

Thus the primary positive and negative discovery classes have identical
length-stratum histograms.

This matching is load-bearing because residue-max pooling has an
extreme-value dependence on sequence length.

The primary signed latent differences are interpreted conditional on this
frozen matched geometry.

No post-activation length reweighting or rematching is permitted.

## 4. Pre-contact confirmatory firewall artifact

Before the first frozen discovery sequence is passed through ESM-2, generate
and commit:

`confirmatory_firewall.json`

It must record at minimum:

- discovery positive count;
- discovery negative count;
- confirmatory positive count;
- confirmatory negative count;
- positive identifier intersection count;
- negative identifier intersection count;
- frozen source-membership file hashes;
- PASS/FAIL status.

Required intersections:

- discovery-positive cluster reps ∩ confirmatory-positive cluster reps = 0
- discovery-negative accessions ∩ confirmatory-negative accessions = 0

Any non-zero intersection is a hard stop before model contact.

## 5. Frozen Arm-B representation score

If the N=139 discovery feature set passes the frozen three-way stability gate,
let:

`S5 = {(j_1,s_1),...,(j_5,s_5)}`

be the five frozen signed latent identities, where each sign is +1 or -1.

Protein-level latent activation remains:

`z[p,j] = max_r a[p,r,j]`

over biological residue positions only.

For each nominated latent j, compute using ONLY the 139 frozen discovery
negatives:

`mu_neg[j] = mean(z[p,j])`

`sigma_neg[j] = sample_sd(z[p,j], ddof=1)`

The frozen one-dimensional Arm-B representation score is:

`R[p] = (1/5) * sum_{(j,s) in S5} s * (z[p,j] - mu_neg[j]) / sigma_neg[j]`

Higher R always denotes more toxin-like representation evidence.

The five latents have equal weight after negative-reference standardization.

No confirmatory observation is used to estimate:

- latent identity;
- sign;
- centering;
- scaling;
- feature weight;
- score-combination rule.

No fitted classifier is used in Arm B.

No alternative maximum, minimum, raw mean across latents, learned linear
combination, logistic regression, or post-confirmatory weighting is permitted.

If any nominated latent has nonfinite or zero discovery-negative sample
standard deviation, Stage 1 terminates as a technical failure.

## 6. Frozen operating-point construction

For either Arm A or Arm B and requested FPR alpha in {0.05, 0.01}:

1. compute scores for all frozen confirmatory negatives;
2. sort negative scores descending;
3. let `k = floor(alpha * n_negative)`;
4. if the kth and (k+1)th ordered scores differ, define the threshold as their
   arithmetic midpoint;
5. if they tie, define the threshold as the tied value;
6. classify a protein positive only when `score > threshold`.

This rule gives empirical confirmatory-negative FPR no greater than the
requested operating point and handles score ties deterministically.

The identical operating-point construction is used across compared arms.

## 7. Discovery-to-confirmatory handoff

If and only if the N=139 discovery set passes all three stability gates, create
and commit before embedding ANY confirmatory sequence:

`CONFIRMATORY_FEATURE_SPEC.json`

It must contain:

- ESM checkpoint and layer;
- SAE source/revision/hash;
- protein pooling rule: `residue_max`;
- five latent IDs;
- five frozen signs;
- the five discovery-negative `mu_neg` values;
- the five discovery-negative `sigma_neg` values;
- score-combination rule:
  `equal_mean_signed_negative_zscore`;
- `k = 5`;
- Jaccard result;
- recurrence result;
- concentration result;
- Stage-1 PASS status;
- hashes of the discovery membership and Stage-1 result artifacts.

After this artifact is committed, the representation score is immutable.

Confirmatory evaluation may evaluate this frozen score but may not alter its
construction.

If Stage 1 fails, no `CONFIRMATORY_FEATURE_SPEC.json` is created and no
confirmatory sequence is embedded.
