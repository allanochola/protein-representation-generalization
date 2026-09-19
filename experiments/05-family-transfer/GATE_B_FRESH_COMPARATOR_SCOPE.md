# Gate B — Fresh Discovery-Only Comparator Scope

**Status:** scope frozen; feature/model selection procedure not yet frozen or
executed.

## Decision forced by provenance loss

The historical Gate-D random forest with AUROC 0.9494 is not an admissible
Experiment 05 confirmatory comparator. Its complete training memberships do not
survive, so cross-accession sequence and biological-family contamination cannot
be excluded.

The 0.9494 result remains historical shortcut-rejection evidence only. It may
motivate a strong comparator but may not be reused, refit by presumed
membership, or treated as a benchmark that the new comparator must reproduce.

Fresh discovery-only comparator construction is the default path and lies on
the critical path before A2.

## Allowed development data

Gate B may use only:

- frozen discovery-positive sequences;
- frozen discovery-negative sequences;
- the frozen A1 family assignments once A1 is complete;
- prospectively frozen sequence-derived, PLM-free features;
- family-grouped development resampling.

Gate B may not access confirmatory sequences, family geometry, annotations,
scores, embeddings, labels joined to features, or performance summaries.

For any family-blocked Stage-1 construction, discovery positives marked
`UNASSIGNED` by A1 are excluded from both fitting and evaluation. They may not
be encoded as singleton groups or pooled into a synthetic family. Development
reports must carry the assigned-positive fraction so comparator adequacy is not
interpreted as applying to the full discovery-positive universe.

## Required specification before fitting

A later executable Gate-B specification must freeze:

1. exact discovery manifests and hashes;
2. allowed sequence-only feature blocks and software versions;
3. bounded classifier and hyperparameter families;
4. preprocessing and missing-value rules;
5. family-grouped resampling driven by A1 assignments;
6. the development-only selection metric and tie/tolerance rule;
7. calibration interface without using calibration families for tuning;
8. deterministic execution identity and output schema;
9. integrity invariants and the failure classification;
10. a single final comparator specification before A2 opens.

No confirmatory comparison is authorized by this scope document.

## Gate-B exit condition

Gate B is complete only when one provenance-clean comparator is frozen with its
feature extractor, classifier, hyperparameters, preprocessing, and code/input
hashes. Failure to establish one closes Gate C under comparator-adequacy Gate C
in the committed A-E nomenclature.
