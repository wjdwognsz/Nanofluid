"""Verifier (exploratory controls for H9 condition C3). Copy of h9_conformal.run() logic for ONE seed with extras:
  * reproduces the family's q_naive/q_aware/q_anchor and anchor coverage (same RNG streams) -> consistency check
  * control A 'aware8': aware quantile from calibration sources with >=8 rows only, NO offset
        (is the width gain from the anchor offset or merely from restricting calibration to >=8-row sources?)
  * control B 'anchor_md': anchors + evaluation restricted to non-anchor rows whose material differs from all anchor
        materials, with q' recalibrated by the same material-disjoint simulation on calibration sources
Writes only to process/verify_H1H9/. Usage: python v7_h9_controls.py DATASET SEED"""
import sys, time, json
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
from vrr_common import make_model, random_folds, group_folds, leak_mask_for_source
from h9_conformal import conformal_q, union_leak

name, seed = sys.argv[1], int(sys.argv[2])
ds = load(name)
X, y, G = ds.X, ds.y, np.asarray(ds.group).astype(str)
M = np.asarray(ds.material).astype(str)
leak = {s: leak_mask_for_source(ds, s) for s in np.unique(G)}
t0 = time.time()
acc = {k: [0, 0, 0.0] for k in ["naive", "aware", "anchor", "aware_on_anchor_rows", "aware8_on_anchor_rows",
                                 "anchor_md", "aware_on_md_rows"]}
md_sources = set()
for f, (tr, te) in enumerate(group_folds(G, 10, seed)):
    tr = tr[~union_leak(leak, np.unique(G[te]), tr)]
    Xtr, ytr, gtr, mtr = X[tr], y[tr], G[tr], M[tr]
    e = y[te] - make_model("RF", seed).fit(Xtr, ytr).predict(X[te])
    r_naive = np.full(len(tr), np.nan)
    for itr, ite in random_folds(len(tr), 5, seed):
        r_naive[ite] = ytr[ite] - make_model("RF", seed).fit(Xtr[itr], ytr[itr]).predict(Xtr[ite])
    r_aware = np.full(len(tr), np.nan)
    for itr, ite in group_folds(gtr, 10, seed):
        itr = itr[~union_leak(leak, np.unique(gtr[ite]), tr[itr])]
        r_aware[ite] = ytr[ite] - make_model("RF", seed).fit(Xtr[itr], ytr[itr]).predict(Xtr[ite])
    q_n, q_a = conformal_q(np.abs(r_naive)), conformal_q(np.abs(r_aware))
    rng1 = np.random.default_rng([seed, f, 1])
    sc, sc_md, big = [], [], []
    for s in sorted(np.unique(gtr)):
        idx = np.where(gtr == s)[0]
        if len(idx) < 8:
            continue
        r, ms = r_aware[idx], mtr[idx]
        big.append(np.abs(r))
        for _ in range(10):
            a = rng1.choice(len(idx), 3, replace=False)
            na = np.ones(len(idx), bool); na[a] = False
            sc.append(np.abs(r[na] - r[a].mean()))
            md = na & ~np.isin(ms, ms[a])
            sc_md.append(np.abs(r[md] - r[a].mean()))
    q_x = conformal_q(np.concatenate(sc))
    q_8 = conformal_q(np.concatenate(big))
    smd = np.concatenate(sc_md)
    q_md = conformal_q(smd) if len(smd) >= 20 else np.nan
    gte, mte = G[te], M[te]
    for k, q in (("naive", q_n), ("aware", q_a)):
        acc[k][0] += int((np.abs(e) <= q).sum()); acc[k][1] += len(e); acc[k][2] += 2 * q * len(e)
    rng2 = np.random.default_rng([seed, f, 2])
    for s in sorted(np.unique(gte)):
        idx = np.where(gte == s)[0]
        if len(idx) < 8:
            continue
        es, ms = e[idx], mte[idx]
        for _ in range(10):
            a = rng2.choice(len(idx), 3, replace=False)
            na = np.ones(len(idx), bool); na[a] = False
            off = es[a].mean()
            md = na & ~np.isin(ms, ms[a])
            k_na, k_md = int(na.sum()), int(md.sum())
            for k, cov, m, q in (("anchor", np.abs(es - off) <= q_x, na, q_x),
                                 ("aware_on_anchor_rows", np.abs(es) <= q_a, na, q_a),
                                 ("aware8_on_anchor_rows", np.abs(es) <= q_8, na, q_8),
                                 ("anchor_md", np.abs(es - off) <= q_md, md, q_md),
                                 ("aware_on_md_rows", np.abs(es) <= q_a, md, q_a)):
                acc[k][0] += int(cov[m].sum()); acc[k][1] += int(m.sum()); acc[k][2] += 2 * q * int(m.sum())
            if k_md:
                md_sources.add(s)
    print(f"  fold {f}: q_n {q_n:.4g} q_a {q_a:.4g} q_x {q_x:.4g} q_aware8 {q_8:.4g} q_md {q_md:.4g} "
          f"(n_md_cal_scores {len(smd)}) {time.time()-t0:.0f}s", flush=True)
res = {k: dict(coverage=round(v[0] / v[1], 4) if v[1] else None, mean_width=round(v[2] / v[1], 5) if v[1] else None,
               n_evals=v[1]) for k, v in acc.items()}
res["ratio_anchor_vs_aware_same_rows"] = round(res["anchor"]["mean_width"] / res["aware_on_anchor_rows"]["mean_width"], 4)
res["ratio_aware8_vs_aware_same_rows"] = round(res["aware8_on_anchor_rows"]["mean_width"] / res["aware_on_anchor_rows"]["mean_width"], 4)
if res["anchor_md"]["n_evals"]:
    res["ratio_anchor_md_vs_aware_md_rows"] = round(res["anchor_md"]["mean_width"] / res["aware_on_md_rows"]["mean_width"], 4)
res["n_sources_with_md_rows"] = len(md_sources)
print(json.dumps({name: {"seed": seed, **res}}, indent=1))
json.dump(res, open(f"/home/user/Nanofluid/contest_poc/v2/process/verify_H1H9/v7_{name}_seed{seed}.json", "w"), indent=1)
