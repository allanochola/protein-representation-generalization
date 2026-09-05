# Experiment 04 — No Public Biological Checkpoint Publication

## Status

**FROZEN BEFORE THE FIRST PROTECTED PHASE-P BIOLOGICAL FIT.**

The repository hosting the scientific and recovery branches is public.

Therefore the existing GitHub recovery branch is not an authorized storage
location for result-bearing Phase-P biological checkpoint artifacts.

## 1. Public recovery branch restriction

Branch:

`recovery/exp04-phase-p-checkpoints`

MUST NOT receive any real Phase-P artifact containing biological result
values produced after protected execution begins.

This prohibition includes, without limitation:

- `main_per_perturbation.csv`
- `permutation_null_per_perturbation.csv`
- partial or complete copies of either CSV
- support coordinates or signed supports derived from biological fits
- AUROC values
- selected C values
- recurrence/statistical outputs
- permutation-null results
- any recovery bundle from which biological result rows can be recovered

The earlier dummy transport-test files remain non-biological and are not
affected by this prohibition.

## 2. What may remain on the public recovery branch

The public recovery branch may contain only non-result-bearing operational
records such as:

- frozen recovery policy text
- scientific HEAD identifiers
- runner SHA-256 identifiers
- checkpoint protocol specifications
- non-biological dummy transport evidence
- metadata that does not disclose biological result values

## 3. Exact enabled execution identity

Scientific branch:

`exp04-depth-and-basis`

Enabled scientific HEAD:

`5277f686ad09ead8921462cb9ed9a53324007c42`

Enabled runner SHA-256:

`e0a39b9c7a83943248166c6251ef273c9505dfece23eff4cbb6531c163cbaeec`

This identity remains the sole authorized Phase-P execution identity.

## 4. Private durable persistence prerequisite

Before the first protected biological fit, a durable checkpoint destination
that does not publish biological result artifacts publicly must be:

1. identified;
2. shown to be non-public for the intended checkpoint objects;
3. tested using non-biological dummy bytes;
4. verified by fresh round-trip retrieval and byte hashes;
5. frozen as the authorized result-bearing recovery destination.

No real Phase-P result-bearing checkpoint may be written to the public GitHub
recovery branch as a substitute.

## 5. Launch boundary

At this policy freeze:

- Phase P source: **ENABLED**
- Phase P execution: **NOT STARTED**
- production output directory: **ABSENT**
- protected biological seeds consumed: **ZERO**
- public result-bearing checkpoint publication: **PROHIBITED**
- private durable checkpoint backend: **NOT YET FROZEN**

Therefore the first protected biological fit remains prohibited until the
private durable checkpoint boundary is completed.

This restriction changes no scientific mechanics, seeds, outputs, stopping
rules, interpretation rules, or recovery semantics.
