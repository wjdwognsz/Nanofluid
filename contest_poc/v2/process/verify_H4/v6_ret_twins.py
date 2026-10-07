"""Verifier check 6: RET (retrain with anchors, weight 5, RF150) at k=3 -- reproduce the main-run numbers with the same rng
draws, then re-score with evaluation rows that are exact (X,y) twins of an anchor removed (within-source duplicates).
Usage: python v6_ret_twins.py DATASET"""
import sys, zlib, json, time
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
from vrr_common import leak_mask_for_source, N_JOBS
from sklearn.ensemble import RandomForestRegressor

OUT = "/home/user/Nanofluid/contest_poc/v2/process/verify_H4"
RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
name = sys.argv[1]; K = 3
crc = lambda s: zlib.crc32(str(s).encode())
rf = lambda: RandomForestRegressor(n_estimators=150, max_features=0.33, min_samples_leaf=2, n_jobs=N_JOBS, random_state=0)
t0 = time.time()
ds = load(name)
info = json.load(open(f"{RAW}/h4_parts/{name}/sources.json"))
xh = pd.util.hash_pandas_object(pd.DataFrame(np.round(ds.X, 9)), index=False).values
D = pd.read_csv(f"{RAW}/h4_anchor_draws.csv.gz", keep_default_na=False, na_values=["", "nan", "NaN"])
D = D[(D.dataset == name) & (D.method == "RET") & (D.k == K)]; D["source"] = D.source.astype(str)
recs = []
for s in info["ret_sources"]:
    te = ds.group == s; lk = leak_mask_for_source(ds, s); trm = ~te & ~lk
    idx = np.where(te)[0]; tr_idx = np.where(trm)[0]; ns = len(idx)
    ys = ds.y[idx]; Xs = ds.X[idx]
    twin = np.array([f"{a}|{b:.9g}" for a, b in zip(xh[idx], ys)])
    pb = rf().fit(ds.X[trm], ds.y[trm]).predict(Xs)
    for r in range(5):
        rng = np.random.default_rng([crc(name), crc(s), K, r])
        loc = np.sort(rng.choice(ns, size=K, replace=False))
        test = np.setdiff1d(np.arange(ns), loc)
        m = rf().fit(np.vstack([ds.X[tr_idx], Xs[loc]]), np.concatenate([ds.y[tr_idx], ys[loc]]),
                     sample_weight=np.concatenate([np.ones(len(tr_idx)), np.full(K, 5.0)]))
        pk = m.predict(Xs)
        main_file = D[(D.source == s) & (D.draw == r)]
        for scope, tt in (("main", test), ("twin_disjoint", test[~np.isin(twin[test], twin[loc])])):
            if len(tt) == 0:
                continue
            r0 = np.sqrt(np.mean((ys[tt] - pb[tt]) ** 2)); rk = np.sqrt(np.mean((ys[tt] - pk[tt]) ** 2))
            recs.append((name, s, r, scope, len(tt), rk / r0 - 1,
                         float(main_file.rel_change.iloc[0]) if (scope == "main" and len(main_file)) else np.nan))
R = pd.DataFrame(recs, columns=["dataset", "source", "draw", "scope", "n_test", "rel_change", "file_rel_change"])
R.to_csv(f"{OUT}/v6_ret_twins_{name}.csv", index=False)
mm = R[R.scope == "main"]
print(name, "max |mine - file| main RET draws:", float(np.nanmax(np.abs(mm.rel_change - mm.file_rel_change))))
for sc, v in R.groupby("scope"):
    p = v.groupby("source").rel_change.mean().values
    rs = np.random.default_rng(0); bs = [p[rs.integers(0, len(p), len(p))].mean() for _ in range(2000)]
    print(f"  RET k3 {sc:13s}: mean {p.mean():+.4f} CI [{np.percentile(bs, 2.5):+.4f},{np.percentile(bs, 97.5):+.4f}] n_src {len(p)}")
print(f"  {time.time() - t0:.0f}s")
