#!/usr/bin/env python3
"""
06_negatives.py — Construct and count candidate matched-negative pools (§5).

Three pools are evaluated descriptively:
  1. Background negatives   — random reviewed Swiss-Prot proteins excluding toxins
  2. Phenotype-matched      — matched on length, secretion, cysteine content
  3. Family-aware           — non-toxic reviewed proteins sharing a Pfam family

The design uses the hardest available pool that meets Gate C's size requirement.
This script counts and characterises. It does not yet assign any negative to
a confirmatory evaluation role.

UniProt API calls here are model-blind: no ESM activations, no predictions.

Outputs:
  results/negative_pool_counts.tsv     (§11: matched-negative counts)
  results/negative_phenotype.tsv       — phenotype-matched pool metadata
  results/negative_family_aware.tsv    — family-aware pool metadata
  data/negatives_phenotype.fasta       — sequences for family-aware pool
  data/negatives_family_aware.fasta
"""

import json, sys, time, requests
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from config import (DATA_DIR, RESULTS_DIR, RANDOM_SEED,
                    GATE_C_PRIMARY_MIN_NEG, GATE_C_SECONDARY_MIN_NEG,
                    FPR_PRIMARY, FPR_SECONDARY)

BASE_URL = "https://rest.uniprot.org/uniprotkb/search"
NEG_FIELDS = [
    "accession", "id", "protein_name", "organism_name", "organism_id",
    "lineage", "length", "sequence",
    "keywords", "protein_existence",
    "ft_signal", "ft_propep",
    "xref_pfam",
    "cc_subcellular_location",
]
PAGE_SIZE = 500
MAX_BG_NEGATIVES = 15_000   # cap to avoid excessive API traffic


def _query_uniprot(query: str, max_results: int = MAX_BG_NEGATIVES) -> list[dict]:
    """Paginate UniProt and return up to max_results entries."""
    params = {
        "query":  query,
        "fields": ",".join(NEG_FIELDS),
        "format": "json",
        "size":   PAGE_SIZE,
    }
    entries, url = [], BASE_URL
    page = 0
    while url and len(entries) < max_results:
        resp = requests.get(url, params=params if page == 0 else None, timeout=120)
        resp.raise_for_status()
        data   = resp.json()
        batch  = data.get("results", [])
        entries.extend(batch)
        link   = resp.headers.get("Link", "")
        url    = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
        params = None
        page  += 1
        time.sleep(0.4)
    return entries[:max_results]


def _sequence(e):
    return e.get("sequence", {}).get("value", "")


def _length(e):
    return e.get("sequence", {}).get("length", 0)


def _has_signal(e):
    return any(f.get("type","").lower() == "signal"
               for f in e.get("features", []))


def _pfam_ids(e):
    return [r["id"] for r in e.get("uniProtKBCrossReferences", [])
            if r.get("database") == "Pfam"]


def _cys_frac(seq):
    return seq.count("C") / len(seq) if seq else 0.0


def _subcellular(e):
    for c in e.get("comments", []):
        if c.get("commentType") == "SUBCELLULAR LOCATION":
            locs = c.get("subcellularLocations", [])
            if locs:
                return locs[0].get("location", {}).get("value", "")
    return ""


def _is_secreted(e):
    sc = _subcellular(e).lower()
    return int("secret" in sc or "extracel" in sc or "extracell" in sc)


