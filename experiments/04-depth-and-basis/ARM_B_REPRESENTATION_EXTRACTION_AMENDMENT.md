# Experiment 04 — Arm-B Representation Extraction Amendment

## Status

**FROZEN BEFORE ARM-B BIOLOGICAL RUNNER IMPLEMENTATION AND BEFORE FRESH
EXPERIMENT-04 BIOLOGICAL EXECUTION**

This amendment resolves implementation-level representation details exposed by
the read-only Experiment-03 provenance audit.

It does not alter:

- the Experiment-04 scientific question;
- the discovery universe;
- the frozen layer set;
- the probe family;
- the frozen C grid;
- the corrected Arm-B resampling mechanics;
- the calibration interpretation;
- the exploratory / descriptive status of biological Arm B;
- or any protected seed boundary.

Fresh biological execution remains closed.

## 1. Reason for this amendment

Experiment-03 frozen artifacts explicitly designate ESM representation layer 18.

They also record:

- ESM-2 650M;
- hidden width 1,280;
- special-token exclusion;
- biological sequence eligibility of 1–1,022 residues;
- successful layer-18 first biological model contact.

However, the exact Python program that produced the complete Experiment-03
biological extraction matrix was not archived.

The repository's generic reusable ESM extractor predates Experiment 03 and
defaults to layer 17 for the earlier secondary-structure extraction path.
It is not evidence that Experiment 03 used layer 17.

Git-history audit found no archived executable statement sufficient to prove
the precise hidden-state tuple index used by the unavailable Experiment-03
full-discovery extraction implementation.

Therefore Experiment 04 distinguishes:

1. the representation layer Experiment 03 explicitly designated and recorded;
2. exact implementation-level equivalence to the unavailable historical
   extractor.

The first is established.

The second cannot be established.

No stronger historical claim is made.

## 2. Layer semantics for Experiment 04 Arm B

The already-frozen Experiment-04 layer set remains unchanged:

- 1
- 9
- 18
- 24
- 30
- 33

For the prospective Experiment-04 Arm-B implementation:

**Layer k means output.hidden_states[k] returned by the frozen Hugging Face
ESM model invocation.**

Accordingly, the exact extraction indices are:

    1, 9, 18, 24, 30, 33

No offset, renumbering, nearest-layer substitution, or post-result remapping
is permitted.

Layer 18 remains the:

**Experiment-03 protocol-designated anchor layer.**

This means that Experiment-03 frozen artifacts designated and recorded
layer 18.

It does not claim that byte-for-byte or implementation-level equivalence to
the unavailable Experiment-03 full-discovery raw ESM extraction program has
been demonstrated.

The five other layers remain the prospectively frozen fresh biological layers:

- 1
- 9
- 24
- 30
- 33

No post-hoc best-layer selection is permitted.

## 3. Sequence handling

Experiment 04 inherits the already-frozen Experiment-03 biological sequence
eligibility rule:

    1 <= biological sequence length <= 1022

No truncation is permitted.

No sliding windows, chunking, window averaging, partial-sequence substitution,
or alternate long-sequence handling may be introduced.

A sequence outside the frozen range is a technical hard stop.

## 4. Special-token handling

For a biological sequence of length L, Experiment-04 Arm-B extraction must
retain exactly the L biological residue positions and exclude all model
special tokens.

Under the prospective Hugging Face interface, the biological residue slice is:

    hidden_state[1:L+1]

The implementation must verify that the resulting first dimension is exactly L.

Excluded positions include:

- BOS / CLS;
- EOS;
- padding;
- any additional framework-specific special token.

A special-token alignment failure is a technical hard stop.

## 5. Raw ESM protein representation

Experiment-04 Arm B uses the raw ESM hidden representation.

For every authorized protein and every frozen layer:

1. obtain the residue-level hidden state;
2. retain biological residues only;
3. verify shape (L, 1280);
4. compute the coordinate-wise maximum over the residue axis;
5. produce exactly one vector of shape (1280,).

Formally:

    v[p,k,j] = max over biological residues r of h[p,k,r,j]

where:

- p is protein;
- k is frozen layer;
- r is biological residue;
- j is raw ESM coordinate.

This raw-ESM pooling implementation is prospective Experiment-04 code.

It must not be described as reuse of the unavailable Experiment-03
full-discovery extraction implementation.

No alternative mean pooling, median pooling, sum pooling, top-q pooling,
CLS pooling, EOS pooling, attention pooling, or length-normalized pooling may
be substituted after biological results are visible.

## 6. Dtype and numerical representation

The repository's earlier generic ESM extractor stored per-residue vectors as
float16.

