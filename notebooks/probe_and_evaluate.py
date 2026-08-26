# ---
# jupyter:
#   jupytext:
#     text_representation: {extension: .py, format_name: percent}
#   kernelspec: {display_name: Python 3, name: python3}
# ---

# %% [markdown]
# # ESM-2 SS-generalization — probe + evaluation
#
# Runs after `extract_embeddings.py` has cached layer-17 embeddings + labels +
# cluster ids. Fits one linear probe on the random-split training data, evaluates
# it on the in-distribution (random) test and the 30%-cluster-held-out (divergent)
# test, does the same for the sequence-local baseline, and computes the two frozen
# quantities Δ_ESM(divergent) and G with cluster-level bootstrap CIs — then applies
# the frozen decision bands. Nothing about the bands or the split is decided here;
# they are fixed in the protocol.

# %%
import os, json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

import sys; sys.path.insert(0, str(Path.cwd().parent))   # repo root on path
from src import probe as sp
print(sp.selftest())

CACHE = Path(os.environ.get("SS_CACHE", "/content/ss_cache"))
EMB = CACHE / "emb"
OUT = Path("results"); OUT.mkdir(exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SEED = 0
W = 3                                                  # local-baseline window (frozen)
EPOCHS, LR, BATCH = 40, 1e-3, 4096                     # fixed probe hyperparameters
torch.manual_seed(SEED); np.random.seed(SEED)

# %% [markdown]
# ## Load manifest and build the cluster-level splits

# %%
mf = pd.read_csv(CACHE / "manifest.csv")
print(f"{len(mf)} proteins, {mf.cluster.nunique()} clusters")
splits = sp.make_splits(mf.cluster.values, seed=SEED)
for k, v in splits.items():
    print(f"  {k}: {len(v)} proteins, {mf.iloc[v].cluster.nunique()} clusters")

def stack(idx, kind):
    """Concatenate per-residue features/labels/cluster over a protein index set.
    kind='esm' uses cached embeddings; kind='local' builds the ±3 baseline."""
    Xs, ys, cs = [], [], []
    for i in idx:
        row = mf.iloc[i]
        d = np.load(EMB / f"{row['id']}.npz")
        y = d["y"]
        X = d["emb"].astype(np.float32) if kind == "esm" else sp.local_window_features(row["seq"], W)
        assert X.shape[0] == len(y), f"align fail {row['id']}"
        Xs.append(X); ys.append(y); cs.append(np.full(len(y), row["cluster"]))
    return np.concatenate(Xs), np.concatenate(ys), np.concatenate(cs)

# %% [markdown]
# ## One linear probe (fixed hyperparameters), fit on random-split train

# %%
def train_probe(Xtr, ytr, in_dim):
    mu, sd = Xtr.mean(0, keepdims=True), Xtr.std(0, keepdims=True) + 1e-6   # z-score (train stats)
    Xtr = (Xtr - mu) / sd
    clf = nn.Linear(in_dim, 3).to(DEVICE)
    opt = torch.optim.Adam(clf.parameters(), lr=LR)
    lossf = nn.CrossEntropyLoss()
    Xt = torch.tensor(Xtr, device=DEVICE); yt = torch.tensor(ytr, device=DEVICE)
    n = len(Xt)
    for ep in range(EPOCHS):
        perm = torch.randperm(n, device=DEVICE)
        for s in range(0, n, BATCH):
            b = perm[s:s + BATCH]
            opt.zero_grad(); loss = lossf(clf(Xt[b]), yt[b]); loss.backward(); opt.step()
    return clf, (mu, sd)

@torch.no_grad()
def predict(clf, scaler, X):
    mu, sd = scaler
    Xt = torch.tensor((X - mu) / sd, device=DEVICE)
    return clf(Xt).argmax(1).cpu().numpy()

def fit_and_eval(kind, in_dim):
    Xtr, ytr, _ = stack(splits["train"], kind)
    clf, scaler = train_probe(Xtr, ytr, in_dim)
    out = {}
    for split in ("random_test", "divergent_test"):
        X, y, c = stack(splits[split], kind)
        yp = predict(clf, scaler, X)
        out[split] = dict(acc=sp.q3_accuracy(y, yp), f1=sp.macro_f1(y, yp),
                          correct=(y == yp).astype(int), cluster=c, y=y, yp=yp)
    return out

esm = fit_and_eval("esm", 1280)
loc = fit_and_eval("local", (2 * W + 1) * 20)

# %% [markdown]
# ## The two frozen quantities, with cluster bootstrap

# %%
acc_esm_rand = esm["random_test"]["acc"]; acc_esm_div = esm["divergent_test"]["acc"]
acc_loc_div = loc["divergent_test"]["acc"]
delta_div = acc_esm_div - acc_loc_div                  # ESM margin over local, on divergent proteins
gap = acc_esm_rand - acc_esm_div                       # degradation random -> divergent

# Δ_div CI: paired on the SAME divergent residues (ESM vs local), resample clusters
d_lo, d_hi = sp.paired_diff_bootstrap(
    esm["divergent_test"]["cluster"], esm["divergent_test"]["correct"],
    loc["divergent_test"]["correct"], reps=2000, seed=SEED)

# G CI: unpaired — resample random-test clusters and divergent-test clusters
# independently (different proteins), recompute the accuracy difference
def unpaired_gap_ci(a, b, reps=2000, seed=SEED):
    rng = np.random.default_rng(seed)
    def acc_boot(cell):
        cl = cell["cluster"]; corr = cell["correct"]; uniq = np.unique(cl)
        idx = {c: np.where(cl == c)[0] for c in uniq}
        pick = rng.choice(uniq, len(uniq), replace=True)
        rows = np.concatenate([idx[c] for c in pick]); return corr[rows].mean()
    g = np.array([acc_boot(a) - acc_boot(b) for _ in range(reps)])
    return float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))
