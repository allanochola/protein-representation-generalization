#!/usr/bin/env python3
"""
04_divergence.py — Assign sequence-divergent status per §4.2 rule.

§4.2: For each cluster C, max_identity(C) = maximum qualifying sequence identity
between any member of C and any positive sequence NOT in C.
A cluster is sequence-divergent iff max_identity(C) < 0.30.

This is an explicit cross-cluster identity check, not implied by clustering.
MMseqs2's greedy set cover is non-transitive: two clusters can have members
that are ≥30% identical without being merged.

Method:
  1. Load cluster assignments.
  2. Run MMseqs2 all-vs-all search on the full positive sequence set.
  3. Filter hits to cross-cluster pairs only.
  4. For each cluster, report max cross-cluster identity.
  5. Flag divergent clusters (max < 0.30).

Also assigns:
  - nearest-reference identity band (<20%, 20-25%, 25-30%, ≥30%)
  - the burned diagnostic partition (§6): deterministic md5-hash assignment.

Inputs:
  data/cleaned_precursor.fasta
  results/clusters_precursor.tsv

Outputs:
  results/divergence_assignment.tsv    (§11: primary divergence table)
  results/diagnostic_burn_ids.txt      (cluster rep accessions in burn partition)
  data/divergent_positive.fasta        (sequences in divergent clusters, for downstream)
  data/reference_positive.fasta        (non-divergent, non-burned clusters)
"""

import subprocess, hashlib, sys, os
from pathlib import Path
from collections import defaultdict

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from config import (DATA_DIR, RESULTS_DIR,
                    MMSEQS2_MIN_SEQ_ID, MMSEQS2_COVERAGE, MMSEQS2_COV_MODE,
                    MMSEQS2_THREADS, MMSEQS2_SENSITIVITY,
                    DIVERGENCE_IDENTITY_CUTOFF,
                    DIAGNOSTIC_BURN_THRESHOLD_BYTE)


def load_clusters(tsv_path: Path) -> tuple[dict, dict]:
    """Returns member→rep and rep→[members] dicts."""
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


def load_sequences(fasta_path: Path) -> dict[str, str]:
    seqs, cur_id, buf = {}, None, []
    with open(fasta_path) as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith(">"):
                if cur_id:
                    seqs[cur_id] = "".join(buf)
                cur_id = line[1:].split()[0]
                buf = []
            else:
                buf.append(line)
    if cur_id:
        seqs[cur_id] = "".join(buf)
    return seqs


def run_all_vs_all(fasta: Path, tmpdir: Path) -> Path:
    """
    Run MMseqs2 easy-search of all sequences against themselves.
    Returns path to the output m8 TSV.
    """
    tmpdir.mkdir(parents=True, exist_ok=True)
    out = tmpdir / "all_vs_all.m8"
    cmd = [
        "mmseqs", "easy-search",
        str(fasta), str(fasta), str(out), str(tmpdir / "tmp"),
        # Search below the 30% gate so nearest-identity bands (<20%, 20-25%,
        # 25-30%) are actually observable. The divergence decision itself is
        # still frozen at DIVERGENCE_IDENTITY_CUTOFF = 0.30.
        "--min-seq-id",   "0.0",
        "-c",             str(MMSEQS2_COVERAGE),
        "--cov-mode",     str(MMSEQS2_COV_MODE),
        "-s",             str(MMSEQS2_SENSITIVITY),
        "--threads",      str(MMSEQS2_THREADS),
        # Force real alignment-derived sequence identity rather than the
        # estimated identity used by the faster search path. `fident` is a
        # fraction in [0,1].
        "--alignment-mode", "3",
        "--format-output", "query,target,fident,alnlen,qlen,tlen",
        "-e",             "1e-3",
    ]
    print("Running all-vs-all search with real alignment identity "
          "(search floor 0.0; divergence gate remains 0.30)…")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return out


def _burn_partition(rep_acc: str) -> bool:
    """True if this representative goes into the burned diagnostic partition."""
    first_byte = int(hashlib.md5(rep_acc.encode()).hexdigest()[:2], 16)
    return first_byte < DIAGNOSTIC_BURN_THRESHOLD_BYTE


