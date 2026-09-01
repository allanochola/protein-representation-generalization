from pathlib import Path
import hashlib
import itertools
import json

import numpy as np
import pandas as pd


# ============================================================
# FROZEN CONSTANTS
# ============================================================

ROOT = Path(__file__).resolve().parents[4]

EXP03 = ROOT / "experiments" / "03-toxin-representation"

STAGE1_BLIND = EXP03 / "stage1_model_blind"
REALIZED = STAGE1_BLIND / "realized_partition"

EXTRACTION = (
    EXP03
    / "stage1_model_contact"
    / "discovery_extraction"
)

OUT = (
    EXP03
    / "stage1_model_contact"
    / "stability_sweep"
    / "results"
)

OUT.mkdir(parents=True, exist_ok=True)

MATRIX_PATH = EXTRACTION / "discovery_max_matrix.npy"
ROWS_PATH = EXTRACTION / "discovery_matrix_rows.tsv"

EXPECTED_MATRIX_SHA256 = (
    "bd4b03181b79b4464721ba42e06cc03aeea05309571ec987c3a588f888ba1296"
)

EXPECTED_ROWS_SHA256 = (
    "ef78d4c62a9142a03b72fd440e19d9093cab73e8d23106178d381838fa14112e"
)

N_LATENTS = 10240
K = 5

N_VALUES = [100, 120, 139]
N_PERTURB = 100
SUBSAMPLE_FRACTION = 0.80

JACCARD_THRESHOLD = 0.60
RECURRENCE_THRESHOLD = 0.80
MIN_RECURRENT_FEATURES = 4
CONCENTRATION_THRESHOLD = 0.35

LENGTH_ORDER = ["<30", "30-75", "76-150", ">150"]


# ============================================================
# HELPERS
# ============================================================

def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def sign_of(x):
    # Frozen convention:
    # d >= 0 => positive sign
    return 1 if x >= 0 else -1


def signed_label(latent, sign):
    return f"{int(latent)}:{'+' if int(sign) > 0 else '-'}"


def rank_latents(d):
    """
    Rank by descending abs(d), ties by lower latent index.
    """

    latent = np.arange(len(d), dtype=np.int64)
    abs_d = np.abs(d)

    # np.lexsort uses last key as primary:
    # primary = -abs_d
    # secondary = latent index
    order = np.lexsort(
        (
            latent,
            -abs_d,
        )
    )

    return order


def nominate(matrix, pos_idx, neg_idx):
    pos_mean = matrix[pos_idx].mean(axis=0)
    neg_mean = matrix[neg_idx].mean(axis=0)

    d = pos_mean - neg_mean

    order = rank_latents(d)
    top = order[:K]

    signed_top = tuple(
        (
            int(j),
            sign_of(float(d[j])),
        )
        for j in top
    )

    return {
        "d": d,
        "order": order,
        "top_latents": tuple(int(j) for j in top),
        "signed_top": signed_top,
    }


def jaccard_signed(a, b):
    A = set(a)
    B = set(b)

    return len(A & B) / len(A | B)


def pairwise_agreement_top1(top1_values):
    vals = list(top1_values)
    n = len(vals)

    if n < 2:
        return np.nan

    same = 0
    total = 0

    for i in range(n):
        for j in range(i + 1, n):
            total += 1
            same += int(vals[i] == vals[j])

    return same / total


def modal_frequency(values):
    values = list(values)

    counts = {}

    for x in values:
        counts[x] = counts.get(x, 0) + 1

    modal_value, modal_count = sorted(
        counts.items(),
        key=lambda kv: (
            -kv[1],
            str(kv[0]),
        ),
    )[0]

    return modal_value, modal_count / len(values)


# ============================================================
# LOAD + VERIFY FROZEN MATRIX
# ============================================================

print("── FROZEN MATRIX VERIFICATION ──")

assert MATRIX_PATH.exists()
assert ROWS_PATH.exists()

matrix_hash = sha256_file(MATRIX_PATH)
rows_hash = sha256_file(ROWS_PATH)

print("matrix SHA-256:", matrix_hash)
print("rows SHA-256:", rows_hash)

