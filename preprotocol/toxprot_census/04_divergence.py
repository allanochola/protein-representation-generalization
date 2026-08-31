#!/usr/bin/env python3
"""
04_divergence.py — Build the fixed reference / candidate divergence census.

Scientific question:
Is a candidate toxin cluster <30% sequence identity to a fixed reference
corpus of known toxin clusters?

Partitioning is frozen BEFORE sequence-similarity evaluation:

  15% diagnostic burn
  65% fixed reference
  20% candidate evaluation

Assignment is deterministic from the cluster representative accession.
Burned clusters never enter the reference or confirmatory candidate set.

A candidate cluster is sequence-divergent iff none of its members has a
qualifying >=30%-identity hit to any member of the fixed reference partition
under the frozen MMseqs2 coverage rule.

Inputs:
  data/cleaned_precursor.fasta
  results/clusters_precursor.tsv

Outputs:
  results/divergence_assignment.tsv
  results/diagnostic_burn_ids.txt
  results/reference_cluster_ids.txt
  results/candidate_cluster_ids.txt
  data/reference_precursor.fasta
  data/candidate_precursor.fasta
  data/divergent_precursor.fasta

No ESM/SAE/model data are touched.
"""

import hashlib
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DATA_DIR,
    RESULTS_DIR,
    MMSEQS2_COVERAGE,
    MMSEQS2_COV_MODE,
    MMSEQS2_THREADS,
    MMSEQS2_SENSITIVITY,
    MMSEQS2_BINARY,
    DIVERGENCE_IDENTITY_CUTOFF,
    DIVERGENCE_BURN_FRAC,
    DIVERGENCE_REFERENCE_FRAC,
    DIVERGENCE_CANDIDATE_FRAC,
)


def load_clusters(tsv_path: Path):
    member_to_rep = {}
    rep_to_members = defaultdict(list)

    with open(tsv_path) as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue

            rep, member = parts[0], parts[1]
            member_to_rep[member] = rep
            rep_to_members[rep].append(member)

    return member_to_rep, dict(rep_to_members)


def load_sequences(fasta_path: Path):
    seqs = {}
    cur_id = None
    buf = []

    with open(fasta_path) as fh:
        for line in fh:
            line = line.rstrip()

            if line.startswith(">"):
                if cur_id is not None:
                    seqs[cur_id] = "".join(buf)

                cur_id = line[1:].split()[0]
                buf = []
            else:
                buf.append(line)

    if cur_id is not None:
        seqs[cur_id] = "".join(buf)

    return seqs


def partition_cluster(rep_acc: str) -> str:
    """
    Deterministic mutually exclusive partition based only on accession hash.

    No labels, sequence identity, cluster size, family annotation, or model
    statistic enters assignment.
    """
    digest = hashlib.md5(rep_acc.encode()).hexdigest()
    x = int(digest[:8], 16) / 0xFFFFFFFF

    burn_cut = DIVERGENCE_BURN_FRAC
    reference_cut = burn_cut + DIVERGENCE_REFERENCE_FRAC

    if x < burn_cut:
        return "burn"
    elif x < reference_cut:
        return "reference"
    else:
        return "candidate"


def write_cluster_fasta(reps, rep_to_members, seqs, out_path: Path):
    n = 0

    with open(out_path, "w") as fh:
        for rep in sorted(reps):
            for member in rep_to_members[rep]:
                if member not in seqs:
                    raise RuntimeError(
                        f"Missing sequence for cluster member {member}"
                    )

                fh.write(f">{member}\n{seqs[member]}\n")
                n += 1

    return n


def run_candidate_vs_reference(
    candidate_fasta: Path,
    reference_fasta: Path,
    tmpdir: Path,
):
    """
    Search candidate sequences against the fixed reference.

    Primary gate:
      any qualifying hit with fident >= 0.30 -> candidate cluster is not
      sequence-divergent.

    Search floor is 0.0 only for descriptive nearest-hit information.
    Sub-30% identity bands are descriptive and never gate the experiment.
    """
    tmpdir.mkdir(parents=True, exist_ok=True)

    out = tmpdir / "candidate_vs_reference.m8"

    cmd = [
        MMSEQS2_BINARY,
        "easy-search",
        str(candidate_fasta),
        str(reference_fasta),
        str(out),
        str(tmpdir / "tmp"),
        "--min-seq-id", "0.0",
        "-c", str(MMSEQS2_COVERAGE),
        "--cov-mode", str(MMSEQS2_COV_MODE),
        "-s", str(MMSEQS2_SENSITIVITY),
        "--threads", str(MMSEQS2_THREADS),
        "--alignment-mode", "3",
        "--format-output",
        "query,target,fident,alnlen,qlen,tlen,evalue",
        "-e", "1e-3",
    ]

    print("Running candidate -> fixed-reference MMseqs2 search...")
    print("Executable:", MMSEQS2_BINARY)

    subprocess.run(cmd, check=True)

    return out


