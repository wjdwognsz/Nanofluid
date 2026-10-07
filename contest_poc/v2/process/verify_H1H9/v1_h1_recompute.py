"""Verifier: recompute H1 verdicts from raw CSVs; check fold grouping; check RMSE from stored predictions."""
import os, sys, glob, json
import numpy as np, pandas as pd
V2 = "/home/user/Nanofluid/contest_poc/v2"
sys.path.insert(0, os.path.join(V2, "scripts"))
RAW = os.path.join(V2, "results/raw")

cv = pd.read_csv(f"{RAW}/h1_cv.csv")
ps = pd.read_csv(f"{RAW}/h1_pseudo.csv")
led = pd.read_csv(f"{V2}/ledger/h1.csv")
summ = json.load(open(f"{V2}/results/h1_summary.json"))

print("counts per (dataset,variant,model,scheme):")
cnt = cv.groupby(["dataset", "variant", "model", "scheme"]).seed.nunique()
print("  min seeds", cnt.min(), "max", cnt.max(), "n cells", len(cnt))
print("  pseudo seeds per unit:", ps.groupby(["dataset", "variant"]).pseudo_seed.nunique().to_dict())

out = []
for (d, v), sub in cv.groupby(["dataset", "variant"]):
    mr = sub.groupby(["model", "scheme"]).rmse.mean()
    gaps = {m: mr[(m, "group")] / mr[(m, "random")] - 1 for m in ["RF", "GB", "KNN"]}
    rf_rand = mr[("RF", "random")]
    pg = ps[(ps.dataset == d) & (ps.variant == v)].rmse / rf_rand - 1
    p95 = np.percentile(pg, 95)
    c1, c2, c3 = gaps["RF"] >= 0.2, gaps["RF"] > p95, max(gaps["GB"], gaps["KNN"]) >= 0.1
    verdict = "PASS" if c1 and c2 and c3 else "FAIL"
    dname = d if v == "raw" else d + "_lineage"
    lv = led[(led.dataset == dname) & (led.test_id == "H1_dataset")].verdict.iloc[0]
    lgap = float(led[(led.dataset == dname) & (led.test_id == "H1_rf_gap")].value.iloc[0])
    # per-seed RF gap with group vs random of same seed: is every seed above 0.2 and above pseudo p95?
    pv = sub[sub.model == "RF"].pivot_table(index="seed", columns="scheme", values="rmse")
    sg = pv.group / pv.random - 1
    out.append(dict(ds=dname, rf=round(gaps["RF"], 4), ledger_rf=lgap, gb=round(gaps["GB"], 3), knn=round(gaps["KNN"], 3),
                    p95=round(p95, 4), pmax=round(pg.max(), 4), min_seed_gap=round(sg.min(), 3), c=f"{int(c1)}{int(c2)}{int(c3)}",
                    verdict=verdict, ledger=lv, match=verdict == lv))
print(pd.DataFrame(out).to_string())
raw7 = [o for o in out if not o["ds"].endswith("_lineage")]
n = sum(o["verdict"] == "PASS" for o in raw7)
print("overall raw:", n, "/", len(raw7), "->", "PASS" if n >= 5 else ("FAIL" if n <= 3 else "PARTIAL"),
      "| ledger:", led[led.test_id == "H1_overall"].verdict.iloc[0])

# ---- fold grouping check: regenerate group folds as h1 does and verify no source straddles train/test
from vrr_data import load
from vrr_common import group_folds, random_folds, copy_mask, subset
for name in ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]:
    ds = load(name)
    bad = 0
    for seed in range(5):
        folds = group_folds(ds.group, 10, seed)
        seen = np.zeros(len(ds.y), int)
        for tr, te in folds:
            seen[te] += 1
            if set(ds.group[tr]) & set(ds.group[te]):
                bad += 1
        assert (seen == 1).all()
    print(f"{name}: n={len(ds.y)} sources={len(set(ds.group))} folds k={len(folds)} straddling folds={bad}")

# ---- RMSE recompute from stored per-seed predictions (parts)
PARTS = os.path.join(RAW, "h1_parts")
mx = 0
for f in sorted(glob.glob(f"{PARTS}/*__pred_*.csv.gz")):
    pr = pd.read_csv(f)
    d, v = pr.dataset.iloc[0], pr.variant.iloc[0]
    meta = pd.read_csv(f"{PARTS}/{d}__{v}__meta.csv.gz")
    pr = pr.merge(meta[["row", "y"]], on="row")
    r = pr.groupby(["model", "seed", "scheme"]).apply(lambda z: np.sqrt(np.mean((z.pred - z.y) ** 2)), include_groups=False)
    for (m, s, sch), val in r.items():
        ref = cv[(cv.dataset == d) & (cv.variant == v) & (cv.model == m) & (cv.seed == s) & (cv.scheme == sch)].rmse.iloc[0]
        mx = max(mx, abs(val / ref - 1))
print("max rel diff RMSE recomputed from stored preds vs h1_cv.csv:", mx)
