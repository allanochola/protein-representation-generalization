# Experiment 04 — Arm-B diagnostic blinding addendum

Status: FROZEN PRE-IMPLEMENTATION / PRE-DIAGNOSTIC

This addendum supplements and, where explicitly stated below, supersedes
`ARM_B_POST_FAILURE_DIAGNOSTIC_CONTRACT.md`.

It is frozen before any diagnostic seed from `910001-910100` is opened.

No runner code is changed by this document.

No diagnostic seed is consumed by this document.

Calibration reserve `4000-4099` remains unopened.

Independent-validation block `2000-2099` remains sealed.


## 1. Purpose

The post-failure probe-fitting diagnostic exists to answer an architecture
question:

    does the amended 80%-within-pool stability machinery operate correctly?

It is not intended to reveal the amended instrument's complete control
distributions before recalibration.

The full diagnostic grid remains frozen at the complete 273-cell Step-1 grid.

This addendum changes only what diagnostic outputs may be exposed or persisted.


## 2. Blinding principle

Calibration reserve `4000-4099` must remain the first block on which the
amended instrument's joint P/S/I/G control distributions are intentionally
exposed for threshold selection.

Therefore the diagnostic block:

    910001-910100

may execute computational steps required to verify the amended architecture,
but may not persist, print, summarize, plot or otherwise expose the diagnostic
block's final calibration statistics.


## 3. Prohibited diagnostic outputs

For diagnostic seeds `910001-910100`, the diagnostic runner must not persist,
print, summarize or plot:

- `P_stat`;
- `S_stat`;
- `I_stat`;
- `G_stat`;
- pairwise unsigned-Jaccard values;
- pairwise signed-Jaccard values;
- distributions of pairwise unsigned Jaccard;
- distributions of pairwise signed Jaccard;
- candidate `PROBE_STABLE` outcomes;
- candidate numerical gamma thresholds;
- any table whose purpose is to compare final P/S/I/G control separation across
  scenarios, tau values, rho values or N.

The diagnostic must not emit a 273-cell analogue of the calibration
cell-statistics table containing P/S/I/G.


## 4. Computation permitted internally

The diagnostic may perform the computations needed to preserve the frozen
probe-fitting pathway.

In particular it may:

- execute Stage A;
- select C using frozen R2 mechanics;
- perform the full-N sparsity refit;
- perform the 80%-within-pool stability refit;
- obtain exact unsigned support;
- obtain exact signed support;
- obtain `K_t_full`;
- obtain `K_t_stab`.

However, quantities that are prohibited diagnostic outputs in §3 may not be
materialized into persisted diagnostic artifacts or surfaced in diagnostic
stdout.

Stage-A AUROC values may exist transiently because Stage A must execute under
the frozen pathway, but the diagnostic runner must not aggregate or expose them
as `P_stat` or as a scenario/tau/rho performance table.


## 5. Architecture outputs that remain permitted

The diagnostic may persist and expose only information needed to test the
amended architecture and its collapse interlocks.

Required architecture-level outputs include:

- diagnostic seed identity;
- scenario / tau / rho / N cell identity;
- selected-C identity or count of distinct selected-C values;
- stream-26 reproducible seed identity;
- stream-27 sklearn random state;
- exact or reproducibly reconstructible stability-subsample membership;
- deterministic stability-subsample membership hash;
- `K_t_full`;
- `K_t_stab`;
- empty-stability-support count;
- singleton-stability-support count;
- stability-fit collapse classification;
- number of distinct stream-26 seed identities;
- number of distinct stability-subsample memberships;
- number of distinct unsigned stability supports;
- largest identical unsigned-support clique.

Unsigned and signed support identities may be persisted only to the extent
required for architecture verification, implementation debugging and later
prospective S7 redesign work.

They must not be automatically reduced by the diagnostic runner into frozen
I/G Jaccard summaries.


## 6. Necessary diagnostic-information leakage

`K_t_full` and `K_t_stab` are necessarily visible because the diagnostic must
distinguish:

- full-fit collapse;
- stability-fit collapse;
- singleton-dominated stability fits.

Selected-C identity is also necessarily visible because the diagnostic must
verify that the stability refit uses the C selected by that perturbation's
frozen Stage-A procedure and must characterize selected-C diversity where
required by the architecture checks.

These quantities are not neutral with respect to later calibration behavior.

They may reveal limited information about:

- support cardinality;
- regularization strength;
- relative model-selection behavior across cells.

That leakage is accepted as necessary for architecture verification.

The diagnostic therefore preserves partial rather than information-theoretic
blindness.

`K_t_full`, `K_t_stab`, selected-C identity and selected-C diversity may not be
used to:

- select `gamma_S` or any other gamma;
- modify the sparsity definition;
- modify the C-selection rule;
- choose a scenario/tau/rho subset;
- rank cells for later inclusion or exclusion;
- otherwise optimize later calibration behavior.


## 7. I/G reconstruction boundary

Because exact support identities may be retained for architecture diagnostics,
I/G could in principle be reconstructed manually after the fact.

This addendum therefore freezes the following procedural firewall:

- the diagnostic runner itself may not calculate or emit final cell-level
  `I_stat` or `G_stat`;
