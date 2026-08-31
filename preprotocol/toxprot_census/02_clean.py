#!/usr/bin/env python3
"""
02_clean.py — Parse raw UniProt JSONL, apply evidence filters (§§2-3),
              and produce the cleaned positive-entry table.

No model data is touched. Model-blind.

Outputs (results/):
  cleaned_entries.tsv         — primary cleaned table (§11 output 1)
  evidence_summary.tsv        — evidence-strength breakdown (§11 output 2)
  duplicate_report.tsv        — exact-sequence duplicate log (§11 output 3)
  length_composition.tsv      — sequence length and composition (§11 output 6)
  mature_chain_sensitivity.tsv— same stats after signal/propeptide removal (§11 output 9)
"""

import json, hashlib, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from config import (DATA_DIR, RESULTS_DIR,
                    EXCLUDE_FRAGMENTS, MAX_NONSTANDARD_FRACTION,
                    MIN_LENGTH, MAX_LENGTH)

AA_STANDARD = set("ACDEFGHIKLMNPQRSTVWY")
AA_NONSTANDARD = set("BJOUXZ")


# ── parsing helpers ──────────────────────────────────────────────────────────

def _protein_name(e: dict) -> str:
    try:
        desc = e["proteinDescription"]
        rec  = desc.get("recommendedName") or desc.get("submittedName", [{}])[0]
        return rec.get("fullName", {}).get("value", "")
    except Exception:
        return ""


def _organism(e: dict) -> tuple[str, int]:
    org  = e.get("organism", {})
    name = org.get("scientificName", "")
    tid  = org.get("taxonId", 0)
    return name, tid


def _lineage(e: dict) -> str:
    lins = e.get("lineages", [])
    names = []

    for item in lins:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            name = (
                item.get("scientificName")
                or item.get("name")
                or item.get("value")
                or ""
            )
            if name:
                names.append(name)

    return "; ".join(names)


def _keywords(e: dict) -> list[str]:
    return [k.get("name", "") for k in e.get("keywords", [])]


def _protein_existence(e: dict) -> str:
    pe = e.get("proteinExistence", "")
    return pe.split(":")[0].strip() if ":" in pe else pe


def _annotation_score(e: dict) -> float:
    return float(e.get("annotationScore", 0))


def _sequence(e: dict) -> str:
    return e.get("sequence", {}).get("value", "")


def _mass(e: dict) -> int:
    return e.get("sequence", {}).get("molWeight", 0)


def _features(e: dict) -> list[dict]:
    return e.get("features", [])


def _has_fragment(e: dict) -> bool:
    if e.get("fragment"):
        return True
    if e.get("sequence", {}).get("fragment"):
        return True
    if any(f.get("type", "").lower() == "non-terminal residue"
           for f in _features(e)):
        return True
    if any(k.get("id", "") == "KW-0903" for k in e.get("keywords", [])):
        return True
    return False


def _signal_propep_range(e: dict) -> tuple[int, int]:
    """
    Return (mature_start_1based, removable_end_1based) using only
    signal/propeptide annotations with explicit finite end positions.

    Features with UNKNOWN or missing boundaries are not trimmed.
    Returns (1, 0) if no removable region has an explicit boundary.
    """
    sig_end = 0
    propep_end = 0

    for f in _features(e):
        ftype = f.get("type", "").lower()

        if ftype not in {"signal", "propep"}:
            continue

        loc = f.get("location", {})
        end_obj = loc.get("end", {})
        end = end_obj.get("value")
        modifier = end_obj.get("modifier")

        # Never invent a cleavage boundary.
        if not isinstance(end, int) or modifier == "UNKNOWN":
            continue

        if ftype == "signal":
            sig_end = max(sig_end, end)
        elif ftype == "propep":
            propep_end = max(propep_end, end)

    removable_end = max(sig_end, propep_end)
    return removable_end + 1, removable_end


def _pfam_ids(e: dict) -> list[str]:
    return [ref["id"] for ref in e.get("uniProtKBCrossReferences", [])
            if ref.get("database") == "Pfam"]


def _interpro_ids(e: dict) -> list[str]:
    return [ref["id"] for ref in e.get("uniProtKBCrossReferences", [])
            if ref.get("database") == "InterPro"]


