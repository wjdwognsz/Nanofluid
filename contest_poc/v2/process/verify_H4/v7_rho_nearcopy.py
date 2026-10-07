"""Verifier check 7 (exploratory): DES_RHO -- held-out rows that still have a NEAR copy (same key, rel diff 1e-4..1e-2)
in the LOPO training set. Re-score OFF/SHR k=3 (main-run draws) with those rows removed from evaluation."""
import sys, zlib
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
name = "DES_RHO"; crc = lambda s: zlib.crc32(str(s).encode())
ds = load(name); yv = ds.df["y_raw"].values
df = pd.DataFrame({"g": ds.group.astype(str), "k": ds.key, "y": yv, "i": np.arange(len(yv))})
meta = pd.read_csv(f"{RAW}/h4_source_meta.csv"); meta = meta[meta.dataset == name].set_index("source")
rows = pd.read_csv(f"{RAW}/h4_base_rows.csv"); rows = rows[rows.dataset == name]
res = []; near_resid = []; other_resid = []
for s, r in rows.groupby("source", sort=False):
    idx = r.row.values.astype(int); e = r.resid_lopo.values; ns = len(e)
    own = df.iloc[idx][["k", "y", "i"]].rename(columns={"y": "ys", "i": "is"})
    mm = df[df.g != s].merge(own, on="k")
    rel = (mm.y - mm.ys).abs() / np.maximum(np.maximum(mm.y.abs(), mm.ys.abs()), 1e-12)
    exact_rows = set(mm.i[rel <= 1e-4])  # removed from training already
    near_s = set(mm["is"][(rel > 1e-4) & (rel <= 1e-2) & ~mm.i.isin(exact_rows)])
    nearflag = np.isin(idx, list(near_s))
    near_resid += list(np.abs(e[nearflag])); other_resid += list(np.abs(e[~nearflag]))
    tau2, sig2 = meta.loc[s, "tau2"], meta.loc[s, "sigma2"]; k = 3; wk = k * tau2 / (k * tau2 + sig2)
    for d in range(30):
        rng = np.random.default_rng([crc(name), crc(s), k, d])
        loc = np.sort(rng.choice(ns, size=k, replace=False)); test = np.setdiff1d(np.arange(ns), loc)
        off = e[loc].mean()
        for scope, tt in (("main", test), ("no_nearcopy_eval", test[~nearflag[test]])):
            if len(tt) == 0: continue
            r0 = np.sqrt(np.mean(e[tt] ** 2))
            for meth, w in (("OFF", 1.0), ("SHR", wk)):
                res.append((s, scope, meth, d, np.sqrt(np.mean((e[tt] - w * off) ** 2)) / r0 - 1))
R = pd.DataFrame(res, columns=["source", "scope", "method", "draw", "rc"])
print("median |LOPO resid| rows with near copy in training:", np.median(near_resid), " others:", np.median(other_resid), " n near rows:", len(near_resid))
for (sc, me), v in R.groupby(["scope", "method"]):
    p = v.groupby("source").rc.mean().values; rs = np.random.default_rng(0)
    bs = [p[rs.integers(0, len(p), len(p))].mean() for _ in range(2000)]
    print(f"  {sc:17s} {me} k3 mean {p.mean():+.4f} CI [{np.percentile(bs,2.5):+.4f},{np.percentile(bs,97.5):+.4f}] n_src {len(p)}")
