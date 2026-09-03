# Experiment 04 — Arm-B diagnostic artifact-loss recovery

Status: FROZEN POST-DIAGNOSTIC / PRE-RECONSTRUCTION

## Historical execution

The Arm-B post-failure architecture diagnostic was executed from:

    d240442046200801b73743446aafcdda10314573

using diagnostic namespace:

    910001-910100

The execution completed:

    273 / 273 cells

and reached the runner's terminal completion state.

Therefore `910001-910100` is CONSUMED and must never again be described
as unopened or as a fresh diagnostic namespace.

## Artifact loss

After successful completion, the Kaggle runtime reset before the generated
diagnostic artifacts were committed or archived outside the ephemeral runtime.

The following completed-run artifacts were lost:

- `architecture_diagnostic/arm_b_post_failure_architecture_per_perturbation.csv`
- `architecture_diagnostic/arm_b_post_failure_architecture_cell_summary.csv`
- `architecture_diagnostic/arm_b_post_failure_architecture_N120_vs_N139.csv`
- `architecture_diagnostic/arm_b_post_failure_architecture_checkpoint_manifest.json`

The preserved console log records successful completion but does not contain
the numerical contents of these files.

This is an artifact-loss event, not a failed diagnostic execution.

## Recovery rule

Artifact reconstruction is permitted only by rerunning the exact frozen
diagnostic implementation from:

    d240442046200801b73743446aafcdda10314573

with the same already-consumed namespace:

    910001-910100

This rerun is classified solely as deterministic artifact reconstruction.

It is not:

- a new diagnostic;
- a second independent experiment;
- additional independent evidence;
- authorization to select a new seed block;
- authorization to alter the runner, generator, grid, seed derivation,
  blinding rules, output schema or interpretation rules.

No intermediate reconstruction result may be used to alter execution.

## Protected namespaces

    910001-910100 = CONSUMED; exact artifact reconstruction only
    4000-4099     = UNOPENED calibration reserve
    2000-2099     = SEALED independent validation

Neither `4000-4099` nor `2000-2099` may be used for recovery.

## Required sequence

Before reconstruction:

1. commit this recovery record alone;
2. push and remote-verify the recovery-record commit;
3. verify the diagnostic runner is byte-identical to the runner at `d240442`;
4. verify the reconstruction output directory contains no authoritative files.

After reconstruction:

1. verify 273/273 completed cells;
2. verify all four authoritative files exist;
3. record SHA-256 hashes and file sizes immediately;
4. commit the reconstructed artifacts before scientific inspection;
5. push and remote-verify that archive checkpoint.

No P/S/I/G threshold selection and no independent-validation access are
authorized by this recovery record.
