"""Verifier: recompute H7 AUCs and paper/source bootstrap CIs with several bootstrap seeds (reads raw h7_scores.csv)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, '/home/user/Nanofluid/contest_poc/v2/scripts')
from h7_failure import unit_boot, fast_auc, SUP, OC
from sklearn.metrics import roc_auc_score
sc = pd.read_csv('/home/user/Nanofluid/contest_poc/v2/results/raw/h7_scores.csv')
for case in ['H7a_PVDF', 'H7b_DES']:
    cs = sc[sc.case == case]
    m = cs.groupby(['model', 'seed']).apply(lambda g: roc_auc_score(g.y, g.score)).groupby('model').mean()
    print(case, 'rows/seed/model', cs.groupby(['model','seed']).size().unique(), 'pos', cs[(cs.model=='RF')&(cs.seed==0)].y.sum(),
          'units', cs.group.nunique())
    print(' sklearn seed-mean AUC', m.round(4).to_dict())
    bs, bo = m[SUP].idxmax(), m[OC].idxmax()
    print(' best', bs, bo, 'diff %.4f' % (m[bs] - m[bo]))
    for bseed in [0, 1, 2, 3, 4]:
        b = unit_boot(cs, [bs, bo], n=2000, seed=bseed)
        d = b[bs] - b[bo]; d = d[~np.isnan(d)]
        print('  bootseed', bseed, 'CI [%.4f, %.4f]' % (np.percentile(d, 2.5), np.percentile(d, 97.5)), 'P(diff<=0)=%.3f' % np.mean(d <= 0))
