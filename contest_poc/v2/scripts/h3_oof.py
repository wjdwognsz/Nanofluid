"""Shared out-of-source predictions for H2 / H3 / H6a (VRR v2).

Implements the residual definition of PREREG.md section 2:
  * H3a/H3b  "출처 밖 잔차 (GroupKFold 10, RF, 누수 복사본 제거)"  -> column p_rm_s0 (seed 0)
  * H2       RF source-CV R^2 to compare with R^2_ceiling          -> p_rm_s0..s4
  * H6a      source-level RMSE with copies kept vs removed          -> p_keep_s* vs p_rm_s*
Folds: vrr_common.group_folds(ds.group, 10, seed), model vrr_common.make_model("RF", seed), seeds 0-4.
  rm   = training excludes the test fold AND the union of leak_mask_for_source(ds, s) over the test-fold sources
  keep = training excludes only the test fold (copies of test sources stay in training)
If a fold has no leak rows, keep == rm (same rows, same seed), so the model is fitted once and reused.

Usage (from v2/scripts):  python h3_oof.py DATASET [DATASET ...]
Output: results/raw/h236_parts/oof_<DATASET>.csv.gz (one row per data row) and oof_<DATASET>_folds.csv (timings).
"""
import os
import sys
import time

import numpy as np
import pandas as pd

from vrr_data import load
from vrr_common import RAW, make_model, group_folds, leak_mask_for_source

SEEDS = [0, 1, 2, 3, 4]
K = 10
PARTS = os.path.join(RAW, "h236_parts")
os.makedirs(PARTS, exist_ok=True)


def run(name):
    t0 = time.time()
    ds = load(name)
    n = len(ds.y)
    srcs = pd.unique(ds.group)
    leak = {s: leak_mask_for_source(ds, s) for s in srcs}
    out = pd.DataFrame({"row": np.arange(n), "source": ds.group, "material": ds.material, "key": ds.key, "y": ds.y})
    out["n_leak_rows_of_source"] = pd.Series(ds.group).map({s: int(leak[s].sum()) for s in srcs}).values
    frec = []
    for sd in SEEDS:
        p_rm = np.full(n, np.nan)
        p_keep = np.full(n, np.nan)
        fold_id = np.full(n, -1)
        for fi, (tr, te) in enumerate(group_folds(ds.group, K, seed=sd)):
            fold_id[te] = fi
            lk = np.zeros(n, bool)
            for s in pd.unique(ds.group[te]):
                lk |= leak[s]
            trm = np.ones(n, bool)
            trm[te] = False
            n_leak = int((lk & trm).sum())
            t1 = time.time()
            m_keep = make_model("RF", sd).fit(ds.X[trm], ds.y[trm])
            p_keep[te] = m_keep.predict(ds.X[te])
            if n_leak:
                trr = trm & ~lk
                p_rm[te] = make_model("RF", sd).fit(ds.X[trr], ds.y[trr]).predict(ds.X[te])
            else:
                p_rm[te] = p_keep[te]
            frec.append(dict(dataset=name, seed=sd, fold=fi, n_test=len(te), n_test_sources=len(pd.unique(ds.group[te])),
                             n_train_keep=int(trm.sum()), n_leak_removed=n_leak, sec=round(time.time() - t1, 2)))
        out[f"fold_s{sd}"] = fold_id
        out[f"p_rm_s{sd}"] = p_rm
        out[f"p_keep_s{sd}"] = p_keep
        print(f"[{name}] seed {sd} done ({time.time() - t0:.1f}s)", flush=True)
    out.to_csv(os.path.join(PARTS, f"oof_{name}.csv.gz"), index=False)
    pd.DataFrame(frec).to_csv(os.path.join(PARTS, f"oof_{name}_folds.csv"), index=False)
    print(f"[{name}] n={n} total {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        run(nm)
