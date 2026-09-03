# Experiment 04 — Arm-B S7 replacement generator specification

**Status:** PROSPECTIVE / PRE-IMPLEMENTATION / PRE-DIAGNOSTIC

This document freezes the replacement design for synthetic scenario S7 before
implementation of the replacement generator and before any probe fit using
diagnostic namespace `920001-920100`.

This specification is subordinate to:

- `SPARSE_PROBE_CALIBRATION.md`
- `ARM_B_POST_FAILURE_ARCHITECTURE_AMENDMENT.md`
- `ARM_B_S7_STEP4B_REDESIGN_DIAGNOSTIC_CONTRACT.md`

No numerical gamma is selected here.
No independent-validation seed is opened here.
No biological activation is accessed here.


## 1. Purpose

The original S7 generator used five fixed-orientation observed proxies for one
latent predictive direction. Those planted proxies had fixed population-favored
signs. The design therefore supplied coordinate interchangeability but did not
plant a genuine mechanism by which the same recurring observed coordinate could
reverse fitted sign under observation subsampling.

Replacement S7 combines:

1. a stable five-coordinate label-generating anchor signal; and
2. one post-label observed shortcut coordinate whose empirical association can
   reverse sign when realized samples contain different balances of aligned and
   anti-aligned high-leverage observations.

The design does not guarantee diagnostic success. It prospectively supplies a
same-coordinate sign-reversal mechanism; the frozen step-4b diagnostic decides
whether the Arm-B probe actually resolves that mechanism.


## 2. Frozen global dimensions

The replacement uses the existing dimensions unchanged:

    N_POS   = 139
    N_NEG   = 139
    N_TOTAL = 278
    P       = 1280

Every generated dataset must contain exactly 139 observations with `y = 1` and
139 observations with `y = 0`.


## 3. Public generator interface

The public interface remains:

    generate_s7(seed: int, tau: float) -> SyntheticDataset

The public `tau` argument must be one of the existing frozen `MASTER_TAU`
values.

No new public tuning parameter is introduced.

The generator must not accept diagnostic perturbation seed, target N, rho,
selected C, stability-subsampling identity, or diagnostic outcomes as inputs.


## 4. Frozen tau handling

Replacement S7 uses the existing `MASTER_TAU` ladder exactly.

Membership is checked with:

    _matches_allowed_tau(tau, MASTER_TAU)

The equal-magnitude five-anchor coefficient magnitude is:

    b = _tau_to_b(tau=tau, k=5)

Thus:

    b = tau / sqrt(5)

No S7-specific tau ladder may be introduced.


## 5. Observed-coordinate layout

The coordinate layout is frozen as:

    anchor_idx     = [0, 1, 2, 3, 4]
    shortcut_idx   = 5
    background_idx = [6, 7, ..., 1279]

The five anchors use the frozen S1 sign template:

    anchor_signs = [+1, +1, -1, +1, -1]

Only coordinate 5 is prospectively designated as a planted
sign-instability coordinate.

The required metadata declaration is exactly:

    "planted_sign_instability_idx": [5]

Coordinates 0-4 are not eligible for the step-4b recurring-coordinate
sign-instability limb.

Coordinates 6-1279 are not eligible for that limb.

The eligible set may not be expanded, contracted, or redefined after any probe
fit using `920001-920100`.


## 6. Frozen RNG streams

All stochastic components use deterministic children of the scenario seed
through the existing:

    _spawn_rng(seed, stream_id)

The replacement streams are frozen as:

    stream 31 = anchor generation
    stream 32 = label noise
    stream 33 = within-class shortcut-regime assignment
    stream 34 = shortcut residual noise
    stream 35 = independent background generation

Streams 31-35 were unused inside the pre-replacement `generate_s7` at the time
this specification was frozen.

No additional S7-v2 stochastic stream may be introduced after this
specification without a prospective amendment made before any diagnostic fit.


## 7. Anchor latent variables and covariance

For observation i, let:

    Z_i = (Z_i1, ..., Z_i5)

with:

    Z_ij ~ iid Normal(0, 1)

generated from stream 31.

The observed anchor coordinates are exactly:

    X_i,0:5 = Z_i

No additional measurement noise or covariance transformation is applied.

Therefore the anchor population covariance matrix is:

    Cov(X_anchor) = I_5


## 8. Anchor coefficients and noiseless score

Let:

    s = (+1, +1, -1, +1, -1)

and:

    b = tau / sqrt(5)

