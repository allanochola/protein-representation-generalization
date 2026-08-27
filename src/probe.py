"""Shared logic for the ESM-2 secondary-structure generalization experiment.

The two parts that break silently live here and are checked offline in selftest():
- Q8->Q3 mapping and label/sequence alignment.
- CLUSTER-level bootstrap — resample whole sequence-identity clusters, not
  residues, because residues within a protein (and within a family) are not
  independent. Resampling residues would manufacture tight, wrong CIs.
"""
import numpy as np

AA = "ACDEFGHIKLMNPQRSTVWY"
AA_IDX = {a: i for i, a in enumerate(AA)}
Q3 = ["H", "E", "C"]                       # helix / strand / coil
Q3_IDX = {c: i for i, c in enumerate(Q3)}

# DSSP 8-state -> 3-state (standard collapse). Used only if a source gives Q8;
# TAPE ships ss3 directly, in which case this is provenance, not computation.
Q8_TO_Q3 = {"H": "H", "G": "H", "I": "H",  # 3-10 / pi helices -> helix
            "E": "E", "B": "E",            # strand / bridge -> strand
            "T": "C", "S": "C", "C": "C", "-": "C", " ": "C", "L": "C"}


def q8_to_q3(labels8):
    return [Q8_TO_Q3[c] for c in labels8]


def local_window_features(seq, w=3):
    """Per-residue one-hot of amino-acid identity in a +/-w window. Non-standard
    residues and out-of-range (padding) positions map to an all-zero block.
    Returns [L, (2w+1)*20]. No ESM — this is the sequence-local baseline."""
    L = len(seq)
    span = 2 * w + 1
    X = np.zeros((L, span * 20), dtype=np.float32)
    for i in range(L):
        for k, j in enumerate(range(i - w, i + w + 1)):
            if 0 <= j < L:
                a = seq[j]
                if a in AA_IDX:
                    X[i, k * 20 + AA_IDX[a]] = 1.0
    return X


def align_ok(seq, labels, mask=None):
    """Length agreement between sequence, per-residue labels, and optional validity
    mask. The single cheapest guard against an off-by-one that would silently
    misattribute every label."""
    if len(seq) != len(labels):
        return False
    if mask is not None and len(mask) != len(seq):
        return False
    return True


def q3_accuracy(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return float((y_true == y_pred).mean())


def macro_f1(y_true, y_pred, n_classes=3):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    f1s = []
    for c in range(n_classes):
        tp = np.sum((y_pred == c) & (y_true == c))
        fp = np.sum((y_pred == c) & (y_true != c))
        fn = np.sum((y_pred != c) & (y_true == c))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return float(np.mean(f1s))


def cluster_bootstrap(cluster_ids, y_true, y_pred, stat_fn, reps=1000, seed=0):
    """Percentile CI by resampling CLUSTERS with replacement. cluster_ids is
    per-residue; each bootstrap draws whole clusters, gathers their residues, and
    recomputes the statistic on that residue set. Residue-level resampling is the
    bug this exists to avoid."""
    rng = np.random.default_rng(seed)
    cluster_ids = np.asarray(cluster_ids)
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    uniq = np.unique(cluster_ids)
    idx_by_cluster = {c: np.where(cluster_ids == c)[0] for c in uniq}
    stats = np.empty(reps)
    for b in range(reps):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        rows = np.concatenate([idx_by_cluster[c] for c in pick])
        stats[b] = stat_fn(y_true[rows], y_pred[rows])
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))


def make_splits(cluster_per_protein, seed=0, div_frac=0.2, indist_frac=0.15):
    """Cluster-level split over the protein list. Returns index arrays:
    - divergent_test: proteins whose cluster is held out entirely (no homolog in
      train, i.e. <30% identity to any training protein);
    - random_test: proteins sampled from the TRAIN clusters — in-distribution,
      homologs may be in train;
    - train: the rest.
    Divergent clusters are disjoint from train/random-test clusters by construction."""
    rng = np.random.default_rng(seed)
    clusters = np.asarray(cluster_per_protein)
    uniq = np.unique(clusters).copy(); rng.shuffle(uniq)
    n_div = max(1, int(round(div_frac * len(uniq))))
    div_clusters = set(uniq[:n_div].tolist())
    is_div = np.array([c in div_clusters for c in clusters])
    div_idx = np.where(is_div)[0]
    train_pool = np.where(~is_div)[0].copy(); rng.shuffle(train_pool)
    n_indist = max(1, int(round(indist_frac * len(train_pool))))
    return dict(train=np.sort(train_pool[n_indist:]),
                random_test=np.sort(train_pool[:n_indist]),
                divergent_test=np.sort(div_idx))


