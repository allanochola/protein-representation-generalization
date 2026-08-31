#!/usr/bin/env python3
"""
07_diagnostics.py — Model-blind shortcut diagnostics on permanently burned data.

Purpose
-------
Test whether the proposed toxin-vs-negative task is nearly trivial from simple
sequence-derived shortcuts before any protein-model representation is examined.

Primary Gate D decision pool:
    sequence-clean family-aware negatives

Descriptive comparison pools:
    sequence-clean phenotype-matched negatives
    sequence-clean background negatives

Positive diagnostic set:
    one representative sequence from every permanently burned positive cluster

Negative diagnostic set:
    deterministic hash-burned subset of each Step 06B filtered negative pool.
    Negatives used here are permanently unavailable for later confirmatory use.

Primary model-blind features:
    sequence length
    20-dimensional amino-acid composition

All features are computed identically from FASTA sequences for positives and
negatives. No asymmetric UniProt metadata is used.

Decision rule
-------------
For the family-aware pool only:

    Gate D FAIL if either diagnostic model reaches
        AUROC > 0.95 OR AUPRC > 0.95

    otherwise Gate D PASS.

Background and phenotype results are descriptive robustness diagnostics and do
not independently determine Gate D.

No ESM, SAE, probe, toxin-prediction, or model-derived feature is touched.

Inputs
------
    data/cleaned_precursor.fasta
    results/clusters_precursor.tsv
    results/diagnostic_burn_ids.txt

    data/negatives_background_filtered.fasta
    data/negatives_phenotype_filtered.fasta
    data/negatives_family_aware_filtered.fasta

Outputs
-------
    results/shortcut_diagnostic_results.tsv
    results/shortcut_feature_importance.tsv
    results/negative_diagnostic_partition.tsv
    results/gate_d_decision.tsv
"""

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DATA_DIR,
    RESULTS_DIR,
    RANDOM_SEED,
    DIAGNOSTIC_BURN_THRESHOLD_BYTE,
)

AUROC_REJECT_THRESHOLD = 0.95
AUPRC_REJECT_THRESHOLD = 0.95

AA_ORDER = list("ACDEFGHIKLMNPQRSTVWY")

POOLS = [
    "background",
    "phenotype",
    "family_aware",
]

PRIMARY_GATE_D_POOL = "family_aware"

N_SPLITS = 5
NEGATIVE_TO_POSITIVE_DIAGNOSTIC_RATIO = 3


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


def load_clusters(path: Path):
    member_to_rep = {}
    rep_to_members = {}

    with open(path) as fh:
        for line in fh:
            parts = line.rstrip().split("\t")

            if len(parts) < 2:
                continue

            rep, member = parts[0], parts[1]

            member_to_rep[member] = rep
            rep_to_members.setdefault(rep, []).append(member)

    return member_to_rep, rep_to_members


def is_diagnostic_burn(accession: str) -> bool:
    """
    Same deterministic burn geometry used by the positive census.
    """
    first_byte = int(
        hashlib.md5(accession.encode()).hexdigest()[:2],
        16,
    )

    return first_byte < DIAGNOSTIC_BURN_THRESHOLD_BYTE


def stable_hash(accession: str) -> str:
    return hashlib.md5(accession.encode()).hexdigest()


def sequence_features(seq: str) -> list[float]:
    """
    Symmetric model-blind features available identically for every sequence.
    """
    n = len(seq)

    if n <= 0:
        raise ValueError("Cannot build features for empty sequence")

    aa_comp = [
        seq.count(aa) / n
        for aa in AA_ORDER
    ]

    return [
        float(n),
        *aa_comp,
    ]


def feature_names():
    return [
        "length",
        *[f"aa_{aa}" for aa in AA_ORDER],
    ]


def build_primary_positive_set(
    pos_sequences: dict[str, str],
    burned_reps: set[str],
):
    """
    One sequence per burned positive cluster: the cluster representative.

    The statistical unit of the positive census is the cluster, so this avoids
    allowing large positive clusters to dominate the shortcut diagnostic.
    """
    missing = sorted(
        rep for rep in burned_reps
        if rep not in pos_sequences
    )

    if missing:
        raise RuntimeError(
            f"{len(missing)} burned cluster representatives are missing "
            f"from cleaned_precursor.fasta; first examples: {missing[:10]}"
        )

    selected = {
        rep: pos_sequences[rep]
        for rep in sorted(burned_reps)
    }

    return selected


def select_negative_diagnostic_set(
    sequences: dict[str, str],
    max_n: int,
):
    """
    Permanently burn negatives by accession hash.

    If the burned subset is larger than needed for the frozen 3:1 diagnostic
    ratio, choose the first max_n accessions in deterministic full-MD5 order.
    """
    burned = {
        acc: seq
        for acc, seq in sequences.items()
        if is_diagnostic_burn(acc)
    }

    burned_sorted = sorted(
        burned,
        key=stable_hash,
    )

    selected_ids = burned_sorted[:max_n]

    selected = {
        acc: burned[acc]
        for acc in selected_ids
    }

    return selected, set(burned)


