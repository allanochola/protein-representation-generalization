# Experiment 04 — Arm B Phase-P Biological Execution Authorization

## Status

**PROSPECTIVE EXECUTION AUTHORIZATION — FROZEN AFTER FINAL PRE-ENABLEMENT
INTEGRITY AUDIT, BEFORE THE MINIMAL ENABLEMENT COMMIT, AND BEFORE ANY
EXPERIMENT-04 PHASE-P BIOLOGICAL PROBE EXECUTION.**

This record freezes the authorization boundary required before the separate
minimal enablement transition.

It does not itself enable the runner, instantiate a protected seed, load a
biological matrix for probing, fit a biological probe, or execute Phase P.

## 1. Exact parent scientific state

Scientific branch:

`exp04-depth-and-basis`

Exact parent HEAD audited before this authorization record:

`3e52262358914de0089e72491ce413d3c91e0a99`

Production runner:

`experiments/04-depth-and-basis/phase_p_biological_probe/run_phase_p_biological_probe.py`

Frozen disabled-runner SHA-256:

`93940e890541ea437aa51c9bc3085e704d6a1ed04b3318937b14c0a7d988f3c2`

Orchestration/output contract:

`experiments/04-depth-and-basis/ARM_B_PHASE_P_ORCHESTRATION_AND_OUTPUT_CONTRACT.md`

Frozen orchestration/output-contract SHA-256:

`39d878469dd7297c40155842fc2f43a6d1165efb0f70d6a11f4c04003b94de92`

The scientific worktree and index were clean at authorization freeze.

The authoritative Phase-P production output directory was absent.

## 2. Frozen biological input integrity

Immediately before this authorization record was created, every frozen
biological input was re-hashed as opaque bytes and matched its prospectively
frozen SHA-256 exactly.

The verified inputs were:

- Phase-E authoritative row manifest:
  `ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e`
- Phase-E provenance:
  `655ea47a8300f1056656378238402cf12dc5a024b96c18117397bb804b02e6dd`
- raw ESM layer 1:
  `204b2d0901b805ce9221b8318883e29dfe2c9a2c1aa18f37b6fc831ef3b08c15`
- raw ESM layer 9:
  `7eb08b17232cbf34c23ac8e246dbeb07bec2197904d4bb24e6717a93c1d03683`
- raw ESM layer 18:
  `c4e408db0963a0cbb90996ebb59b5e83cd86a9120de1a968cd4b7d80f5fa440e`
- raw ESM layer 24:
  `78c34e2c4419fb1ba850e383ab56b06b864412e65ba5046379983ff9e1190336`
- raw ESM layer 30:
  `ebc98537034ea7946b4c634d4a0a3fff18f503428b3f182c79360a604159c98b`
- raw ESM layer 33:
  `64e626858aa8e2a0a323af5121520f969f942679f8cbec4d27c7116bc8501f0d`
- frozen 21-dimensional baseline:
  `95fa09075b24dbd11133bdf157f9e4a9b27a01f54d644860a074d5bae4c32d98`
- baseline provenance:
  `98f72c402c07d2e5a48e41a6d8fd0d88dd57af6ccf0acd252fd4b7ca86cbb25f`

No `.npy` array was loaded by that final byte-level audit.

No biological label was parsed by that audit.

## 3. Protected biological namespaces

Main Phase-P biological perturbation namespace:

`1000001-1000100`

Status immediately before authorization freeze:

**AUTHORIZED / UNCONSUMED / NOT MATERIALIZED**

Permutation-null namespace:

`1100001-1100100`

Status immediately before authorization freeze:

**AUTHORIZED / UNCONSUMED / NOT MATERIALIZED**

No protected `SeedSequence`, RNG, child seed, membership, split, fold,
probe random state, or stability membership was instantiated by this
authorization step.

## 4. Hard-disable state immediately before enablement

Immediately before this authorization record:

`ENABLE_PHASE_P_BIOLOGICAL_PROBING: Final[bool] = False`

remained literal `False`.

The terminal `PhasePContractError` at the end of `run_enabled_phase_p()`
also remained intact.

Therefore biological execution remained mechanically unreachable while this
authorization was frozen.

## 5. Authorized next repository boundary

After this authorization record is committed, pushed, and remote-verified,
the next allowed scientific repository mutation is a **separate minimal
enablement commit**.

That enablement must only perform the already-designed transition required
to make the frozen production wiring reachable.

It must not change:

- representation matrices;
- biological labels;
- baseline;
- layer set;
- target-N values;
- C grid;
- seed derivation;
- protected namespaces;
- Stage-A mechanics;
- Stage-B mechanics;
- stability mechanics;
- support semantics;
- permutation-null mechanics;
- replay mechanics;
- output schema;
- checkpoint/resume semantics;
- scientific thresholds;
- interpretation rules.

The enablement commit must remain distinct from first biological execution.

## 6. Execution remains unopened by this document

This record authorizes the later separate enablement boundary subject to the
frozen contracts.

It does **not** itself run Phase P.

Before the first protected biological fit, the exact enabled scientific HEAD
and enabled runner SHA-256 must be frozen and reconciled with the separately
maintained recovery/checkpoint policy.

No biological result may be inspected before that recovery identity is
coherent.

## 7. Current state

At this authorization freeze:

- Phase E: **COMPLETE / FROZEN**
- Phase-P mechanics: **FROZEN**
- orchestration/persistence implementation: **FROZEN**
- synthetic dry-run/resume validation: **PASS / FROZEN**
- frozen biological inputs: **BYTE-EXACT**
- main namespace `1000001-1000100`: **AUTHORIZED / UNCONSUMED**
- null namespace `1100001-1100100`: **AUTHORIZED / UNCONSUMED**
- production output directory: **ABSENT**
- outer biological execution gate: **FALSE**
- terminal enabled-path stop: **INTACT**
- biological execution: **NOT YET STARTED**
- protected biological seeds consumed: **ZERO**

The next permitted boundary is the separate minimal enablement commit.
