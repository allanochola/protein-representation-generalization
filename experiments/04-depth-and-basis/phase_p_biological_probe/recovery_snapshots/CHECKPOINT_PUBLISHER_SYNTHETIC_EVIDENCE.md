# Experiment 04 — Checkpoint Publisher Synthetic Evidence

## Status

**PASS — NO BIOLOGICAL EXECUTION.**

The external recovery publisher was implemented and tested before the first
protected Phase-P biological fit.

Publisher:

`experiments/04-depth-and-basis/phase_p_biological_probe/recovery_snapshots/phase_p_checkpoint_publisher.py`

Publisher SHA-256:

`14aac71efb5480be3f66f42aff1e53bd3cc9d811ce97490544a3d0ad5f64a166`

Scientific execution identity remained:

- branch: `exp04-depth-and-basis`
- HEAD: `5277f686ad09ead8921462cb9ed9a53324007c42`
- runner SHA-256: `e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec`

## Synthetic-only test scope

The self-test used temporary synthetic CSV and JSON files only.

It did not:

- import Experiment-04 scientific code;
- load biological matrices;
- load biological labels;
- instantiate RNG or SeedSequence;
- access protected seed namespaces;
- execute a biological fit;
- create or version a Kaggle Dataset;
- upload any file to Kaggle.

## Frozen mechanics exercised

PASS:

1. zero durable rows do not trigger publication;
2. nine newly durable rows do not trigger publication;
3. ten newly durable rows trigger the fixed main-arm cadence;
4. changing opaque synthetic result values without changing row count does
   not change the publication decision;
5. remote verified row count is used as the cadence baseline;
6. main-arm completion triggers the mandatory main boundary;
7. null-arm cadence is fixed at ten newly durable rows;
8. null-arm completion triggers the mandatory null boundary;
9. final completion can trigger the final boundary;
10. no duplicate publication occurs when remote and local counts match;
11. impossible remote-ahead state is rejected;
12. null-before-main state is rejected;
13. unexpected production-output files are rejected;
14. permitted artifacts are staged byte-for-byte;
15. no production artifact is sorted, filtered, repaired, normalized,
    truncated, or otherwise transformed.

## Important limitation

The publisher's live Kaggle transport is intentionally not enabled by this
commit.

The next preregistered boundary is one live **NON-BIOLOGICAL** transport test
against the already-frozen PRIVATE Kaggle Dataset.

Phase P remains:

**ENABLED BUT NOT STARTED**

Protected seed consumption remains:

**ZERO**
