"""c3 sensitivity: PHYS comparator under v1's mechanical physics_prior rule (poc_transfer.py), all tie-breaks."""
import numpy as np, pandas as pd
R = "/home/user/Nanofluid/contest_poc/v2/results/raw"
st = pd.read_csv(f"{R}/h8_source_target.csv"); st = st[~st.is_permuted]
def v1prior(src, par):
    if src.startswith("X_"):
        return 0.5 if src == "X_CED" else 0.0  # (H2O targets: X_water_* absent; X_CED 1.5? no: rel X_CED=0.5)
    ts, _, tg = par.split("_"); ss, sf, sg = src.split("_")
    if ss == ts and sg == tg: return 2.0
    if ss == ts: return 1.5
    if sg == tg: return 1.0
    return 0.5
rows = []
for t, q in st.groupby("target"):
    par = t.replace("_sub40", "")
    pr = q.source.map(lambda s: v1prior(s, par))
    best = q[pr == pr.max()]
    rows.append(dict(target=t, tie_set=list(best.source), gains=list(best.mean_gain.round(3)),
                     any_neg=bool((best.mean_gain < -0.01).any()), all_neg=bool((best.mean_gain < -0.01).all()),
                     v2_phys=q[q.is_phys].source.iloc[0], v2_phys_gain=round(q[q.is_phys].mean_gain.iloc[0], 3)))
D = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
print(D.to_string())
print("v1-rule PHYS neg targets: best-case tie-break", int(D.all_neg.sum()), "worst-case", int(D.any_neg.sum()), "(GATE=3, TOP=3; c3 needs PHYS>3)")