That behavior belongs to the earlier secondary-structure extraction path and
is not inherited automatically by Experiment 04 Arm B.

Experiment-04 Arm-B extraction is prospectively frozen as follows.

### Model/extraction computation

No explicit float16 conversion is permitted.

No automatic mixed-precision context is introduced by the Experiment-04
runner.

Residue hidden states are converted, if necessary, to PyTorch float32 before
coordinate-wise maximum pooling.

### Protein-level archive representation

Each pooled raw-ESM protein vector is stored as NumPy float32 with exact shape:

    (1280,)

Any non-finite value is a technical hard stop.

No alternate storage dtype may be chosen after biological results are
observed.

## 7. Experiment-03 comparison language

The following statement is permitted:

**Layer 18 is the Experiment-03 protocol-designated anchor layer.**

The following stronger statement is not supported by the archived repository
and must not be made:

**The Experiment-04 layer-18 raw ESM vector is proven to be generated by the
identical historical Experiment-03 extraction implementation.**

The historical full-discovery extraction-producing program is unavailable.

This is a provenance limitation, not evidence that Experiment 03 used another
layer.

## 8. Biological and confirmatory firewalls

This amendment does not open biological execution.

Confirmatory data remain completely excluded.

Protected seed states remain:

    4000-4099 : UNOPENED
    2000-2099 : SEALED

Consumed synthetic ranges remain consumed / closed:

    910001-910100
    920001-920100
    930001-930100

No new seed range is created by this amendment.

## 9. Next authorized stage

After this amendment is reviewed and frozen in repository history, the next
authorized stage is:

**Implement the Experiment-04 biological Arm-B runner in HARD-DISABLED state.**

That implementation must instantiate this amendment and the existing
Experiment-04 biological execution contract without performing fresh
biological computation.

## 10. Prospective scientific scoping refinements

The following refinements are frozen before fresh Experiment-04 biological
representation extraction or biological probe execution.

They are intended to improve interpretability of Arm B without changing the
underlying biological question, the frozen raw-ESM layer set, the primary
max-pooling rule, the frozen probe family, or the corrected Arm-B resampling
mechanics.

### 10.1 Model-blind realized-partition audit

Before fresh ESM representation extraction, the exact frozen 139-positive /
139-negative discovery universe must undergo a model-blind sequence audit.

This audit may use only already-authorized discovery sequences and metadata.

It must report, by biological class:

- sequence-length distributions;
- the frozen length-stratum counts;
- class-wise empirical length quantiles or equivalent distribution summaries;
- the shape of any observed length separation rather than reducing it to a
  single mean difference;
- the 20 standard amino-acid composition fractions.

This audit is descriptive.

It must not:

- change discovery membership;
- remove proteins;
- create balancing rules;
- alter the frozen N = 100, 120, 139 partitions;
- introduce a biological pass/fail threshold;
- tune the representation;
- or inspect fresh ESM activations.

The purpose is to make simple sequence-level alternatives visible before
representation results are observed.

### 10.2 Frozen simple-sequence baseline

Arm B will include a prospectively frozen 21-dimensional simple-sequence
baseline consisting of:

- biological sequence length;
- the 20 standard amino-acid composition fractions.

Where the Arm-B mechanics are applicable, this baseline must use the same
frozen discovery target-N partitions and the same perturbation identity as the
raw-ESM arm.

The baseline is not a claim that all possible sequence-level confounding has
been removed.

In particular, sequence length as a scalar baseline captures monotone
length-associated separation directly, while the pre-extraction audit is
retained to expose more complicated distributional relationships.

The baseline exists to distinguish:

**raw-representation accessibility**

from the weaker alternative:

**recoverability from simple length and amino-acid composition statistics.**

### 10.3 Paired raw-ESM minus baseline AUROC difference

For each perturbation for which both the raw-ESM arm and 21-dimensional
baseline produce an AUROC, report the paired descriptive difference:

    delta_AUROC_t =
        AUROC_raw_ESM_t - AUROC_sequence_baseline_t

The raw-ESM and baseline values must share the same perturbation identity.

The distribution of this paired difference may be summarized descriptively,
including its median and distributional spread.

No new significance threshold, decision boundary, or biological PASS/FAIL gate
may be created from this statistic.

Its role is to show whether the raw-ESM-versus-simple-sequence difference is
consistent across the already-frozen resampling geometry.

### 10.4 Scoped label-permutation null for support statistics

Because raw ESM coordinates have real anisotropy and correlation structure,
synthetic sparse-support calibration does not by itself establish the null
behavior of L1 support statistics on the biological representation covariance.

