# Experiment 04 — Exploratory Biological Arm-B Execution Contract

## Status

**FROZEN BEFORE FRESH BIOLOGICAL ARM-B EXECUTION**

Experiment 04 remains active.

This document prospectively governs exploratory biological execution of
Arm B. Its creation is a documentation freeze only and does not itself
authorize fresh biological computation.

The exact repository parent from which this contract is frozen is:

`dd8bf0d97b34bf43e24f2f9a7a24f8a1a75b4628`

At this boundary:

- Experiment 01 is complete with verdict `H_repr`.
- Experiment 02 is closed.
- Experiment 03 is complete; its preregistered SAE stability gate failed.
- S7-v2 is rejected / closed under its frozen strong-calibration criterion.
- Arm B is operationally adequate.
- Biological Arm B is exploratory / descriptive / calibration-limited.
- Fresh Experiment-04 biological execution has not yet been opened.
- gamma is `NONE`.
- `910001-910100` is consumed / closed.
- `920001-920100` is consumed / closed.
- `930001-930100` is consumed / closed.
- `4000-4099` is unopened.
- `2000-2099` is sealed.


## 1. Scientific question

The simple framing is a smoke detector.

Experiment 03 asked whether the SAE/control panel exposed a stable
toxin-associated alarm. It did not satisfy the preregistered stability gate.

Experiment 04 Arm B asks:

> **Is there actually smoke in the building?**

Operationally:

> **Is toxin-associated information detectably accessible in the raw ESM-2
> representation even when the SAE does not expose it as a stable feature?**

At the lay level, the primary question is:

> **Does it detect smoke?**

The additional quantities measured by Arm B — sparsity, recurrence, support
similarity, coefficient signs, and resampling stability — characterize and
defend the instrument. They do not replace the primary biological question.


## 2. Calibration interpretation

The corrected Arm-B instrument is operational.

After fixing the resampling architecture:

- support resolution passed all 9/9 S7-v2 acceptance cells;
- sparse supports were non-degenerate;
- structured sparse signal could be recovered.

S7-v2 nevertheless failed the stronger preregistered signed-instability
certification.

Observed S7-v2 strong-calibration results:

- overall acceptance: `0/9`;
- recurrence `R`: `24-59`, versus frozen `R >= 71`;
- minority sign `M`: `0-7`, versus frozen `M >= 8`;
- strict `G < I`: `3/9`.

The following statements must remain distinct:

> **Instrument operational: YES.**

> **Strong sign-instability calibration: NO.**

The failed S7-v2 thresholds must not be lowered, reinterpreted, replaced,
or retrofitted.

They are not validated biological gates.

Biological Arm-B outputs are therefore exploratory, descriptive, and
calibration-limited.


## 3. Biological discovery universe

Biological Arm B inherits the Experiment-03 discovery geometry:

- 139 toxin-positive proteins;
- 139 family-aware negative proteins;
- authoritative realized per-class target sizes `N = 100, 120, 139`.

The confirmatory universe remains completely excluded.

No confirmatory examples may be used for:

- representation extraction;
- regularization selection;
- perturbation construction;
- model fitting;
- stability analysis;
- threshold construction;
- exploratory inspection;
- biological-performance troubleshooting;
- or any other Arm-B computation.


## 4. Model and representation

Model:

- ESM-2 650M.

Raw hidden width:

- 1,280 coordinates.

Protocol-defined layers:

- layer 1;
- layer 9;
- layer 18;
- layer 24;
- layer 30;
- layer 33.

Layer 18 is the already-observed Experiment-03 anchor.

Fresh biological layers are:

- layer 1;
- layer 9;
- layer 24;
- layer 30;
- layer 33.

No post-hoc best-layer selection is permitted.

For each authorized protein and layer:

1. use the raw residue-level ESM hidden representation;
2. exclude model special tokens;
3. apply coordinate-wise maximum pooling over biological residues only;
4. produce exactly one 1,280-dimensional vector per protein.

No alternative pooling rule may be introduced after biological results are
observed.


## 5. Probe family