g_lo, g_hi = unpaired_gap_ci(esm["random_test"], esm["divergent_test"])

verdict = sp.verdict(delta_div, gap)

# %% [markdown]
# ## Results

# %%
rows = [
    dict(cell="ESM_random", acc=acc_esm_rand, macro_f1=esm["random_test"]["f1"]),
    dict(cell="ESM_divergent", acc=acc_esm_div, macro_f1=esm["divergent_test"]["f1"]),
    dict(cell="local_random", acc=loc["random_test"]["acc"], macro_f1=loc["random_test"]["f1"]),
    dict(cell="local_divergent", acc=acc_loc_div, macro_f1=loc["divergent_test"]["f1"]),
]
pd.DataFrame(rows).to_csv(OUT / "ss_generalization.csv", index=False)

summary = dict(
    delta_esm_divergent=round(delta_div, 4), delta_ci=[round(d_lo, 4), round(d_hi, 4)],
    G=round(gap, 4), G_ci=[round(g_lo, 4), round(g_hi, 4)],
    acc_esm_random=round(acc_esm_rand, 4), acc_esm_divergent=round(acc_esm_div, 4),
    acc_local_divergent=round(acc_loc_div, 4), verdict=verdict)
json.dump(summary, open(OUT / "ss_summary.json", "w"), indent=2)

print(f"ESM  Q3: random {acc_esm_rand:.3f} | divergent {acc_esm_div:.3f}")
print(f"local Q3 divergent: {acc_loc_div:.3f}")
print(f"Δ_ESM(divergent) = {delta_div:+.3f}  CI [{d_lo:+.3f}, {d_hi:+.3f}]   (ESM over local baseline)")
print(f"G (random-divergent) = {gap:+.3f}  CI [{g_lo:+.3f}, {g_hi:+.3f}]")
print(f"\nVERDICT (frozen bands): {verdict}")

# %%
prov = dict(model="facebook/esm2_t33_650M_UR50D", layer=17, window=W,
            epochs=EPOCHS, lr=LR, batch=BATCH, seed=SEED,
            splits={k: int(len(v)) for k, v in splits.items()},
            n_clusters=int(mf.cluster.nunique()))
json.dump(prov, open(OUT / "provenance.json", "w"), indent=2)
print("wrote results/ss_generalization.csv, ss_summary.json, provenance.json")
