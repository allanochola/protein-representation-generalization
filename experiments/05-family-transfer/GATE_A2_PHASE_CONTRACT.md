# Gate A2 phase contract

**Status:** Frozen before confirmatory metadata access. A2-I is implemented but
hard-disabled. A2-S and A2-C are not authorized.

## Purpose and acknowledged leakage

Gate A2 opens confirmatory family metadata required by Gate C. This is not
outcome evaluation, but it leaks weak information about confirmatory difficulty.
The opening is necessary and is recorded explicitly.

A2 may not alter the comparator, Layer 24, the estimand, materiality threshold,
grouping parameters, or any scientific decision rule.

## Frozen inputs

- positive membership:
  `experiments/03-toxin-representation/stage1_model_blind/confirmatory_positive_universe.tsv`
- expected positive rows: 161
- negative membership:
  `experiments/03-toxin-representation/stage1_model_blind/confirmatory_negative_universe.tsv`
- expected negative rows: 3,541

No confirmatory FASTA is currently tracked.

## A2-I — membership intake

A2-I may open only the two frozen TSV membership files and the already-open
278-record discovery manifest.

It may report and archive only:

- exact input SHA-256 values;
- input headers;
- row counts;
- unique accession counts;
- accession overlap between positive and negative confirmatory membership;
- accession overlap with discovery;
- frozen-length presence and basic integrity, but no length distribution;
- a canonical accession-only manifest;
- explicit `confirmatory_metadata_accessed: true`;
- explicit `confirmatory_outcomes_accessed: false`.

Exactly one accession column must resolve from:

`accession, identifier, protein_id, uniprot_accession`

A length column is optional at intake, but at most one may resolve from:

`length, frozen_length, sequence_length, retrieved_length`

Ambiguous accession or length fields stop with
`A2_INTAKE_SCHEMA_MISMATCH`. A missing accession field also stops. No alias may
be added after headers are observed without a prospective amendment.

Columns containing any of the following are prohibited:

`auroc, auprc, tpr, fpr, score, prediction, probability, threshold, embedding, activation`

A2-I performs no sequence retrieval, annotation, clustering, family assignment,
component calculation, model loading, prediction, scoring, or evaluation.

## A2-S — sequence recovery and grouping scans

A2-S remains unavailable until the A2-I archive is committed.

Before authorization it must freeze:

- sequence source and release;
- handling of obsolete, replaced, missing, or length-mismatched accessions;
- canonical FASTA serialization;
- Pfam 37 `--cut_ga`;
- the inherited MMseqs2 source and parameters;
- archive-before-census ordering.

A2-S may archive raw retrieval and scan products. It may not compute components
or geometry.

## A2-C — confirmatory geometry census

A2-C remains unavailable until the A2-S archive is committed.

It will read only committed A2-I and A2-S artifacts and report:

- positive, negative, and mixed component counts;
- negative-component size distribution and concentration;
- number of independent negative threshold-setting units;
- cross-label Pfam and MMseqs2 edge provenance;
- discovery-to-confirmatory component bridges;
- whether the 161 positives remain family-disjoint;
- inputs required by Gate C.

A2-C may not load either model or compute predictions, scores, thresholds,
AUROC, AUPRC, TPR, FPR, or the Gate C resolvability surface.

## Ordering

`A2-I freeze -> authorize -> execute -> audit -> archive -> close`

then

`A2-S freeze -> authorize -> execute -> audit -> archive -> close`

then

`A2-C freeze -> authorize -> execute -> audit -> archive -> close`

Gate C remains blocked until A2-C is archived and closed.
