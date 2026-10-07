import sys, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h8_gate as H
RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
# (1) repro files
a = pd.read_csv(f"{RAW}/h8_parts/h8_s_exp_H2O_r0_policy.csv"); b = pd.read_csv(f"{RAW}/h8_repro/h8_rerun_s_exp_H2O_r0_policy.csv")
m = a.merge(b, on=["repeat", "fold", "policy"], suffixes=("", "_b"))
print("repro policy: max |score diff|", (m.top_score - m.top_score_b).abs().max(), "same chosen", (m.chosen_source.fillna("") == m.chosen_source_b.fillna("")).all(),
      "max |gain diff| per fold", round((m.gain - m.gain_b).abs().max(), 4))
print(m.groupby("policy").apply(lambda d: round(abs(d.gain.mean() - d.gain_b.mean()), 5)).to_string())
# (2) independent transfer-model gain for s_exp_He r0, fold 0..4, TOP source
TASKS, TARGETS, FEAT = H.load_all()
t, rep = "s_exp_He", 0
ser, parent = TARGETS[t]; tk = list(ser.index); y = ser.values
X = np.vstack([FEAT[k] for k in tk])
folds = list(KFold(5, shuffle=True, random_state=rep).split(np.arange(len(y))))
pol = pd.read_csv(f"{RAW}/h8_policy.csv"); pol = pol[(pol.target == t) & (pol.repeat == rep)]
S = TASKS["s_sim_CH4"]; g = np.zeros(len(y))
for tr, te in folds:
    ex = {tk[i] for i in te}; sk = [k for k in S.index if k not in ex]
    g[te] = RandomForestRegressor(n_estimators=100, max_features=0.2, n_jobs=1, random_state=11).fit(np.vstack([FEAT[k] for k in sk]), S.loc[sk].values).predict(X[te])
rf = lambda: RandomForestRegressor(n_estimators=300, max_features=0.33, min_samples_leaf=2, n_jobs=1, random_state=rep)
for f, (tr, te) in enumerate(folds):
    pn = rf().fit(X[tr], y[tr]).predict(X[te])
    lin = LinearRegression().fit(g[tr, None], y[tr]); res = y[tr] - lin.predict(g[tr, None])
    pt = lin.predict(g[te, None]) + rf().fit(X[tr], res).predict(X[te])
    rn, rt = np.sqrt(np.mean((y[te]-pn)**2)), np.sqrt(np.mean((y[te]-pt)**2))
    row = pol[(pol.fold == f) & (pol.policy == "TOP")].iloc[0]
    print(f"fold {f}: TOP file={row.chosen_source} gain {row.gain:+.4f} | mine (s_sim_CH4) gain {(rn-rt)/rn:+.4f}  rmse_none file {row.rmse_none:.5f} mine {rn:.5f}")