def build_xy(
    pos_sequences: dict[str, str],
    neg_sequences: dict[str, str],
):
    X_pos = np.asarray([
        sequence_features(seq)
        for seq in pos_sequences.values()
    ], dtype=float)

    X_neg = np.asarray([
        sequence_features(seq)
        for seq in neg_sequences.values()
    ], dtype=float)

    X = np.vstack([X_pos, X_neg])

    y = np.asarray(
        [1] * len(X_pos)
        + [0] * len(X_neg),
        dtype=int,
    )

    # Positive groups are cluster representatives.
    # Each negative accession is its own group.
    groups = np.asarray(
        [f"pos::{acc}" for acc in pos_sequences]
        + [f"neg::{acc}" for acc in neg_sequences],
        dtype=object,
    )

    return X, y, groups


def evaluate_pool(
    pool: str,
    pos_sequences: dict[str, str],
    neg_sequences: dict[str, str],
):
    X, y, groups = build_xy(
        pos_sequences,
        neg_sequences,
    )

    cv = StratifiedGroupKFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_SEED,
    )

    models = [
        (
            "logistic_regression",
            Pipeline([
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000,
                        random_state=RANDOM_SEED,
                    ),
                ),
            ]),
        ),
        (
            "random_forest",
            RandomForestClassifier(
                n_estimators=300,
                min_samples_leaf=2,
                random_state=RANDOM_SEED,
                n_jobs=-1,
            ),
        ),
    ]

    rows = []
    importance_rows = []

    names = feature_names()

    for model_name, model in models:
        fold_aurocs = []
        fold_auprcs = []

        for fold, (train_idx, test_idx) in enumerate(
            cv.split(X, y, groups)
        ):
            model.fit(
                X[train_idx],
                y[train_idx],
            )

            probs = model.predict_proba(
                X[test_idx]
            )[:, 1]

            fold_aurocs.append(
                roc_auc_score(
                    y[test_idx],
                    probs,
                )
            )

            fold_auprcs.append(
                average_precision_score(
                    y[test_idx],
                    probs,
                )
            )

        auroc_mean = float(
            np.mean(fold_aurocs)
        )

        auprc_mean = float(
            np.mean(fold_auprcs)
        )

        shortcut_flag = (
            auroc_mean > AUROC_REJECT_THRESHOLD
            or auprc_mean > AUPRC_REJECT_THRESHOLD
        )

        rows.append({
            "pool": pool,
            "model": model_name,
            "n_positive_clusters": len(pos_sequences),
            "n_negative_diagnostic": len(neg_sequences),
            "n_folds": N_SPLITS,
            "auroc_mean": round(auroc_mean, 4),
            "auroc_sd": round(
                float(np.std(fold_aurocs, ddof=1)),
                4,
            ),
            "auprc_mean": round(auprc_mean, 4),
            "auprc_sd": round(
                float(np.std(fold_auprcs, ddof=1)),
                4,
            ),
            "shortcut_flag": int(shortcut_flag),
        })

        # Fit once on the full diagnostic set only for descriptive
        # feature-importance reporting. These values never enter Gate D.
        model.fit(X, y)

        if model_name == "logistic_regression":
            values = np.abs(
                model.named_steps["clf"].coef_[0]
            )

        else:
            values = model.feature_importances_

        for feature, value in zip(names, values):
            importance_rows.append({
                "pool": pool,
                "model": model_name,
                "feature": feature,
                "importance": float(value),
            })

    return rows, importance_rows


