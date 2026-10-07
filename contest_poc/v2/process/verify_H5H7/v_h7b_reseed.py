"""Verifier: re-run H7b supervised (RF, HGB) with new seeds 5-9 (new source folds), with and without leak-copy removal,
and the one-class models trained on the success-only reference (same as h7_failure.run_b). Writes per-seed AUCs."""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, '/home/user/Nanofluid/contest_poc/v2/scripts')
from vrr_data import load
from vrr_common import group_folds, leak_mask_for_source
from h7_failure import sup_scores, oc_scores, des_reference, fast_auc
OUT = '/home/user/Nanofluid/contest_poc/v2/process/verify_H5H7/h7b_reseed.csv'
t0 = time.time()
mp = load('DES_MP'); X, y, src = mp.X, (mp.y > 298.15).astype(int), mp.group
leak = {s: leak_mask_for_source(mp, s) for s in np.unique(src)}
ref = des_reference(mp.feats); Xr = ref[mp.feats].values.astype(float)
rows = []
seeds = [int(s) for s in sys.argv[1].split(',')]
for seed in seeds:
    for m in ['IF', 'OCSVM', 'KNN5']:
        rows.append(dict(seed=seed, model=m, variant='ref', auc=fast_auc(y, oc_scores(m, Xr, X, seed))))
    for lk_on in [False, True]:
        sc = {m: np.full(len(y), np.nan) for m in ['RF', 'HGB']}
        for tr, te in group_folds(src, 10, seed):
            if lk_on:
                lk = np.zeros(len(y), bool)
                for s in np.unique(src[te]): lk |= leak[s]
                tr = tr[~lk[tr]]
            for m in sc: sc[m][te] = sup_scores(m, X[tr], y[tr], X[te], seed)
        for m in sc:
            rows.append(dict(seed=seed, model=m, variant='leakrm' if lk_on else 'asis', auc=fast_auc(y, sc[m])))
    print(seed, f'{time.time()-t0:.0f}s', [ (r['model'], r['variant'], round(r['auc'],4)) for r in rows if r['seed']==seed], flush=True)
    pd.DataFrame(rows).to_csv(OUT.replace('.csv', f'_{"_".join(map(str,seeds))}.csv'), index=False)
