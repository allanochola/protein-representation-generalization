#!/usr/bin/env python3
"""
05_families.py — Family annotation, concentration diagnostics, and Gate V2.

Implements §4.3 (family-disjoint status) and §7 (family + homology-transfer audit).

Gate V2:
  V2-A: sequence-divergent (no ≥30% identity cross-cluster)
  V2-B: sequence-divergent AND family-disjoint
        (no shared Pfam family with any reference-set cluster)

Missing Pfam annotations are flagged and reported separately.
They are never silently counted as evidence of family disjointness.

Inputs:
  results/cleaned_entries.tsv
  results/divergence_assignment.tsv

Outputs:
  results/family_concentration.tsv        — family × cluster breakdown (§11 output 5)
  results/gatev2_audit.tsv                — V2-A and V2-B cluster classification
  results/annotation_coverage.tsv         — Pfam/InterPro coverage stats
"""

import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, RESULTS_DIR, GATE_B_MAX_FAMILY_FRAC


def _parse_ids(s: str) -> list[str]:
    """Parse pipe-separated ID string, drop empty."""
    if pd.isna(s) or not str(s).strip():
        return []
    return [x.strip() for x in str(s).split("|") if x.strip()]


def run():
    entries_path = Path(RESULTS_DIR) / "cleaned_entries.tsv"
    div_path     = Path(RESULTS_DIR) / "divergence_assignment.tsv"

    for p in (entries_path, div_path):
        if not p.exists():
            sys.exit(f"Missing {p} — run prior steps first")

    entries = pd.read_csv(entries_path, sep="\t", dtype=str)
    div     = pd.read_csv(div_path,     sep="\t")

    # ── merge family annotations onto divergence table ────────────────────────
    # Cluster representative = cluster_rep in div.
    # Build rep → pfam_ids, interpro_ids mapping from entries.
    rep_to_pfam    = {}
    rep_to_interpro = {}
    rep_to_toxkw   = {}
    rep_to_lineage  = {}

    for _, row in entries.iterrows():
        acc  = row["accession"]
        pfam = _parse_ids(row.get("pfam_ids", ""))
        ipr  = _parse_ids(row.get("interpro_ids", ""))
        tkw  = _parse_ids(row.get("toxin_keywords", ""))
        lin  = str(row.get("lineage", ""))
        rep_to_pfam[acc]      = pfam
        rep_to_interpro[acc]  = ipr
        rep_to_toxkw[acc]     = tkw
        rep_to_lineage[acc]   = lin

    # Also accumulate family annotations across all members in each cluster.
    # But we only have rep-level info from cleaned_entries (members are sequences
    # too, but all have their own rows). Group by clusters via the cluster tsv.
    # Easier: for family annotation, use the entries table — each protein has its own.
    # Map accession → cluster_rep.
    # We need the cluster membership file.
    cluster_tsv = Path(RESULTS_DIR) / "clusters_precursor.tsv"
    member_to_rep = {}
    if cluster_tsv.exists():
        with open(cluster_tsv) as fh:
            for line in fh:
                parts = line.rstrip().split("\t")
                if len(parts) >= 2:
                    member_to_rep[parts[1]] = parts[0]

    # For each cluster, collect all Pfam families across all members.
    cluster_pfam_families = defaultdict(set)
    cluster_toxin_kw      = defaultdict(set)
    cluster_lineages       = defaultdict(list)

    for _, row in entries.iterrows():
        acc = row["accession"]
        rep = member_to_rep.get(acc, acc)   # if not in map, is its own rep
        for pf in _parse_ids(row.get("pfam_ids", "")):
            cluster_pfam_families[rep].add(pf)
        for kw in _parse_ids(row.get("toxin_keywords", "")):
            cluster_toxin_kw[rep].add(kw)
        cluster_lineages[rep].append(str(row.get("lineage", "")))

    # ── corpus-wide Pfam occurrence map ──────────────────────────────────────
    # Family-disjointness is a property of the frozen positive corpus.
    # For cluster C, compare its Pfam families against ALL OTHER positive
    # clusters. Diagnostic burn affects later data use, not whether biological
    # relatives exist in the corpus.
    pfam_to_clusters = defaultdict(set)

    for rep, pfams in cluster_pfam_families.items():
        for pf in pfams:
            pfam_to_clusters[pf].add(rep)

    all_pfam_families = set(pfam_to_clusters)

    # ── cluster length metadata ───────────────────────────────────────────────
    acc_to_length = {
        row["accession"]: int(row["length"])
        for _, row in entries.iterrows()
    }

    cluster_lengths = defaultdict(list)

    for acc, rep in member_to_rep.items():
        if acc in acc_to_length:
            cluster_lengths[rep].append(acc_to_length[acc])

    def _length_bin(length):
        if length is None:
            return "unknown"
        if length < 30:
            return "<30"
        if length <= 75:
            return "30-75"
        if length <= 150:
            return "76-150"
        return ">150"

    # ── Gate V2 classification ────────────────────────────────────────────────
    gatev2_rows = []
    for _, row in div.iterrows():
        rep       = row["cluster_rep"]
        is_div    = row["is_divergent"] == 1
        is_burned = row["in_diagnostic_burn"] == 1

        pfams = cluster_pfam_families.get(rep, set())
        has_pfam = len(pfams) > 0
        shared_pfam = {
            pf for pf in pfams
            if any(
                other_rep != rep
                for other_rep in pfam_to_clusters.get(pf, set())
            )
        }

        # V2-A: sequence-divergent and not diagnostically burned.
        v2a = is_div and not is_burned

        # V2-B is defined only within the usable V2-A population.
        if not v2a:
            v2b = False
            annotation_status = "not_v2a"
        elif not has_pfam:
            # Missing Pfam cannot establish family disjointness.
            v2b = False
            annotation_status = "missing_pfam"
        elif shared_pfam:
            v2b = False
            annotation_status = "shared_pfam"
        else:
            v2b = True
            annotation_status = "disjoint"

        lengths = cluster_lengths.get(rep, [])
        rep_length = acc_to_length.get(rep)
        min_length = min(lengths) if lengths else None
        median_length = (
            float(pd.Series(lengths).median())
            if lengths else None
        )
        max_length = max(lengths) if lengths else None
        is_singleton = int(len(lengths) == 1)
        length_bin = _length_bin(median_length)

        # Dominant toxin keyword for this cluster
        dominant_kw = sorted(cluster_toxin_kw.get(rep, {"unknown"}),
                             key=lambda x: x)[0]

        # Broad taxonomic group (kingdom level)
        lins = cluster_lineages.get(rep, [""])
        tax_group = _tax_group(lins[0] if lins else "")

        gatev2_rows.append({
            "cluster_rep":          rep,
            "n_members":            int(row["n_members"]),
            "is_divergent_v2a":     int(v2a),
            "is_disjoint_v2b":      int(v2b),
            "annotation_status":    annotation_status,
            "pfam_families":        "|".join(sorted(pfams)),
            "shared_with_ref":      "|".join(sorted(shared_pfam)),
            "dominant_toxin_kw":    dominant_kw,
            "tax_group":            tax_group,
            "in_diagnostic_burn":   int(is_burned),
            "representative_length": rep_length,
            "min_length":            min_length,
            "median_length":         median_length,
            "max_length":            max_length,
            "length_bin":            length_bin,
            "is_singleton":          is_singleton,
        })

    gv2 = pd.DataFrame(gatev2_rows)
    gv2.to_csv(Path(RESULTS_DIR) / "gatev2_audit.tsv", sep="\t", index=False)

    # ── family concentration ──────────────────────────────────────────────────
    # Per-cluster: which Pfam families are present, how many clusters per family?
    family_cluster_counts = defaultdict(int)
    for _, row in gv2.iterrows():
        if row["is_divergent_v2a"]:
            for pf in _parse_ids(row["pfam_families"]):
                family_cluster_counts[pf] += 1

    total_div = gv2["is_divergent_v2a"].sum()
    fam_rows = []
    for pf, n in sorted(family_cluster_counts.items(),
                         key=lambda x: -x[1]):
        fam_rows.append({
            "pfam_family":      pf,
            "n_divergent_clusters": n,
            "frac_of_divergent":    round(n / total_div, 4) if total_div else 0,
        })
    fam_df = pd.DataFrame(fam_rows)
    fam_df.to_csv(Path(RESULTS_DIR) / "family_concentration.tsv",
                   sep="\t", index=False)

    # ── annotation coverage ───────────────────────────────────────────────────
    n_div = int(gv2["is_divergent_v2a"].sum())
    n_v2b = int(gv2["is_disjoint_v2b"].sum())

    v2a_df = gv2[gv2["is_divergent_v2a"] == 1].copy()

    assert set(v2a_df["annotation_status"]).issubset(
        {"missing_pfam", "shared_pfam", "disjoint"}
    )

    n_no_pfam = int(
        (v2a_df["annotation_status"] == "missing_pfam").sum()
    )
    n_shared = int(
        (v2a_df["annotation_status"] == "shared_pfam").sum()
    )
    n_disjoint = int(
        (v2a_df["annotation_status"] == "disjoint").sum()
    )

    assert n_no_pfam + n_shared + n_disjoint == n_div
    assert n_disjoint == n_v2b

    ann_cov = pd.DataFrame([{
        "n_total_clusters":           int(div.shape[0]),
        "n_divergent_v2a":            n_div,
        "n_disjoint_v2b":             n_v2b,
        "n_missing_pfam_annotation":  n_no_pfam,
        "n_shared_pfam_with_ref":     n_shared,
        "n_confirmed_disjoint":       n_disjoint,
        "pct_div_missing_pfam":       round(n_no_pfam / n_div, 3) if n_div else 0,
    }])
    ann_cov.to_csv(Path(RESULTS_DIR) / "annotation_coverage.tsv",
                   sep="\t", index=False)

    # ── V2-B length/singleton stratification ─────────────────────────────────
    strat_rows = []

    for length_bin, sub in v2a_df.groupby("length_bin", dropna=False):
        strat_rows.append({
            "stratum_type": "length_bin",
            "stratum": length_bin,
            "n_v2a": len(sub),
            "n_missing_pfam": int(
                (sub["annotation_status"] == "missing_pfam").sum()
            ),
            "n_shared_pfam": int(
                (sub["annotation_status"] == "shared_pfam").sum()
            ),
            "n_v2b": int(sub["is_disjoint_v2b"].sum()),
            "v2b_fraction": round(
                sub["is_disjoint_v2b"].mean(), 4
            ) if len(sub) else 0,
        })

    for singleton, sub in v2a_df.groupby("is_singleton"):
        strat_rows.append({
            "stratum_type": "singleton_status",
            "stratum": (
                "singleton"
                if int(singleton) == 1
                else "non_singleton"
            ),
            "n_v2a": len(sub),
            "n_missing_pfam": int(
                (sub["annotation_status"] == "missing_pfam").sum()
            ),
            "n_shared_pfam": int(
                (sub["annotation_status"] == "shared_pfam").sum()
            ),
            "n_v2b": int(sub["is_disjoint_v2b"].sum()),
            "v2b_fraction": round(
                sub["is_disjoint_v2b"].mean(), 4
            ) if len(sub) else 0,
        })

    strat_df = pd.DataFrame(strat_rows)

    strat_df.to_csv(
        Path(RESULTS_DIR) / "gatev2_length_stratification.tsv",
        sep="\t",
        index=False,
    )

    # ── Gate B check ──────────────────────────────────────────────────────────
    gate_b_pass = True
    if len(fam_df) > 0:
        top_frac = fam_df.iloc[0]["frac_of_divergent"]
        gate_b_pass = top_frac <= GATE_B_MAX_FAMILY_FRAC
    else:
        top_frac = 0.0

    # ── console summary ───────────────────────────────────────────────────────
    print(f"\n── Family structure & Gate V2 ────────────────────────────────")
    print(f"  Unique Pfam families in positive corpus: {len(all_pfam_families)}")
    print(f"  V2-A (sequence-divergent):             {n_div}")
    print(f"  V2-B (divergent + family-disjoint):    {n_v2b}")
    print(f"    of which: missing Pfam → uncounted:  {n_no_pfam}")
    print(f"    of which: shared Pfam with ref:       {n_shared}")
    print(f"    of which: confirmed disjoint:         {n_disjoint}")
    print(f"\n── Gate B — family concentration ─────────────────────────────")
    if len(fam_df) > 0:
        print(f"  Largest family: {fam_df.iloc[0]['pfam_family']} "
              f"({top_frac:.1%} of divergent clusters)")
        print(f"  Gate B threshold: ≤{GATE_B_MAX_FAMILY_FRAC:.0%}")
        print(f"  Gate B: {'PASS' if gate_b_pass else 'FAIL'}")
        print(f"\n  Top-5 Pfam families by divergent-cluster count:")
        print(fam_df.head(5).to_string(index=False))
    print(f"\nOutputs → {RESULTS_DIR}/")


def _tax_group(lineage: str) -> str:
    lin = lineage.lower()
    for kw, label in [("mammalia", "Mammal"), ("reptilia", "Reptile"),
                       ("amphibia", "Amphibian"), ("actinopteri", "Fish"),
                       ("arachnida", "Arachnid"), ("insecta", "Insect"),
                       ("cnidaria", "Cnidarian"), ("mollusca", "Mollusc"),
                       ("echinodermata", "Echinoderm"),
                       ("bacteria", "Bacteria"), ("fungi", "Fungi"),
                       ("viridiplantae", "Plant")]:
        if kw in lin:
            return label
    return "Other/Unknown"


if __name__ == "__main__":
    run()