def run():
    data_dir = Path(DATA_DIR)
    results_dir = Path(RESULTS_DIR)

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    pos_fasta = (
        data_dir / "cleaned_precursor.fasta"
    )

    cluster_path = (
        results_dir / "clusters_precursor.tsv"
    )

    burn_path = (
        results_dir / "diagnostic_burn_ids.txt"
    )

    for path in [
        pos_fasta,
        cluster_path,
        burn_path,
    ]:
        if not path.exists():
            sys.exit(
                f"Missing {path} — run prior census steps first"
            )

    pos_sequences = load_fasta(
        pos_fasta
    )

    _, rep_to_members = load_clusters(
        cluster_path
    )

    burned_reps = {
        line.strip()
        for line in burn_path.read_text().splitlines()
        if line.strip()
    }

    # Every burned ID must actually identify a positive cluster.
    unknown_burn = (
        burned_reps
        - set(rep_to_members)
    )

    if unknown_burn:
        raise RuntimeError(
            f"Burn list contains {len(unknown_burn)} unknown clusters"
        )

    positive_diagnostic = (
        build_primary_positive_set(
            pos_sequences,
            burned_reps,
        )
    )

    n_pos = len(
        positive_diagnostic
    )

    if n_pos < 20:
        raise RuntimeError(
            f"Only {n_pos} burned positive clusters; "
            "diagnostic support is inadequate"
        )

    max_negative_diagnostic = (
        NEGATIVE_TO_POSITIVE_DIAGNOSTIC_RATIO
        * n_pos
    )

    result_rows = []
    importance_rows = []
    partition_rows = []

    print(
        "\n── Frozen shortcut diagnostic geometry ───────────────────────"
    )

    print(
        f"Burned positive clusters: {n_pos}"
    )

    for pool in POOLS:
        filtered_fasta = (
            data_dir
            / f"negatives_{pool}_filtered.fasta"
        )

        if not filtered_fasta.exists():
            raise RuntimeError(
                f"Missing {filtered_fasta} — run Step 06B first"
            )

        all_negative = load_fasta(
            filtered_fasta
        )

        selected_negative, all_burned_negative = (
            select_negative_diagnostic_set(
                all_negative,
                max_negative_diagnostic,
            )
        )

        if len(selected_negative) < n_pos:
            raise RuntimeError(
                f"{pool}: only {len(selected_negative)} burned negatives "
                f"for {n_pos} burned positive clusters"
            )

        # Record the permanent negative diagnostic partition.
        for acc in sorted(all_negative):
            burned = acc in all_burned_negative
            selected = acc in selected_negative

            partition_rows.append({
                "pool": pool,
                "accession": acc,
                "in_diagnostic_burn": int(burned),
                "selected_for_gate_d": int(selected),
                "available_for_confirmatory": int(not burned),
            })

        n_confirmatory_remaining = (
            len(all_negative)
            - len(all_burned_negative)
        )

        print(
            f"{pool:12s}: filtered={len(all_negative):5d} | "
            f"burned={len(all_burned_negative):4d} | "
            f"Gate-D sample={len(selected_negative):4d} | "
            f"confirmatory remaining={n_confirmatory_remaining:5d}"
        )

        rows, imps = evaluate_pool(
            pool,
            positive_diagnostic,
            selected_negative,
        )

        result_rows.extend(rows)
        importance_rows.extend(imps)

    results_df = pd.DataFrame(
        result_rows
    )

    importance_df = pd.DataFrame(
        importance_rows
    )

    partition_df = pd.DataFrame(
        partition_rows
    )

    results_df.to_csv(
        results_dir
        / "shortcut_diagnostic_results.tsv",
        sep="\t",
        index=False,
    )

    importance_df.to_csv(
        results_dir
        / "shortcut_feature_importance.tsv",
        sep="\t",
        index=False,
    )

    partition_df.to_csv(
        results_dir
        / "negative_diagnostic_partition.tsv",
        sep="\t",
        index=False,
    )

    # --------------------------------------------------------------
    # Gate D is decided ONLY from the hardest family-aware pool.
    # --------------------------------------------------------------

    primary_rows = results_df[
        results_df["pool"]
        == PRIMARY_GATE_D_POOL
    ]

    if len(primary_rows) != 2:
        raise RuntimeError(
            "Expected exactly two family-aware diagnostic model rows"
        )

    gate_d_fail = bool(
        primary_rows["shortcut_flag"].any()
    )

    gate_d = (
        "FAIL"
        if gate_d_fail
        else "PASS"
    )

    gate_d_df = pd.DataFrame([{
        "gate_d_decision": gate_d,
        "primary_pool": PRIMARY_GATE_D_POOL,
        "auroc_threshold": AUROC_REJECT_THRESHOLD,
        "auprc_threshold": AUPRC_REJECT_THRESHOLD,
        "n_positive_clusters": n_pos,
        "negative_burn_rule": (
            f"md5 first byte < "
            f"{DIAGNOSTIC_BURN_THRESHOLD_BYTE}"
        ),
        "negative_diagnostic_ratio_cap": (
            NEGATIVE_TO_POSITIVE_DIAGNOSTIC_RATIO
        ),
        "feature_set": (
            "sequence_length_plus_20aa_composition"
        ),
        "note": (
            "Family-aware sequence-clean diagnostic exceeded "
            "shortcut threshold."
            if gate_d_fail
            else
            "Family-aware sequence-clean task not rejected by "
            "frozen shortcut thresholds."
        ),
    }])

    gate_d_df.to_csv(
        results_dir
        / "gate_d_decision.tsv",
        sep="\t",
        index=False,
    )

    print(
        "\n── Model-blind shortcut diagnostics ──────────────────────────"
    )

    print(
        results_df[
            [
                "pool",
                "model",
                "n_positive_clusters",
                "n_negative_diagnostic",
                "auroc_mean",
                "auprc_mean",
                "shortcut_flag",
            ]
        ].to_string(index=False)
    )

    print(
        f"\nGate D ({PRIMARY_GATE_D_POOL}): {gate_d}"
    )

    print(
        f"Reject thresholds: AUROC > "
        f"{AUROC_REJECT_THRESHOLD:.2f} OR "
        f"AUPRC > {AUPRC_REJECT_THRESHOLD:.2f}"
    )

    print(
        f"\nOutputs -> {RESULTS_DIR}/"
    )


if __name__ == "__main__":
    run()