assert matrix_hash == EXPECTED_MATRIX_SHA256
assert rows_hash == EXPECTED_ROWS_SHA256

matrix = np.load(
    MATRIX_PATH,
    mmap_mode="r",
)

rows = pd.read_csv(
    ROWS_PATH,
    sep="\t",
)

assert matrix.shape == (278, N_LATENTS)
assert rows.shape[0] == 278

assert list(rows["matrix_row"]) == list(range(278))

assert set(rows["class_name"]) == {
    "positive",
    "negative",
}

if not np.isfinite(matrix).all():
    raise RuntimeError(
        "STOP — discovery matrix contains NaN/Inf."
    )

print("PASS — frozen biological matrix verified.")


# ============================================================
# FROZEN ID -> MATRIX ROW
# ============================================================

row_lookup = {}

for row in rows.itertuples(index=False):
    key = (
        str(row.class_name),
        str(row.identifier),
    )

    if key in row_lookup:
        raise RuntimeError(
            f"Duplicate matrix identifier: {key}"
        )

    row_lookup[key] = int(row.matrix_row)


# ============================================================
# LOAD NESTED FROZEN DISCOVERY SETS
# ============================================================

subsets = {}

for N in N_VALUES:

    pos_file = REALIZED / f"discovery_positive_n{N}.tsv"
    neg_file = REALIZED / f"discovery_negative_n{N}.tsv"

    pos = pd.read_csv(
        pos_file,
        sep="\t",
    )

    neg = pd.read_csv(
        neg_file,
        sep="\t",
    )

    assert len(pos) == N
    assert len(neg) == N

    pos_ids = list(
        pos["cluster_rep"].astype(str)
    )

    neg_ids = list(
        neg["accession"].astype(str)
    )

    pos_idx = np.array(
        [
            row_lookup[
                ("positive", identifier)
            ]
            for identifier in pos_ids
        ],
        dtype=np.int64,
    )

    neg_idx = np.array(
        [
            row_lookup[
                ("negative", identifier)
            ]
            for identifier in neg_ids
        ],
        dtype=np.int64,
    )

    assert len(set(pos_idx)) == N
    assert len(set(neg_idx)) == N

    subsets[N] = {
        "pos_df": pos,
        "neg_df": neg,
        "pos_ids": pos_ids,
        "neg_ids": neg_ids,
        "pos_idx": pos_idx,
        "neg_idx": neg_idx,
    }


# ============================================================
# VERIFY NESTEDNESS AGAINST ACTUAL IDS
# ============================================================

assert set(subsets[100]["pos_ids"]).issubset(
    set(subsets[120]["pos_ids"])
)

assert set(subsets[120]["pos_ids"]).issubset(
    set(subsets[139]["pos_ids"])
)

assert set(subsets[100]["neg_ids"]).issubset(
    set(subsets[120]["neg_ids"])
)

assert set(subsets[120]["neg_ids"]).issubset(
    set(subsets[139]["neg_ids"])
)


# ============================================================
# FULL-DATA NOMINATION FOR N=100/120/139
# ============================================================

full = {}

for N in N_VALUES:

    full[N] = nominate(
        matrix,
        subsets[N]["pos_idx"],
        subsets[N]["neg_idx"],
    )


# ============================================================
# COMPLETE N=139 LATENT SCORE TABLE
# ============================================================

d139 = full[139]["d"]
order139 = full[139]["order"]

rank139 = np.empty(
    N_LATENTS,
    dtype=np.int64,
)

rank139[order139] = (
    np.arange(N_LATENTS)
    + 1
)

score_table = pd.DataFrame({
    "latent_id":
        np.arange(N_LATENTS, dtype=np.int64),

    "signed_mean_difference":
        d139.astype(np.float64),

    "absolute_mean_difference":
        np.abs(d139).astype(np.float64),

    "sign":
        np.where(
            d139 >= 0,
            "+",
            "-",
        ),

    "rank":
        rank139,
})

score_table = score_table.sort_values(
    "rank"
)

