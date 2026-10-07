"""Verifier: H9 recompute from h9_rows.csv.gz (+ independent replication of the anchor draws) and verdict check."""
import os, sys, json, math
import numpy as np, pandas as pd
V2 = "/home/user/Nanofluid/contest_poc/v2"
RAW = f"{V2}/results/raw"
rows = pd.read_csv(f"{RAW}/h9_rows.csv.gz")
conf = pd.read_csv(f"{RAW}/h9_conformal.csv")
pers = pd.read_csv(f"{RAW}/h9_per_source.csv")
led = pd.read_csv(f"{V2}/ledger/h9.csv")
summ = json.load(open(f"{V2}/results/h9_summary.json"))
sys.path.insert(0, f"{V2}/scripts")
from vrr_data import load

out = []
for d in ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]:
    r = rows[rows.dataset == d]
    ds = load(d)
    n = len(ds.y)
    # structure: each row once per seed, each source in exactly one fold per seed
    per_seed_rows = r.groupby("seed").row.agg(["size", "nunique"])
    assert (per_seed_rows["size"] == n).all() and (per_seed_rows["nunique"] == n).all(), d
    assert (r.groupby(["seed", "source"]).fold.nunique() == 1).all(), d
    # y matches loader
    yy = ds.y[r.row.values]
    ymax = np.max(np.abs(yy - r.y.values) / np.maximum(1e-9, np.abs(yy)))
    src_ok = (np.asarray(ds.group).astype(str)[r.row.values] == r.source.values).all()
    e = (r.y - r.pred).values
    cov_n = (np.abs(e) <= r.q_naive.values).mean()
    cov_a = (np.abs(e) <= r.q_aware.values).mean()
    # replicate anchors
    cov_x, n_x, cov_sx, wx, wa = 0, 0, 0, 0.0, 0.0
    persrc = {}
    for (seed, f), g in r.groupby(["seed", "fold"], sort=True):
        g = g  # file order = te order
        gte = g.source.values
        eg = (g.y - g.pred).values
        qx, qa = g.q_anchor.iloc[0], g.q_aware.iloc[0]
        rng2 = np.random.default_rng([int(seed), int(f), 2])
        for s in sorted(np.unique(gte)):
            idx = np.where(gte == s)[0]
            if len(idx) < 8:
                continue
            es = eg[idx]
            for _ in range(10):
                a = rng2.choice(len(idx), 3, replace=False)
                na = np.ones(len(idx), bool); na[a] = False
                off = es[a].mean()
                c = int((np.abs(es[na] - off) <= qx).sum()); k = int(na.sum())
                cov_x += c; n_x += k; wx += 2 * qx * k; wa += 2 * qa * k
                cov_sx += int((np.abs(es[na]) <= qa).sum())
                pc = persrc.setdefault(s, [0, 0]); pc[0] += c; pc[1] += k
    cx = cov_x / n_x
    ratio = wx / wa
    sm = summ["datasets"][d]
    c1, c2, c3 = cov_n < 0.85, cov_a >= 0.87, (ratio <= 0.9) and (cx >= 0.87)
    psrc = pd.DataFrame(persrc, index=["c", "n"]).T
    out.append(dict(ds=d, y_maxrel=f"{ymax:.1e}", src_ok=src_ok, naive=round(cov_n, 4), naive_sum=round(sm["methods"]["naive"]["coverage"], 4),
                    aware=round(cov_a, 4), aware_sum=round(sm["methods"]["aware"]["coverage"], 4),
                    anchor=round(cx, 4), anchor_sum=round(sm["methods"]["anchor"]["coverage"], 4),
                    aware_same=round(cov_sx / n_x, 4), ratio=round(ratio, 4),
                    ratio_sum=round(sm["anchor_width_ratio_vs_aware_same_rows"]["value"], 4),
                    C=f"{int(c1)}{int(c2)}{int(c3)}", anchor_src_avg=round((psrc.c / psrc.n).mean(), 3),
                    n_leak_removed_mean=round(conf[(conf.dataset == d) & (conf.method == 'aware')].n_leak_removed.mean(), 1)))
pd.set_option("display.width", 250)
o = pd.DataFrame(out)
print(o.to_string())
C = {k: sum(int(x[i]) for x in o.C) for i, k in enumerate(["C1", "C2", "C3"])}
print("conditions:", C, "-> H9", "PASS" if C["C1"] >= 4 and C["C2"] >= 5 and C["C3"] >= 3 else "FAIL",
      "| ledger:", led[led.test_id == "H9_overall"].verdict.iloc[0])
# per-seed anchor coverage and ratio per dataset (stability across seeds)
cx = conf[conf.method == "anchor"].assign(cn=lambda z: z.coverage * z.n)
sx = conf[conf.method == "aware_on_anchor_rows"]
ps = cx.groupby(["dataset", "seed"]).apply(lambda z: z.cn.sum() / z.n.sum(), include_groups=False).unstack()
print("per-seed anchor coverage:\n", ps.round(3).to_string())
wr = (cx.assign(w=cx.width * cx.n).groupby(["dataset", "seed"]).w.sum() /
      sx.assign(w=sx.width * sx.n).groupby(["dataset", "seed"]).w.sum()).unstack()
print("per-seed width ratio:\n", wr.round(3).to_string())