def run():
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    entries_path = Path(RESULTS_DIR) / "cleaned_entries.tsv"
    if not entries_path.exists():
        sys.exit("Missing cleaned_entries.tsv — run 02_clean.py first")

    positives = pd.read_csv(entries_path, sep="\t")

    # Collect Pfam families from the positive set for family-aware negatives.
    positive_pfam = set()
    for row in positives["pfam_ids"].dropna():
        for pf in str(row).split("|"):
            if pf.strip():
                positive_pfam.add(pf.strip())

    positive_accs = set(positives["accession"])

    # ── 1. Background negatives ───────────────────────────────────────────────
    print("Fetching background negatives (reviewed Swiss-Prot, NOT KW-0800)…")
    bg_query = "reviewed:true AND NOT keyword:KW-0800 AND protein_existence:1"
    bg_entries = _query_uniprot(bg_query, MAX_BG_NEGATIVES)
    bg_entries = [e for e in bg_entries
                  if e.get("primaryAccession","") not in positive_accs]

    print(f"  Background: {len(bg_entries)} entries")

    # ── 2. Phenotype-matched negatives ────────────────────────────────────────
    # Strategy: pull secreted/extracellular proteins of similar length range.
    # Short peptides: length ≤ 100, has signal peptide
    # Long proteins:  length > 100, secreted/extracellular
    print("Fetching phenotype-matched negatives…")
    pheno_short_q = (
        "reviewed:true AND NOT keyword:KW-0800 "
        "AND length:[5 TO 100] AND ft_signal:* "
        "AND protein_existence:1"
    )
    pheno_long_q = (
        "reviewed:true AND NOT keyword:KW-0800 "
        "AND length:[101 TO 1000] "
        "AND cc_subcellular_location:Secreted "
        "AND protein_existence:1"
    )
    ph_short = _query_uniprot(pheno_short_q, 5000)
    ph_long  = _query_uniprot(pheno_long_q,  5000)
    pheno_entries = (
        [e for e in ph_short if e.get("primaryAccession","") not in positive_accs] +
        [e for e in ph_long  if e.get("primaryAccession","") not in positive_accs]
    )
    print(f"  Phenotype-matched: {len(pheno_entries)} entries")

    # ── 3. Family-aware negatives ─────────────────────────────────────────────
    # Non-toxic reviewed proteins from the same Pfam families.
    print("Fetching family-aware negatives…")
    fa_entries_all = []
    for pf in sorted(positive_pfam)[:50]:   # cap to 50 families for API courtesy
        q = (f"reviewed:true AND NOT keyword:KW-0800 "
             f"AND database:(type:pfam id:{pf})")
        batch = _query_uniprot(q, 300)
        fa_entries_all.extend(
            e for e in batch
            if e.get("primaryAccession","") not in positive_accs
        )
        time.sleep(0.3)

    # deduplicate by accession
    seen, fa_entries = set(), []
    for e in fa_entries_all:
        acc = e.get("primaryAccession","")
        if acc not in seen:
            seen.add(acc)
            fa_entries.append(e)
    print(f"  Family-aware: {len(fa_entries)} entries")

    # ── write phenotype metadata ──────────────────────────────────────────────
    def _to_row(e, pool):
        seq = _sequence(e)
        return {
            "accession":   e.get("primaryAccession",""),
            "pool":        pool,
            "length":      _length(e),
            "cys_frac":    round(_cys_frac(seq), 4),
            "has_signal":  int(_has_signal(e)),
            "is_secreted": _is_secreted(e),
            "pfam_ids":    "|".join(_pfam_ids(e)),
        }

    pheno_df = pd.DataFrame([_to_row(e, "phenotype_matched") for e in pheno_entries])
    fa_df    = pd.DataFrame([_to_row(e, "family_aware")      for e in fa_entries])

    pheno_df.to_csv(Path(RESULTS_DIR) / "negative_phenotype.tsv",    sep="\t", index=False)
    fa_df.to_csv(   Path(RESULTS_DIR) / "negative_family_aware.tsv", sep="\t", index=False)

    # Write FASTA
    for pool_name, pool_entries in [("phenotype", pheno_entries),
                                     ("family_aware", fa_entries)]:
        with open(Path(DATA_DIR) / f"negatives_{pool_name}.fasta", "w") as fh:
            for e in pool_entries:
                acc = e.get("primaryAccession","")
                seq = _sequence(e)
                if seq:
                    fh.write(f">{acc}\n{seq}\n")

    # ── Gate C evaluation ─────────────────────────────────────────────────────
    summary = pd.DataFrame([
        {"pool": "background",
         "n_available": len(bg_entries),
         "gate_c_primary_pass":    int(len(bg_entries) >= GATE_C_PRIMARY_MIN_NEG),
         "gate_c_secondary_pass":  int(len(bg_entries) >= GATE_C_SECONDARY_MIN_NEG)},
        {"pool": "phenotype_matched",
         "n_available": len(pheno_entries),
         "gate_c_primary_pass":    int(len(pheno_entries) >= GATE_C_PRIMARY_MIN_NEG),
         "gate_c_secondary_pass":  int(len(pheno_entries) >= GATE_C_SECONDARY_MIN_NEG)},
        {"pool": "family_aware",
         "n_available": len(fa_entries),
         "gate_c_primary_pass":    int(len(fa_entries) >= GATE_C_PRIMARY_MIN_NEG),
         "gate_c_secondary_pass":  int(len(fa_entries) >= GATE_C_SECONDARY_MIN_NEG)},
    ])
    summary["fpr_primary"]   = FPR_PRIMARY
    summary["fpr_secondary"] = FPR_SECONDARY
    summary["gate_c_primary_threshold"]   = GATE_C_PRIMARY_MIN_NEG
    summary["gate_c_secondary_threshold"] = GATE_C_SECONDARY_MIN_NEG
    summary.to_csv(Path(RESULTS_DIR) / "negative_pool_counts.tsv",
                   sep="\t", index=False)

    print(f"\n── Gate C — negative support ──────────────────────────────────")
    print(summary[["pool","n_available","gate_c_primary_pass",
                   "gate_c_secondary_pass"]].to_string(index=False))
    print(f"\nOutputs → {RESULTS_DIR}/")


if __name__ == "__main__":
    run()
