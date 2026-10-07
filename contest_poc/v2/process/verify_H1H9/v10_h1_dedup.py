"""Verifier: H1 rule re-run on data with within-source exact (key,y) duplicates collapsed. Same seeds as family (0-4,
pseudo 0-19). Usage: python v10_h1_dedup.py DATASET"""
import sys, time
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/process/verify_H1H9")
from vrr_data import load
from vrr_common import make_model, random_folds, group_folds, pseudo_groups, rmse, subset
from v9_dedup_mask import within_source_dup_mask
name = sys.argv[1]
ds0 = load(name)
ds = subset(ds0, ~within_source_dup_mask(ds0), "_dedup")
n = len(ds.y); t0 = time.time()
print(name, "rows", len(ds0.y), "->", n, "sources", len(set(ds.group)))
def oof(folds, model, seed):
    p = np.full(n, np.nan)
    for tr, te in folds:
        p[te] = make_model(model, seed).fit(ds.X[tr], ds.y[tr]).predict(ds.X[te])
    return p
res = []
for model in ["RF", "GB", "KNN"]:
    for seed in range(5):
        for sch, folds in (("random", random_folds(n, 5, seed)), ("group", group_folds(ds.group, 10, seed)),
                           ("material", group_folds(ds.material, 10, seed))):
            if sch == "material" and model != "RF":
                continue
            res.append(dict(model=model, seed=seed, scheme=sch, rmse=rmse(ds.y, oof(folds, model, seed))))
    print(model, f"{time.time()-t0:.0f}s", flush=True)
r = pd.DataFrame(res); mr = r.groupby(["model", "scheme"]).rmse.mean()
gaps = {m: mr[(m, "group")] / mr[(m, "random")] - 1 for m in ["RF", "GB", "KNN"]}
pg = np.array([rmse(ds.y, oof(group_folds(pseudo_groups(ds.group, seed=j), 10, seed=j), "RF", j)) / mr[("RF", "random")] - 1
               for j in range(20)])
p95 = np.percentile(pg, 95)
c = (gaps["RF"] >= 0.2, gaps["RF"] > p95, max(gaps["GB"], gaps["KNN"]) >= 0.1)
print({k: round(v, 4) for k, v in gaps.items()}, "material gap RF", round(mr[("RF", "material")] / mr[("RF", "random")] - 1, 4),
      "RMSE RF random/group", round(mr[("RF", "random")], 4), round(mr[("RF", "group")], 4))
print(f"pseudo p95 {p95:.4f} max {pg.max():.4f}; conditions {c} -> {'PASS' if all(c) else 'FAIL'} ({time.time()-t0:.0f}s)")
r.to_csv(f"/home/user/Nanofluid/contest_poc/v2/process/verify_H1H9/dedup_h1_{name}.csv", index=False)
