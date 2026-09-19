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
7. `IMPLEMENTATION_FAILURE_CLASSIFICATION.md` — frozen distinction between a
   void implementation run, a valid surprising result, and a scientific gate
   failure.
8. `GATE_A_SPLIT_AND_ORDER.md` — frozen A1/A2 firewall, run order, routing
   table, and A1 execution discipline.
9. `PFAM_PROVENANCE_ARCHAEOLOGY.md` — recovered historical Pfam semantics,
   hashes, and the missing-artifact boundary.
10. `COMPARATOR_PROVENANCE_ARCHAEOLOGY.md` — recovered 0.9494 Gate-D model
    construction and unresolved cross-accession/family contamination status.

These documents are Phase-0 scaffolds, not a complete frozen confirmatory
protocol. Clauses explicitly labelled frozen are binding and cannot be revised
in response to census, simulation, or protected results. Phase 0 may end in
pre-data closure if any gate fails.

## Prohibited until protocol freeze

- ESM embedding extraction for confirmatory candidates;
- fitting or scoring either classifier on protected families;
- examining protected labels together with predictions or representations;
- threshold selection from protected negatives;
- layer selection using held-out toxin-transfer performance;
- changing the `+0.10` target after learning protected results.

## Frozen primary representation

The primary representation is raw ESM-2 650M **layer 24**. It was selected
while the confirmatory universe remained dark as an admissible representative
of the mid-to-late-layer plateau observed in Experiment 04.

Layer 24 is not claimed to be the optimal ESM-2 layer. A null Experiment 05
result is therefore a result about this frozen layer under the specified
family holdout, not a universal negative claim about ESM-2. Layer 18 is
secondary and reference-only and may not replace layer 24 after unblinding.
