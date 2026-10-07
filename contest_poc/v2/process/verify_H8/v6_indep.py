"""Independent re-implementation (no h8_gate modelling functions) of cross-fitted source predictions and
nested scores for s_exp_He repeat 0, for 4 sources (TOP-chosen + PHYS + 2 permuted), compared to h8_scores.csv.
Also asserts that no test-fold polymer key is in the source training set for g[te]."""
import sys, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h8_gate as H  # only for the in-memory featurised data
TASKS, TARGETS, FEAT = H.load_all()
t, rep = "s_exp_He", 0
ser, parent = TARGETS[t]; tk = list(ser.index); y = ser.values
X = lambda ks: np.vstack([FEAT[k] for k in ks])
folds = list(KFold(5, shuffle=True, random_state=rep).split(np.arange(len(y))))
sc = pd.read_csv("/home/user/Nanofluid/contest_poc/v2/results/raw/h8_scores.csv")
sc = sc[(sc.target == t) & (sc.repeat == rep)]
pol = pd.read_csv("/home/user/Nanofluid/contest_poc/v2/results/raw/h8_policy.csv")
tops = pol[(pol.target == t) & (pol.repeat == rep) & (pol.policy == "TOP")].chosen_source.unique().tolist()
perms = {}
for i in range(10):
    b = H.PERM_BASES[i % 5]; B = TASKS[b]
    perms[f"PERM{i:02d}_{b}"] = pd.Series(np.random.default_rng(500 + i).permutation(B.values), index=B.index)
srcs = tops[:2] + [H.PHYS[t], "PERM00_p_exp_O2", "PERM03_X_CED"]
for s in srcs:
    S = perms.get(s, TASKS.get(s))
    g = np.zeros(len(y))
    for tr, te in folds:
        excl = {tk[i] for i in te}
        sk = [k for k in S.index if k not in excl]
        assert not (set(sk) & excl)
        m = RandomForestRegressor(n_estimators=100, max_features=0.2, n_jobs=1, random_state=11).fit(X(sk), S.loc[sk].values)
        g[te] = m.predict(X([tk[i] for i in te]))
    for f, (tr, te) in enumerate(folds):
        mine = abs(np.corrcoef(g[tr], y[tr])[0, 1])
        theirs = sc[(sc.fold == f) & (sc.source == s)].score.iloc[0]
        print(f"{s:22s} fold {f}: score mine {mine:.10f} file {theirs:.10f} diff {abs(mine-theirs):.1e}")
