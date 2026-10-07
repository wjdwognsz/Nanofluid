"""Verifier check 5: (a) independence of bootstrap units -- eligible sources linked by copy relations (vrr_common.copy_relations)
are merged into clusters (connected components) and the k=3 CI is recomputed with a cluster bootstrap;
(b) recompute pooled gap closure from the per-source table + prep.npz random-CV predictions.
Usage: python v5_units_gap.py DATASET [...]"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
from vrr_common import copy_relations, rmse

RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
PS = pd.read_csv(f"{RAW}/h4_anchor_per_source.csv", keep_default_na=False, na_values=["", "NaN"]); PS["source"] = PS.source.astype(str)
CU = pd.read_csv(f"{RAW}/h4_curves.csv")
for name in sys.argv[1:]:
    ds = load(name)
    ps = PS[PS.dataset == name]
    elig = sorted(ps.source.unique())
    cr = copy_relations(ds)
    cr = cr[cr.copy_relation & cr.s1.isin(elig) & cr.s2.isin(elig)] if len(cr) else cr
    # connected components
    par = {s: s for s in elig}
    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for a, b in zip(cr.s1, cr.s2):
        par[f(a)] = f(b)
    cl = {s: f(s) for s in elig}
    ncl = len(set(cl.values()))
    out = [f"{name}: {len(elig)} eligible sources, {len(cr)} copy-related eligible pairs -> {ncl} clusters"]
    for m in ("OFF", "SHR"):
        v = ps[(ps.method == m) & (ps.k == 3)].set_index("source").draw_mean_rel_change
        c = pd.Series(cl).loc[v.index]
        groups = [v[c == u].values for u in c.unique()]
        rs = np.random.default_rng(0); bs = []
        for _ in range(2000):
            pick = rs.integers(0, len(groups), len(groups))
            allv = np.concatenate([groups[i] for i in pick]); bs.append(allv.mean())
        out.append(f"  {m} k3 mean {v.mean():+.4f} cluster-bootstrap CI [{np.percentile(bs, 2.5):+.4f},{np.percentile(bs, 97.5):+.4f}]")
    # gap closure recompute (pooled) for SHR k3
    z = np.load(f"{RAW}/h4_parts/{name}/prep.npz", allow_pickle=True)
    em = np.isin(ds.group.astype(str), elig)
    rand_pool = np.mean([rmse(ds.y[em], z["p_rand"][em, j]) for j in range(z["p_rand"].shape[1])])
    for m in ("OFF", "SHR"):
        sub = ps[(ps.method == m) & (ps.k == 3)]
        r0 = np.sqrt(sub.sse0_mean.sum() / sub.n_test.sum()); rk = np.sqrt(sub.ssek_mean.sum() / sub.n_test.sum())
        cu = CU[(CU.dataset == name) & (CU.method == m) & (CU.k == 3) & (CU.scope == "all_eligible")].iloc[0]
        out.append(f"  gap closure {m} k3 pooled: mine {(r0 - rk) / (r0 - rand_pool):+.3f} vs file {cu.gap_closure_pooled:+.3f} "
                   f"(RMSE0 {r0:.4g}, RMSEk {rk:.4g}, randCV {rand_pool:.4g})")
    print("\n".join(out), flush=True)
