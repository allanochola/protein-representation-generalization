# ---
# jupyter:
#   jupytext:
#     text_representation: {extension: .py, format_name: percent}
#   kernelspec: {display_name: Python 3, name: python3}
# ---

# %% [markdown]
# # Embedding extraction (run first, GPU)
#
# Loads TAPE secondary structure as the labeled protein source, reclusters at 30%
# identity (MMseqs2 — TAPE's split is not used), and caches ESM-2 **layer-17**
# per-residue embeddings + Q3 labels per protein, with a manifest carrying the
# cluster id. Computes no probe and no metric. Thin driver over `src/`.

# %%
import os
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import torch

import sys; sys.path.insert(0, str(Path.cwd().parent))   # repo root on path
from src import probe as sp
from src import clustering as cl
from src import extract_esm2 as ex
print(sp.selftest())

LAYER = 17
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
assert DEVICE == "cuda", "extraction needs a GPU (ESM-2 650M)"
TAPE_DIR = os.environ.get("TAPE_DIR", "/content/tape_ss")
CACHE = Path(os.environ.get("SS_CACHE", "/content/ss_cache")); CACHE.mkdir(exist_ok=True)
EMB = CACHE / "emb"; EMB.mkdir(exist_ok=True)

# %% [markdown]
# ## 1. Load + clean TAPE, then cluster at 30% identity
#
# Download once, e.g.:
#   `wget http://s3.amazonaws.com/proteindata/data_pytorch/secondary_structure.tar.gz`
# then untar into TAPE_DIR.

# %%
clean, (seq_key, ss_key) = cl.load_tape_ss(TAPE_DIR)
print(f"clean proteins: {len(clean)}  (fields seq='{seq_key}', ss3='{ss_key}')")
# class-balance sanity BEFORE mass extraction — Q3 should be ~0.35/0.22/0.43 (H/E/C).
ys = np.concatenate([p["y"] for p in clean[:200]])
print("Q3 balance (first 200):", {sp.Q3[k]: round((ys == k).mean(), 3) for k in range(3)})
assert set(np.unique(ys)).issubset({0, 1, 2}), "ss3 labels not in {0,1,2} — check H/E/C order"

clu = cl.cluster_30(clean, str(CACHE))
n_clusters = len(set(clu.values()))
print(f"clusters at 30% identity: {n_clusters}")
assert n_clusters > 20, "too few clusters — inspect mmseqs.log"

# %% [markdown]
# ## 2. ESM-2 layer-17 per-residue embeddings, cached per protein

# %%
tok, model = ex.load_model(device=DEVICE)
manifest = []
for j, p in enumerate(clean):
    fp = EMB / f"{p['id']}.npz"
    if not fp.exists():
        emb = ex.embed_layer(tok, model, p["seq"], layer=LAYER, device=DEVICE)
        np.savez_compressed(fp, emb=emb, y=p["y"])
    payload = (
        p["seq"].encode("utf-8")
        + b"\\0"
        + np.asarray(p["y"], dtype=np.uint8).tobytes()
    )
    record_key = hashlib.sha256(payload).hexdigest()

    manifest.append(dict(
        id=p["id"],
        cluster=clu.get(p["id"], p["id"]),
        record_key=record_key,
        seq=p["seq"],
        n_res=len(p["seq"]),
        npz=str(fp),
    ))
    if j % 200 == 0:
        print(f"  embedded {j+1}/{len(clean)}")

mf = pd.DataFrame(manifest)

# Replace arbitrary MMseqs representative IDs with an intrinsic cluster key:
# SHA256(sorted content-derived record keys belonging to the cluster)).
stable_cluster = {}

for old_cluster, g in mf.groupby("cluster", sort=False):
    members = sorted(g["record_key"].tolist())
    payload = "\\n".join(members).encode("ascii")
    stable_cluster[old_cluster] = hashlib.sha256(payload).hexdigest()

mf["cluster"] = mf["cluster"].map(stable_cluster)

# Canonical protein row order. This makes the seed-0 random-test sampling
# independent of LMDB enumeration order and arbitrary pXXXX identifiers.
mf = (
    mf.sort_values("record_key")
      .reset_index(drop=True)
)

assert mf["record_key"].is_unique
assert mf["record_key"].is_monotonic_increasing
assert mf["cluster"].nunique() == n_clusters

mf.to_csv(CACHE / "manifest.csv", index=False)

print(
    f"cached {len(mf)} proteins across {n_clusters} clusters -> {CACHE}"
)
print("manifest canonicalization: content-derived record + cluster keys")
