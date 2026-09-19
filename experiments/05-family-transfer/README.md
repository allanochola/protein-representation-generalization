# Experiment 05 — Family-Transfer Toxin Detection

**Status: PHASE 0 / PRE-PROTOCOL — confirmatory computation prohibited**

Experiment 05 is a new scientific object created from the exact Experiment 04
closure commit `1306a5ff30a99c92433c8e9970df5e7269db468c`.

Experiment 04 remains closed. Nothing in this directory authorizes reopening,
recomputing, reinterpreting, or spending its protected data.

## North star

> Does ESM-2 provide a transferable increase in toxin-detection sensitivity
> over a strong frozen sequence-only predictor at a fixed 5% false-positive
> rate when biological families are genuinely held out?

Primary estimand:

`DeltaTPR@FPR5 = TPR_ESM@5%FPR - TPR_SEQ@5%FPR`

Minimum scientifically interesting effect:

`DeltaTPR@FPR5 = +0.10`

This threshold is fixed for Phase 0 and may not be weakened in response to a
small candidate universe.

## Phase-0 deliverables

1. `PRE_PROTOCOL.md` — boundaries, estimand, gates, and decision sequence.
2. `CANDIDATE_UNIVERSE_SPEC.md` — provenance and metadata-only census plan.
3. `FAMILY_INDEPENDENCE_AUDIT.md` — candidate biological-unit definitions and
   leakage audit.
4. `COMPARATOR_CENSUS.md` — sequence-only comparator candidates and selection
   criteria.
5. `RESOLVABILITY_PLAN.md` — family-level power, precision, and FPR-tail plan.
6. `FIREWALL.md` — protected-data rules and authorization conditions.

These documents are design scaffolds, not a frozen protocol. Phase 0 may end
in pre-data closure if any gate fails.

## Prohibited until protocol freeze

- ESM embedding extraction for confirmatory candidates;
- fitting or scoring either classifier on protected families;
- examining protected labels together with predictions or representations;
- threshold selection from protected negatives;
- layer selection using held-out toxin-transfer performance;
- changing the `+0.10` target after learning protected results.
