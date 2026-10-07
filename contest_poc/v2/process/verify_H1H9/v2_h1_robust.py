"""Verifier: H1 robustness — (a) gap excluding physically implausible y rows (PREREG H5 R1 ranges);
(b) gap with source-level jackknife (drop each source; min over sources) ; (c) top-1 share check from summary."""
import os, sys, json
import numpy as np, pandas as pd
V2 = "/home/user/Nanofluid/contest_poc/v2"
PARTS = os.path.join(V2, "results/raw/h1_parts")
summ = json.load(open(f"{V2}/results/h1_summary.json"))

def load_pred(d, v, tag):
    pr = pd.read_csv(f"{PARTS}/{d}__{v}__pred_{tag}.csv.gz")
    meta = pd.read_csv(f"{PARTS}/{d}__{v}__meta.csv.gz")
    return pr.merge(meta[["row", "source", "y"]], on="row")

units = {("ES1", "raw"): "RF-GB-KNN", ("ES2", "raw"): "RF-GB-KNN", ("DYE", "raw"): "RF-GB-KNN", ("DES_RHO", "raw"): "RF",
         ("DES_ETA", "raw"): "RF", ("DES_MP", "raw"): "RF-GB-KNN", ("IL_CELL", "raw"): "RF-GB-KNN",
         ("DES_RHO", "lineage"): "RF-GB-KNN", ("DES_ETA", "lineage"): "RF-GB-KNN"}
# implausible ranges (H5 R1): density 0.5-3.0 g/cm3; viscosity 0.2 cP - 1e7 cP (y is log10 cP)
plaus = {"DES_RHO": lambda y: (y >= 0.5) & (y <= 3.0), "DES_ETA": lambda y: (y >= np.log10(0.2)) & (y <= 7)}
rows = []
for (d, v), tag in units.items():
    pr = load_pred(d, v, tag)
    pr = pr[pr.model == "RF"]
    pr["se"] = (pr.pred - pr.y) ** 2
    se = pr.groupby(["scheme", "row", "source", "y"]).se.mean().reset_index()
    g = se[se.scheme == "group"].sort_values("row").reset_index(drop=True)
    r = se[se.scheme == "random"].sort_values("row").reset_index(drop=True)
    base = np.sqrt(g.se.sum() / r.se.sum()) - 1
    res = dict(unit=f"{d}/{v}", gap_rmse_of_meanSE=round(base, 3))
    if d in plaus:
        ok = plaus[d](g.y.values)
        res["n_implausible"] = int((~ok).sum())
        res["gap_plausible_only"] = round(np.sqrt(g.se[ok].sum() / r.se[ok].sum()) - 1, 3)
    # source jackknife: drop each source
    G = g.groupby("source").se.sum(); R = r.groupby("source").se.sum()
    jk = np.sqrt((G.sum() - G) / (R.sum() - R)) - 1
    res["jk_min_gap"] = round(jk.min(), 3); res["jk_min_source"] = jk.idxmin()
    # drop top-3 sources by group SE
    top3 = G.sort_values(ascending=False).index[:3]
    res["gap_wo_top3"] = round(np.sqrt(G.drop(top3).sum() / R.drop(top3).sum()) - 1, 3)
    # median per-source ratio and share worse
    ratio = np.sqrt(G / g.groupby("source").size()) / np.sqrt(R / r.groupby("source").size())
    res["median_src_ratio"] = round(ratio.median(), 3)
    res["share_src_worse"] = round((ratio > 1).mean(), 3)
    rows.append(res)
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).to_string())
for k in ["DYE", "DES_RHO"]:
    s = summ["datasets"][k]
    print(k, {x: s[x] for x in ["rf_top1_source_share_of_group_SE", "rf_gap_without_top1_source", "rf_top1_source_n_rows",
                                 "rf_source_avg_gap", "rf_median_source_ratio_group_random"]})