- no companion analysis script may be executed on diagnostic block
  `910001-910100` to reconstruct P/S/I/G before calibration block `4000-4099`
  has completed threshold selection;
- no pairwise-Jaccard diagnostic table may be produced before that point.

This restriction applies even though reconstruction would be technically
possible from persisted supports.


## 8. N=120 versus N=139 comparison after blinding

The secondary N=120 versus N=139 comparison remains required, but its scope is
restricted to architecture quantities.

It may compare:

- distinct stability-subsample counts;
- distinct stability-support counts;
- largest identical-support clique sizes;
- selected-C diversity;
- `K_t_stab`;
- stability-fit collapse classifications.

It may not compare or report:

- P;
- S;
- I;
- G.

Any wording in the original diagnostic contract requiring I or G in this
secondary comparison is superseded by this addendum.

For avoidance of ambiguity, the architecture amendment's requirement that the
amended I/G measurement be validated before S7 redesign is also narrowed by
this blinding rule.

Before `4000-4099`, "validated" means that the machinery supplying I/G has
passed its frozen architecture checks:

- correct stability-subsample construction;
- correct stream-26 and stream-27 derivation;
- genuine observation-level perturbation;
- correct unsigned and signed support extraction;
- persistence of `K_t_stab` and collapse diagnostics.

It does not mean that diagnostic `I_stat` or `G_stat` values have been
calculated, inspected or shown to separate controls.

Those final statistics remain blinded until the calibration stage described
below.

This blinding rule governs diagnostic block `910001-910100` only.

The later S7-redesign diagnostic required by the architecture amendment's
step 4b must use its own prospectively frozen diagnostic contract and its own
declared seed namespace.

Any pairwise-Jaccard or support-resolution measurement required to satisfy
step 4b must be governed by that future contract rather than performed on
`910001-910100`.

That future contract must separately state what may be exposed, persisted and
used for S7 redesign before any of its seeds are opened.


## 9. Superseded diagnostic-contract clauses

This addendum supersedes only the portions of
`ARM_B_POST_FAILURE_DIAGNOSTIC_CONTRACT.md` that permit or require diagnostic
reporting of final P/S/I/G statistics.

Specifically:

- §3 permission to characterize realized P/S/I/G is narrowed by this addendum;
- §7 required diagnostic records must omit final P/S/I/G summaries;
- §9 primary architecture diagnostic must omit I/G outputs;
- §10 N=120 versus N=139 comparison must omit I/G outputs;
- any pre-calibration requirement to empirically validate realized I/G values
  is narrowed to validation of the architecture and support-producing mechanics
  specified in this addendum.

All other frozen elements of the diagnostic contract remain unchanged,
including:

- namespace `910001-910100`;
- complete 273-cell grid;
- streams 26 and 27;
- seed materialization;
- membership invariants;
- collapse classification;
- S7 firewall;
- diagnostic completion conditions;
- protection of `4000-4099`;
- protection of `2000-2099`.


## 10. Calibration blindness after diagnostic completion

Completion of the diagnostic block does not authorize inspection of final
control-separation statistics from that block.

Threshold selection must occur only after opening the separately reserved
calibration block:

    4000-4099

under the fully frozen amended instrument.

The intended chronology is therefore:

1. freeze architecture amendment;
2. freeze diagnostic contract;
3. freeze this blinding addendum;
4. implement diagnostic machinery;
5. run `910001-910100` for architecture verification only;
6. freeze any prospectively required S7 redesign and related diagnostics;
7. freeze the complete amended instrument;
8. open `4000-4099`;
9. first expose amended P/S/I/G control distributions;
10. select and freeze numerical gamma thresholds;
11. only after all validation prerequisites are met, open `2000-2099` once.


## 11. Implementation requirement

The diagnostic implementation must enforce the blinding rules that can be
enforced structurally through its output schema.

Fields prohibited by §3 must be absent from persisted diagnostic cell-summary
artifacts.

Diagnostic stdout must likewise avoid printing final P/S/I/G statistics or
pairwise-Jaccard summaries.

This schema-level protection does not make the retained diagnostic artifacts
information-theoretically blind.

Exact unsigned and signed supports are intentionally retained where required
for architecture verification, implementation debugging and prospective later
S7 work. Final I/G quantities are therefore technically reconstructible from
those retained supports.

The prohibition in §7 against reconstructing those quantities before
`4000-4099` completes threshold selection is consequently a procedural
firewall over intentionally retained data, not a guarantee supplied by the
artifact schema itself.

The implementation must enforce schema-level blinding where possible, and the
procedural firewall governs derivations that cannot be prevented without
discarding required diagnostic information.

Any implementation that directly persists or exposes prohibited summary
quantities before `4000-4099` is opened violates this addendum and must not be
used as the frozen diagnostic runner.


## 12. Firewall

Before implementation:

    910001-910100 = untouched diagnostic namespace
    4000-4099     = untouched calibration reserve
    2000-2099     = sealed independent validation

Writing, reviewing, committing and pushing this addendum consumes no seed.

No runner or generator implementation may begin from this addendum until it
has been reviewed, committed, pushed and verified against the remote HEAD.