The anchor coefficient vector is:

    beta_anchor = b * s

The noiseless label score is:

    eta_i = b * sum_j s_j Z_ij

Because the five anchors are independent standard normals:

    Var(eta_i) = tau^2

The shortcut coordinate does not participate in `eta_i`.


## 9. Label mechanism

Labels are generated before construction of the shortcut coordinate.

Using stream 32:

    y = _balanced_labels_from_score(
        score=eta,
        rng=rng_label,
        noise_scale=1.0,
    )

The existing helper therefore supplies its existing logistic noise mechanism
and assigns class 1 to the top 139 realized values, producing exactly 139
positives and 139 negatives.

Define:

    ell_i = +1  if y_i = 1
            -1  if y_i = 0

This label mechanism is frozen unchanged.


## 10. Post-label shortcut construction

Observed coordinate 5 is constructed only after `y` has been generated.

It is therefore a synthetic post-label shortcut/artifact rather than a direct
label-generating coordinate.

For observation i:

    X_i,5 = A_i * ell_i + epsilon_i

where:

    epsilon_i ~ iid Normal(0, 0.25^2)

using stream 34.

The amplitude `A_i` is determined by exactly one of three regimes:

    base regime         : A_i = +0.02
    aligned-leverage    : A_i = +8.00
    anti-aligned        : A_i = -8.00

The terminology refers to the shortcut orientation relative to `ell_i`.

These amplitudes are frozen synthetic-design constants, not diagnostic tuning
parameters.


## 11. Shortcut-regime counts

Regime membership is assigned separately within each observed class.

For each class there are exactly:

    10 aligned-leverage observations
    10 anti-aligned observations
    119 base observations

Therefore, over the complete 278-observation dataset, there are exactly:

    20 aligned-leverage observations
    20 anti-aligned observations
    238 base observations

The three regimes are mutually exclusive and exhaustive.


## 12. Frozen class-processing order for stream 33

Create exactly one regime-assignment RNG:

    rng_regime = _spawn_rng(seed, 33)

The class-processing order is frozen as:

    class 0 first
    class 1 second

For each class in that order:

1. obtain the observation indices satisfying `y == class_value`;
2. sort those indices in ascending observation-index order before
   randomization;
3. call `rng_regime.permutation(...)` once on that ordered 139-index vector;
4. assign the first 10 permuted indices to aligned-leverage;
5. assign the next 10 permuted indices to anti-aligned;
6. assign the remaining 119 permuted indices to base.

No separate class-specific RNG stream is used.

This class order and sequential use of stream 33 are part of the frozen
generator definition.


## 13. Planted same-coordinate sign-reversal mechanism

Within one class, the deterministic shortcut-amplitude sum in the complete
dataset is:

    119 * 0.02 + 10 * 8.00 + 10 * (-8.00)
    = 2.38

Thus the complete class has only a weak positive net deterministic shortcut
orientation.

A one-observation imbalance between retained aligned and retained anti-aligned
high-leverage observations changes the deterministic amplitude sum by 8.00 in
magnitude.

Because:

    8.00 > 2.38

observation subsampling can reverse the empirical orientation of coordinate 5
without changing coordinate identity.

This is the prospectively planted same-coordinate sign-instability mechanism.

This algebra is a design rationale only. It is not a claim that every
subsample, fitted model, tau cell, or target-N cell will produce a sign
reversal.


## 14. Background coordinates

Coordinates 6 through 1279 are generated from stream 35 as independent
standard-normal background:

    X_i,j ~ iid Normal(0,1)
    for j = 6,...,1279

They use a child RNG distinct from the anchor, label, regime-assignment, and
shortcut-residual streams.


## 15. Construction and covariance interpretation

The five anchor coordinates are mutually independent standard normals in the
population.

The background coordinates are independent standard normals generated from a
separate deterministic child RNG stream.

Coordinate 5 is different. It is explicitly constructed after label generation
from:

1. the realized class indicator `ell_i`;
2. a within-class regime assignment; and
3. independent residual noise.

Accordingly, coordinate 5 must not be described as an independent Gaussian
covariate or as part of the anchor covariance model.

Its dependence on the realized label is deliberate and must be represented in
the dataset metadata.


## 16. Frozen beta vector

The returned `beta` vector has length 1280 and is frozen as:

    beta[0:5] = b * [+1,+1,-1,+1,-1]
    beta[5]   = 0.0
    beta[6:]  = 0.0

Coordinate 5 has zero direct beta because it is not used to generate labels.

