"""Re-grade H8 criteria with leak-corrected (feature-identity exclusion) per-target gains substituted for d_exp_*.
Targets whose TOP choices never held an escaped twin (s_exp_*, p_exp_*, sub40) keep the original values."""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_common import boot_ci
T = pd.read_csv("/home/user/Nanofluid/contest_poc/v2/results/raw/h8_targets.csv").set_index("target")
F = pd.read_csv("/home/user/Nanofluid/contest_poc/v2/process/verify_H8/featex_compare.csv").set_index("target")
res = {}
for pl in ["GATE", "TOP", "PHYS", "ALL3"]:
    g = T[f"gain_{pl}"].copy()
    for t in F.index:
        g[t] = F.loc[t, f"{pl}_featex"]
    res[pl] = g
D = pd.DataFrame(res)
print(D.round(4).to_string())
neg = {pl: int((D[pl] < -0.01).sum()) for pl in D}
print("neg", neg, "mean", D.mean().round(4).to_dict(), "GATE CI", np.round(boot_ci(D.GATE.values), 4))
c1 = neg["GATE"] <= 1; c2 = D.GATE.mean() > 0; c3 = neg["GATE"] < neg["TOP"] or neg["GATE"] < neg["PHYS"]
print("c1", c1, "c2", c2, "c3", c3, "->", "PASS" if c1 and c2 and c3 else "FAIL")
D.to_csv("/home/user/Nanofluid/contest_poc/v2/process/verify_H8/corrected_targets.csv")
