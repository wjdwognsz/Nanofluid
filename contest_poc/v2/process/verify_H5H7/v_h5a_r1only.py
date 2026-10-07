"""Verifier: H5a UNIT recovery when only R1 (per-row physical range, no cross-row/test-fold information) is used as the filter.
Same injection seeds as the family (0..), same folds/RF seed. Usage: DATASET ETYPE seed_lo seed_hi"""
import sys, time, os, numpy as np, pandas as pd
sys.path.insert(0, '/home/user/Nanofluid/contest_poc/v2/scripts')
from h5_audit import base_ds, inject, fold_map, folds_from_map, cv_pred, PARTS
from vrr_audit import rule_r1, CFG, family
from vrr_common import rmse
name, et, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
ds = base_ds(name); n = len(ds.y); orig = np.load(os.path.join(PARTS, f'orig_pred_{name}.npy')); fmap = fold_map(ds)
fam = pd.read_csv('/home/user/Nanofluid/contest_poc/v2/results/raw/h5_injection.csv')
rows = []
for seed in range(lo, hi + 1):
    t0 = time.time()
    di, inj, _ = inject(ds, et, seed)
    r1y, r1t = rule_r1(di, CFG[family(di.name)]); r1 = r1y | r1t
    folds = folds_from_map(di.group, fmap)
    p_inj = cv_pred(di.X, di.y, folds, seed=0)
    p_r1 = cv_pred(di.X, di.y, folds, train_mask=~r1, seed=0)
    clean = ~inj[:n]
    fr = fam[(fam.dataset == name) & (fam.etype == et) & (fam.seed == seed)].iloc[0]
    rows.append(dict(seed=seed, rmse_orig=rmse(ds.y[clean], orig[clean]), rmse_inj=rmse(ds.y[clean], p_inj[:n][clean]),
                     rmse_filt_R1=rmse(ds.y[clean], p_r1[:n][clean]), fam_rmse_inj=fr.rmse_inj, fam_rmse_filt=fr.rmse_filt,
                     n_R1=int(r1.sum()), tp_R1=int((r1 & inj).sum()), fam_tp_R1=int(fr.tp_R1)))
    print(rows[-1], f'{time.time()-t0:.0f}s', flush=True)
d = pd.DataFrame(rows); d.to_csv(f'/home/user/Nanofluid/contest_poc/v2/process/verify_H5H7/h5a_r1only_{name}_{et}.csv', index=False)
print('recovery R1-only = %.3f' % ((d.rmse_inj.mean() - d.rmse_filt_R1.mean()) / (d.rmse_inj.mean() - d.rmse_orig.mean())))
