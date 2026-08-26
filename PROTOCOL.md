# Program protocol

Scope: whether biological information encoded in protein-foundation-model representations generalizes across sequence divergence — the question that joins the generalization failure found in [bio-capability-probing](https://github.com/allanochola/bio-capability-probing) to the context- and architecture-dependence found in [protein-foundation-models](https://github.com/allanochola/protein-foundation-models).

Method discipline shared by every experiment in this repository:

- Each experiment freezes an experiment-level `PROTOCOL.md` — hypotheses, splits, baselines, decision bands, and technical kill criteria — **before any embedding is extracted**. Preregistration is enforced by ordering.
- Generalization is tested against explicit divergence controls (sequence-identity cluster-held-out splits), never a random split alone.
- Every representation probe is compared against a non-representation baseline, so "the model encodes X" is distinguishable from trivial local cues.
- Effects are defined relative to baselines, with **cluster-level** confidence intervals (residues within a protein, and proteins within a family, are not independent).
- One experiment at a time. A new experiment is added only after the previous one returns a clear result — the repository grows by earning it, not by accumulation.

Current experiment: [`experiments/01-secondary-structure/PROTOCOL.md`](experiments/01-secondary-structure/PROTOCOL.md).