The shortcut must not receive a nonzero ground-truth coefficient.

Unlike the original S7, replacement S7 has an identifiable direct
label-generating observed-space coefficient vector on the five anchor
coordinates.


## 17. Diagnostic meaning of coordinate 5

Coordinate 5 is the only coordinate whose fitted coefficient sign is
prospectively eligible for the step-4b recurring-coordinate sign-instability
criterion.

A qualifying event therefore requires the same coordinate 5 to:

1. recur in at least the contractually required number of stability fits; and
2. appear with both positive and negative fitted coefficient signs in the
   contractually required counts.

Switching among different coordinates does not satisfy this criterion.

Sign changes in coordinates 0-4 or 6-1279 are descriptive only for this
diagnostic and cannot satisfy the planted-coordinate limb.


## 18. Required metadata keys

The replacement `SyntheticDataset.metadata` dictionary must contain all of the
following keys:

    design_version
    design_name
    tau
    b
    anchor_idx
    anchor_signs
    shortcut_idx
    planted_sign_instability_idx
    background_idx
    shortcut_base_amplitude
    shortcut_aligned_amplitude
    shortcut_anti_amplitude
    shortcut_residual_sd
    n_aligned_per_class
    n_anti_per_class
    n_base_per_class
    shortcut_is_post_label
    shortcut_direct_beta_nonzero
    observed_beta_identifiable
    rng_stream_anchor
    rng_stream_label
    rng_stream_regime
    rng_stream_shortcut_noise
    rng_stream_background
    aligned_idx
    anti_idx
    base_idx
    aligned_idx_by_class
    anti_idx_by_class
    base_idx_by_class
    noise_scale

The following metadata values are frozen exactly:

    design_version               = "S7-v2"
    design_name                  = "stable_anchors_heterogeneous_signed_shortcut"

    anchor_idx                   = [0,1,2,3,4]
    anchor_signs                 = [1,1,-1,1,-1]

    shortcut_idx                 = 5
    planted_sign_instability_idx = [5]
    background_idx               = [6,7,...,1279]

    shortcut_base_amplitude      = 0.02
    shortcut_aligned_amplitude   = 8.0
    shortcut_anti_amplitude      = -8.0
    shortcut_residual_sd         = 0.25

    n_aligned_per_class          = 10
    n_anti_per_class             = 10
    n_base_per_class             = 119

    shortcut_is_post_label       = True
    shortcut_direct_beta_nonzero = False
    observed_beta_identifiable   = True

    rng_stream_anchor            = 31
    rng_stream_label             = 32
    rng_stream_regime            = 33
    rng_stream_shortcut_noise    = 34
    rng_stream_background        = 35

    noise_scale                  = 1.0

The metadata key:

    planted_sign_instability_idx

is not descriptive bookkeeping that may be reconstructed after the diagnostic.

It is the prospective declaration of the only observed coordinate eligible to
satisfy the step-4b recurring-coordinate sign-instability limb.

Its value must be exactly:

    [5]


## 19. Realized regime-membership metadata

The realized overall regime memberships must be stored under:

    aligned_idx
    anti_idx
    base_idx

Each list must be sorted into ascending observation-index order before it is
placed in metadata.

The canonical metadata representation must therefore describe set membership,
not the order produced by stream 33.

The by-class regime memberships must be stored under:

    aligned_idx_by_class
    anti_idx_by_class
    base_idx_by_class

Each by-class object must be a dictionary with exactly the string keys:

    "0"
    "1"

For example, the representation shape is:

    {
        "0": [...],
        "1": [...],
    }

Every contained observation-index list must be sorted in ascending order.

The permutation sequence itself must not be used as the canonical metadata
representation of regime membership.


## 20. Required structural invariants

The replacement implementation must enforce the following structural
invariants before returning the dataset.

1. `X.shape == (278, 1280)`.

2. `y.shape == (278,)`.

3. `beta.shape == (1280,)`.

4. Exactly 139 observations have `y == 1`.

5. Exactly 139 observations have `y == 0`.

6. Every value in `X` is finite.

7. Every value in `beta` is finite.

8. Anchor coordinates are exactly:

       [0,1,2,3,4]

9. Anchor signs are exactly:

       [1,1,-1,1,-1]

10. Shortcut coordinate is exactly:

        5

11. Prospectively eligible sign-instability coordinates are exactly:

        [5]

12. Background coordinates are exactly:

        [6,7,...,1279]

13. The aligned, anti-aligned, and base membership sets are pairwise disjoint.

