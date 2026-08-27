
import os, json, sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

sys.path.insert(0, str(Path.cwd().parent))
from src import probe as sp

print(sp.selftest())

CACHE = Path(os.environ.get("SS_CACHE", "/content/ss_cache"))
EMB = CACHE / "emb"
MM = CACHE / "memmap"
MM.mkdir(exist_ok=True)

OUT = Path("results")
OUT.mkdir(exist_ok=True)

CKPT = OUT / "checkpoints"
CKPT.mkdir(exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

SEED = 0
W = 3
EPOCHS = 40
LR = 1e-3
BATCH = 4096
CHUNK = 16384

torch.manual_seed(SEED)
np.random.seed(SEED)

mf = pd.read_csv(CACHE / "manifest.csv")

assert "record_key" in mf.columns, (
    "manifest lacks content-derived record_key; rerun canonical manifest step"
)
assert mf["record_key"].is_unique, "record_key must be unique"
assert mf["record_key"].is_monotonic_increasing, (
    "manifest must be canonically sorted by record_key"
)

print(f"{len(mf)} proteins, {mf.cluster.nunique()} clusters")

splits = sp.make_splits(mf.cluster.values, seed=SEED)

for k, v in splits.items():
    print(
        f"  {k}: {len(v)} proteins, "
        f"{mf.iloc[v].cluster.nunique()} clusters"
    )


# ------------------------------------------------------------------
# Build disk-backed residue arrays once
# ------------------------------------------------------------------

lengths = mf["n_res"].astype(int).to_numpy()
offsets = np.zeros(len(mf) + 1, dtype=np.int64)
offsets[1:] = np.cumsum(lengths)

N = int(offsets[-1])

emb_path = MM / "esm_f16.dat"
y_path = MM / "labels_u8.dat"
protein_path = MM / "protein_i32.dat"

if not emb_path.exists():
    print(f"\nbuilding memmap for {N:,} residues")

    emb_mm = np.memmap(
        emb_path,
        mode="w+",
        dtype=np.float16,
        shape=(N, 1280),
    )

    y_mm = np.memmap(
        y_path,
        mode="w+",
        dtype=np.uint8,
        shape=(N,),
    )

    p_mm = np.memmap(
        protein_path,
        mode="w+",
        dtype=np.int32,
        shape=(N,),
    )

    for i, row in mf.iterrows():
        d = np.load(EMB / f"{row['id']}.npz")
        X = d["emb"]
        y = d["y"]

        a, b = offsets[i], offsets[i + 1]

        assert X.shape == (b - a, 1280)
        assert len(y) == b - a

        emb_mm[a:b] = X
        y_mm[a:b] = y
        p_mm[a:b] = i

        if (i + 1) % 1000 == 0:
            print(f"  consolidated {i+1}/{len(mf)} proteins")

    emb_mm.flush()
    y_mm.flush()
    p_mm.flush()

    np.save(MM / "offsets.npy", offsets)

    print("memmap consolidation complete")
else:
    print("\nusing existing memmap cache")


emb_mm = np.memmap(
    emb_path,
    mode="r",
    dtype=np.float16,
    shape=(N, 1280),
)

y_mm = np.memmap(
    y_path,
    mode="r",
    dtype=np.uint8,
    shape=(N,),
)

p_mm = np.memmap(
    protein_path,
    mode="r",
    dtype=np.int32,
    shape=(N,),
)


# ------------------------------------------------------------------
# Residue index helpers
# ------------------------------------------------------------------

def residue_indices(protein_idx):
    parts = [
        np.arange(offsets[i], offsets[i + 1], dtype=np.int64)
        for i in protein_idx
    ]
    return np.concatenate(parts)


train_rows = residue_indices(splits["train"])
rand_rows = residue_indices(splits["random_test"])
div_rows = residue_indices(splits["divergent_test"])

print(
    f"\nresidues: train={len(train_rows):,} "
    f"random={len(rand_rows):,} "
    f"divergent={len(div_rows):,}"
)


# ------------------------------------------------------------------
# Streaming normalization
# ------------------------------------------------------------------

def streaming_mean_sd(rows):
    s1 = np.zeros(1280, dtype=np.float64)
    s2 = np.zeros(1280, dtype=np.float64)
    n = 0

    for s in range(0, len(rows), CHUNK):
        rr = rows[s:s+CHUNK]

        X = np.asarray(
            emb_mm[rr],
            dtype=np.float32
        )

        s1 += X.sum(0, dtype=np.float64)
        s2 += np.square(X, dtype=np.float32).sum(
            0,
            dtype=np.float64
        )

        n += len(rr)

    mu = s1 / n
    var = np.maximum(
        s2 / n - mu * mu,
        0.0
    )

    sd = np.sqrt(var) + 1e-6

    return (
        mu.astype(np.float32),
        sd.astype(np.float32),
    )


esm_norm_path = CKPT / "esm_normalization.npz"

if esm_norm_path.exists():
    z = np.load(esm_norm_path)
    mu_esm = z["mu"].astype(np.float32)
    sd_esm = z["sd"].astype(np.float32)
    print("\nloaded ESM train normalization checkpoint")
else:
    print("\ncomputing ESM train normalization")
    mu_esm, sd_esm = streaming_mean_sd(train_rows)
    np.savez(
        esm_norm_path,
        mu=mu_esm,
        sd=sd_esm,
    )
    print("saved ESM train normalization checkpoint")


# ------------------------------------------------------------------
# ESM linear probe
# ------------------------------------------------------------------

def train_esm():
    torch.manual_seed(SEED)

    clf = nn.Linear(1280, 3).to(DEVICE)

    opt = torch.optim.Adam(
        clf.parameters(),
        lr=LR
    )

    lossf = nn.CrossEntropyLoss()

    for ep in range(EPOCHS):
        rng = np.random.default_rng(SEED + ep)

        perm = rng.permutation(train_rows)

        total_loss = 0.0
        seen = 0

        for s in range(0, len(perm), BATCH):
            rr = perm[s:s+BATCH]

            X = np.asarray(
                emb_mm[rr],
                dtype=np.float32
            )

            X = (X - mu_esm) / sd_esm

            y = np.asarray(
                y_mm[rr],
                dtype=np.int64
            )

            Xt = torch.from_numpy(X).to(DEVICE)
            yt = torch.from_numpy(y).to(DEVICE)

            opt.zero_grad(set_to_none=True)

            loss = lossf(
                clf(Xt),
                yt
            )

            loss.backward()
            opt.step()

            total_loss += float(loss.detach()) * len(rr)
            seen += len(rr)

        if ep == 0 or (ep + 1) % 5 == 0:
            print(
                f"  ESM epoch {ep+1:02d}/{EPOCHS} "
                f"loss={total_loss/seen:.5f}"
            )

    return clf


@torch.no_grad()
def predict_esm(clf, rows):
    out = []

    for s in range(0, len(rows), CHUNK):
        rr = rows[s:s+CHUNK]

        X = np.asarray(
            emb_mm[rr],
            dtype=np.float32
        )

        X = (X - mu_esm) / sd_esm

        Xt = torch.from_numpy(X).to(DEVICE)

        yp = clf(Xt).argmax(1).cpu().numpy()

        out.append(yp)

    return np.concatenate(out)


esm_ckpt = CKPT / "esm_probe.pt"

if esm_ckpt.exists():
    esm_clf = nn.Linear(1280, 3).to(DEVICE)
    esm_clf.load_state_dict(
        torch.load(
            esm_ckpt,
            map_location=DEVICE,
            weights_only=True,
        )
    )
    print("\nloaded ESM probe checkpoint")
else:
    esm_clf = train_esm()
    torch.save(esm_clf.state_dict(), esm_ckpt)
    print("saved ESM probe checkpoint")

yp_rand = predict_esm(
    esm_clf,
    rand_rows
)

yp_div = predict_esm(
    esm_clf,
    div_rows
)

y_rand = np.asarray(
    y_mm[rand_rows],
    dtype=np.int64
)

y_div = np.asarray(
    y_mm[div_rows],
    dtype=np.int64
)


# ------------------------------------------------------------------
# Local ±3 baseline
# ------------------------------------------------------------------

def local_matrix(protein_idx):
    Xs = []
    ys = []
    cs = []

    for i in protein_idx:
        row = mf.iloc[i]

        d = np.load(
            EMB / f"{row['id']}.npz"
        )

        y = d["y"]

        X = sp.local_window_features(
            row["seq"],
            W
        )

        Xs.append(X)
        ys.append(y)
        cs.append(
            np.full(
                len(y),
                row["cluster"]
            )
        )

    return (
        np.concatenate(Xs),
        np.concatenate(ys),
        np.concatenate(cs),
    )


# Local features are only 140-D, so materialization is safe.
Xloc_train, yloc_train, _ = local_matrix(
    splits["train"]
)

mu_loc = Xloc_train.mean(
    0,
    keepdims=True
)

sd_loc = Xloc_train.std(
    0,
    keepdims=True
) + 1e-6

Xloc_train = (
    Xloc_train - mu_loc
) / sd_loc


torch.manual_seed(SEED)

loc_clf = nn.Linear(
    Xloc_train.shape[1],
    3
).to(DEVICE)

loc_opt = torch.optim.Adam(
    loc_clf.parameters(),
    lr=LR
)

lossf = nn.CrossEntropyLoss()

Xt = torch.tensor(
    Xloc_train,
    device=DEVICE,
    dtype=torch.float32
)

yt = torch.tensor(
    yloc_train,
    device=DEVICE,
    dtype=torch.long
)

nloc = len(Xt)

local_ckpt = CKPT / "local_probe.pt"

if local_ckpt.exists():
    loc_clf.load_state_dict(
        torch.load(
            local_ckpt,
            map_location=DEVICE,
            weights_only=True,
        )
    )
    print("\nloaded local probe checkpoint")
else:
    for ep in range(EPOCHS):
        g = torch.Generator(
            device=DEVICE
        )
        g.manual_seed(SEED + ep)

        perm = torch.randperm(
            nloc,
            generator=g,
            device=DEVICE
        )

        for s in range(0, nloc, BATCH):
            b = perm[s:s+BATCH]

            loc_opt.zero_grad()

            loss = lossf(
                loc_clf(Xt[b]),
                yt[b]
            )

            loss.backward()
            loc_opt.step()

        if ep == 0 or (ep + 1) % 5 == 0:
            print(
                f"  local epoch {ep+1:02d}/{EPOCHS}"
            )

    torch.save(loc_clf.state_dict(), local_ckpt)
    print("saved local probe checkpoint")


@torch.no_grad()
def local_eval(protein_idx):
    X, y, c = local_matrix(protein_idx)

    X = (
        X - mu_loc
    ) / sd_loc

    preds = []

    for s in range(0, len(y), CHUNK):
        Xt = torch.tensor(
            X[s:s+CHUNK],
            device=DEVICE,
            dtype=torch.float32
        )

        preds.append(
            loc_clf(Xt)
            .argmax(1)
            .cpu()
            .numpy()
        )

    yp = np.concatenate(preds)

    return dict(
        acc=sp.q3_accuracy(y, yp),
        f1=sp.macro_f1(y, yp),
        correct=(y == yp).astype(np.int8),
        cluster=c,
        y=y,
        yp=yp,
    )


# ------------------------------------------------------------------
# Build result cells
# ------------------------------------------------------------------

cluster_rand = np.concatenate([
    np.full(
        offsets[i+1] - offsets[i],
        mf.iloc[i]["cluster"]
    )
    for i in splits["random_test"]
])

cluster_div = np.concatenate([
    np.full(
        offsets[i+1] - offsets[i],
        mf.iloc[i]["cluster"]
    )
    for i in splits["divergent_test"]
])


esm = {
    "random_test": dict(
        acc=sp.q3_accuracy(
            y_rand,
            yp_rand
        ),
        f1=sp.macro_f1(
            y_rand,
            yp_rand
        ),
        correct=(
            y_rand == yp_rand
        ).astype(np.int8),
        cluster=cluster_rand,
        y=y_rand,
        yp=yp_rand,
    ),
    "divergent_test": dict(
        acc=sp.q3_accuracy(
            y_div,
            yp_div
        ),
        f1=sp.macro_f1(
            y_div,
            yp_div
        ),
        correct=(
            y_div == yp_div
        ).astype(np.int8),
        cluster=cluster_div,
        y=y_div,
        yp=yp_div,
    ),
}


loc = {
    "random_test": local_eval(
        splits["random_test"]
    ),
    "divergent_test": local_eval(
        splits["divergent_test"]
    ),
}


# ------------------------------------------------------------------
# Frozen quantities
# ------------------------------------------------------------------

acc_esm_rand = esm[
    "random_test"
]["acc"]

acc_esm_div = esm[
    "divergent_test"
]["acc"]

acc_loc_div = loc[
    "divergent_test"
]["acc"]

delta_div = (
    acc_esm_div
    - acc_loc_div
)

gap = (
    acc_esm_rand
    - acc_esm_div
)

# Persist the primary confirmatory quantities BEFORE bootstrap.
# These are computed under the already-frozen definitions.
primary = {
    "ESM_random_Q3": float(acc_esm_rand),
    "ESM_random_macro_F1": float(esm["random_test"]["f1"]),
    "ESM_divergent_Q3": float(acc_esm_div),
    "ESM_divergent_macro_F1": float(esm["divergent_test"]["f1"]),
    "local_random_Q3": float(loc["random_test"]["acc"]),
    "local_random_macro_F1": float(loc["random_test"]["f1"]),
    "local_divergent_Q3": float(acc_loc_div),
    "local_divergent_macro_F1": float(loc["divergent_test"]["f1"]),
    "Delta_ESM_divergent": float(delta_div),
    "G": float(gap),
}

primary_path = OUT / "primary_metrics_prebootstrap.json"

with open(primary_path, "w") as fh:
    json.dump(primary, fh, indent=2)

print("\n=== PRIMARY CONFIRMATORY METRICS (saved before bootstrap) ===")
for k, v in primary.items():
    print(f"{k}: {v:.6f}")
print("saved:", primary_path)


d_lo, d_hi = sp.paired_diff_bootstrap(
    esm["divergent_test"]["cluster"],
    esm["divergent_test"]["correct"],
    loc["divergent_test"]["correct"],
    reps=2000,
    seed=SEED,
)


def unpaired_gap_ci(
    a,
    b,
    reps=2000,
    seed=SEED
):
    rng = np.random.default_rng(seed)

    def acc_boot(cell):
        cl = cell["cluster"]
        corr = cell["correct"]

        uniq = np.unique(cl)

        idx = {
            c: np.where(cl == c)[0]
            for c in uniq
        }

        pick = rng.choice(
            uniq,
            len(uniq),
            replace=True
        )

        rows = np.concatenate([
            idx[c]
            for c in pick
        ])

        return corr[rows].mean()

    vals = np.array([
        acc_boot(a)
        - acc_boot(b)
        for _ in range(reps)
    ])

    return (
        float(np.percentile(vals, 2.5)),
        float(np.percentile(vals, 97.5)),
    )


g_lo, g_hi = unpaired_gap_ci(
    esm["random_test"],
    esm["divergent_test"]
)

verdict = sp.verdict(
    delta_div,
    gap
)


# ------------------------------------------------------------------
# Results
# ------------------------------------------------------------------

rows = [
    dict(
        cell="ESM_random",
        acc=acc_esm_rand,
        macro_f1=esm["random_test"]["f1"]
    ),
    dict(
        cell="ESM_divergent",
        acc=acc_esm_div,
        macro_f1=esm["divergent_test"]["f1"]
    ),
    dict(
        cell="local_random",
        acc=loc["random_test"]["acc"],
        macro_f1=loc["random_test"]["f1"]
    ),
    dict(
        cell="local_divergent",
        acc=acc_loc_div,
        macro_f1=loc["divergent_test"]["f1"]
    ),
]

pd.DataFrame(rows).to_csv(
    OUT / "ss_generalization.csv",
    index=False
)

summary = dict(
    delta_esm_divergent=round(
        delta_div,
        4
    ),
    delta_ci=[
        round(d_lo, 4),
        round(d_hi, 4)
    ],
    G=round(
        gap,
        4
    ),
    G_ci=[
        round(g_lo, 4),
        round(g_hi, 4)
    ],
    acc_esm_random=round(
        acc_esm_rand,
        4
    ),
    acc_esm_divergent=round(
        acc_esm_div,
        4
    ),
    acc_local_divergent=round(
        acc_loc_div,
        4
    ),
    verdict=verdict
)

json.dump(
    summary,
    open(
        OUT / "ss_summary.json",
        "w"
    ),
    indent=2
)


print(
    f"\nESM Q3: random "
    f"{acc_esm_rand:.3f} | "
    f"divergent {acc_esm_div:.3f}"
)

print(
    f"local Q3 divergent: "
    f"{acc_loc_div:.3f}"
)

print(
    f"Delta_ESM(divergent) = "
    f"{delta_div:+.3f} "
    f"CI [{d_lo:+.3f}, {d_hi:+.3f}]"
)

print(
    f"G (random-divergent) = "
    f"{gap:+.3f} "
    f"CI [{g_lo:+.3f}, {g_hi:+.3f}]"
)

print(
    f"\nVERDICT (frozen bands): "
    f"{verdict}"
)


prov = dict(
    model="facebook/esm2_t33_650M_UR50D",
    layer=17,
    window=W,
    epochs=EPOCHS,
    lr=LR,
    batch=BATCH,
    seed=SEED,
    evaluator="memmap-v1",
    previous_attempts=[
        "attempt1: host RAM SIGKILL before metrics",
        "attempt2: repeated-npz-I/O stop before metrics"
    ],
    splits={
        k: int(len(v))
        for k, v in splits.items()
    },
    n_clusters=int(
        mf.cluster.nunique()
    ),
    n_residues=N,
)

json.dump(
    prov,
    open(
        OUT / "provenance.json",
        "w"
    ),
    indent=2
)

print(
    "wrote results/ss_generalization.csv, "
    "ss_summary.json, provenance.json"
)
