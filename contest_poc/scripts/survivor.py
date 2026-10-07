"""Reproduce: success-only (one-class) vs failure-inclusive supervised detection of unstable
electrospinning, leave-one-failure-paper-out (Cogni-e-SpinDB, PVDF)."""
import sys, numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import roc_auc_score
d = pd.read_csv(sys.argv[1])
d = d[d["polymer(s)"] == "PVDF"].copy()
d["rh"] = pd.to_numeric(d["humidity_%"].astype(str).str.split("-").str[0], errors="coerce")
d["drum"] = (d.collector_type != "Flat").astype(float)
d["wv"] = (d.solution_concentration_unit == "w/v%").astype(float)
for s in ["DMF", "ACETONE", "DMAC", "DMSO", "NMP"]:
    d["s_" + s] = d["solvent(s)"].str.contains(s).astype(float)
F = ["solution_concentration", "voltage_kv", "flow_rate_ml/h", "tip_collector_distance_cm", "needle_diameter_g",
     "rotation_speed_rpm", "temperature_c", "rh", "drum", "wv"] + [c for c in d if c.startswith("s_")]
X = d[F].fillna(d[F].median()).values
y = (~d.was_formation_stable).astype(int).values
paper = d.doi.values
fail_papers = sorted(set(paper[y == 1]))
print("PVDF rows", len(d), "failures", y.sum(), "failure papers", len(fail_papers))
res = {"oneclass_IF": [], "supervised_RF": [], "y": []}
for p in fail_papers:
    te = paper == p
    tr = ~te
    iso = IsolationForest(n_estimators=300, random_state=0).fit(X[tr & (y == 0)])
    res["oneclass_IF"] += list(-iso.score_samples(X[te]))
    rf = RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=0).fit(X[tr], y[tr])
    res["supervised_RF"] += list(rf.predict_proba(X[te])[:, 1])
    res["y"] += list(y[te])
yy = np.array(res["y"])
for k in ["oneclass_IF", "supervised_RF"]:
    print(k, "pooled AUC", round(roc_auc_score(yy, res[k]), 3), "n test", len(yy), "fails", yy.sum())
# per-paper AUC (within-paper discrimination)
