# Experiment 03 — independent synthetic validation result

**Status:** PASS

The frozen Experiment 03 feature-set instrument was evaluated on an
independent synthetic seed namespace after calibration was closed.

No threshold search or parameter selection was performed during this run.

## Frozen instrument

A dataset passes the feature-set instrument only if all three conditions hold:

1. median pairwise Jaccard >= 0.60
2. at least 4 of 5 full-dataset nominated signed latents recur in >=80% of
   perturbations
3. median fixed-top-5 concentration >= 0.35

The concentration threshold 0.35 was fixed before independent validation.

## Independent seed namespace

Validation outer seeds used:

10,000,000
+ 100,000 * regime_index
+ 1,000 * N
+ replicate_index

The generator used `numpy.random.default_rng`.

No calibration outer seed was reused.

## Primary N=139 result

| Regime | Final instrument PASS rate | Frozen criterion | Result |
|---|---:|---:|---|
| B near tie | 0.100 | <=0.100 | PASS |
| C stable five | 0.816 | >=0.700 | PASS |
| D diffuse sixteen | 0.064 | <=0.100 | PASS |

Overall independent validation: **PASS**.

The B near-tie result lies exactly on the preregistered 0.10 upper boundary.
It therefore passes under the frozen `<=0.10` rule, but with no margin.

## Discovery-size behavior

Final instrument PASS rates:

| Regime | N=100 | N=120 | N=139 |
|---|---:|---:|---:|
| A stable single | 0.078 | 0.058 | 0.078 |
| B near tie | 0.104 | 0.088 | 0.100 |
| C stable five | 0.546 | 0.676 | 0.816 |
| D diffuse sixteen | 0.054 | 0.088 | 0.064 |

Stable-five recovery increases with discovery support, while the diffuse-sixteen
negative control remains below the frozen primary false-positive ceiling at
N=139.

## Interpretation

The independently validated instrument supports detection of a reproducible,
compact five-feature representation under the frozen synthetic model.

It does not establish biological meaning, causal mechanism, toxin-specific
representation, or confirmatory performance.

Those remain questions for the biological stages of Experiment 03.

## Model-contact boundary

No Experiment 03 biological ESM embedding, SAE activation, biological feature
score, or confirmatory representation statistic was observed during
calibration or independent synthetic validation.

The next permitted step is to freeze the biological stability-sweep
specification before first Experiment 03 model contact.