def assign(label: str = "precursor"):
    cluster_tsv  = Path(RESULTS_DIR) / f"clusters_{label}.tsv"
    fasta_path   = Path(DATA_DIR)    / f"cleaned_{label}.fasta"
    tmpdir       = Path(DATA_DIR)    / f"mmseqs_div_tmp_{label}"

    if not cluster_tsv.exists():
        sys.exit(f"Missing {cluster_tsv} — run 03_cluster.sh first")
    if not fasta_path.exists():
        sys.exit(f"Missing {fasta_path} — run 02_clean.py first")

    member_to_rep, rep_to_members = load_clusters(cluster_tsv)
    seqs = load_sequences(fasta_path)

    all_reps = sorted(rep_to_members.keys())
    n_total  = len(all_reps)
    print(f"Loaded {n_total} clusters, {len(member_to_rep)} member rows")

    # ── all-vs-all cross-cluster identity ────────────────────────────────────
    m8_path = run_all_vs_all(fasta_path, tmpdir)

    # For each cluster, track the max cross-cluster identity seen by any member.
    max_cross_id: dict[str, float] = defaultdict(float)

    with open(m8_path) as fh:
        for line in fh:
            parts = line.rstrip().split("\t")
            if len(parts) < 3:
                continue
            q, t = parts[0], parts[1]
            if q == t:
                continue                     # self-hit
            q_rep = member_to_rep.get(q)
            t_rep = member_to_rep.get(t)
            if q_rep is None or t_rep is None:
                continue
            if q_rep == t_rep:
                continue                     # within-cluster hit
            fident = float(parts[2])
            max_cross_id[q_rep] = max(max_cross_id[q_rep], fident)

    # ── build output table ────────────────────────────────────────────────────
    rows = []
    burn_ids = []

    for rep in all_reps:
        max_id   = max_cross_id.get(rep, 0.0)
        divergent = max_id < DIVERGENCE_IDENTITY_CUTOFF
        burned    = _burn_partition(rep)

        # identity band
        if max_id < 0.20:
            band = "<20%"
        elif max_id < 0.25:
            band = "20-25%"
        elif max_id < 0.30:
            band = "25-30%"
        else:
            band = ">=30%"

        rows.append({
            "cluster_rep":             rep,
            "n_members":               len(rep_to_members[rep]),
            "max_cross_cluster_id":    round(max_id, 4),
            "identity_band":           band,
            "is_divergent":            int(divergent),
            "in_diagnostic_burn":      int(burned),
            "usable_divergent":        int(divergent and not burned),
        })

        if burned:
            burn_ids.append(rep)

    df = pd.DataFrame(rows)
    out_path = Path(RESULTS_DIR) / "divergence_assignment.tsv"
    df.to_csv(out_path, sep="\t", index=False)

    # write burn-partition IDs
    burn_path = Path(RESULTS_DIR) / "diagnostic_burn_ids.txt"
    Path(burn_path).write_text("\n".join(burn_ids) + "\n")

    # ── write divergent FASTA for downstream use ─────────────────────────────
    divergent_reps = set(df[df["is_divergent"] == 1]["cluster_rep"])
    reference_reps = set(df[(df["is_divergent"] == 0) &
                            (df["in_diagnostic_burn"] == 0)]["cluster_rep"])

    _write_cluster_fasta(divergent_reps, rep_to_members, seqs,
                         Path(DATA_DIR) / f"divergent_{label}.fasta")
    _write_cluster_fasta(reference_reps, rep_to_members, seqs,
                         Path(DATA_DIR) / f"reference_{label}.fasta")

    # ── console summary ───────────────────────────────────────────────────────
    n_div    = df["is_divergent"].sum()
    n_burned = df["in_diagnostic_burn"].sum()
    n_usable = df["usable_divergent"].sum()
    div_frac = n_div / n_total if n_total else 0

    print(f"\n── Divergence summary ({label}) ──────────────────────────────")
    print(f"  Total clusters          : {n_total}")
    print(f"  Sequence-divergent      : {n_div}  ({div_frac:.1%} of total)")
    print(f"    identity band <20%    : {(df['identity_band'] == '<20%').sum()}")
    print(f"    identity band 20-25%  : {(df['identity_band'] == '20-25%').sum()}")
    print(f"    identity band 25-30%  : {(df['identity_band'] == '25-30%').sum()}")
    print(f"  Diagnostic burn         : {n_burned}  "
          f"({n_burned/n_total:.1%}, target ~{DIAGNOSTIC_BURN_THRESHOLD_BYTE/256:.1%})")
    print(f"  Usable divergent        : {n_usable}")
    print(f"  (Planning assumption was {0.20:.0%} divergent fraction)")
    print(f"\nOutput → {out_path}")
    print(f"Burn IDs → {burn_path}")


def _write_cluster_fasta(reps, rep_to_members, seqs, out_path):
    with open(out_path, "w") as fh:
        for rep in sorted(reps):
            for member in rep_to_members.get(rep, [rep]):
                if member in seqs:
                    fh.write(f">{member}\n{seqs[member]}\n")


if __name__ == "__main__":
    assign("precursor")