score_table.to_csv(
    OUT / "n139_signed_latent_scores.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# FULL NOMINATED FEATURE SETS
# ============================================================

top5_rows = []

for N in N_VALUES:

    result = full[N]

    for rank, (latent, sign) in enumerate(
        result["signed_top"],
        start=1,
    ):
        top5_rows.append({
            "n_per_class": N,
            "rank": rank,
            "latent_id": latent,
            "sign":
                "+" if sign > 0 else "-",
            "signed_identity":
                signed_label(latent, sign),
            "signed_mean_difference":
                float(result["d"][latent]),
            "absolute_mean_difference":
                float(abs(result["d"][latent])),
        })

top5_df = pd.DataFrame(top5_rows)

top5_df.to_csv(
    OUT / "full_dataset_top5.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# PERTURBATIONS
# ============================================================

perturbation_records = []
membership_records = []
length_records = []

per_N_perturbations = {}

for N in N_VALUES:

    print(f"Running biological stability sweep N={N}...")

    pos_idx_all = subsets[N]["pos_idx"]
    neg_idx_all = subsets[N]["neg_idx"]

    pos_df = subsets[N]["pos_df"].reset_index(drop=True)
    neg_df = subsets[N]["neg_df"].reset_index(drop=True)

    n_sub = int(
        np.floor(
            SUBSAMPLE_FRACTION * N
        )
    )

    perturbations = []

    for b in range(N_PERTURB):

        seed = (
            20_000_000
            + 100_000 * N
            + b
        )

        # Frozen rule:
        # fresh default_rng PER perturbation.
        rng = np.random.default_rng(seed)

        pos_local = np.sort(
            rng.choice(
                N,
                size=n_sub,
                replace=False,
            )
        )

        neg_local = np.sort(
            rng.choice(
                N,
                size=n_sub,
                replace=False,
            )
        )

        pos_idx = pos_idx_all[
            pos_local
        ]

        neg_idx = neg_idx_all[
            neg_local
        ]

        result = nominate(
            matrix,
            pos_idx,
            neg_idx,
        )

        perturbations.append({
            "b": b,
            "seed": seed,
            "d": result["d"],
            "signed_top":
                result["signed_top"],
            "top_latents":
                result["top_latents"],
        })

        for cls, local_indices, df in [
            (
                "positive",
                pos_local,
                pos_df,
            ),
            (
                "negative",
                neg_local,
                neg_df,
            ),
        ]:

            id_col = (
                "cluster_rep"
                if cls == "positive"
                else "accession"
            )

            for local_i in local_indices:

                membership_records.append({
                    "n_per_class": N,
                    "perturbation": b,
                    "seed": seed,
                    "class_name": cls,
                    "identifier":
                        str(
                            df.loc[
                                local_i,
                                id_col,
                            ]
                        ),
                })

            selected_strata = (
                df.loc[
                    local_indices,
                    "length_stratum_stage1",
                ]
                .value_counts()
                .reindex(
                    LENGTH_ORDER,
                    fill_value=0,
                )
            )

            for stratum in LENGTH_ORDER:

                length_records.append({
                    "n_per_class": N,
                    "perturbation": b,
                    "seed": seed,
                    "class_name": cls,
                    "length_stratum":
                        stratum,
                    "count":
                        int(
                            selected_strata[
                                stratum
                            ]
                        ),
                })

    per_N_perturbations[N] = perturbations


# ============================================================
# STABILITY METRICS
# ============================================================

summary_rows = []
recurrence_rows = []

for N in N_VALUES:

    perturbations = per_N_perturbations[N]

    signed_sets = [
        p["signed_top"]
        for p in perturbations
    ]

    pairwise_jaccards = [
        jaccard_signed(a, b)
        for a, b in itertools.combinations(
            signed_sets,
            2,
        )
    ]

    median_jaccard = float(
        np.median(pairwise_jaccards)
    )

    fixed_signed_top = (
        full[N]["signed_top"]
    )

    recurrence = {}

    for signed_feature in fixed_signed_top:

        freq = np.mean(
            [
                signed_feature
                in set(p["signed_top"])
                for p in perturbations
            ]
        )

        recurrence[
            signed_feature
        ] = float(freq)

        recurrence_rows.append({
            "n_per_class": N,
            "latent_id":
                signed_feature[0],
            "sign":
                "+"
                if signed_feature[1] > 0
                else "-",
            "signed_identity":
                signed_label(*signed_feature),
            "inclusion_frequency":
                float(freq),
            "recurrent_at_0_80":
                bool(
                    freq
                    >= RECURRENCE_THRESHOLD
                ),
        })

    n_recurrent = int(
        sum(
            freq
            >= RECURRENCE_THRESHOLD
            for freq in recurrence.values()
        )
    )

    # Fixed latent identities for concentration.
    fixed_latents = [
        x[0]
        for x in fixed_signed_top
    ]

    concentrations = []

    for p in perturbations:

        mass = np.abs(
            p["d"]
        )

        denominator = float(
            mass.sum()
        )

        if not np.isfinite(denominator):
            raise RuntimeError(
                "Nonfinite concentration denominator."
            )

        if denominator <= 0:
            raise RuntimeError(
                "Zero concentration denominator."
            )

        numerator = float(
            mass[
                fixed_latents
            ].sum()
        )

        concentrations.append(
            numerator / denominator
        )

    median_concentration = float(
        np.median(concentrations)
    )

    top1 = [
        p["signed_top"][0]
        for p in perturbations
    ]

    modal_top1, modal_top1_freq = (
        modal_frequency(top1)
    )

    top1_agreement = (
        pairwise_agreement_top1(
            top1
        )
    )

    overlap_with_n139 = len(
        set(full[N]["signed_top"])
        & set(full[139]["signed_top"])
    )

    jaccard_pass = (
        median_jaccard
        >= JACCARD_THRESHOLD
    )

    recurrence_pass = (
        n_recurrent
        >= MIN_RECURRENT_FEATURES
    )

    concentration_pass = (
        median_concentration
        >= CONCENTRATION_THRESHOLD
    )

    # Only N=139 is a primary verdict.
    final_pass = (
        jaccard_pass
        and recurrence_pass
        and concentration_pass
    )

    summary_rows.append({
        "n_per_class":
            N,

        "median_pairwise_jaccard":
            median_jaccard,

        "jaccard_threshold":
            JACCARD_THRESHOLD,

        "jaccard_pass":
            bool(jaccard_pass),

        "n_recurrent_of_5":
            n_recurrent,

        "recurrence_threshold":
            RECURRENCE_THRESHOLD,

        "min_recurrent_features":
            MIN_RECURRENT_FEATURES,

        "recurrence_pass":
            bool(recurrence_pass),

        "median_fixed_top5_concentration":
            median_concentration,

        "concentration_threshold":
            CONCENTRATION_THRESHOLD,

        "concentration_pass":
            bool(concentration_pass),

        "three_way_pass":
            bool(final_pass),

        "signed_top5_overlap_with_n139":
            overlap_with_n139,

        "modal_top1_signed_identity":
            signed_label(
                *modal_top1
            ),

        "modal_top1_frequency":
            float(modal_top1_freq),

        "pairwise_top1_agreement":
            float(top1_agreement),

        "primary_decision":
            bool(N == 139),
    })


summary_df = pd.DataFrame(
    summary_rows
)

recurrence_df = pd.DataFrame(
    recurrence_rows
)

summary_df.to_csv(
    OUT / "stability_summary.tsv",
    sep="\t",
    index=False,
)

recurrence_df.to_csv(
    OUT / "feature_recurrence.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# PERTURBATION MEMBERSHIP + LENGTH COMPOSITION
# ============================================================

membership_df = pd.DataFrame(
    membership_records
)

membership_df.to_csv(
    OUT / "perturbation_membership.tsv",
    sep="\t",
    index=False,
)

length_df = pd.DataFrame(
    length_records
)

length_summary = (
    length_df
    .groupby(
        [
            "n_per_class",
            "class_name",
            "length_stratum",
        ],
        as_index=False,
    )
    .agg(
        mean_count=("count", "mean"),
        min_count=("count", "min"),
        max_count=("count", "max"),
    )
)

length_summary["exhaustion_limited_note"] = ""

mask = (
    (length_summary["n_per_class"] == 139)
    & (
        length_summary["length_stratum"]
        == ">150"
    )
)

length_summary.loc[
    mask,
    "exhaustion_limited_note",
] = (
    "N=139 >150 discovery-positive source membership "
    "is exhaustion-limited; perturbation stability is "
    "conditional on the frozen realized pool."
)

length_summary.to_csv(
    OUT / "perturbation_length_composition.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# PER-LENGTH-STRATUM DESCRIPTIVES
#
# Frozen N=139 nominated features ONLY.
# These do not alter nomination or gates.
# ============================================================

n139_top5 = full[139]["signed_top"]

stratum_rows = []

pos139 = subsets[139]["pos_df"].reset_index(drop=True)
neg139 = subsets[139]["neg_df"].reset_index(drop=True)

pos_idx139 = subsets[139]["pos_idx"]
neg_idx139 = subsets[139]["neg_idx"]

for stratum in LENGTH_ORDER:

    pos_local = np.where(
        pos139[
            "length_stratum_stage1"
        ].to_numpy()
        == stratum
    )[0]

    neg_local = np.where(
        neg139[
            "length_stratum_stage1"
        ].to_numpy()
        == stratum
    )[0]

    pos_indices = pos_idx139[
        pos_local
    ]

    neg_indices = neg_idx139[
        neg_local
    ]

    assert len(pos_indices) == len(
        neg_indices
    )

    pos_means = matrix[
        pos_indices
    ].mean(axis=0)

    neg_means = matrix[
        neg_indices
    ].mean(axis=0)

    d_stratum = (
        pos_means
        - neg_means
    )

    for rank, (latent, frozen_sign) in enumerate(
        n139_top5,
        start=1,
    ):

        observed_d = float(
            d_stratum[latent]
        )

        stratum_rows.append({
            "length_stratum":
                stratum,

            "n_positive":
                len(pos_indices),

            "n_negative":
                len(neg_indices),

            "n139_feature_rank":
                rank,

            "latent_id":
                latent,

            "frozen_sign":
                "+"
                if frozen_sign > 0
                else "-",

            "stratum_signed_mean_difference":
                observed_d,

            "stratum_sign":
                "+"
                if observed_d >= 0
                else "-",

            "sign_matches_full_n139":
                bool(
                    sign_of(observed_d)
                    == frozen_sign
                ),

            "exhaustion_limited":
                bool(
                    stratum == ">150"
                ),
        })


stratum_df = pd.DataFrame(
    stratum_rows
)

stratum_df.to_csv(
    OUT / "n139_top5_length_stratum_descriptives.tsv",
    sep="\t",
    index=False,
)


# ============================================================
# N=139 FINAL DECISION
# ============================================================

primary = (
    summary_df[
        summary_df[
            "n_per_class"
        ] == 139
    ]
    .iloc[0]
)

top5_139 = (
    top5_df[
        top5_df[
            "n_per_class"
        ] == 139
    ]
    .sort_values(
        "rank"
    )
)

decision = {
    "stage":
        "Experiment 03 Stage 1 biological SAE stability sweep",

    "status":
        (
            "PASS"
            if bool(
                primary[
                    "three_way_pass"
                ]
            )
            else "FAIL"
        ),

    "primary_n_per_class":
        139,

    "n139_top5_signed_features": [
        {
            "rank":
                int(row.rank),

            "latent_id":
                int(row.latent_id),

            "sign":
                str(row.sign),

            "signed_identity":
                str(
                    row.signed_identity
                ),

            "signed_mean_difference":
                float(
                    row.signed_mean_difference
                ),
        }
        for row in top5_139.itertuples(
            index=False
        )
    ],

    "gates": {
        "median_pairwise_jaccard": {
            "value":
                float(
                    primary[
                        "median_pairwise_jaccard"
                    ]
                ),
            "threshold":
                JACCARD_THRESHOLD,
            "pass":
                bool(
                    primary[
                        "jaccard_pass"
                    ]
                ),
        },

        "recurrence": {
            "n_recurrent_of_5":
                int(
                    primary[
                        "n_recurrent_of_5"
                    ]
                ),
            "inclusion_threshold":
                RECURRENCE_THRESHOLD,
            "minimum_recurrent_features":
                MIN_RECURRENT_FEATURES,
            "pass":
                bool(
                    primary[
                        "recurrence_pass"
                    ]
                ),
        },

        "fixed_top5_concentration": {
            "value":
                float(
                    primary[
                        "median_fixed_top5_concentration"
                    ]
                ),
            "threshold":
                CONCENTRATION_THRESHOLD,
            "pass":
                bool(
                    primary[
                        "concentration_pass"
                    ]
                ),
        },
    },

    "three_way_and_pass":
        bool(
            primary[
                "three_way_pass"
            ]
        ),

    "single_feature_statistics": {
        "status":
            "DESCRIPTIVE_ONLY",

        "modal_top1_signed_identity":
            str(
                primary[
                    "modal_top1_signed_identity"
                ]
            ),

        "modal_top1_frequency":
            float(
                primary[
                    "modal_top1_frequency"
                ]
            ),

        "pairwise_top1_agreement":
            float(
                primary[
                    "pairwise_top1_agreement"
                ]
            ),

        "single_feature_verdict_permitted":
            False,
    },

    "length_geometry": {
        "n139_joint_matching":
            {
                "<30": 9,
                "30-75": 22,
                "76-150": 29,
                ">150": 79,
            },

        "long_stratum_exhaustion_limited":
            True,

        "interpretation":
            (
                "N=139 >150 behavior is conditional on the "
                "frozen realized discovery pool and must not "
                "be interpreted as independent stability over "
                "alternative long-protein memberships."
            ),
    },

    "analysis_boundary": {
        "latent_ranking_observed":
            True,

        "feature_nomination_observed":
            True,

        "confirmatory_sequences_processed":
            False,

        "confirmatory_representation_statistics_observed":
            False,
    },
}


decision_path = (
    OUT
    / "STAGE1_DECISION.json"
)

decision_path.write_text(
    json.dumps(
        decision,
        indent=2,
    )
    + "\n"
)


# ============================================================
# HASH ALL RESULT ARTIFACTS
# ============================================================

result_files = [
    OUT / "n139_signed_latent_scores.tsv",
    OUT / "full_dataset_top5.tsv",
    OUT / "stability_summary.tsv",
    OUT / "feature_recurrence.tsv",
    OUT / "perturbation_membership.tsv",
    OUT / "perturbation_length_composition.tsv",
    OUT / "n139_top5_length_stratum_descriptives.tsv",
    OUT / "STAGE1_DECISION.json",
]

hashes = {
    path.name:
        sha256_file(path)
    for path in result_files
}

hash_path = (
    OUT
    / "RESULT_HASHES.json"
)

hash_path.write_text(
    json.dumps(
        hashes,
        indent=2,
    )
    + "\n"
)


# ============================================================
# OUTPUT — FIRST SCIENTIFIC RESULT
# ============================================================

print("\n── STAGE 1 N=139 TOP-5 SIGNED SET ──")

print(
    top5_139[
        [
            "rank",
            "latent_id",
            "sign",
            "signed_mean_difference",
        ]
    ].to_string(
        index=False
    )
)

print("\n── STAGE 1 STABILITY SUMMARY ──")

print(
    summary_df.to_string(
        index=False
    )
)

print("\n── STAGE 1 N=139 RECURRENCE ──")

print(
    recurrence_df[
        recurrence_df[
            "n_per_class"
        ] == 139
    ].to_string(
        index=False
    )
)

print("\n── STAGE 1 LENGTH-STRATUM DESCRIPTIVES ──")

print(
    stratum_df.to_string(
        index=False
    )
)

print("\n── STAGE 1 DECISION ──")

print(
    json.dumps(
        decision,
        indent=2,
    )
)

print("\n── RESULT HASHES ──")

print(
    json.dumps(
        hashes,
        indent=2,
    )
)