14. The union of the three regime sets is exactly all 278 observation indices.

15. Within class 0 there are exactly:

        10 aligned
        10 anti-aligned
        119 base

16. Within class 1 there are exactly:

        10 aligned
        10 anti-aligned
        119 base

17. Overall there are exactly:

        20 aligned
        20 anti-aligned
        238 base

18. Every aligned observation uses deterministic amplitude:

        +8.0

19. Every anti-aligned observation uses deterministic amplitude:

        -8.0

20. Every base observation uses deterministic amplitude:

        +0.02

21. Shortcut residual noise has frozen standard deviation:

        0.25

22. `beta[5] == 0.0`.

23. `beta[6:]` is identically zero.

24. `beta[0:5]` equals:

        b * S1_SIGNS

25. Label generation occurs before shortcut construction in implementation
    dataflow.

26. Regime assignment occurs after realized `y` exists.

27. Regime assignment depends only on the scenario seed and realized labels,
    not on target N, rho, perturbation identity, selected C, stability
    membership, or diagnostic outcome.

28. Stream 33 is consumed sequentially in frozen class order:

        class 0
        class 1

29. The three stored overall regime membership lists are sorted.

30. The stored by-class regime membership lists are sorted.

31. Metadata regime memberships agree exactly with the realized regime
    assignments used to construct coordinate 5.

32. The metadata value:

        planted_sign_instability_idx

    equals exactly:

        [5]

33. The metadata value:

        shortcut_is_post_label

    is exactly:

        True

34. The metadata value:

        shortcut_direct_beta_nonzero

    is exactly:

        False

35. The metadata value:

        observed_beta_identifiable

    is exactly:

        True

36. The existing `_validate_dataset(ds)` validation is still executed after
    S7-specific construction checks.


## 21. No feature standardization

The frozen Arm-B sparse probe operates on the raw observed coordinates without
feature standardization.

Therefore the shortcut amplitudes:

    +8.0
    -8.0

are deliberately large relative to the unit-scale anchor and background
coordinates.

This is an intentional synthetic stress-test property frozen prospectively.

The S7 replacement must not receive scenario-specific standardization,
normalization, or amplitude rescaling in the diagnostic runner.

The shortcut amplitudes may not be revised after `920001-920100` is opened.


## 22. Relationship to the frozen diagnostic acceptance rule

This generator specification does not alter the frozen step-4b diagnostic
contract.

The candidate is evaluated in exactly the nine acceptance cells:

    N in {100, 120, 139}
    tau_index in {6, 7, 8}

A cell satisfies the support-resolution limb only under the separately frozen
step-4b support criterion.

A cell satisfies the recurring-coordinate sign-instability limb only under the
separately frozen recurrence and minority-sign criteria.

For that sign-instability limb, only the coordinates named prospectively by:

    planted_sign_instability_idx

are eligible.

Under this specification that set is exactly:

    [5]

Therefore only repeated selection of coordinate 5 with both fitted coefficient
signs can satisfy the planted recurring-coordinate sign-instability limb.

Coordinate switching cannot satisfy that limb.

Sign changes on anchor or background coordinates cannot satisfy that limb.

Each acceptance cell must also satisfy the separately frozen aggregate signed
effect requirement:

    G_stat < I_stat

The generator passes step 4b only if all nine acceptance cells satisfy every
required limb.

Failure of any one of the nine cells rejects this S7-v2 candidate.

No minimum numerical value of `I_stat - G_stat` is introduced here.


## 23. Diagnostic-support interpretation

The support-resolution rule remains exactly the rule frozen in the step-4b
diagnostic contract.

This generator specification does not reinterpret that rule as proving that
the sample median itself is formed by two supports of size at least three.

It supplies only the replacement synthetic mechanism.

Whether the realized pairwise signed and unsigned Jaccard distributions have
sufficient resolution is determined by the frozen diagnostic.

Likewise, the algebraic shortcut sign-reversal mechanism specified above does
not itself establish fitted sign instability.

That must be demonstrated prospectively in the diagnostic using coordinate 5.


## 24. No tuning after diagnostic opening

Once any probe fit using a seed in `920001-920100` occurs, that namespace is
consumed for this candidate.

After that first fit, the following may not be changed for S7-v2:

- anchor coordinates;
- anchor signs;
- tau handling;
- shortcut coordinate;
- `planted_sign_instability_idx`;
- shortcut amplitudes;
- shortcut residual standard deviation;
- per-class regime counts;
- class-processing order;
- regime-assignment algorithm;
- RNG stream IDs;
- beta semantics;
- metadata eligibility semantics;
- feature scaling;
- acceptance-cell definition.

