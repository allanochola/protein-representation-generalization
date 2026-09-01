# Experiment 03 — first biological model-contact recovery record

**Status:** FIRST CONTACT OCCURRED; ORIGINAL LOCAL JSON LOST IN KAGGLE RESET

The first Experiment-03 biological model contact occurred after the complete
pre-contact chain had been committed and pushed through model-provenance commit
`978b14f`.

The integration run processed exactly one frozen discovery-positive protein:

- identifier: `P85006`
- frozen class: positive
- sequence length: 28
- sequence SHA-256:
  `4650bfdfac229fc19979dd57ed6b1fa5218085f0a4d5d309f4fee58867395ec9`

Observed integration result:

- device: CPU
- ESM checkpoint: pinned `facebook/esm2_t33_650M_UR50D`
- representation layer: 18
- token count: 30
- residue embedding shape: `(28, 1280)`
- InterPLM SAE residue activation shape: `(28, 10240)`
- residue-max protein vector shape: `(10240,)`
- feature ranking observed: false
- feature nomination observed: false
- confirmatory sequences processed: false
- integration status: PASS

The Hugging Face `EsmModel` loader reported unused language-model-head weights
and missing pooler weights. Neither component was used for the frozen layer-18
residue representation.

The run wrote an intended local artifact:

`stage1_model_contact/FIRST_MODEL_CONTACT.json`

before the Kaggle working runtime subsequently reset.

The reset removed `/kaggle/working`, including the uncommitted JSON artifact
and repository checkout. The scientific event itself had already occurred and
must not be reclassified as "no model contact."

No latent identity, ranked feature, feature association, confirmatory score,
or confirmatory sequence was inspected before the reset.

## Recovery rule

The exact frozen one-protein integration procedure may now be rerun solely to
reproduce and persist the lost engineering artifact.

That rerun is a reproduction of the already-observed first-contact event, not
a new first-contact decision or an opportunity to modify the frozen pipeline.

Any mismatch in:

- sequence identifier or SHA-256;
- token count;
- layer-18 shape;
- SAE shape;
- pooling shape;
- finite-value checks;

is a technical discrepancy and stops the pipeline before full discovery
extraction.