Therefore one scoped label-permutation null is prospectively authorized for:

- layer 18 only;
- N = 139 only;
- 100 perturbations;
- the frozen raw-ESM matrix;
- the same corrected Arm-B probe machinery where applicable.

The representation matrix must remain unchanged.

Only the biological labels are permuted for this null.

The null is intended to contextualize:

- support size;
- support recurrence;
- related unsigned support-stability summaries.

It must not be used to:

- create a new biological acceptance threshold;
- replace the failed S7-v2 signed-instability criterion;
- declare a biological PASS or FAIL;
- tune regularization rules after observing results;
- select a preferred layer;
- or redefine the primary Arm-B biological question.

Signed-support instability remains descriptive because the strong S7-v2
signed-instability calibration did not pass its frozen criterion.

### 10.5 Family / cluster interpretation boundary

Protein-level Arm-B perturbation stability is interpreted as robustness within
the frozen discovery universe.

It is not evidence of cross-family toxin generalization.

A raw probe may exploit biologically real family or fold structure, including
toxin-family structure.

Such a result remains relevant to representation accessibility but supports a
different claim from family-held-out generalization.

Where frozen family or cluster identifiers are already available, their
composition may be recorded for each perturbation as descriptive metadata.

No family-held-out redesign or family-based acceptance gate is introduced in
Experiment 04 by this amendment.

### 10.6 Extraction and probing are separate execution phases

Fresh biological representation extraction and biological probing are frozen
as separate execution phases.

#### Phase E — discovery representation extraction

Phase E may:

- load the frozen ESM-2 model;
- process only the already-authorized 278 discovery proteins;
- extract only the six frozen raw-ESM layers:
  1, 9, 18, 24, 30, 33;
- apply the prospectively frozen biological-residue-only coordinate-wise max
  pooling rule;
- archive float32 protein-level matrices;
- write row-identity and provenance manifests;
- compute structural integrity checks and cryptographic hashes.

For each layer the expected matrix geometry is:

    278 x 1280

Phase E must not:

- open or consume a biological perturbation seed namespace;
- perform train/test perturbations;
- perform cross-validation;
- fit an L1 probe;
- compute AUROC;
- compute support size;
- compute recurrence;
- compute signed-support statistics;
- inspect confirmatory data;
- or make biological performance interpretations.

The Phase-E artifacts must pass structural and provenance validation and be
frozen in repository history before Phase P begins.

#### Phase P — exploratory biological probing

Phase P consumes the immutable Phase-E matrices.

Only Phase P may invoke the prospectively authorized biological perturbation
namespace and execute the frozen Arm-B probe mechanics.

The perturbation namespace must be frozen separately before Phase P is enabled.

A failed Phase-E extraction therefore does not consume or retire a biological
probe seed namespace.

### 10.7 Interpretive hierarchy

The Experiment-04 Arm-B biological readout is interpreted in the following
order.

Primary:

1. raw-ESM predictive accessibility;
2. raw-ESM versus the 21-dimensional simple-sequence baseline;
3. the paired per-perturbation raw-ESM minus baseline AUROC difference;
4. the six-layer depth profile.

Supporting:

5. unsigned support size and recurrence, contextualized by the scoped
   layer-18 / N=139 label-permutation null.

Descriptive / calibration-limited:

6. signed-support and coefficient-orientation behavior.

The failure of the frozen S7-v2 strong signed-instability criterion remains
unchanged and must not be reinterpreted as a pass.

### 10.8 Items explicitly unchanged

This amendment does not change:

- the biological discovery universe;
- N = 100, 120, 139;
- the raw-ESM layer set:
  1, 9, 18, 24, 30, 33;
- layer 18 as the Experiment-03 protocol-designated anchor;
- coordinate-wise biological-residue max pooling as the primary raw-ESM
  representation;
- the L1-logistic probe family;
- the frozen C grid;
- the corrected Arm-B perturbation and refit mechanics;
- the exploratory / descriptive / calibration-limited status of biological
  Arm B;
- the confirmatory firewall;
- the failed S7-v2 strong signed-instability verdict;
- or any existing protected seed boundary.

Layer 0 is not added.

Mean pooling is not added.

No family-holdout arm is added.

No new biological decision threshold is added.

No new seed namespace is created by this amendment.

Protected seed states remain:

    4000-4099 : UNOPENED
    2000-2099 : SEALED

Consumed synthetic ranges remain:

    910001-910100
    920001-920100
    930001-930100

Fresh biological extraction remains disabled until separately enabled.

Fresh biological probing remains disabled until separately enabled.
