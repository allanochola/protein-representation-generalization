# Gate A2 mapping repair 001

The voided writer emitted four mapping fields. The original freeze cell
serialized six: protein_id, universe, class_name, accession,
sequence_length, sequence_sha256.

This repair restores that exact header and row serialization, with ASCII
encoding, identifier order, LF endings and a final LF. Length and SHA-256
are derived from each verified sequence.

The frozen mapping remains 472,162 bytes with SHA-256
877b255acc77df84607e546078c42686d4184f0f08b9204892f016f54661a037.
The joint FASTA identity and all scientific scan parameters are unchanged.

A committed regression invokes only the pure build_joint function,
reproduces both frozen identities from committed inputs, and checks
invariance to input insertion order. It does not import or execute the
full runner, invoke scanners, or compute family geometry.

This commit leaves A2_SCAN_AUTHORIZED false. Authorization requires its
own subsequent commit. The original void record is retained unchanged.
