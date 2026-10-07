"""Verifier: re-run the shared out-of-source predictions (same code path as h3_oof.py) for one seed.
Usage: python v6_oof_seed.py SEED DATASET [DATASET...]  -> verify_H2H3H6/oof_<DS>_s<SEED>.csv.gz"""
import os, sys, time
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import numpy as np, pandas as pd
from vrr_data import load
from vrr_common import make_model, group_folds, leak_mask_for_source
OUT = "/home/user/Nanofluid/contest_poc/v2/process/verify_H2H3H6"
sd = int(sys.argv[1])
for name in sys.argv[2:]:
    t0 = time.time(); ds = load(name); n = len(ds.y)
    leak = {s: leak_mask_for_source(ds, s) for s in pd.unique(ds.group)}
    p_rm = np.full(n, np.nan); p_keep = np.full(n, np.nan); fid = np.full(n, -1)
    for fi, (tr, te) in enumerate(group_folds(ds.group, 10, seed=sd)):
        fid[te] = fi
        lk = np.zeros(n, bool)
        for s in pd.unique(ds.group[te]): lk |= leak[s]
        trm = np.ones(n, bool); trm[te] = False
        mk = make_model("RF", sd).fit(ds.X[trm], ds.y[trm]); p_keep[te] = mk.predict(ds.X[te])
        if (lk & trm).any():
            p_rm[te] = make_model("RF", sd).fit(ds.X[trm & ~lk], ds.y[trm & ~lk]).predict(ds.X[te])
        else:
            p_rm[te] = p_keep[te]
    pd.DataFrame({"source": ds.group, "y": ds.y, "fold": fid, "p_rm": p_rm, "p_keep": p_keep}).to_csv(
        os.path.join(OUT, f"oof_{name}_s{sd}.csv.gz"), index=False)
    print(name, sd, f"{time.time()-t0:.1f}s", flush=True)
