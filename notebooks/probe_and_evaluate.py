# ESM-2 SS-generalization — memory-safe confirmatory evaluation
#
# Technical amendment only: the original evaluator was SIGKILLed before producing
# any metric because it materialized the full residue x 1280 matrix in RAM.
# Scientific design, estimator class, hyperparameters, splits, metrics and frozen
# decision bands are unchanged.

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
OUT = Path("results")
OUT.mkdir(exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SEED = 0
W = 3
EPOCHS, LR, BATCH = 40, 1e-3, 4096

torch.manual_seed(SEED)
np.random.seed(SEED)

mf = pd.read_csv(CACHE / "manifest.csv")
print(f"{len(mf)} proteins, {mf.cluster.nunique()} clusters")

splits = sp.make_splits(mf.cluster.values, seed=SEED)
for k, v in splits.items():
    print(f"  {k}: {len(v)} proteins, {mf.iloc[v].cluster.nunique()} clusters")


def load_protein(i, kind):
    row = mf.iloc[int(i)]
    d = np.load(EMB / f"{row['id']}.npz")
    y = d["y"].astype(np.int64, copy=False)

    if kind == "esm":
        X = d["emb"]
    else:
        X = sp.local_window_features(row["seq"], W)

    assert X.shape[0] == len(y), f"align fail {row['id']}"
    return X, y, row["cluster"]


def streaming_stats(idx, kind, in_dim):
    """Exact feature mean/std without materializing the training matrix."""
    n = 0
    s1 = np.zeros(in_dim, dtype=np.float64)
    s2 = np.zeros(in_dim, dtype=np.float64)

    for j, i in enumerate(idx):
        X, _, _ = load_protein(i, kind)
        X = X.astype(np.float64, copy=False)
        n += X.shape[0]
        s1 += X.sum(axis=0)
        s2 += np.square(X).sum(axis=0)

        if (j + 1) % 1000 == 0:
            print(f"  stats {kind}: {j+1}/{len(idx)} proteins")

    mu = s1 / n
    var = np.maximum(s2 / n - mu * mu, 0.0)
    sd = np.sqrt(var) + 1e-6

    return mu.astype(np.float32), sd.astype(np.float32), int(n)


def residue_batches(idx, kind, mu, sd, epoch):
    """Stream proteins in a deterministic shuffled order and emit residue batches.

    The original implementation shuffled all residues globally each epoch. That is
    impossible without materializing the full residue matrix. This implementation
    instead shuffles protein order and residues within each protein deterministically
    from the same fixed seed. Probe class/optimizer/LR/epochs/batch size are unchanged.
    """
    rng = np.random.default_rng(SEED + epoch)

    order = np.asarray(idx).copy()
    rng.shuffle(order)

    bx, by = [], []
    nbuf = 0

    for i in order:
        X, y, _ = load_protein(i, kind)

        perm = rng.permutation(len(y))
        X = X[perm].astype(np.float32, copy=False)
        y = y[perm]

        X = (X - mu) / sd

        pos = 0
        while pos < len(y):
            need = BATCH - nbuf
            take = min(need, len(y) - pos)

            bx.append(X[pos:pos+take])
            by.append(y[pos:pos+take])
            nbuf += take
            pos += take

            if nbuf == BATCH:
                yield np.concatenate(bx), np.concatenate(by)
                bx, by, nbuf = [], [], 0

    if nbuf:
        yield np.concatenate(bx), np.concatenate(by)


def train_probe_streaming(idx, kind, in_dim):
    print(f"\ncomputing train normalization: {kind}")
    mu, sd, n = streaming_stats(idx, kind, in_dim)
    print(f"  train residues: {n}")

    torch.manual_seed(SEED)

    clf = nn.Linear(in_dim, 3).to(DEVICE)
    opt = torch.optim.Adam(clf.parameters(), lr=LR)
    lossf = nn.CrossEntropyLoss()

    for ep in range(EPOCHS):
        clf.train()
        total_loss = 0.0
        seen = 0

        for Xb, yb in residue_batches(idx, kind, mu, sd, ep):
            Xt = torch.from_numpy(Xb).to(DEVICE)
            yt = torch.from_numpy(yb).to(DEVICE)

            opt.zero_grad(set_to_none=True)
            loss = lossf(clf(Xt), yt)
            loss.backward()
            opt.step()

            total_loss += float(loss.detach()) * len(yb)
            seen += len(yb)

        if ep == 0 or (ep + 1) % 5 == 0:
            print(
                f"  {kind} epoch {ep+1:02d}/{EPOCHS} "
                f"loss={total_loss/seen:.5f}"
            )

    return clf, (mu, sd)


@torch.no_grad()
def evaluate_streaming(clf, scaler, idx, kind):
    """Evaluate protein-by-protein; retain only labels/predictions/cluster ids."""
    clf.eval()
    mu, sd = scaler

    ys, yps, cs = [], [], []

    for j, i in enumerate(idx):
        X, y, cluster = load_protein(i, kind)
        X = X.astype(np.float32, copy=False)
        X = (X - mu) / sd

        preds = []
        for s in range(0, len(y), BATCH):
            Xt = torch.from_numpy(X[s:s+BATCH]).to(DEVICE)
            preds.append(clf(Xt).argmax(1).cpu().numpy())

        yp = np.concatenate(preds)

        ys.append(y)
        yps.append(yp)
        cs.append(np.full(len(y), cluster))

        if (j + 1) % 1000 == 0:
            print(f"  eval {kind}: {j+1}/{len(idx)} proteins")

    y = np.concatenate(ys)
    yp = np.concatenate(yps)
    c = np.concatenate(cs)

    return dict(
        acc=sp.q3_accuracy(y, yp),
        f1=sp.macro_f1(y, yp),
        correct=(y == yp).astype(np.int8),
        cluster=c,
        y=y,
        yp=yp,
    )


def fit_and_eval(kind, in_dim):
    clf, scaler = train_probe_streaming(splits["train"], kind, in_dim)

    out = {}
    for split in ("random_test", "divergent_test"):
        print(f"\nevaluating {kind}: {split}")
        out[split] = evaluate_streaming(
            clf, scaler, splits[split], kind
        )

    return out


# Confirmatory analysis: same order as frozen evaluator.
esm = fit_and_eval("esm", 1280)
loc = fit_and_eval("local", (2 * W + 1) * 20)

acc_esm_rand = esm["random_test"]["acc"]
acc_esm_div = esm["divergent_test"]["acc"]
acc_loc_div = loc["divergent_test"]["acc"]

delta_div = acc_esm_div - acc_loc_div
gap = acc_esm_rand - acc_esm_div


d_lo, d_hi = sp.paired_diff_bootstrap(
    esm["divergent_test"]["cluster"],
    esm["divergent_test"]["correct"],
    loc["divergent_test"]["correct"],
    reps=2000,
    seed=SEED,
)


def unpaired_gap_ci(a, b, reps=2000, seed=SEED):
    rng = np.random.default_rng(seed)

    def acc_boot(cell):
        cl = cell["cluster"]
        corr = cell["correct"]
        uniq = np.unique(cl)
        idx = {c: np.where(cl == c)[0] for c in uniq}
        pick = rng.choice(uniq, len(uniq), replace=True)
        rows = np.concatenate([idx[c] for c in pick])
        return corr[rows].mean()

    g = np.array(
        [acc_boot(a) - acc_boot(b) for _ in range(reps)]
    )
    return (
        float(np.percentile(g, 2.5)),
        float(np.percentile(g, 97.5)),
    )


g_lo, g_hi = unpaired_gap_ci(
    esm["random_test"], esm["divergent_test"]
)

verdict = sp.verdict(delta_div, gap)

rows = [
    dict(
        cell="ESM_random",
        acc=acc_esm_rand,
        macro_f1=esm["random_test"]["f1"],
    ),
    dict(
        cell="ESM_divergent",
        acc=acc_esm_div,
        macro_f1=esm["divergent_test"]["f1"],
    ),
    dict(
        cell="local_random",
        acc=loc["random_test"]["acc"],
        macro_f1=loc["random_test"]["f1"],
    ),
    dict(
        cell="local_divergent",
        acc=acc_loc_div,
        macro_f1=loc["divergent_test"]["f1"],
    ),
]

pd.DataFrame(rows).to_csv(
    OUT / "ss_generalization.csv", index=False
)

summary = dict(
    delta_esm_divergent=round(delta_div, 4),
    delta_ci=[round(d_lo, 4), round(d_hi, 4)],
    G=round(gap, 4),
    G_ci=[round(g_lo, 4), round(g_hi, 4)],
    acc_esm_random=round(acc_esm_rand, 4),
    acc_esm_divergent=round(acc_esm_div, 4),
    acc_local_divergent=round(acc_loc_div, 4),
    verdict=verdict,
)

json.dump(
    summary,
    open(OUT / "ss_summary.json", "w"),
    indent=2,
)

print(
    f"\nESM  Q3: random {acc_esm_rand:.3f} | "
    f"divergent {acc_esm_div:.3f}"
)
print(f"local Q3 divergent: {acc_loc_div:.3f}")
print(
    f"Delta_ESM(divergent) = {delta_div:+.3f} "
    f" CI [{d_lo:+.3f}, {d_hi:+.3f}]"
)
print(
    f"G (random-divergent) = {gap:+.3f} "
    f" CI [{g_lo:+.3f}, {g_hi:+.3f}]"
)
print(f"\nVERDICT (frozen bands): {verdict}")

prov = dict(
    model="facebook/esm2_t33_650M_UR50D",
    layer=17,
    window=W,
    epochs=EPOCHS,
    lr=LR,
    batch=BATCH,
    seed=SEED,
    evaluator="streaming-v1",
    first_attempt="SIGKILL before metrics; host RAM exhaustion",
    minibatch_order=(
        "protein order shuffled each epoch; residues shuffled "
        "within protein; scientific design unchanged"
    ),
    splits={k: int(len(v)) for k, v in splits.items()},
    n_clusters=int(mf.cluster.nunique()),
)

json.dump(
    prov,
    open(OUT / "provenance.json", "w"),
    indent=2,
)

print(
    "wrote results/ss_generalization.csv, "
    "ss_summary.json, provenance.json"
)
