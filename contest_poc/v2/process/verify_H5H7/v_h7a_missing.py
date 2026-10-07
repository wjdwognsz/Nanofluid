"""Verifier (exploratory): H7a with missingness-indicator features removed (reporting-style confound check)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, '/home/user/Nanofluid/contest_poc/v2/scripts')
from vrr_data import load_es1_failure, ES1_FEATS
from h7_failure import oc_scores, sup_scores, fast_auc
ds = load_es1_failure('PVDF'); y, paper = ds.y.astype(int), ds.group
fps = sorted(set(paper[y == 1]))
df = pd.DataFrame(ds.X, columns=ES1_FEATS)
te_all = np.isin(paper, fps)
for c in ['needle_diameter_g_missing', 'temperature_c_missing', 'rh_missing']:
    print(c, 'fail rate when missing=1: %.3f (n=%d), missing=0: %.3f (n=%d)' % (
        y[df[c] == 1].mean() if (df[c] == 1).any() else np.nan, (df[c] == 1).sum(), y[df[c] == 0].mean(), (df[c] == 0).sum()))
drop = [i for i, f in enumerate(ES1_FEATS) if not f.endswith('_missing')]
drop2 = [i for i, f in enumerate(ES1_FEATS) if not f.startswith("needle_diameter_g")]
for label, cols in [("no needle_diameter (value+missing)", drop2)]:
    X = ds.X[:, cols]
    res = {m: [] for m in ['RF', 'HGB', 'IF', 'OCSVM', 'KNN5']}
    for seed in range(3):
        sc = {m: np.full(len(y), np.nan) for m in res}
        for p in fps:
            te = paper == p; tr = ~te
            for m in ['IF', 'OCSVM', 'KNN5']: sc[m][te] = oc_scores(m, X[tr & (y == 0)], X[te], seed)
            for m in ['RF', 'HGB']: sc[m][te] = sup_scores(m, X[tr], y[tr], X[te], seed)
        for m in res: res[m].append(fast_auc(y[te_all], sc[m][te_all]))
    print(label, {m: round(float(np.mean(v)), 4) for m, v in res.items()})
