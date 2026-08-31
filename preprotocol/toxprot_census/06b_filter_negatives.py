#!/usr/bin/env python3
"""
06b_filter_negatives.py — Remove negatives with ≥30% identity to any positive
and issue the final Gate C pass/fail.
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DATA_DIR,
    RESULTS_DIR,
    MMSEQS2_BINARY,
    MMSEQS2_COVERAGE,
    MMSEQS2_COV_MODE,
    MMSEQS2_THREADS,
    MMSEQS2_SENSITIVITY,
    DIVERGENCE_IDENTITY_CUTOFF,
    GATE_C_PRIMARY_MIN_NEG,
    GATE_C_SECONDARY_MIN_NEG,
    FPR_PRIMARY,
    FPR_SECONDARY,
)

POOLS = ["background", "phenotype", "family_aware"]


def load_fasta(path: Path) -> dict[str, str]:
    seqs = {}
    cur_id = None
    buf = []

    with open(path) as fh:
        for line in fh:
            line = line.rstrip()

            if line.startswith(">"):
                if cur_id is not None:
                    seqs[cur_id] = "".join(buf)
                cur_id = line[1:].split()[0].strip()
                buf = []
            else:
                buf.append(line)

    if cur_id is not None:
        seqs[cur_id] = "".join(buf)

    return seqs


def write_fasta(seqs: dict[str, str], path: Path):
    with open(path, "w") as fh:
        for acc, seq in seqs.items():
            fh.write(f">{acc}\n{seq}\n")


def find_overlapping(neg_fasta, pos_fasta, tmpdir, label):
    tmpdir.mkdir(parents=True, exist_ok=True)

    m8_out = tmpdir / f"{label}_vs_pos.m8"

    cmd = [
        MMSEQS2_BINARY,
        "easy-search",
        str(neg_fasta),
        str(pos_fasta),
        str(m8_out),
        str(tmpdir / "tmp"),
        "--min-seq-id", str(DIVERGENCE_IDENTITY_CUTOFF),
        "-c", str(MMSEQS2_COVERAGE),
        "--cov-mode", str(MMSEQS2_COV_MODE),
        "-s", str(MMSEQS2_SENSITIVITY),
        "--threads", str(MMSEQS2_THREADS),
        "--alignment-mode", "3",
        "--format-output", "query,target,fident",
        "-e", "1e-3",
    ]

    print(f"Searching {label} negatives against positives...")

    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.DEVNULL,
    )

    overlapping = set()

    if m8_out.exists():
        with open(m8_out) as fh:
            for line in fh:
                parts = line.rstrip().split("\t")
                if len(parts) < 3:
                    continue

                if float(parts[2]) >= DIVERGENCE_IDENTITY_CUTOFF:
                    overlapping.add(parts[0])

    return overlapping


def run():
    data_dir = Path(DATA_DIR)
    results_dir = Path(RESULTS_DIR)

    pos_fasta = data_dir / "cleaned_precursor.fasta"
    counts_path = results_dir / "negative_pool_counts.tsv"

    if not pos_fasta.exists():
        sys.exit("Missing cleaned_precursor.fasta")

    if not counts_path.exists():
        sys.exit("Missing negative_pool_counts.tsv — run Step 6A first")

    counts = pd.read_csv(counts_path, sep="\t")

    pool_map = {
        "background": "background",
        "phenotype": "phenotype_matched",
        "family_aware": "family_aware",
    }

    expected = {}

    for pool, summary_name in pool_map.items():
        rows = counts[counts["pool"] == summary_name]

        if len(rows) != 1:
            raise RuntimeError(
                f"Expected exactly one Step 6A row for {summary_name}"
            )

        expected[pool] = int(
            rows.iloc[0]["candidate_n_available"]
        )

    overlap_rows = []
    gate_rows = []

    for pool in POOLS:
        neg_fasta = data_dir / f"negatives_{pool}.fasta"

        if not neg_fasta.exists():
            raise RuntimeError(f"Missing {neg_fasta}")

        neg_seqs = load_fasta(neg_fasta)
        n_candidate = len(neg_seqs)

        if n_candidate != expected[pool]:
            raise RuntimeError(
                f"{pool}: FASTA has {n_candidate} sequences, "
                f"Step 6A recorded {expected[pool]}"
            )

        tmpdir = data_dir / f"mmseqs_06b_tmp_{pool}"

        overlapping = find_overlapping(
            neg_fasta,
            pos_fasta,
            tmpdir,
            pool,
        )

        kept = {
            acc: seq
            for acc, seq in neg_seqs.items()
            if acc not in overlapping
        }

        n_removed = len(overlapping)
        n_filtered = len(kept)

        write_fasta(
            kept,
            data_dir / f"negatives_{pool}_filtered.fasta",
        )

        primary_pass = n_filtered >= GATE_C_PRIMARY_MIN_NEG
        secondary_pass = n_filtered >= GATE_C_SECONDARY_MIN_NEG

        overlap_rows.append({
            "pool": pool,
            "n_candidate": n_candidate,
            "n_overlap_removed": n_removed,
            "pct_removed": round(n_removed / n_candidate, 4),
            "n_filtered": n_filtered,
        })

        gate_rows.append({
            "pool": pool,
            "n_filtered": n_filtered,
            "primary_threshold": GATE_C_PRIMARY_MIN_NEG,
            "secondary_threshold": GATE_C_SECONDARY_MIN_NEG,
            "fpr_primary": FPR_PRIMARY,
            "fpr_secondary": FPR_SECONDARY,
            "gate_c_primary_pass": int(primary_pass),
            "gate_c_secondary_pass": int(secondary_pass),
            "gate_c_status": "PASS" if primary_pass else "FAIL",
        })

        print(
            f"{pool}: {n_candidate} candidate -> "
            f"{n_removed} removed -> {n_filtered} retained"
        )

    overlap_df = pd.DataFrame(overlap_rows)
    gate_df = pd.DataFrame(gate_rows)

    overlap_df.to_csv(
        results_dir / "negative_overlap_report.tsv",
        sep="\t",
        index=False,
    )

    gate_df.to_csv(
        results_dir / "negative_pool_counts.tsv",
        sep="\t",
        index=False,
    )

    print("\n── Gate C final verdict ──")
    print(
        gate_df[
            [
                "pool",
                "n_filtered",
                "gate_c_primary_pass",
                "gate_c_secondary_pass",
                "gate_c_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    run()
