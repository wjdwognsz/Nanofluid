"""Verifier: H1 re-run with different seeds (5..9) and different pseudo seeds (20..39) for one dataset.
Usage: python v3_h1_reseed.py DATASET"""
import os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
from vrr_common import make_model, random_folds, group_folds, pseudo_groups, rmse

name = sys.argv[1]
models = sys.argv[2].split(",") if len(sys.argv) > 2 else ["RF", "GB", "KNN"]
ds = load(name)
n = len(ds.y)
t0 = time.time()

def oof(folds, model, seed):
    p = np.full(n, np.nan)
    for tr, te in folds:
        p[te] = make_model(model, seed).fit(ds.X[tr], ds.y[tr]).predict(ds.X[te])
    return p

res = []
for model in models:
    for seed in range(5, 10):
        for sch, folds in (("random", random_folds(n, 5, seed)), ("group", group_folds(ds.group, 10, seed))):
            res.append(dict(model=model, seed=seed, scheme=sch, rmse=rmse(ds.y, oof(folds, model, seed))))
    print(model, f"{time.time()-t0:.0f}s", flush=True)
r = pd.DataFrame(res)
mr = r.groupby(["model", "scheme"]).rmse.mean().unstack()
gaps = (mr.group / mr.random - 1)
print("gaps seeds 5-9:", gaps.round(4).to_dict())
pg = []
for j in range(20, 40):
    pgr = pseudo_groups(ds.group, seed=j)
    pg.append(rmse(ds.y, oof(group_folds(pgr, 10, seed=j), "RF", j)) / mr.loc["RF", "random"] - 1)
pg = np.array(pg)
print(f"pseudo seeds 20-39: p95 {np.percentile(pg, 95):.4f} max {pg.max():.4f} mean {pg.mean():.4f}")
c1 = gaps["RF"] >= 0.2; c2 = gaps["RF"] > np.percentile(pg, 95)
c3 = max(gaps.get("GB", -9), gaps.get("KNN", -9)) >= 0.1
print("conditions", c1, c2, c3, "verdict", "PASS" if c1 and c2 and c3 else "FAIL", f"({time.time()-t0:.0f}s)")
r.to_csv(f"/home/user/Nanofluid/contest_poc/v2/process/verify_H1H9/reseed_h1_{name}.csv", index=False)
