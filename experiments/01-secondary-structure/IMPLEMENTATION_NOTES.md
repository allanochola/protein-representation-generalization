# Implementation notes

## Confirmatory evaluation attempt 1 — technical failure

The first confirmatory evaluation attempt was terminated by the host operating
system with exit code -9 before producing any evaluation metric.

Post-failure diagnosis showed:

- cached proteins: 11,373
- cached residues: 2,875,432
- embedding dimension: 1,280
- full embedding matrix at float32: approximately 13.71 GB
- Colab host RAM: approximately 12.67 GB

The original evaluator materialized the complete training embedding matrix,
standardized it into another array, and then copied it to a Torch tensor.
The failure is therefore attributable to host-memory exhaustion.

No Q3 accuracy, macro-F1, Delta_ESM, G, bootstrap interval, or experimental
verdict was observed before this implementation change.

### Frozen quantities unchanged

The memory-safe evaluator must preserve:

- ESM-2 650M
- layer 17
- 30% sequence-identity clustering and seed-0 split
- +/-3 local-sequence baseline
- linear three-class probe
- Adam optimizer
- learning rate 1e-3
- 40 epochs
- batch size 4096
- seed 0
- Q3 and macro-F1 metrics
- cluster-level bootstrap
- Delta_ESM and G definitions
- preregistered decision bands

Only data loading, standardization, minibatch construction, and evaluation
storage may change to avoid materializing the full residue matrix.


## Confirmatory evaluation attempt 2 — technical performance failure

The memory-safe streaming evaluator was manually terminated after more than
40 minutes before producing any evaluation metric or result file.

The bottleneck was repeated decompression and loading of thousands of per-protein
`.npz` embedding files on every training epoch. No Q3 accuracy, macro-F1,
Delta_ESM, G, bootstrap interval, or verdict was observed.

The next evaluator consolidates the already-frozen cached embeddings into a
disk-backed NumPy memmap. This changes storage/access only and restores the
original global residue-level permutation each epoch while keeping RAM bounded.

All frozen scientific quantities and probe hyperparameters remain unchanged.


## Pre-result clustering reproducibility amendment

During environment reconstruction, repeated MMseqs2 clustering of the same
11,373 cleaned proteins produced a one-cluster discrepancy: 11,042 versus
11,043 clusters.

The underlying labeled dataset was unchanged:
- 11,373 proteins
- 2,875,432 residues
- overall Q3 balance: H=0.3614, E=0.2127, C=0.4259

No confirmatory Q3 accuracy, macro-F1, Delta_ESM, G, bootstrap interval, or
verdict had been observed.

To remove clustering nondeterminism before analysis, the proteins were ordered
deterministically by protein id and reclustered at 30% identity with MMseqs2
build:

eec9c354be4276d2373996af2e50808b1390d527

using --threads 1.

The resulting 11,043-cluster partition was reproduced exactly on an independent
second run, including identical protein-to-cluster assignments. This
deterministic partition is frozen for the confirmatory analysis.


## Confirmatory evaluation attempt 3 — runtime termination after training

The disk-backed memmap evaluator successfully completed:

- consolidation of all 2,875,432 residue embeddings,
- ESM probe training for all 40 frozen epochs,
- local-sequence baseline training for all 40 frozen epochs.

The Colab runtime was then disconnected before evaluation output was produced.

No Q3 accuracy, macro-F1, Delta_ESM, G, bootstrap interval, or experimental
verdict was observed.

To prevent loss of completed computation on future runs, the evaluator was
amended to checkpoint the ESM normalization, ESM probe, and local probe, and to
write the primary confirmatory metrics to disk immediately after evaluation and
before bootstrap.

The frozen scientific design, model, layer, clustering, split, baseline, probe
class, optimizer, hyperparameters, metrics, bootstrap, and decision bands remain
unchanged.
