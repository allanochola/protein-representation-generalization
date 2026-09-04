# Experiment 04 — Arm B Calibration-Limited Continuation Amendment

## Status

**Prospective continuation amendment.**

This amendment is frozen after completion and archival of the protected
S7-v2 Step-4b diagnostic and before any biological Arm-B analysis is
opened under this continuation decision.

It does not modify the frozen S7-v2 result, does not revise any S7-v2
acceptance threshold, and does not retroactively change any candidate
decision.

---

## 1. Frozen S7-v2 result

S7-v2 was evaluated exactly once under diagnostic namespace
`930001-930100`.

The prospectively frozen candidate rule required all nine acceptance
cells (`tau_index` 6, 7, and 8 crossed with target N = 100, 120, and
139) to pass all three limbs:

1. support resolution;
2. recurring-coordinate two-sign instability; and
3. strict signed-versus-unsigned separation (`G_stat < I_stat`).

S7-v2 passed **0/9** acceptance cells and is therefore permanently:

**REJECTED under the frozen strong-calibration rule.**

The S7-v2 verdict must not be rescued through retrospective threshold
changes, acceptance-region changes, alternative aggregation rules, or
rerunning namespace `930001-930100`.

---

## 2. Failure anatomy

The corrected stability-resampling implementation produced non-degenerate
supports.

Support resolution passed all nine acceptance cells.

For the prospectively planted sign-instability coordinate, coordinate 5,
within the nine frozen acceptance cells:

- recurrence `R_5` ranged from **24 to 59 selections per 100 stability
  perturbations**;
- median recurrence was **30/100**;
- the frozen recurrence requirement was `R >= 71`;
- minority-sign recurrence `M_5 = min(n_plus, n_minus)` ranged from
  **0 to 7**;
- median minority-sign recurrence was **3**;
- the frozen minority-sign requirement was `M >= 8`;
- strict `G_stat < I_stat` occurred in **3/9** acceptance cells.

Thus the primary S7-v2 failure was insufficient recurrence of the planted
coordinate under the frozen sparse-probe instrument, accompanied by
insufficient minority-sign recurrence.

The failure is not interpreted as a repeat of the previously identified
N=139 identical-resampling architecture artifact. The corrected
resampling/stability machinery generated substantial, non-degenerate
supports across all nine acceptance cells.

---

## 3. Interpretation boundary

The S7-v2 outcome supports the following limited implementation-level
conclusion:

> The corrected Arm-B sparse-probe and stability-resampling machinery is
> operational and capable of producing non-degenerate, variable sparse
> supports.

It does **not** establish that the S7-v2 strong signed-instability
criterion is successfully calibrated.

In particular:

- `R >= 71` is not treated as a validated biological recurrence cutoff;
- `M >= 8` is not treated as a validated biological minority-sign cutoff;
- the rejected S7-v2 9-of-9 candidate rule is not transferred to
  biological data as a validated inferential rule;
- S7-v2 remains rejected and is not relabeled as a calibration pass.

---

## 4. Arm-B continuation decision

Experiment 04 Arm B may proceed to biological protein representations as
**calibration-limited exploratory analysis**.

The purpose of this continuation is to characterize what the corrected
supervised sparse-probe instrument reveals in the biological
representation space while explicitly carrying forward the incomplete
sign-instability calibration.

Arm-B biological results may be used descriptively and comparatively to
study questions such as:

- whether supervised linear information is accessible in raw protein
  representations where the SAE arm is weak or absent;
- how sparse the selected raw-coordinate supports are;
- how stable those supports are under the frozen resampling machinery;
- whether coordinates recur across perturbations;
- whether selected coefficients display sign variation;
- how these patterns differ across preregistered layers;
- and whether raw-representation accessibility is consistent with
  information being distributed or misaligned with the SAE basis.

These analyses do not, by themselves, constitute confirmatory evidence
of calibrated recurring-coordinate sign instability.

---

## 5. Prohibited reinterpretations

The following are prohibited under this amendment:

1. relabeling S7-v2 as PASS;
2. lowering `R >= 71` or `M >= 8` and reclassifying the archived S7-v2
   result;
3. redefining the frozen nine-cell acceptance region;
4. rerunning S7-v2 in namespace `930001-930100`;
5. treating `R >= 71` or `M >= 8` as validated protein-data thresholds;
6. describing biological sign variation as confirmatory evidence of
   signed-support instability solely on the basis of S7-v2;
7. using biological outcomes to retrospectively redesign the S7-v2
   decision rule;
8. selecting a gamma threshold from the S7-v2 archive.

---

## 6. Biological Arm-B evidential status

Unless a separate prospective calibration and decision contract is
frozen before the relevant biological outcome is accessed, Arm-B
biological stability/sign analyses under this continuation are:

**EXPLORATORY / DESCRIPTIVE / CALIBRATION-LIMITED.**

This designation does not prevent Arm B from contributing to the broader
Experiment 04 comparison between:

- SAE-feature accessibility, and
- supervised accessibility in the raw representation basis.

However, the strength of any biological claim must reflect the
calibration limitation documented here.

---

## 7. Scientific firewall at amendment freeze

At the time this amendment is frozen:

- `910001-910100` — CONSUMED / CLOSED
- `920001-920100` — CONSUMED / CLOSED
- `930001-930100` — CONSUMED / CLOSED
- `4000-4099` — UNOPENED
- `2000-2099` — SEALED
- gamma — NONE
- S7-v2 — EVALUATED ONCE / REJECTED
- biological Arm-B continuation under this amendment — NOT YET EXECUTED

No biological activation, biological probe fit, validation seed, or new
calibration namespace is opened by this documentation-only amendment.

---

## 8. North-star interpretation

The purpose of Experiment 04 remains to distinguish absence of accessible
biological information from basis misalignment or distributed
accessibility.

The S7-v2 rejection is retained as a real calibration limitation.

The continuation decision is therefore not that the calibration
succeeded, but that the corrected instrument has demonstrated sufficient
operational behavior to support a clearly labeled exploratory biological
comparison while preserving the failed strong-calibration result.
