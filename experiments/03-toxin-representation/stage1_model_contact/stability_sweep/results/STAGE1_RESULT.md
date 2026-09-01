# Experiment 03 Stage 1 result

**Status: FAIL — confirmatory stage remains closed.**

The frozen biological SAE stability sweep was executed once on the committed
278 × 10,240 discovery matrix.

## N=139 nominated signed features

1. 4983:− — d = −0.188818
2. 9573:− — d = −0.187280
3. 2073:+ — d = +0.186379
4. 1679:− — d = −0.182887
5. 2221:− — d = −0.182022

## Frozen three-way stability gate

- median pairwise Jaccard: 0.428571
  - required: >=0.60
  - FAIL

- recurrent nominated features: 1 of 5
  - recurrence definition: inclusion frequency >=0.80
  - required: >=4 of 5
  - FAIL

- median fixed-top-5 concentration: 0.005882
  - required: >=0.35
  - FAIL

Overall Stage-1 verdict: **FAIL**.

All three preregistered stability components failed.

## Recurrence

- 4983:− — 0.95
- 9573:− — 0.76
- 2073:+ — 0.57
- 1679:− — 0.61
- 2221:− — 0.48

Only one nominated signed feature satisfied the frozen >=0.80 recurrence rule.

Single-feature statistics remain descriptive only and cannot produce an
alternative verdict.

## Length-stratum limitation

The >150 stratum is exhaustion-limited under the frozen discovery geometry.

All five N=139 nominated features retain their full-set signs in the >150
stratum, whereas multiple nominated features weaken or reverse sign in shorter
strata.

This is reported descriptively only. It does not rescue the failed stability
gate and must not be interpreted as independent evidence of stable nomination
over alternative long-protein discovery memberships.

## Confirmatory firewall

No confirmatory sequence was embedded, scored, or inspected during Stage 1.

Because Stage 1 failed:

- no `CONFIRMATORY_FEATURE_SPEC.json` is created;
- no confirmatory representation extraction is permitted;
- no confirmatory ΔTPR is computed;
- no layer, SAE, pooling rule, feature-set size, or stability threshold is
  changed in response to this result.

## Interpretation

Under the preregistered ESM-2 650M layer-18 / normalized InterPLM SAE /
residue-max representation, the discovery data do not support a compact,
stable k=5 toxin-associated representation.

Class-associated latent differences are present in the full discovery sample,
but their identities are unstable under the frozen perturbation procedure and
the fixed top five capture only a very small fraction of total differential
latent-score mass.

Experiment 03 therefore closes at Stage 1 without confirmatory evaluation.
