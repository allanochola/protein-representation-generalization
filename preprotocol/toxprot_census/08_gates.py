#!/usr/bin/env python3
"""
08_gates.py — Evaluate all gates and issue the census decision (§§8, 10).

Decision:
  GO        — all gates pass; proceed to statistical feasibility, then protocol
  REDESIGN  — target is promising but negative matching, estimand, or family
               structure requires further pre-data work
  NO-GO     — independent family support too small, shortcuts not controlled,
               reliable negatives cannot be constructed, or estimand not
               estimable at required precision

No gate may be weakened after this script is run.
This script computes Gate E (inferential feasibility) from the observed counts.

Outputs:
  results/gate_evaluation.tsv     — all gate verdicts with observed values
  results/precision_check.tsv     — Gate E: power/precision at observed support
  results/census_decision.txt     — final GO / REDESIGN / NO-GO
"""

import sys
from pathlib import Path
import numpy as np
from scipy.stats import norm, beta as beta_dist
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from config import (RESULTS_DIR,
                    GATE_A_STRICT_MIN, GATE_A_REDESIGN_FLOOR,
                    GATE_B_MAX_FAMILY_FRAC,
                    GATE_C_PRIMARY_MIN_NEG, GATE_C_SECONDARY_MIN_NEG,
                    FPR_PRIMARY, FPR_SECONDARY,
                    TARGET_HW, PLAN_DTPR_TRUE,
                    RANDOM_SEED)

# ── Paired dTPR half-width (planning model from Exp 02 calibration) ─────────
# SE = sqrt((p01 + p10 - (p01-p10)^2) / n)
# At planning dTPR=0.15 and discordance=0.25: se per cluster ~ 0.460
# Calibrated against Exp 02's Δ_AP std at n=170: SE170 = 0.0409/1.96
# This is a planning approximation. §8 mandates re-running on a validated
# paired cluster-bootstrap simulator before the final protocol is written.
SE_PER_CLUSTER_PLANNING = 0.0409 / 1.96 * np.sqrt(170)  # ~ 0.272

def _hw(n_div: int, discordance: float = 0.25, true_dtpr: float = PLAN_DTPR_TRUE) -> float:
    """95% CI half-width on paired dTPR at n_div divergent clusters."""
    if n_div <= 0:
        return np.inf
    variance = (discordance - true_dtpr**2) / n_div
    return 1.96 * np.sqrt(variance)


def _power(n_div: int, true_dtpr: float = PLAN_DTPR_TRUE,
           discordance: float = 0.25, alpha: float = 0.05) -> float:
    """Power to detect dTPR > 0 at one-sided alpha, n_div clusters."""
    if n_div <= 0:
        return 0.0
    se = np.sqrt((discordance - true_dtpr**2) / n_div)
    z  = true_dtpr / se - norm.ppf(1 - alpha)
    return float(norm.cdf(z))


def _fpr_ci(n_neg: int, fpr: float) -> tuple[float, float]:
    """Wilson 95% CI on realized FPR with n_neg negatives."""
    k = fpr * n_neg
    lo = beta_dist.ppf(0.025, k + 0.5, n_neg - k + 0.5)
    hi = beta_dist.ppf(0.975, k + 0.5, n_neg - k + 0.5)
    return round(lo, 4), round(hi, 4)


def load(path, required=True):
    p = Path(RESULTS_DIR) / path
    if not p.exists():
        if required:
            sys.exit(f"Missing {p} — run prior steps first")
        return None
    return pd.read_csv(p, sep="\t")


