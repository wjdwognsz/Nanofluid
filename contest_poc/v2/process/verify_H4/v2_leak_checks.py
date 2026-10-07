"""Verifier check 2: leakage audit for H4 (independent of h4_anchor.py).
(a) re-derive the held-out source's leak rows with an independent implementation and compare with h4_source_meta;
(b) near-copies missed by rtol=1e-4 (same key, rel diff in (1e-4, 1e-2]) left in training;
(c) exact feature-vector duplicates (any key) of held-out rows in training with |dy| tiny;
(d) within-source replicate structure (anchors that are replicates of evaluation rows);
(e) re-score OFF/SHR k=3 with key-disjoint and X-disjoint evaluation (same rng draws as the main run, cached LOPO residuals).
Usage: python v2_leak_checks.py DATASET"""
import sys, zlib, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load

RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
OUT = "/home/user/Nanofluid/contest_poc/v2/process/verify_H4"
name = sys.argv[1]
ds = load(name)
yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
meta = pd.read_csv(f"{RAW}/h4_source_meta.csv", keep_default_na=False, na_values=["", "NaN"])
meta = meta[meta.dataset == name].copy(); meta["source"] = meta.source.astype(str)
rows = pd.read_csv(f"{RAW}/h4_base_rows.csv", keep_default_na=False, na_values=["", "NaN"])
rows = rows[rows.dataset == name].copy(); rows["source"] = rows.source.astype(str)
crc = lambda s: zlib.crc32(str(s).encode())

df = pd.DataFrame({"g": ds.group.astype(str), "k": ds.key, "y": yv})
Xr = np.round(ds.X, 9)
xh = pd.util.hash_pandas_object(pd.DataFrame(Xr), index=False).values
df["xh"] = xh
out = []
for s in meta.source:
    te = (df.g == s).values
    own = df[te]
    oth = df[~te]
    # independent leak: merge on key, compare values
    mm = oth.reset_index().merge(own[["k", "y"]].rename(columns={"y": "ys"}), on="k")
    rel = (mm.y - mm.ys).abs() / np.maximum(np.maximum(mm.y.abs(), mm.ys.abs()), 1e-12)
    leak_idx = set(mm["index"][rel <= 1e-4])
    near_idx = set(mm["index"][(rel > 1e-4) & (rel <= 1e-2)]) - leak_idx
    tr = np.ones(len(df), bool); tr[te] = False; tr[list(leak_idx)] = False
    # (c) X duplicates in training of held-out rows
    trdf = df[tr]
    xm = own.reset_index().merge(trdf[["xh", "y"]].rename(columns={"y": "yt"}), on="xh")
    relx = (xm.y - xm.yt).abs() / np.maximum(np.maximum(xm.y.abs(), xm.yt.abs()), 1e-12)
    # held-out rows that have a same-key near copy (1e-4<rel<=1e-2) in training
    near_rows_s = set(mm[(rel > 1e-4) & (rel <= 1e-2)].merge(own.reset_index()[["index", "k"]], on="k", suffixes=("", "_s"))["index_s"]) if len(near_idx) else set()
    # (d) within-source replicates
    kc = own.k.value_counts()
    rep_rows = int(own.k.map(kc).gt(1).sum())
    yrep = own.groupby("k").y.transform(lambda v: v.duplicated(keep=False)).sum()
    xc = own.xh.value_counts()
    xrep_rows = int(own.xh.map(xc).gt(1).sum())
    m = meta.set_index("source").loc[s]
    out.append(dict(dataset=name, source=s, n_rows=int(te.sum()), n_leak_mine=len(leak_idx), n_leak_h4=int(m.n_leak_rows_removed),
                    n_train_mine=int(tr.sum()), n_train_h4=int(m.n_train_rows),
                    n_nearcopy_train_rows=len(near_idx), n_heldout_rows_with_nearcopy=len(near_rows_s),
                    n_heldout_rows_with_Xdup_in_train=int(xm["index"].nunique()),
                    n_heldout_rows_with_Xdup_and_same_y_in_train=int(xm["index"][relx <= 1e-4].nunique()),
                    n_rows_in_repeated_key_within_source=rep_rows, n_rows_identical_key_and_y_within_source=int(yrep),
                    n_rows_in_repeated_X_within_source=xrep_rows))
L = pd.DataFrame(out)
L.to_csv(f"{OUT}/v2_leak_{name}.csv", index=False)
tot = L[[c for c in L.columns if c.startswith("n_")]].sum()
print(name, "sources", len(L), "| leak count mismatches:", int((L.n_leak_mine != L.n_leak_h4).sum()),
      "| train count mismatches:", int((L.n_train_mine != L.n_train_h4).sum()))
print(tot.to_string())

# (e) key-disjoint and X-disjoint re-scoring of OFF/SHR k in {1,3}
res = []
for s, r in rows.groupby("source", sort=False):
    idx = r.row.values.astype(int)
    e = r.resid_lopo.values
    keys = ds.key[idx]; xs = xh[idx]; mats = ds.material[idx]
    mt = meta.set_index("source").loc[s]
    tau2, sig2 = float(mt.tau2), float(mt.sigma2)
    ns = len(e)
    for k in (1, 3):
        wk = k * tau2 / (k * tau2 + sig2) if tau2 > 0 else 0.0
        for d in range(30):
            rng = np.random.default_rng([crc(name), crc(s), k, d])
            loc = np.sort(rng.choice(ns, size=k, replace=False))
            base_test = np.setdiff1d(np.arange(ns), loc)
            off = e[loc].mean()
            for scope, test in (("main", base_test),
                                ("key_disjoint", base_test[~np.isin(keys[base_test], keys[loc])]),
                                ("X_disjoint", base_test[~np.isin(xs[base_test], xs[loc])])):
                if len(test) == 0:
                    continue
                r0 = np.sqrt(np.mean(e[test] ** 2))
                for meth, w in (("OFF", 1.0), ("SHR", wk)):
                    rk = np.sqrt(np.mean((e[test] - w * off) ** 2))
                    res.append((name, s, scope, meth, k, d, len(test), rk / r0 - 1))
R = pd.DataFrame(res, columns=["dataset", "source", "scope", "method", "k", "draw", "n_test", "rel_change"])
R.to_csv(f"{OUT}/v2_disjoint_{name}.csv.gz", index=False, compression="gzip")
P = R.groupby(["scope", "method", "k", "source"]).rel_change.mean().reset_index()
for (sc, me, k), v in P.groupby(["scope", "method", "k"]):
    vv = v.rel_change.values
    rs = np.random.default_rng(0)
    bs = [vv[rs.integers(0, len(vv), len(vv))].mean() for _ in range(2000)]
    print(f"  {sc:13s} {me} k={k}: mean {vv.mean():+.4f} CI [{np.percentile(bs, 2.5):+.4f},{np.percentile(bs, 97.5):+.4f}] "
          f"median {np.median(vv):+.4f} n_src {len(vv)}")
