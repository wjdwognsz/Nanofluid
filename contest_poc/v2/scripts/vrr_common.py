"""Shared protocol pieces for VRR v2 (models, folds, lineage, bootstrap, ledger).
All hypothesis scripts must use these so that results are comparable across tests."""
import csv
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, GroupKFold

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
RESULTS = os.path.join(V2, "results")
RAW = os.path.join(RESULTS, "raw")
LEDGER = os.path.join(V2, "ledger")
os.makedirs(RAW, exist_ok=True)
os.makedirs(LEDGER, exist_ok=True)
N_JOBS = int(os.environ.get("VRR_NJOBS", "2"))
MODELS = ("RF", "GB", "KNN")  # RF = primary; GB, KNN = robustness classes


def make_model(name="RF", seed=0):
    if name == "RF":
        return RandomForestRegressor(n_estimators=300, max_features=0.33, min_samples_leaf=2,
                                     n_jobs=N_JOBS, random_state=seed)
    if name == "GB":
        return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, min_samples_leaf=10,
                                             random_state=seed)
    if name == "KNN":
        return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=10, weights="distance"))
    raise ValueError(name)


def random_folds(n, k=5, seed=0):
    return list(KFold(k, shuffle=True, random_state=seed).split(np.arange(n)))


def group_folds(groups, k=10, seed=0):
    """GroupKFold with a seeded relabelling so that different seeds give different groupings."""
    g = pd.Series(groups).astype(str)
    u = g.unique()
    perm = dict(zip(u, np.random.default_rng(seed).permutation(len(u))))
    gi = g.map(perm).values
    k = min(k, len(u))
    return list(GroupKFold(n_splits=k).split(np.zeros(len(g)), groups=gi))


def pseudo_groups(groups, seed=0):
    """Negative control: random partition of rows into fake 'sources' with the real size distribution."""
    sizes = pd.Series(groups).value_counts().values
    lab = np.repeat(np.arange(len(sizes)), sizes)
    return np.random.default_rng(seed).permutation(lab).astype(str)


def cv_predict(X, y, folds, model="RF", seed=0):
    pred = np.full(len(y), np.nan)
    for tr, te in folds:
        pred[te] = make_model(model, seed).fit(X[tr], y[tr]).predict(X[te])
    return pred


def rmse(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = ~(np.isnan(a) | np.isnan(b))
    return float(np.sqrt(np.mean((a[m] - b[m]) ** 2)))


def r2(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2))


def boot_ci(values, stat=np.mean, n=2000, seed=0, alpha=0.05):
    """Bootstrap CI over independent units (e.g. per-source values)."""
    v = np.asarray(values, float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return (float("nan"), float("nan"))
    rs = np.random.default_rng(seed)
    bs = [stat(v[rs.integers(0, len(v), len(v))]) for _ in range(n)]
    return (float(np.percentile(bs, 100 * alpha / 2)), float(np.percentile(bs, 100 * (1 - alpha / 2))))


# ------------------------------------------------------------------ lineage (copied values)
def copy_relations(ds, min_shared=3, frac=0.8, rtol=1e-4):
    """Source pairs that share >= min_shared exact keys and report identical values (|rel diff|<rtol)
    for >= frac of them -> one is a copy of the other (compilation re-reporting).
    Returns DataFrame [s1, s2, shared, identical_frac]."""
    yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
    d = pd.DataFrame({"k": ds.key, "g": ds.group, "y": yv}).groupby(["k", "g"]).y.mean().reset_index()
    multi = d[d.k.isin(d.groupby("k").g.nunique().loc[lambda s: s > 1].index)]
    rows = []
    for k, sub in multi.groupby("k"):
        gs, ys = sub.g.values, sub.y.values
        for i in range(len(gs)):
            for j in range(i + 1, len(gs)):
                a, b = sorted([gs[i], gs[j]])
                same = abs(ys[i] - ys[j]) <= rtol * max(abs(ys[i]), abs(ys[j]), 1e-12)
                rows.append((a, b, same))
    if not rows:
        return pd.DataFrame(columns=["s1", "s2", "shared", "identical_frac"])
    p = pd.DataFrame(rows, columns=["s1", "s2", "same"]).groupby(["s1", "s2"]).same.agg(["size", "mean"]).reset_index()
    p.columns = ["s1", "s2", "shared", "identical_frac"]
    p["copy_relation"] = (p.shared >= min_shared) & (p.identical_frac >= frac)
    return p


def copy_mask(ds, rtol=1e-4):
    """Boolean mask of rows that are copies: same key AND identical value as a row of a *different*
    source that has fewer total rows (the smaller source is treated as the original measurement)."""
    yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
    size = pd.Series(ds.group).value_counts()
    d = pd.DataFrame({"k": ds.key, "g": ds.group, "y": yv, "n": pd.Series(ds.group).map(size).values})
    mask = np.zeros(len(d), bool)
    for k, sub in d.groupby("k"):
        if sub.g.nunique() < 2:
            continue
        idx = sub.index.values
        for i in idx:
            for j in idx:
                if d.g[i] == d.g[j]:
                    continue
                same = abs(d.y[i] - d.y[j]) <= rtol * max(abs(d.y[i]), abs(d.y[j]), 1e-12)
                # i is the copy if j comes from a smaller source (tie: lexicographic)
                if same and (d.n[j] < d.n[i] or (d.n[j] == d.n[i] and d.g[j] < d.g[i])):
                    mask[i] = True
    return mask


def leak_mask_for_source(ds, s, rtol=1e-4):
    """Rows of OTHER sources whose (key, value) duplicates a row of source s (would leak s into training)."""
    yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
    own = {}
    for k, v in zip(ds.key[ds.group == s], yv[ds.group == s]):
        own.setdefault(k, []).append(v)
    m = np.zeros(len(yv), bool)
    for i, (k, g, v) in enumerate(zip(ds.key, ds.group, yv)):
        if g != s and k in own and any(abs(v - o) <= rtol * max(abs(v), abs(o), 1e-12) for o in own[k]):
            m[i] = True
    return m


def subset(ds, mask, name_suffix=""):
    from vrr_data import DS
    mask = np.asarray(mask, bool)
    return DS(name=ds.name + name_suffix, y_name=ds.y_name, y_unit=ds.y_unit, df=ds.df[mask].reset_index(drop=True),
              X=ds.X[mask], feats=ds.feats, y=ds.y[mask], group=ds.group[mask], key=ds.key[mask],
              material=ds.material[mask], audit=ds.audit)


# ------------------------------------------------------------------ ledger
LEDGER_COLS = ["hypothesis", "test_id", "dataset", "model", "metric", "value", "ci_lo", "ci_hi",
               "threshold", "verdict", "n_units", "note"]


def ledger_write(path, rows):
    """rows: list of dicts with LEDGER_COLS keys. Overwrites the hypothesis file each run."""
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in LEDGER_COLS})
