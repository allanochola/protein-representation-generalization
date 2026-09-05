# Experiment 04 — External Publisher Live Dummy Transport Evidence

## Status

**PASS — NON-BIOLOGICAL TRANSPORT ONLY.**

No protected Phase-P biological fit had begun when this evidence was created.

Scientific identity:

- branch: `exp04-depth-and-basis`
- HEAD: `5277f686ad09ead8921462cb9ed9a53324007c42`
- enabled runner SHA-256: `e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec`

Recovery publisher:

- parent recovery commit: `9f0e6fa76daa198b0ecb066af8e87794358ebfd2`
- transport-enabled SHA-256: `48f09d3d1da3e7892311a898c14e243e2e94dc909abe13ddd3aae8cb8b873c1f`

Private checkpoint backend:

`ocholla/exp04-phase-p-private-checkpoints`

Visibility:

**PRIVATE**

## Transport test

The reusable publisher transport path created exactly one new Kaggle Dataset
version containing NON-BIOLOGICAL dummy bytes only.

No `-d` or `--delete-old-versions` option was used.

The test:

1. waited for asynchronous Dataset readiness;
2. reconfirmed PRIVATE visibility;
3. verified remote file visibility;
4. fresh-downloaded all three dummy files;
5. verified exact SHA-256 identity.

Original dummy SHA-256:

`7b191489bc390df25da4c2e57381e4d7fa2f5848eed88db1cd92a84e40764d94`

Version dummy SHA-256:

`c16ce846f9ef48c63abf50194434b8bbbcfab0aaf266c93c111eac3a6578f53b`

Publisher transport dummy SHA-256:

`3d02534325dcd16c17b136a2a489d6fedb517908ab60c2362f552e3a01b60efb`

## Python 3.12 recovery note

The first live-dummy test attempt stopped before any Dataset-version request
because a dynamically loaded module had not been registered in `sys.modules`
before `exec_module()`. Python 3.12 `dataclasses` required that registration.

The publisher file itself was preserved byte-for-byte. The recovery attempt
registered the module in memory before execution and resumed from the
pre-mutation boundary.

## Safety boundary

This transport test did not:

- execute Phase P;
- load biological matrices;
- load biological labels;
- instantiate RNG or SeedSequence;
- consume protected seed namespaces;
- write production Phase-P output;
- publish biological results.

Biological live publication remains disabled from the publisher's ordinary
CLI entry point.

Phase P remains:

**ENABLED BUT NOT STARTED**

Protected seed consumption remains:

**ZERO**
