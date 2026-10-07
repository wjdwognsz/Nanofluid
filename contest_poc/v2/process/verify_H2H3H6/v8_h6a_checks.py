"""Verifier: H6a robustness. (a) seed-11 change; (b) exclude dominant compilation source from evaluation;
(c) random-removal control (DES_RHO, DES_ETA seed 0): drop as many RANDOM non-leak training rows as there are leak rows
    -> isolates 'less training data' from 'copies of the test rows'."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
from vrr_common import make_model, group_folds, leak_mask_for_source, rmse
P = "/home/user/Nanofluid/contest_poc/v2/results/raw/"; V = "/home/user/Nanofluid/contest_poc/v2/process/verify_H2H3H6/"
mode = sys.argv[1]
if mode == "stats":
    for name in ["DES_RHO", "DES_ETA"]:
        o = pd.read_csv(V + f"oof_{name}_s11.csv.gz")
        ch = rmse(o.y, o.p_keep) / rmse(o.y, o.p_rm) - 1
        se_k = (o.y - o.p_keep) ** 2; se_r = (o.y - o.p_rm) ** 2
        t = pd.DataFrame({"g": o.source, "k": se_k, "r": se_r}).groupby("g").sum()
        rs = np.random.default_rng(99); bs = []
        for _ in range(2000):
            ix = rs.integers(0, len(t), len(t)); bs.append(np.sqrt(t.k.values[ix].sum() / t.r.values[ix].sum()) - 1)
        print(name, "seed11 change", round(ch, 4), "source-boot CI", np.round(np.percentile(bs, [2.5, 97.5]), 4))
        l = pd.read_csv(P + "h6_leak.csv"); l = l[l.dataset == name]
        big = l.sort_values("n_rows").iloc[-1]
        r = l[l.source != big.source]
        print("   seed0-4 pooled change excluding largest source", big.source, f"({int(big.n_rows)} rows, change {big.change:+.3f}):",
              round(np.sqrt(r.sse_keep.sum() / r.sse_rm.sum()) - 1, 4))
else:
    name = mode; sd = 0
    ds = load(name); n = len(ds.y)
    leak = {s: leak_mask_for_source(ds, s) for s in pd.unique(ds.group)}
    p_ctrl = np.full(n, np.nan)
    rng = np.random.default_rng(2024)
    for fi, (tr, te) in enumerate(group_folds(ds.group, 10, seed=sd)):
        lk = np.zeros(n, bool)
        for s in pd.unique(ds.group[te]): lk |= leak[s]
        trm = np.ones(n, bool); trm[te] = False
        nl = int((lk & trm).sum())
        cand = np.where(trm & ~lk)[0]
        drop = rng.choice(cand, size=min(nl, len(cand) - 1), replace=False) if nl else np.array([], int)
        trc = trm.copy(); trc[drop] = False   # leak rows KEPT, random rows removed
        p_ctrl[te] = make_model("RF", sd).fit(ds.X[trc], ds.y[trc]).predict(ds.X[te])
    o = pd.read_csv(P + f"h236_parts/oof_{name}.csv.gz")
    rk, rr, rc = rmse(ds.y, o.p_keep_s0), rmse(ds.y, o.p_rm_s0), rmse(ds.y, p_ctrl)
    print(name, f"seed0 RMSE keep {rk:.5f} | rm(leak removed) {rr:.5f} | control(random rows removed, copies kept) {rc:.5f}")
    print("   keep/rm-1", round(rk / rr - 1, 4), "| keep/control-1", round(rk / rc - 1, 4), "| control/rm-1", round(rc / rr - 1, 4))
