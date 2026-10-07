"""Verifier: recompute H8 verdicts from raw CSVs (independent of h8_gate.aggregate)."""
import json, numpy as np, pandas as pd
R = "/home/user/Nanofluid/contest_poc/v2/results"
pol = pd.read_csv(f"{R}/raw/h8_policy.csv")
sc = pd.read_csv(f"{R}/raw/h8_scores.csv")
S = json.load(open(f"{R}/h8_summary.json"))
print("policy rows", len(pol), "score rows", len(sc))
print(pol.groupby(["target"]).apply(lambda d: (d.repeat.nunique(), d.fold.nunique(), len(d))).to_string())
# 1) structural checks from per-source scores
bad = []
for (t, r, f), q in sc.groupby(["target", "repeat", "fold"]):
    perm = q[q.is_permuted]
    real = q[~q.is_permuted]
    thr = np.percentile(perm.score.values, 95)
    top = real.loc[real.score.idxmax()]
    P = pol[(pol.target == t) & (pol.repeat == r) & (pol.fold == f)].set_index("policy")
    if len(perm) != 10: bad.append((t, r, f, "nperm", len(perm)))
    if abs(thr - P.loc["GATE", "threshold95"]) > 1e-12: bad.append((t, r, f, "thr"))
    if top.source != P.loc["TOP", "chosen_source"]: bad.append((t, r, f, "top", top.source, P.loc["TOP", "chosen_source"]))
    if abs(top.gain_if_used - P.loc["TOP", "gain"]) > 1e-12: bad.append((t, r, f, "topgain"))
    phys = q[q.source == P.loc["PHYS", "chosen_source"]]
    if abs(phys.gain_if_used.iloc[0] - P.loc["PHYS", "gain"]) > 1e-12: bad.append((t, r, f, "physgain"))
    gopen = top.score > thr
    if bool(P.loc["GATE", "gate_open"]) != gopen: bad.append((t, r, f, "gate"))
    exp_g = top.gain_if_used if gopen else 0.0
    if abs(exp_g - P.loc["GATE", "gain"]) > 1e-12: bad.append((t, r, f, "gategain", exp_g, P.loc["GATE", "gain"]))
    gm = top.score > perm.score.max()
    if abs((top.gain_if_used if gm else 0.0) - P.loc["GATE_MAX", "gain"]) > 1e-12: bad.append((t, r, f, "gmax"))
    top3 = list(real.sort_values("score", ascending=False).source[:3])
    if "|".join(top3) != P.loc["ALL3", "chosen_source"]: bad.append((t, r, f, "all3", top3, P.loc["ALL3", "chosen_source"]))
    # target itself / parent never in pool
    parent = t.replace("_sub40", "")
    if t in set(real.source) or parent in set(real.source): bad.append((t, r, f, "self-in-pool"))
    # permuted never chosen
print("structural mismatches:", len(bad), bad[:10])
# 2) per-target gains and verdicts
rows = []
for t, p in pol.groupby("target", sort=False):
    r = dict(target=t)
    for pl in ["PHYS", "TOP", "GATE", "ALL3", "GATE_MAX"]:
        r[pl] = p[p.policy == pl].gain.mean()
    r["open"] = p[p.policy == "GATE"].gate_open.astype(bool).sum()
    r["nf"] = (p.policy == "GATE").sum()
    rows.append(r)
T = pd.DataFrame(rows).set_index("target")
print(T.round(4).to_string())
neg = {pl: int((T[pl] < -0.01).sum()) for pl in ["PHYS", "TOP", "GATE", "ALL3", "GATE_MAX"]}
mg = {pl: T[pl].mean() for pl in neg}
print("neg", neg); print("mean", {k: round(v, 4) for k, v in mg.items()})
c1 = neg["GATE"] <= 1; c2 = mg["GATE"] > 0; c3 = neg["GATE"] < neg["TOP"] or neg["GATE"] < neg["PHYS"]
print("c1", c1, "c2", c2, "c3", c3, "overall", "PASS" if c1 and c2 and c3 else "FAIL")
print("summary:", S["verdict"], S["criteria_met"], S["negative_transfer_targets"], {k: round(v, 4) for k, v in S["mean_gain"].items()})
print("gate open folds", int(T.open.sum()), "/", int(T.nf.sum()))
# margins: how far each target is from the -1% bar
print((T.GATE + 0.01).sort_values().round(4).to_string())
