# Experiment 04 — Phase-P Recovery Policy Enabled-Identity Addendum

## Status

**FROZEN AFTER THE SEPARATE MINIMAL PHASE-P ENABLEMENT COMMIT AND BEFORE
THE FIRST PROTECTED BIOLOGICAL FIT.**

This document is an append-only recovery-policy identity update.

It does not modify the previously frozen crash-recovery semantics.

It does not execute Phase P.

It does not instantiate, materialize, inspect, or consume any protected
biological or permutation-null seed.

## 1. Superseded pre-enablement identity

The original recovery policy was frozen while the scientific source remained
hard-disabled.

That earlier frozen scientific identity was:

- scientific HEAD:
  `3e52262358914de0089e72491ce413d3c91e0a99`
- production runner SHA-256:
  `93940e890541ea437aa51c9bc3085e704d6a1ed04b3318937b14c0a7d988f3c2`

That identity remains historically valid for the pre-enablement state but is
no longer the executable Phase-P recovery identity.

## 2. Authorization boundary

The separate prospective biological-execution authorization commit is:

`947d66bbce0705a185794f284cbd1ee891f0beb4`

That commit did not modify or execute the production runner.

## 3. Enabled scientific recovery identity

The exact scientific identity authorized for first Phase-P biological
execution and all subsequent resume/recovery operations is now:

Scientific branch:

`exp04-depth-and-basis`

Enabled scientific HEAD:

`5277f686ad09ead8921462cb9ed9a53324007c42`

Enabled production runner:

`experiments/04-depth-and-basis/phase_p_biological_probe/run_phase_p_biological_probe.py`

Enabled runner SHA-256:

`e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec`

These values are immutable for this execution identity.

## 4. Recovery rule after first protected fit begins

Once the first protected Phase-P fit begins:

- `5277f686ad09ead8921462cb9ed9a53324007c42` is the only valid scientific HEAD for this execution;
- `e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec` is the only valid production-runner SHA-256;
- no fresh execution identity may be substituted;
- no new seed namespace may be selected;
- no completed valid atomic row may be rerun or repaired;
- any interruption is a resume of this exact execution identity;
- recovery must restore only independently verified durable checkpoint bytes;
- restored artifacts must be accepted only if the frozen runner's existing
  manifest/schema/key/semantic validation passes exactly.

Any scientific HEAD or runner-SHA mismatch is a hard STOP.

## 5. Pre-first-fit state

At this addendum freeze:

- scientific source: **ENABLED**
- scientific HEAD: `5277f686ad09ead8921462cb9ed9a53324007c42`
- enabled runner SHA-256: `e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec`
- scientific worktree/index: **CLEAN**
- production output directory: **ABSENT**
- main namespace `1000001-1000100`: **AUTHORIZED / UNCONSUMED**
- null namespace `1100001-1100100`: **AUTHORIZED / UNCONSUMED**
- first protected biological fit: **NOT STARTED**
- protected seeds consumed: **ZERO**

## 6. Existing recovery semantics remain unchanged

This addendum changes only the scientific identity recognized by recovery.

The previously frozen rules remain in force, including:

- recovery branch remains append-only;
- no force-push, reset, or history rewrite;
- checkpoint publication is operational only;
- output values must never alter execution mechanics;
- manifest mismatch is a hard STOP;
- malformed/duplicate/unexpected rows are hard STOP conditions;
- partial trailing writes are not automatically repaired;
- uncertain execution identity or rerun status is a hard STOP;
- completed-state re-entry is validation-only;
- no post-hoc tuning or interpretation-responsive modification is permitted.

## 7. Execution boundary

Freezing this addendum does not itself execute Phase P.

Only after this addendum is committed, pushed, and remote-verified may the
workflow proceed to the final launch boundary.

The first protected fit will consume the already-authorized execution identity.
After that point, interruption means resume only.
