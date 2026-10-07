"""PoC-4: 'virtual round-robin' + anchor (reference-sample) calibration on Cogni-e-SpinDB.
(a) variance decomposition of out-of-paper residuals (paper share)
(b) leave-one-paper-out: base model -> k anchor records from the new paper -> offset correction
    compared with simply pooling anchors into training; 30 random anchor draws; bootstrap CI over papers.
Usage: python poc_anchor.py <cogni.csv> <outdir>
"""
import json
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

sys.argv_backup = list(sys.argv)
SRC, OUT = sys.argv[1], sys.argv[2]
# reuse the harmonized feature construction from poc_electrospin.py
import importlib.util
spec = importlib.util.spec_from_file_location("es", "poc_electrospin_features.py")
es = importlib.util.module_from_spec(spec)
sys.argv = ["x", SRC]
spec.loader.exec_module(es)
d, X, y, doi, poly = es.d, es.X, es.y, es.doi, es.poly


def rf(seed=0):
    return RandomForestRegressor(n_estimators=150, max_features=0.5, min_samples_leaf=2, n_jobs=4, random_state=seed)


papers = pd.Series(doi).value_counts()
targets = papers[papers >= 8].index.tolist()
KS = [0, 1, 2, 3, 5]
R = 30
rec = []
lopo_bias, within_var = {}, {}
for p in targets:
    te = doi == p
    base = rf(1).fit(X[~te], y[~te])
    pb_all = base.predict(X[te])
    idx = np.where(te)[0]
    res_all = y[te] - pb_all
    lopo_bias[p] = float(res_all.mean()); within_var[p] = float(res_all.var(ddof=1))
    for k in KS:
        for r in range(R if k else 1):
            rs = np.random.default_rng(1000 * r + k)
            loc = rs.choice(len(idx), size=k, replace=False) if k else np.array([], int)
            test_loc = np.setdiff1d(np.arange(len(idx)), loc)
            yt = y[idx[test_loc]]
            off = res_all[loc].mean() if k else 0.0
            pred_offset = pb_all[test_loc] + off
            methods = [("offset", pred_offset)]
            if k == 0:
                methods.append(("pooled", pb_all[test_loc]))
            elif r < 5:
                tr = np.concatenate([np.where(~te)[0], idx[loc]])
                methods.append(("pooled", rf(2).fit(X[tr], y[tr]).predict(X[idx[test_loc]])))
            for nm, pr in methods:
                rec.append(dict(paper=p, polymer=poly[te][0], n=int(te.sum()), k=k, rep=r, method=nm,
                                sse=float(np.sum((yt - pr) ** 2)), sst=float(np.sum((yt - y.mean()) ** 2)),
                                n_test=len(yt), mae=float(np.mean(np.abs(yt - pr)))))
    print(p[:40], te.sum(), "bias", round(lopo_bias[p], 3), flush=True)

df = pd.DataFrame(rec)
df.to_csv(f"{OUT}/anchor_records.csv", index=False)
# (a) variance decomposition of LOPO residuals: between-paper bias variance vs within
b = np.array(list(lopo_bias.values())); w = np.array(list(within_var.values()))
share = float(np.var(b, ddof=1) / (np.var(b, ddof=1) + np.mean(w)))
summary = {"n_papers_eval": len(targets), "paper_bias_share_of_LOPO_error": share,
           "median_abs_paper_bias_log10": float(np.median(np.abs(b))),
           "median_abs_paper_bias_fold": float(10 ** np.median(np.abs(b)))}
rng = np.random.default_rng(0)
for nm in ["offset", "pooled"]:
    for k in KS:
        g = df[(df.method == nm) & (df.k == k)].groupby("paper")[["sse", "n_test", "mae"]].mean()
        rmse = np.sqrt(g.sse.sum() / g.n_test.sum())
        boots = []
        pl = g.index.values
        for _ in range(2000):
            s = rng.choice(pl, len(pl))
            gg = g.loc[s]
            boots.append(np.sqrt(gg.sse.sum() / gg.n_test.sum()))
        summary[f"{nm}_k{k}"] = {"rmse": float(rmse), "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                                 "median_paper_mae": float(g.mae.median())}
# paired comparison offset vs k0 (per paper)
for k in KS[1:]:
    a = df[(df.method == "offset") & (df.k == k)].groupby("paper").sse.mean() / df[(df.method == "offset") & (df.k == k)].groupby("paper").n_test.mean()
    b0 = df[(df.method == "offset") & (df.k == 0)].groupby("paper").sse.mean() / df[(df.method == "offset") & (df.k == 0)].groupby("paper").n_test.mean()
    summary[f"frac_papers_improved_offset_k{k}"] = float(np.mean(a.loc[b0.index] < b0))
json.dump(summary, open(f"{OUT}/anchor_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