A failed cell may not be repaired by changing the generator and continuing on
unused seeds from `920001-920100`.

A rejected S7-v2 candidate requires a new prospective redesign contract and a
new untouched diagnostic namespace.


## 25. No hidden parameter sweep

The frozen S7-v2 constants are a single prospectively specified design.

There is no authorized sweep over:

- base amplitude;
- aligned amplitude;
- anti-aligned amplitude;
- shortcut residual noise;
- aligned count;
- anti-aligned count;
- base count;
- shortcut coordinate identity;
- eligible sign-instability coordinate identity.

No selection among multiple hidden S7-v2 candidates may be made using
`920001-920100`.

Any future generator-only theoretical or structural calculation must not use
the diagnostic perturbation namespace and must not be represented as
independent diagnostic evidence.


## 26. Biological firewall

Replacement S7 is purely synthetic.

The generator and its pre-diagnostic implementation audit must not load,
inspect, derive from, or condition on:

- ESM representations;
- InterPLM SAE activations;
- protein sequences;
- toxin annotations;
- catalytic-site annotations;
- biological class labels;
- Experiment-04 biological evaluation outputs;
- independent-validation outputs.

The generator operates only on deterministic synthetic arrays derived from its
scenario seed and the frozen generator definition.


## 27. Seed-state firewall

At specification freeze, the protected namespaces are:

    910001-910100 = CONSUMED / CLOSED
    920001-920100 = ASSIGNED / UNOPENED
    4000-4099     = UNOPENED calibration reserve
    2000-2099     = SEALED independent validation

This document does not authorize use of any of those protected blocks.

In particular:

- `910001-910100` remains closed historical architecture-diagnostic evidence;
- `920001-920100` remains unopened until the fully audited and remotely
  verified step-4b runner is explicitly enabled;
- `4000-4099` remains untouched;
- `2000-2099` remains sealed.

No gamma has been selected.

No S7 redesign diagnostic has been executed.


## 28. Implementation fidelity requirement

The replacement implementation must be a direct realization of this
specification.

Implementation audits must verify, before any probe fit, that:

1. the generator has no diagnostic-seed argument;
2. streams 31-35 are used for exactly the components frozen here;
3. labels are generated before shortcut construction;
4. regime assignment is conditioned on realized class labels only;
5. class order is exactly 0 then 1;
6. coordinate 5 is the sole planted sign-instability coordinate;
7. metadata contains `planted_sign_instability_idx = [5]`;
8. beta for coordinate 5 is exactly zero;
9. no S7-specific feature standardization exists;
10. no protected diagnostic or validation seed literal is embedded in the
    generator;
11. `_validate_dataset(ds)` remains executed;
12. realized metadata agrees with the construction actually used.

Any implementation mismatch must be corrected before the generator is committed
as the frozen S7-v2 implementation.


## 29. Frozen next sequence

After this complete specification is committed and live-remote verified, the
allowed sequence is:

1. implement S7-v2 exactly in `synthetic_generators.py`;
2. perform a read-only / generator-only implementation audit;
3. correct implementation mismatches before any probe fit;
4. commit the generator implementation;
5. push and verify the exact live remote generator commit;
6. implement the step-4b diagnostic runner;
7. audit the runner without opening `920001-920100`;
8. commit the runner hard-disabled;
9. push and verify the disabled runner;
10. enable diagnostic execution in a separate commit;
11. push and verify the enabled runner;
12. only then execute the first probe fit using `920001-920100`;
13. archive diagnostic outputs before scientific interpretation;
14. apply the frozen 9/9 acceptance rule;
15. if S7-v2 is rejected, close the consumed namespace and require a new
    prospective redesign with a new untouched namespace.

This specification itself does not authorize a diagnostic execution.


## 30. Freeze statement

The complete S7-v2 generator is prospectively defined by this document before
implementation and before use of `920001-920100`.

The diagnostically meaningful planted sign-instability coordinate set is frozen
as:

    planted_sign_instability_idx = [5]

That declaration is part of the scientific design, not a post-hoc annotation.

No generator outcome, sparse-probe outcome, signed-support outcome, Jaccard
outcome, `I_stat`, `G_stat`, or diagnostic PASS/FAIL result was used to choose
among realized results from `920001-920100`, because that namespace remained
unopened when this specification was written.