The biological Arm-B probe is L1-regularized logistic regression.

Regularization selection is discovery-only.

The frozen C grid is:

`1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0`

Where applicable, biological Arm B inherits the corrected Arm-B mechanics:

- deterministic perturbations;
- Stage-A split;
- 5-fold cross-validation;
- frozen R2 C-selection rule;
- full-target-N refit;
- independent 80%-within-target-N stability refit;
- unsigned supports;
- signed supports;
- 100 perturbations per N/layer.

These mechanics must not be altered in response to biological outcomes.


## 6. Biological outputs

The biological execution is explicitly exploratory and descriptive.

Arm B may report quantities needed to answer and characterize the question
of raw representational accessibility, including biological probe performance
and the inherited instrumentation quantities.

However:

- no failed synthetic threshold becomes a biological gate;
- no new biological threshold may be invented after results are observed;
- no biological pass/fail criterion may be reverse-engineered from the data;
- no S7-v2 threshold may be weakened;
- no result may be promoted to confirmatory status merely because it appears
  strong.

The biological question is whether toxin-associated information appears
detectably accessible in the raw representation.

The calibration limitation must accompany interpretation of the result.


## 7. Arm A versus Arm B

Arm A asks:

> Does the SAE expose a stable toxin-associated feature representation?

Arm B asks:

> Can the raw ESM representation detect toxin-associated information?

A pattern of:

`Arm A weak + Arm B strong`

would be evidence consistent with a representation-basis gap, SAE-basis
misalignment, and/or distributed accessibility.

It would not by itself establish:

- a causal toxin mechanism;
- a uniquely toxin-specific mechanism;
- a mechanistic feature decomposition;
- or proof that the SAE failed for one particular causal reason.


## 8. Required execution sequence

Fresh biological execution is not opened by this document.

The required sequence after this freeze is:

1. read-only audit of the Experiment-03 extraction and partition machinery;
2. implement the biological Arm-B runner in a hard-disabled state;
3. static audit of the disabled runner;
4. non-biological smoke test;
5. commit and push the disabled runner;
6. make a separate minimal enablement commit;
7. commit and push the enablement;
8. only then open fresh biological execution;
9. after execution begins, archive the authorized outputs, commit them, and
   push them without inserting a human decision point after seeing the first
   fresh biological results.

Implementation, audit, smoke-test, enablement, execution, archive, commit,
and push boundaries must remain distinguishable in repository history.


## 9. Hard scientific firewalls

Until separately and prospectively authorized:

- do not open `4000-4099`;
- do not open `2000-2099`;
- do not use confirmatory data;
- do not invent biological thresholds;
- do not tune the instrument to make the biological experiment pass;
- do not change the frozen C grid after seeing biological results;
- do not select layers post hoc;
- do not substitute an alternate representation or pooling rule;
- do not weaken the failed S7-v2 calibration criterion;
- do not reinterpret S7-v2 as having passed;
- do not treat exploratory biological outputs as preregistered confirmatory
  evidence.

Consumed seed ranges remain consumed and closed:

- `910001-910100`;
- `920001-920100`;
- `930001-930100`.

Protected ranges remain protected:

- `4000-4099`: unopened;
- `2000-2099`: sealed.


## 10. Workflow discipline

Execution proceeds one Kaggle cell at a time.

Each returned cell output must be interpreted before the next execution cell
is issued.

Operational decisions use explicit `PASS` or `STOP` boundaries.

No post-hoc tuning is permitted.

The experiment is not required to succeed.

The objective is to determine what the frozen instrument reports under the
authorized biological design while preserving the scientific firewalls.


## 11. Freeze statement

This contract is frozen before any fresh Experiment-04 biological Arm-B
activation extraction or probe execution.

Its purpose is to ensure that the biological question, data boundary,
representation, layer set, probe family, regularization grid, inherited
resampling mechanics, calibration limitation, interpretation rules, and
execution sequence are fixed before fresh biological results can influence
them.

The governing parent at freeze is exactly:

`dd8bf0d97b34bf43e24f2f9a7a24f8a1a75b4628`