def paired_diff_bootstrap(cluster_ids, correct_a, correct_b, reps=1000, seed=0):
    """CI for mean(correct_a) - mean(correct_b) over the SAME residues,
    resampling whole clusters.

    Uses per-cluster sufficient statistics rather than repeatedly materializing
    residue-index arrays. This is mathematically identical to concatenating all
    residues belonging to each sampled cluster, including repeated clusters.
    """
    rng = np.random.default_rng(seed)

    cluster_ids = np.asarray(cluster_ids)
    ca = np.asarray(correct_a, dtype=np.float64)
    cb = np.asarray(correct_b, dtype=np.float64)

    uniq, inv = np.unique(cluster_ids, return_inverse=True)
    k = len(uniq)

    n = np.bincount(inv, minlength=k).astype(np.float64)
    sum_a = np.bincount(inv, weights=ca, minlength=k)
    sum_b = np.bincount(inv, weights=cb, minlength=k)

    d = np.empty(reps, dtype=np.float64)

    for b in range(reps):
        pick = rng.choice(k, size=k, replace=True)
        multiplicity = np.bincount(pick, minlength=k)

        denom = np.dot(multiplicity, n)

        d[b] = (
            np.dot(multiplicity, sum_a)
            - np.dot(multiplicity, sum_b)
        ) / denom

    return (
        float(np.percentile(d, 2.5)),
        float(np.percentile(d, 97.5)),
    )


def verdict(delta_div, gap):
    """Frozen decision bands (SS_GENERALIZATION_PROTOCOL.md)."""
    if delta_div >= 0.08 and gap <= 0.10:
        return "H_repr"
    if delta_div <= 0.03 or gap >= 0.15:
        return "H_shortcut"
    return "unresolved"


def selftest():
    rng = np.random.default_rng(0)

    # Q8->Q3
    assert q8_to_q3(list("HGIEBTSC-")) == list("HHHEECCCC")

    # local window: shape, and the center block one-hots the residue itself
    X = local_window_features("ACDXG", w=1)          # X is non-standard -> zero block
    assert X.shape == (5, 3 * 20)
    assert X[0, 1 * 20 + AA_IDX["A"]] == 1.0          # center of residue 0 is 'A'
    assert X[3].sum() == 2.0                           # pos3 'X' center zero; neighbors D,G only

    # metrics
    yt = np.array([0, 0, 1, 1, 2, 2]); yp = np.array([0, 0, 1, 2, 2, 2])
    assert abs(q3_accuracy(yt, yp) - 5 / 6) < 1e-9
    assert 0.0 <= macro_f1(yt, yp) <= 1.0

    # cluster bootstrap resamples CLUSTERS: a 2-cluster set can only ever yield
    # residue counts that are sums of whole-cluster sizes -> CI must be wider than
    # a (wrong) residue-level resample of the same data.
    cl = np.array([0]*50 + [1]*50)
    yt2 = np.array([0]*100)
    yp2 = np.array([0]*50 + [1]*50)                    # cluster 0 all-correct, cluster 1 all-wrong
    lo, hi = cluster_bootstrap(cl, yt2, yp2, q3_accuracy, reps=2000, seed=1)
    assert lo == 0.0 and hi == 1.0                     # only whole-cluster draws -> acc in {0,.33,.5,.67,1}, extremes hit
    # residue-level would give ~[0.40,0.60]; the wide interval proves cluster-level

    # verdict bands
    assert verdict(0.09, 0.05) == "H_repr"
    assert verdict(0.02, 0.05) == "H_shortcut"
    assert verdict(0.09, 0.20) == "H_shortcut"
    assert verdict(0.05, 0.12) == "unresolved"

    # make_splits: no cluster leakage between train/random-test and divergent-test,
    # and random-test proteins come from train clusters (in-distribution)
    clusters = np.repeat(np.arange(20), 5)             # 100 proteins, 20 clusters of 5
    sp_ = make_splits(clusters, seed=0)
    tr, rt, dv = sp_["train"], sp_["random_test"], sp_["divergent_test"]
    assert len(set(tr) | set(rt) | set(dv)) == 100     # partition covers all
    assert len(set(tr) & set(dv)) == 0 and len(set(rt) & set(dv)) == 0
    div_cl = set(clusters[dv]); train_cl = set(clusters[tr]) | set(clusters[rt])
    assert div_cl.isdisjoint(train_cl)                 # divergent clusters unseen in training
    assert set(clusters[rt]).issubset(set(clusters[tr]))  # in-distribution: random-test clusters are trained on

    # paired_diff_bootstrap runs and brackets the point difference
    cl3 = np.repeat(np.arange(10), 20)
    a = (rng.random(200) < 0.8).astype(int); b = (rng.random(200) < 0.6).astype(int)
    lo3, hi3 = paired_diff_bootstrap(cl3, a, b, reps=500, seed=2)
    assert lo3 <= (a.mean() - b.mean()) <= hi3
    return "ss_probe selftest: OK"


if __name__ == "__main__":
    print(selftest())
