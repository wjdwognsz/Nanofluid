"""Verifier: H5a re-run with NEW injection seeds (does not write into results/). Usage: DATASET ETYPE seed_lo seed_hi"""
import sys, time, numpy as np, pandas as pd, os
sys.path.insert(0, '/home/user/Nanofluid/contest_poc/v2/scripts')
from h5_audit import base_ds, inject, fold_map, folds_from_map, cv_pred, mean_source_rmse, DESIGNATED, PARTS
from vrr_audit import audit
from vrr_common import rmse
name, et, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
OUT = f'/home/user/Nanofluid/contest_poc/v2/process/verify_H5H7/h5a_reseed_{name}_{et}.csv'
ds = base_ds(name); n = len(ds.y)
orig = np.load(os.path.join(PARTS, f'orig_pred_{name}.npy'))
fmap = fold_map(ds)
rows = pd.read_csv(OUT).to_dict('records') if os.path.exists(OUT) else []
for seed in range(lo, hi + 1):
    t0 = time.time()
    di, inj, _ = inject(ds, et, seed)
    fl = audit(di)
    folds = folds_from_map(di.group, fmap)
    p_inj = cv_pred(di.X, di.y, folds, seed=0)
    p_f = cv_pred(di.X, di.y, folds, train_mask=~fl['any'].values, seed=0)
    clean = ~inj[:n]
    des = fl[DESIGNATED[et]].values
    r = dict(seed=seed, recall=(des & inj).sum() / inj.sum(), precision=(des & inj).sum() / max(des.sum(), 1),
             prec_R1=(fl.R1.values & inj).sum() / max(fl.R1.sum(), 1), rec_R1=(fl.R1.values & inj).sum() / inj.sum(),
             rmse_orig=rmse(ds.y[clean], orig[clean]), rmse_inj=rmse(ds.y[clean], p_inj[:n][clean]),
             rmse_filt=rmse(ds.y[clean], p_f[:n][clean]),
             msrc_orig=mean_source_rmse(ds.y, orig, ds.group, clean), msrc_inj=mean_source_rmse(ds.y, p_inj[:n], ds.group, clean),
             msrc_filt=mean_source_rmse(ds.y, p_f[:n], ds.group, clean), sec=round(time.time() - t0, 1))
    rows.append(r); pd.DataFrame(rows).to_csv(OUT, index=False)
    print(name, et, r, flush=True)
