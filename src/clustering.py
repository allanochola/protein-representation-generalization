"""TAPE secondary-structure loading and 30%-identity MMseqs2 clustering.

TAPE is used only as the labeled protein source (sequences + per-residue Q3). Its
own train/test split is NOT used — sequences are pooled, cleaned, and reclustered
here to build the divergence split the experiment rests on.
"""
import os
import glob
import pickle
import subprocess
import numpy as np

from . import probe as sp


def load_tape_ss(data_dir, max_len=1022, min_len=20):
    """Pool the TAPE SS lmdb splits into cleaned proteins [{id, seq, y}], y as
    per-residue Q3 indices (H=0, E=1, C=2). Returns (proteins, (seq_key, ss_key))."""
    import lmdb
    records = []
    for f in glob.glob(os.path.join(data_dir, "secondary_structure_*.lmdb")):
        env = lmdb.open(f, readonly=True, lock=False)
        with env.begin() as txn:
            for key, val in txn.cursor():
                if key == b"num_examples":
                    continue
                records.append(pickle.loads(val))
    assert records, f"no TAPE lmdb found in {data_dir}"
    seq_key = "primary"
    ss_key = "ss3" if "ss3" in records[0] else "secondary_structure"

    def to_idx(ss):
        if isinstance(ss[0], (int, np.integer)):
            return np.asarray(ss, dtype=np.int64)      # TAPE ss3 ints (verify H/E/C order on first run)
        return np.asarray([sp.Q3_IDX[sp.Q8_TO_Q3[c]] for c in ss], dtype=np.int64)

    clean, seen = [], set()
    for i, r in enumerate(records):
        seq = r[seq_key]
        seq = seq.decode() if isinstance(seq, bytes) else seq
        ss = r[ss_key]
        if not (min_len <= len(seq) <= max_len):
            continue
        if not sp.align_ok(seq, ss):
            continue
        if seq in seen:
            continue
        seen.add(seq)
        clean.append({"id": f"p{i}", "seq": seq, "y": to_idx(ss)})
    return clean, (seq_key, ss_key)


def cluster_30(clean, out_dir, min_seq_id=0.3):
    """Write a FASTA, run MMseqs2 easy-cluster, return {protein_id: cluster_rep}.
    Installs the MMseqs2 static binary if none is on PATH."""
    os.makedirs(out_dir, exist_ok=True)
    fasta = os.path.join(out_dir, "seqs.fasta")
    with open(fasta, "w") as fh:
        for p in clean:
            fh.write(f">{p['id']}\n{p['seq']}\n")
    tsv = os.path.join(out_dir, "clu_cluster.tsv")
    if not os.path.exists(tsv):
        if subprocess.run(["which", "mmseqs"], capture_output=True).returncode != 0:
            subprocess.run(
                "wget -q https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz -O /tmp/m.tar.gz "
                "&& tar xzf /tmp/m.tar.gz -C /tmp", shell=True, check=True)
            os.environ["PATH"] += ":/tmp/mmseqs/bin"
        subprocess.run(
            f"mmseqs easy-cluster {fasta} {out_dir}/clu {out_dir}/tmp "
            f"--min-seq-id {min_seq_id} -c 0.8 --cov-mode 1 > {out_dir}/mmseqs.log 2>&1",
            shell=True, check=True)
    clu = {}
    for line in open(tsv):
        rep, mem = line.split()
        clu[mem] = rep
    return clu
