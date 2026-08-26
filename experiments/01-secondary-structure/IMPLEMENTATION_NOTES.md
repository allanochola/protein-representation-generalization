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
