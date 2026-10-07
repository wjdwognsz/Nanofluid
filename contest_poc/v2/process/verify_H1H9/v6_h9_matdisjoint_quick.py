"""Verifier (exploratory): with the family's q' and the same anchor draws, coverage of anchor-adjusted intervals on
non-anchor rows whose MATERIAL differs from all 3 anchor materials (anchors = random rows may share material with
evaluated rows, e.g. same DES at another temperature)."""
import sys
import numpy as np, pandas as pd
V2 = "/home/user/Nanofluid/contest_poc/v2"
sys.path.insert(0, f"{V2}/scripts")
from vrr_data import load
rows = pd.read_csv(f"{V2}/results/raw/h9_rows.csv.gz")
out = []
for d in ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]:
    ds = load(d)
    mat = np.asarray(ds.material).astype(str)
    r = rows[rows.dataset == d]
    tot = {"all": [0, 0], "md": [0, 0], "same": [0, 0], "md_aware": [0, 0]}
    for (seed, f), g in r.groupby(["seed", "fold"], sort=True):
        gte, eg, mg = g.source.values, (g.y - g.pred).values, mat[g.row.values]
        qx, qa = g.q_anchor.iloc[0], g.q_aware.iloc[0]
        rng2 = np.random.default_rng([int(seed), int(f), 2])
        for s in sorted(np.unique(gte)):
            idx = np.where(gte == s)[0]
            if len(idx) < 8:
                continue
            es, ms = eg[idx], mg[idx]
            for _ in range(10):
                a = rng2.choice(len(idx), 3, replace=False)
                na = np.ones(len(idx), bool); na[a] = False
                off = es[a].mean()
                cov = np.abs(es - off) <= qx
                md = na & ~np.isin(ms, ms[a])
                same = na & np.isin(ms, ms[a])
                for k, m in (("all", na), ("md", md), ("same", same)):
                    tot[k][0] += int(cov[m].sum()); tot[k][1] += int(m.sum())
                tot["md_aware"][0] += int((np.abs(es[md]) <= qa).sum()); tot["md_aware"][1] += int(md.sum())
    out.append(dict(ds=d, anchor_cov_all=round(tot["all"][0] / tot["all"][1], 4),
                    share_eval_rows_sharing_anchor_material=round(tot["same"][1] / tot["all"][1], 3),
                    anchor_cov_material_disjoint=round(tot["md"][0] / max(1, tot["md"][1]), 4),
                    anchor_cov_same_material=round(tot["same"][0] / max(1, tot["same"][1]), 4),
                    aware_cov_material_disjoint=round(tot["md_aware"][0] / max(1, tot["md_aware"][1]), 4)))
pd.set_option("display.width", 250)
print(pd.DataFrame(out).to_string())