def assign(label="precursor"):
    results_dir = Path(RESULTS_DIR)
    data_dir = Path(DATA_DIR)

    results_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    cluster_tsv = results_dir / f"clusters_{label}.tsv"
    fasta_path = data_dir / f"cleaned_{label}.fasta"

    if not cluster_tsv.exists():
        sys.exit(f"Missing {cluster_tsv} — run 03_cluster.sh first")

    if not fasta_path.exists():
        sys.exit(f"Missing {fasta_path} — run 02_clean.py first")

    member_to_rep, rep_to_members = load_clusters(cluster_tsv)
    seqs = load_sequences(fasta_path)

    all_reps = sorted(rep_to_members)

    if len(member_to_rep) != len(seqs):
        raise RuntimeError(
            f"Cluster/FASTA mismatch: {len(member_to_rep)} clustered members "
            f"vs {len(seqs)} sequences"
        )

    partitions = {
        rep: partition_cluster(rep)
        for rep in all_reps
    }

    burn_reps = {
        rep for rep, part in partitions.items()
        if part == "burn"
    }

    reference_reps = {
        rep for rep, part in partitions.items()
        if part == "reference"
    }

    candidate_reps = {
        rep for rep, part in partitions.items()
        if part == "candidate"
    }

    if burn_reps & reference_reps:
        raise RuntimeError("Burn/reference partition overlap")

    if burn_reps & candidate_reps:
        raise RuntimeError("Burn/candidate partition overlap")

    if reference_reps & candidate_reps:
        raise RuntimeError("Reference/candidate partition overlap")

    if (
        len(burn_reps)
        + len(reference_reps)
        + len(candidate_reps)
        != len(all_reps)
    ):
        raise RuntimeError("Partition assignment does not cover all clusters")

    reference_fasta = data_dir / f"reference_{label}.fasta"
    candidate_fasta = data_dir / f"candidate_{label}.fasta"

    n_ref_seq = write_cluster_fasta(
        reference_reps,
        rep_to_members,
        seqs,
        reference_fasta,
    )

    n_candidate_seq = write_cluster_fasta(
        candidate_reps,
        rep_to_members,
        seqs,
        candidate_fasta,
    )

    print("\n-- Frozen partition geometry --")
    print(f"Total clusters      : {len(all_reps)}")
    print(f"Diagnostic burn     : {len(burn_reps)}")
    print(f"Fixed reference     : {len(reference_reps)}")
    print(f"Candidate evaluation: {len(candidate_reps)}")
    print(f"Reference sequences : {n_ref_seq}")
    print(f"Candidate sequences : {n_candidate_seq}")

    tmpdir = data_dir / f"mmseqs_div_tmp_{label}"

    m8_path = run_candidate_vs_reference(
        candidate_fasta,
        reference_fasta,
        tmpdir,
    )

    max_identity = defaultdict(float)
    best_target = {}
    qualifying_ge30 = set()

    with open(m8_path) as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")

            if len(parts) < 7:
                continue

            query, target = parts[0], parts[1]
            fident = float(parts[2])

            q_rep = member_to_rep.get(query)

            if q_rep not in candidate_reps:
                continue

            if fident > max_identity[q_rep]:
                max_identity[q_rep] = fident
                best_target[q_rep] = target

            if fident >= DIVERGENCE_IDENTITY_CUTOFF:
                qualifying_ge30.add(q_rep)

    rows = []

    for rep in all_reps:
        part = partitions[rep]

        if part == "candidate":
            max_id = max_identity.get(rep, 0.0)
            is_divergent = rep not in qualifying_ge30

            if max_id == 0.0:
                band = "no_reported_hit"
            elif max_id < 0.20:
                band = "<20%_reported"
            elif max_id < 0.25:
                band = "20-25%_reported"
            elif max_id < 0.30:
                band = "25-30%_reported"
            else:
                band = ">=30%"
        else:
            max_id = None
            is_divergent = False
            band = "not_evaluated"

        rows.append({
            "cluster_rep": rep,
            "n_members": len(rep_to_members[rep]),
            "partition": part,
            "max_reference_identity": (
                round(max_id, 4)
                if max_id is not None
                else None
            ),
            "nearest_identity_band": band,
            "has_reference_hit_ge30": (
                int(rep in qualifying_ge30)
                if part == "candidate"
                else None
            ),
            "is_sequence_divergent": int(is_divergent),
            "usable_for_confirmatory_divergence": int(is_divergent),
            "best_reference_target": best_target.get(rep, ""),
        })

    df = pd.DataFrame(rows)

    out_path = results_dir / "divergence_assignment.tsv"
    df.to_csv(out_path, sep="\t", index=False)

    (results_dir / "diagnostic_burn_ids.txt").write_text(
        "\n".join(sorted(burn_reps)) + "\n"
    )

    (results_dir / "reference_cluster_ids.txt").write_text(
        "\n".join(sorted(reference_reps)) + "\n"
    )

    (results_dir / "candidate_cluster_ids.txt").write_text(
        "\n".join(sorted(candidate_reps)) + "\n"
    )

    divergent_reps = set(
        df.loc[
            df["is_sequence_divergent"] == 1,
            "cluster_rep",
        ]
    )

    divergent_fasta = data_dir / f"divergent_{label}.fasta"

    n_divergent_sequences = write_cluster_fasta(
        divergent_reps,
        rep_to_members,
        seqs,
        divergent_fasta,
    )

    n_candidate = len(candidate_reps)
    n_divergent = len(divergent_reps)

    print("\n-- Divergence summary --")
    print(f"Candidate clusters          : {n_candidate}")
    print(f"Sequence-divergent clusters : {n_divergent}")

    if n_candidate:
        print(
            f"Divergent fraction candidate: "
            f"{n_divergent / n_candidate:.1%}"
        )
    else:
        print("Divergent fraction candidate: NA")

    print(f"Divergent sequences         : {n_divergent_sequences}")

    candidate_df = df[df["partition"] == "candidate"]

    print("\nDescriptive nearest-reference bands:")
    for band, count in (
        candidate_df["nearest_identity_band"]
        .value_counts()
        .sort_index()
        .items()
    ):
        print(f"  {band}: {count}")

    print(f"\nOutput -> {out_path}")
    print(
        "\nIMPORTANT: family-disjoint status is NOT established here. "
        "Step 05 is still required before Gate A."
    )


if __name__ == "__main__":
    assign("precursor")