def _function_comment(e: dict) -> str:
    for c in e.get("comments", []):
        if c.get("commentType") == "FUNCTION":
            texts = c.get("texts", [])
            if texts:
                return texts[0].get("value", "")
    return ""


def _subcellular_comment(e: dict) -> str:
    for c in e.get("comments", []):
        if c.get("commentType") == "SUBCELLULAR LOCATION":
            locs = c.get("subcellularLocations", [])
            if locs:
                loc = locs[0].get("location", {})
                return loc.get("value", "")
    return ""


# ── nonstandard residue check ────────────────────────────────────────────────

def _nonstandard_frac(seq: str) -> float:
    ns = sum(1 for aa in seq if aa in AA_NONSTANDARD)
    return ns / len(seq) if seq else 1.0


def _cysteine_frac(seq: str) -> float:
    return seq.count("C") / len(seq) if seq else 0.0


def _aa_composition(seq: str) -> dict[str, float]:
    n = len(seq)
    if n == 0:
        return {}
    c = Counter(seq)
    return {aa: c.get(aa, 0) / n for aa in sorted(AA_STANDARD)}


# ── main ─────────────────────────────────────────────────────────────────────

def clean():
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    raw_path = Path(DATA_DIR) / "raw_toxprot.jsonl"

    if not raw_path.exists():
        sys.exit(f"raw_toxprot.jsonl not found — run 01_pull.py first")

    records, dup_log = [], []
    exclusion_counts = Counter()
    seen_seqs        = {}   # sequence_md5 → first accession

    with open(raw_path) as fh:
        for line in fh:
            e   = json.loads(line)
            acc = e.get("primaryAccession", "")
            seq = _sequence(e)

            # ── evidence filter: fragment ──────────────────────────────────
            if EXCLUDE_FRAGMENTS and _has_fragment(e):
                exclusion_counts["fragment"] += 1
                continue

            # ── evidence filter: sequence quality ─────────────────────────
            if not seq:
                exclusion_counts["no_sequence"] += 1
                continue
            ns_frac = _nonstandard_frac(seq)
            if ns_frac > MAX_NONSTANDARD_FRACTION:
                exclusion_counts["high_nonstandard"] += 1
                continue

            length = len(seq)
            if not (MIN_LENGTH <= length <= MAX_LENGTH):
                exclusion_counts["length_out_of_range"] += 1
                continue

            # ── exact-sequence deduplication ──────────────────────────────
            seq_md5 = hashlib.md5(seq.encode()).hexdigest()
            if seq_md5 in seen_seqs:
                dup_log.append({"duplicate_acc": acc,
                                "first_seen_acc": seen_seqs[seq_md5],
                                "seq_md5": seq_md5,
                                "length": length})
                exclusion_counts["exact_duplicate"] += 1
                continue
            seen_seqs[seq_md5] = acc

            # ── mature-chain region ───────────────────────────────────────
            mature_start, precursor_removable_end = _signal_propep_range(e)
            has_signal   = any(f.get("type","").lower() == "signal"
                               for f in _features(e))
            has_propep   = any(f.get("type","").lower() == "propep"
                               for f in _features(e))

            # Remove all annotated N-terminal signal/propeptide sequence.
            # precursor_removable_end is 1-based inclusive.
            mature_seq = (
                seq[precursor_removable_end:]
                if precursor_removable_end > 0
                else seq
            )
            mature_start = precursor_removable_end + 1
            mature_length = len(mature_seq)

            # ── protein-existence code ────────────────────────────────────
            pe_raw   = _protein_existence(e)
            pe_code  = int(pe_raw[0]) if pe_raw and pe_raw[0].isdigit() else 5

            org_name, org_id = _organism(e)
            kws              = _keywords(e)
            toxin_kws        = [k for k in kws if "toxin" in k.lower()
                                 or "venom" in k.lower()]

            records.append({
                "accession":          acc,
                "entry_name":         e.get("uniProtkbId", ""),
                "protein_name":       _protein_name(e),
                "organism":           org_name,
                "organism_id":        org_id,
                "lineage":            _lineage(e),
                "length":             length,
                "mature_start":       mature_start,
                "mature_length":      mature_length,
                "has_signal":         int(has_signal),
                "has_propep":         int(has_propep),
                "protein_existence":  pe_code,
                "annotation_score":   _annotation_score(e),
                "cysteine_frac":      round(_cysteine_frac(seq), 4),
                "mature_cysteine_frac": round(_cysteine_frac(mature_seq), 4),
                "nonstandard_frac":   round(ns_frac, 5),
                "pfam_ids":           "|".join(_pfam_ids(e)),
                "interpro_ids":       "|".join(_interpro_ids(e)),
                "toxin_keywords":     "|".join(toxin_kws),
                "function_comment":   _function_comment(e)[:300],
                "subcellular_loc":    _subcellular_comment(e),
                "seq_md5":            seq_md5,
                # full sequence for FASTA output — trimmed in display
                "_seq":               seq,
                "_mature_seq":        mature_seq,
            })

    df = pd.DataFrame(records)

    # ── write cleaned entries ─────────────────────────────────────────────────
    out_cols = [c for c in df.columns if not c.startswith("_")]
    df[out_cols].to_csv(Path(RESULTS_DIR) / "cleaned_entries.tsv",
                        sep="\t", index=False)

    # ── write FASTA (full precursor) ──────────────────────────────────────────
    with open(Path(DATA_DIR) / "cleaned_precursor.fasta", "w") as fh:
        for _, row in df.iterrows():
            fh.write(f">{row['accession']}\n{row['_seq']}\n")

    with open(Path(DATA_DIR) / "cleaned_mature.fasta", "w") as fh:
        for _, row in df.iterrows():
            fh.write(f">{row['accession']}\n{row['_mature_seq']}\n")

    # ── evidence summary ──────────────────────────────────────────────────────
    ev_summary = (
        df.groupby("protein_existence")
          .size()
          .reset_index(name="count")
    )
    ev_summary["description"] = ev_summary["protein_existence"].map({
        1: "Evidence at protein level",
        2: "Evidence at transcript level",
        3: "Inferred from homology",
        4: "Predicted",
        5: "Uncertain",
    }).fillna("Unknown")
    ev_summary.to_csv(Path(RESULTS_DIR) / "evidence_summary.tsv",
                      sep="\t", index=False)

    # ── duplicate report ─────────────────────────────────────────────────────
    pd.DataFrame(dup_log).to_csv(Path(RESULTS_DIR) / "duplicate_report.tsv",
                                  sep="\t", index=False)

    # ── length and composition summary ───────────────────────────────────────
    length_summary = df["length"].describe().to_frame().T
    length_summary["pct_under_76"]  = (df["length"] <= 75).mean()
    length_summary["pct_under_101"] = (df["length"] <= 100).mean()
    length_summary["pct_under_251"] = (df["length"] <= 250).mean()
    length_summary["mean_cys_frac"] = df["cysteine_frac"].mean()
    length_summary["mean_mature_cys_frac"] = df["mature_cysteine_frac"].mean()
    length_summary.to_csv(Path(RESULTS_DIR) / "length_composition.tsv",
                           sep="\t", index=False)

    # ── mature-chain sensitivity ──────────────────────────────────────────────
    mature_summary = df["mature_length"].describe().to_frame().T
    mature_summary["n_with_signal"]  = df["has_signal"].sum()
    mature_summary["n_with_propep"]  = df["has_propep"].sum()
    mature_summary["frac_annotated"] = (
        (df["has_signal"] | df["has_propep"]).mean()
    )
    mature_summary.to_csv(Path(RESULTS_DIR) / "mature_chain_sensitivity.tsv",
                           sep="\t", index=False)

    # ── console summary ───────────────────────────────────────────────────────
    print("\n── Cleaning summary ──────────────────────────────────────────")
    for reason, n in exclusion_counts.items():
        print(f"  Excluded ({reason}): {n}")
    print(f"  Retained: {len(df)}")
    print(f"\n── Evidence distribution ─────────────────────────────────────")
    print(ev_summary.to_string(index=False))
    print(f"\n── Length percentiles ────────────────────────────────────────")
    print(f"  median {df['length'].median():.0f}, "
          f"mean {df['length'].mean():.0f}, "
          f"max {df['length'].max()}, "
          f"≤75 aa: {(df['length'] <= 75).mean():.1%}")
    print(f"\nOutputs written to {RESULTS_DIR}/")


if __name__ == "__main__":
    clean()
