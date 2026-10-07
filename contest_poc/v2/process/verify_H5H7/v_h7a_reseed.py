"""Verifier: H7a re-run with seeds 5-9 (same procedure as h7_failure.run_a) + cross-paper duplicate-key check."""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, '/home/user/Nanofluid/contest_poc/v2/scripts')
from vrr_data import load_es1_failure
from h7_failure import oc_scores, sup_scores, fast_auc, unit_boot
t0 = time.time()
ds = load_es1_failure('PVDF'); X, y, paper = ds.X, ds.y.astype(int), ds.group
fps = sorted(set(paper[y == 1]))
# duplicate check: does a failure-paper test row share key (or identical feature vector) with a row in another paper?
key = pd.Series(ds.key); P = pd.Series(paper)
dupk = dupx = 0; dupx_samelab = 0
Xr = np.round(X, 6)
for p in fps:
    te = np.where(paper == p)[0]; tr = np.where(paper != p)[0]
    ktr = set(key[tr]); dupk += sum(k in ktr for k in key[te])
    xtr = {tuple(r): y[i] for i, r in zip(tr, Xr[tr])}
    for i in te:
        t = tuple(Xr[i])
        if t in xtr:
            dupx += 1; dupx_samelab += int(xtr[t] == y[i])
print('test rows', int(np.isin(paper, fps).sum()), 'with same key in another paper', dupk, 'identical X in another paper', dupx, 'of which same label', dupx_samelab)
rows = []
for seed in range(5, 10):
    for p in fps:
        te = paper == p; tr = ~te
        sc = {m: oc_scores(m, X[tr & (y == 0)], X[te], seed) for m in ['IF', 'OCSVM', 'KNN5']}
        sc.update({m: sup_scores(m, X[tr], y[tr], X[te], seed) for m in ['RF', 'HGB']})
        idx = np.where(te)[0]
        for m, s in sc.items():
            rows += [('H7a_PVDF', m, seed, int(i), p, int(y[i]), float(v)) for i, v in zip(idx, s)]
df = pd.DataFrame(rows, columns=['case', 'model', 'seed', 'row', 'group', 'y', 'score'])
df.to_csv('/home/user/Nanofluid/contest_poc/v2/process/verify_H5H7/h7a_reseed_scores.csv.gz', index=False)
au = df.groupby(['model', 'seed']).apply(lambda g: fast_auc(g.y.values, g.score.values)).unstack()
print(au.round(4)); m = au.mean(1); print(m.round(4).to_dict())
bs, bo = m[['RF', 'HGB']].idxmax(), m[['IF', 'OCSVM', 'KNN5']].idxmax()
b = unit_boot(df, [bs, bo], n=2000, seed=0); d = b[bs] - b[bo]; d = d[~np.isnan(d)]
print('best', bs, bo, 'diff %.4f CI [%.4f, %.4f]' % (m[bs] - m[bo], np.percentile(d, 2.5), np.percentile(d, 97.5)), f'{time.time()-t0:.0f}s')