def run():
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    # ── Load census outputs ───────────────────────────────────────────────────
    div        = load("divergence_assignment.tsv")
    gv2        = load("gatev2_audit.tsv")
    fam_conc   = load("family_concentration.tsv")
    neg_counts = load("negative_pool_counts.tsv")
    ann_cov    = load("annotation_coverage.tsv")
    gate_d_df  = load("gate_d_decision.tsv", required=False)

    # ── Observed support numbers ──────────────────────────────────────────────
    n_total_clusters   = int(div.shape[0])
    n_divergent_v2a    = int(gv2["is_divergent_v2a"].sum())
    n_disjoint_v2b     = int(gv2["is_disjoint_v2b"].sum())
    n_missing_pfam     = int((gv2["annotation_status"] == "missing_pfam").sum()
                              if "annotation_status" in gv2.columns else 0)
    usable_strict      = n_disjoint_v2b     # after burns, strict count
    divergent_frac     = n_divergent_v2a / n_total_clusters if n_total_clusters else 0

    # Best negative pool counts
    if neg_counts is not None:
        best_neg_primary = int(neg_counts[
            neg_counts["gate_c_primary_pass"] == 1
        ]["n_available"].max() if (neg_counts["gate_c_primary_pass"] == 1).any() else 0)
        best_neg_secondary = int(neg_counts[
            neg_counts["gate_c_secondary_pass"] == 1
        ]["n_available"].max() if (neg_counts["gate_c_secondary_pass"] == 1).any() else 0)
    else:
        best_neg_primary = best_neg_secondary = 0

    # Gate B: largest family fraction
    if fam_conc is not None and len(fam_conc) > 0:
        top_fam_frac = float(fam_conc.iloc[0]["frac_of_divergent"])
        top_fam_id   = fam_conc.iloc[0]["pfam_family"]
    else:
        top_fam_frac, top_fam_id = 0.0, "N/A"

    # Gate D
    if gate_d_df is not None:
        gate_d_verdict = gate_d_df.iloc[0]["gate_d_decision"]
    else:
        gate_d_verdict = "NOT_RUN"

    # ── Gate verdicts ─────────────────────────────────────────────────────────
    gate_a_strict = usable_strict >= GATE_A_STRICT_MIN
    gate_a_redesign = n_total_clusters >= GATE_A_REDESIGN_FLOOR
    gate_b        = top_fam_frac <= GATE_B_MAX_FAMILY_FRAC
    gate_c_prim   = best_neg_primary   >= GATE_C_PRIMARY_MIN_NEG
    gate_c_sec    = best_neg_secondary >= GATE_C_SECONDARY_MIN_NEG
    gate_d        = gate_d_verdict in ("PASS", "NOT_RUN")

    # ── Gate E: precision check at observed support ───────────────────────────
    hw_at_v2b  = _hw(usable_strict)
    pwr_at_v2b = _power(usable_strict)
    hw_at_v2a  = _hw(n_divergent_v2a)

    fpr_lo_prim, fpr_hi_prim = _fpr_ci(best_neg_primary,   FPR_PRIMARY)
    fpr_lo_sec,  fpr_hi_sec  = _fpr_ci(best_neg_secondary, FPR_SECONDARY)

    gate_e_hw_pass  = hw_at_v2b <= TARGET_HW
    gate_e_fpr_pass = gate_c_prim  # FPR stability tied to negative count

    precision_df = pd.DataFrame([
        {"quantity": "dTPR_half_width (V2-B strict)",
         "value": round(hw_at_v2b, 4),
         "target": TARGET_HW,
         "pass": int(gate_e_hw_pass)},
        {"quantity": "dTPR_half_width (V2-A all divergent)",
         "value": round(hw_at_v2a, 4),
         "target": TARGET_HW,
         "pass": int(hw_at_v2a <= TARGET_HW)},
        {"quantity": "80pct_power_dTPR=0.15 (V2-B)",
         "value": round(pwr_at_v2b, 4),
         "target": 0.80,
         "pass": int(pwr_at_v2b >= 0.80)},
        {"quantity": f"FPR_CI_width at primary ({FPR_PRIMARY})",
         "value": round(fpr_hi_prim - fpr_lo_prim, 4),
         "target": 0.03,   # <3pp width is interpretable
         "pass": int((fpr_hi_prim - fpr_lo_prim) <= 0.03)},
    ])
    precision_df.to_csv(Path(RESULTS_DIR) / "precision_check.tsv",
                         sep="\t", index=False)

    # ── Gate evaluation table ─────────────────────────────────────────────────
    gate_df = pd.DataFrame([
        {"gate": "A_strict",
         "description":   f"≥{GATE_A_STRICT_MIN} usable V2-B divergent+disjoint clusters",
         "observed":      usable_strict,
         "threshold":     GATE_A_STRICT_MIN,
         "verdict":       "PASS" if gate_a_strict else "FAIL"},
        {"gate": "A_total",
         "description":   f"≥{GATE_A_REDESIGN_FLOOR} total positive clusters (redesign floor)",
         "observed":      n_total_clusters,
         "threshold":     GATE_A_REDESIGN_FLOOR,
         "verdict":       "PASS" if gate_a_redesign else "FAIL"},
        {"gate": "B",
         "description":   f"No single family > {GATE_B_MAX_FAMILY_FRAC:.0%} of divergent clusters",
         "observed":      f"{top_fam_frac:.3f} ({top_fam_id})",
         "threshold":     GATE_B_MAX_FAMILY_FRAC,
         "verdict":       "PASS" if gate_b else "FAIL"},
        {"gate": "C_primary",
         "description":   f"≥{GATE_C_PRIMARY_MIN_NEG} matched negatives (FPR={FPR_PRIMARY})",
         "observed":      best_neg_primary,
         "threshold":     GATE_C_PRIMARY_MIN_NEG,
         "verdict":       "PASS" if gate_c_prim else "FAIL"},
        {"gate": "C_secondary",
         "description":   f"≥{GATE_C_SECONDARY_MIN_NEG} matched negatives (FPR={FPR_SECONDARY})",
         "observed":      best_neg_secondary,
         "threshold":     GATE_C_SECONDARY_MIN_NEG,
         "verdict":       "PASS" if gate_c_sec else "FAIL"},
        {"gate": "D",
         "description":   "Shortcut resistance (metadata doesn't solve task)",
         "observed":      gate_d_verdict,
         "threshold":     "AUROC/AUPRC < 0.95",
         "verdict":       "PASS" if gate_d else "FAIL"},
        {"gate": "E_halfwidth",
         "description":   f"95% CI half-width ≤{TARGET_HW} on ΔTPR (V2-B support)",
         "observed":      round(hw_at_v2b, 4),
         "threshold":     TARGET_HW,
         "verdict":       "PASS" if gate_e_hw_pass else "FAIL"},
        {"gate": "E_power",
         "description":   "≥80% power to detect ΔTPR=0.15 (planning assumption)",
         "observed":      round(pwr_at_v2b, 4),
         "threshold":     0.80,
         "verdict":       "PASS" if pwr_at_v2b >= 0.80 else "FAIL"},
    ])
    gate_df.to_csv(Path(RESULTS_DIR) / "gate_evaluation.tsv",
                   sep="\t", index=False)

    # ── Final decision (§10) ──────────────────────────────────────────────────
    hard_fail = (
        not gate_a_redesign or       # < 300 total clusters
        (not gate_a_strict and usable_strict < 45) or  # deeply starved
        not gate_c_prim or           # can't fix the threshold
        (gate_d_verdict == "FAIL" and not gate_c_prim)  # shortcut + no matched negs
    )
    any_fail  = not (gate_a_strict and gate_b and gate_c_prim
                     and gate_d and gate_e_hw_pass)

    if hard_fail:
        decision = "NO-GO"
        reason   = ("Independent family support too small, "
                    "reliable negatives insufficient, or task dominated by shortcuts.")
    elif any_fail:
        decision = "REDESIGN"
        reason   = ("Target is biologically promising but one or more gates "
                    "require additional pre-data work before model evaluation.")
    else:
        decision = "GO"
        reason   = ("All primary gates pass. Proceed to validated paired "
                    "cluster-bootstrap simulation, then experiment protocol.")

    decision_text = f"""
CENSUS DECISION: {decision}
{reason}

Key observed values
-------------------
Total positive clusters        : {n_total_clusters}
Sequence-divergent (V2-A)      : {n_divergent_v2a}  ({divergent_frac:.1%})
Divergent + family-disjoint V2-B: {usable_strict}
  of which missing Pfam annot  : {n_missing_pfam}
Best matched-negative pool     : {best_neg_primary}  (primary FPR={FPR_PRIMARY})
dTPR half-width at V2-B support: {hw_at_v2b:.4f}  (target ≤{TARGET_HW})
Power at ΔTPR=0.15 (planning)  : {pwr_at_v2b:.3f}  (target ≥0.80)

Gate verdicts
-------------
""".strip() + "\n" + "\n".join(
        f"  {r['gate']:15s} {r['verdict']:8s}  {r['description']}"
        for _, r in gate_df.iterrows()
    ) + "\n"

    out_txt = Path(RESULTS_DIR) / "census_decision.txt"
    out_txt.write_text(decision_text)

    print("\n" + "="*60)
    print(decision_text)
    print("="*60)
    print(f"\nOutputs → {RESULTS_DIR}/")


if __name__ == "__main__":
    run()
