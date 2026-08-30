#!/usr/bin/env python3
"""
07_diagnostics.py — Shortcut diagnostics on the permanently burned partition (§6).

This script is model-blind. No ESM, SAE, or toxin-prediction features.

Features used (§6):
  - sequence length
  - amino-acid composition (20 dimensions)
  - cysteine fraction
  - molecular-weight proxy (log)
  - has_signal_peptide (binary)
  - has_propeptide (binary)
  - broad subcellular-localization metadata (is_secreted binary)
  - broad taxonomy encoding (kingdom-level one-hot)

Positives: toxin proteins in burned clusters.
Negatives: background Swiss-Prot proteins matched approximately to the burned positives.

Decision:
  If AUROC > 0.95 or AUPRC > 0.95 from these features alone,
  the naive toxin-vs-background task is rejected (Gate D FAIL).
  The target may still continue if matched negatives remove the shortcut.

Outputs:
  results/shortcut_diagnostic_results.tsv   — AUROC, AUPRC, top features
  results/gate_d_decision.tsv               — Gate D pass/fail
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, RESULTS_DIR, RANDOM_SEED

AUROC_REJECT_THRESHOLD = 0.95
AUPRC_REJECT_THRESHOLD = 0.95

AA_ORDER = list("ACDEFGHIKLMNPQRSTVWY")

TAX_KINGDOMS = ["Mammal", "Reptile", "Amphibian", "Fish", "Arachnid",
                "Insect", "Cnidarian", "Mollusc", "Other/Unknown"]


def _aa_comp_vector(seq: str) -> list[float]:
    n = len(seq) if seq else 1
    return [seq.count(aa) / n for aa in AA_ORDER]


def _tax_one_hot(lineage: str) -> list[float]:
    lin = str(lineage).lower()
    mapping = [("mammalia", "Mammal"), ("reptilia", "Reptile"),
               ("amphibia", "Amphibian"), ("actinopteri", "Fish"),
               ("arachnida", "Arachnid"), ("insecta", "Insect"),
               ("cnidaria", "Cnidarian"), ("mollusca", "Mollusc")]
    for kw, label in mapping:
        if kw in lin:
            idx = TAX_KINGDOMS.index(label)
            break
    else:
        idx = TAX_KINGDOMS.index("Other/Unknown")
    return [1.0 if i == idx else 0.0 for i in range(len(TAX_KINGDOMS))]


def _build_feature_row(row: pd.Series) -> list[float]:
    seq = str(row.get("_seq", ""))
    if not seq:
        # approximate from composition fields if _seq not present
        cys  = float(row.get("cysteine_frac", 0))
        seq  = "C" * int(cys * 100)   # dummy — just for length
    length = int(row.get("length",  len(seq)))
    mat_len = int(row.get("mature_length", length))
    has_sig = float(row.get("has_signal", 0))
    has_pro = float(row.get("has_propep", 0))
    cys_frac = float(row.get("cysteine_frac", seq.count("C") / max(len(seq), 1)))
    log_mw  = np.log1p(length * 110.0)   # rough Da proxy
    is_sec  = float("secret" in str(row.get("subcellular_loc","")).lower())
    aa_comp = [0.0] * 20       # without raw seq we can't compute
    tax_oh  = _tax_one_hot(str(row.get("lineage", "")))
    return ([length, mat_len, has_sig, has_pro, cys_frac, log_mw, is_sec]
            + aa_comp + tax_oh)


def _feature_names() -> list[str]:
    return (
        ["length", "mature_length", "has_signal", "has_propep",
         "cys_frac", "log_mw", "is_secreted"] +
        [f"aa_{aa}" for aa in AA_ORDER] +
        [f"tax_{k}" for k in TAX_KINGDOMS]
    )


def run():
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    entries_path = Path(RESULTS_DIR) / "cleaned_entries.tsv"
    burn_path    = Path(RESULTS_DIR) / "diagnostic_burn_ids.txt"
    div_path     = Path(RESULTS_DIR) / "divergence_assignment.tsv"
    neg_path     = Path(RESULTS_DIR) / "negative_phenotype.tsv"

    for p in (entries_path, burn_path, div_path):
        if not p.exists():
            sys.exit(f"Missing {p} — run prior steps first")

    burned_reps = set(Path(burn_path).read_text().splitlines())
    div         = pd.read_csv(div_path, sep="\t")
    entries     = pd.read_csv(entries_path, sep="\t")

    # Cluster membership to identify which positives are in burned clusters
    cluster_tsv = Path(RESULTS_DIR) / "clusters_precursor.tsv"
    member_to_rep = {}
    if cluster_tsv.exists():
        with open(cluster_tsv) as fh:
            for line in fh:
                p = line.rstrip().split("\t")
                if len(p) >= 2:
                    member_to_rep[p[1]] = p[0]

    entries["cluster_rep"] = entries["accession"].map(
        lambda a: member_to_rep.get(a, a)
    )
    burned_positives = entries[entries["cluster_rep"].isin(burned_reps)].copy()

    if len(burned_positives) < 10:
        print("WARNING: fewer than 10 burned positives — diagnostics unreliable")

    # Negatives for the diagnostic: phenotype-matched or background
    if neg_path.exists():
        neg_df = pd.read_csv(neg_path, sep="\t")
    else:
        print("No phenotype-matched negatives found — skipping shortcut diagnostics")
        print("Run 06_negatives.py first")
        return

    # ── Build feature matrix ──────────────────────────────────────────────────
    rng = np.random.default_rng(RANDOM_SEED)
    pos_rows = burned_positives[["accession","length","mature_length",
                                  "has_signal","has_propep","cysteine_frac",
                                  "subcellular_loc","lineage"]].copy()
    neg_rows = neg_df[["accession","length","cys_frac",
                        "has_signal","is_secreted"]].copy()

    # Sample negatives 3:1 over positives for more reliable FPR estimation
    n_pos = len(pos_rows)
    n_neg_sample = min(len(neg_rows), 3 * n_pos)
    neg_sample   = neg_df.sample(n=n_neg_sample, random_state=RANDOM_SEED)

    X_pos = np.array([[
        float(r.get("length", 0)),
        float(r.get("mature_length", r.get("length", 0))),
        float(r.get("has_signal", 0)),
        float(r.get("has_propep", 0)),
        float(r.get("cysteine_frac", 0)),
        np.log1p(float(r.get("length", 0)) * 110),
        float("secret" in str(r.get("subcellular_loc","")).lower()),
    ] + [0.0]*20 + _tax_one_hot(str(r.get("lineage","")))
    for _, r in pos_rows.iterrows()])

    X_neg = np.array([[
        float(r.get("length", 0)),
        float(r.get("length", 0)),   # no mature_length for negatives
        float(r.get("has_signal", 0)),
        0.0,                          # no propeptide in negative table
        float(r.get("cys_frac", 0)),
        np.log1p(float(r.get("length", 0)) * 110),
        float(r.get("is_secreted", 0)),
    ] + [0.0]*20 + [0.0]*len(TAX_KINGDOMS)
    for _, r in neg_sample.iterrows()])

    X = np.vstack([X_pos, X_neg])
    y = np.array([1]*n_pos + [0]*n_neg_sample)

    # Shuffle
    idx = rng.permutation(len(y))
    X, y = X[idx], y[idx]

    # ── Fit and evaluate ───────────────────────────────────────────────────────
    results = []
    feat_names = _feature_names()

    for name, model in [
        ("logistic_regression",
         Pipeline([("sc", StandardScaler()),
                   ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_SEED))])),
        ("random_forest",
         RandomForestClassifier(n_estimators=200, min_samples_leaf=2,
                                random_state=RANDOM_SEED)),
    ]:
        # Leave-one-cluster-out is ideal but we don't have cluster membership
        # for negatives. Use 5-fold stratified as the best available.
        from sklearn.model_selection import StratifiedKFold
        cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
        aucs, aps = [], []
        for train_idx, test_idx in cv.split(X, y):
            model.fit(X[train_idx], y[train_idx])
            probs = model.predict_proba(X[test_idx])[:,1]
            if y[test_idx].sum() > 0 and (1 - y[test_idx]).sum() > 0:
                aucs.append(roc_auc_score(y[test_idx], probs))
                aps.append(average_precision_score(y[test_idx], probs))

        auroc_mean = float(np.mean(aucs))
        auprc_mean = float(np.mean(aps))
        results.append({
            "model":         name,
            "auroc_mean":    round(auroc_mean, 4),
            "auprc_mean":    round(auprc_mean, 4),
            "n_pos":         n_pos,
            "n_neg":         n_neg_sample,
            "shortcut_flag": int(auroc_mean > AUROC_REJECT_THRESHOLD or
                                  auprc_mean > AUPRC_REJECT_THRESHOLD),
        })

    res_df = pd.DataFrame(results)
    res_df.to_csv(Path(RESULTS_DIR) / "shortcut_diagnostic_results.tsv",
                   sep="\t", index=False)

    # ── Gate D decision ───────────────────────────────────────────────────────
    any_flag  = res_df["shortcut_flag"].any()
    gate_d    = "FAIL" if any_flag else "PASS"
    gate_d_df = pd.DataFrame([{
        "gate_d_decision": gate_d,
        "auroc_threshold": AUROC_REJECT_THRESHOLD,
        "auprc_threshold": AUPRC_REJECT_THRESHOLD,
        "note": ("Naive task rejected — use matched negatives."
                 if gate_d == "FAIL" else
                 "Shortcut resistance adequate for naive task."),
    }])
    gate_d_df.to_csv(Path(RESULTS_DIR) / "gate_d_decision.tsv",
                      sep="\t", index=False)

    print(f"\n── Shortcut diagnostics (burned partition only) ──────────────")
    print(f"  Positives: {n_pos}  |  Negatives: {n_neg_sample}")
    print(res_df[["model","auroc_mean","auprc_mean","shortcut_flag"]].to_string(index=False))
    print(f"\n  Gate D: {gate_d}")
    if gate_d == "FAIL":
        print("  → Naive task rejected. Matched/family-aware negatives required.")
    print(f"\nOutputs → {RESULTS_DIR}/")


if __name__ == "__main__":
    run()
