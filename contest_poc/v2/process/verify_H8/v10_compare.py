"""Compare verifier re-runs with the original parts.
seed  : per-target GATE/TOP/PHYS mean gain for new repeats 3,4 vs original 0-2 (and pooled 0-4).
featex: per-target and per-source (twin-affected) gains with feature-identity exclusion vs original (same repeats)."""
import glob, os, numpy as np, pandas as pd
VD = "/home/user/Nanofluid/contest_poc/v2/process/verify_H8"
RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
orig = pd.read_csv(f"{RAW}/h8_policy.csv"); osc = pd.read_csv(f"{RAW}/h8_scores.csv")
def load(mode, kind):
    fs = sorted(glob.glob(f"{VD}/{mode}_parts/h8_*_{kind}.csv"))
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True) if fs else None
out = []
sp = load("seed", "policy")
if sp is not None:
    for t, q in sp.groupby("target"):
        o = orig[orig.target == t]
        r = dict(target=t, new_reps=sorted(q.repeat.unique()))
        for pl in ["GATE", "TOP", "PHYS", "ALL3"]:
            r[f"{pl}_orig"] = o[o.policy == pl].gain.mean()
            r[f"{pl}_new"] = q[q.policy == pl].gain.mean()
            for rep, qq in q[q.policy == pl].groupby("repeat"):
                r[f"{pl}_r{rep}"] = qq.gain.mean()
            r[f"{pl}_r0-4"] = pd.concat([o[o.policy == pl], q[q.policy == pl]]).gain.mean()
        for rep, qq in o[o.policy == "GATE"].groupby("repeat"):
            r[f"GATE_orig_r{rep}"] = qq.gain.mean()
        r["gate_open_new"] = q[q.policy == "GATE"].gate_open.astype(bool).mean()
        r["neg_orig"] = r["GATE_orig"] < -0.01; r["neg_new"] = r["GATE_new"] < -0.01; r["neg_r0-4"] = r["GATE_r0-4"] < -0.01
        out.append(r)
    S = pd.DataFrame(out).set_index("target").T
    print("=== SEED re-run (new outer repeats; unmodified code) ===")
    print(S.to_string())
    S.T.to_csv(f"{VD}/seed_compare.csv")
fp = load("featex", "policy"); fs = load("featex", "scores")
if fp is not None:
    rows = []
    for t, q in fp.groupby("target"):
        reps = sorted(q.repeat.unique())
        o = orig[(orig.target == t) & orig.repeat.isin(reps)]
        r = dict(target=t, reps=reps)
        for pl in ["GATE", "TOP", "PHYS", "ALL3", "NONE"]:
            r[f"{pl}_orig"] = o[o.policy == pl].gain.mean() if pl != "NONE" else o[o.policy == pl].rmse.mean()
            r[f"{pl}_featex"] = q[q.policy == pl].gain.mean() if pl != "NONE" else q[q.policy == pl].rmse.mean()
        r["TOP_same_choice_frac"] = (o[o.policy == "TOP"].sort_values(["repeat", "fold"]).chosen_source.values ==
                                     q[q.policy == "TOP"].sort_values(["repeat", "fold"]).chosen_source.values).mean()
        r["neg_orig"] = r["GATE_orig"] < -0.01; r["neg_featex"] = r["GATE_featex"] < -0.01
        rows.append(r)
    F = pd.DataFrame(rows).set_index("target").T
    print("=== FEATEX re-run (feature-identity exclusion; same repeats) ===")
    print(F.to_string())
    F.T.to_csv(f"{VD}/featex_compare.csv")
    # per source change
    m = fs.merge(osc, on=["target", "repeat", "fold", "source"], suffixes=("_fx", "_or"))
    ps = m.groupby(["target", "source"]).agg(g_or=("gain_if_used_or", "mean"), g_fx=("gain_if_used_fx", "mean"),
                                             s_or=("score_or", "mean"), s_fx=("score_fx", "mean")).reset_index()
    ps["d_gain"] = ps.g_fx - ps.g_or
    ps.to_csv(f"{VD}/featex_per_source.csv", index=False)
    for t, q in ps.groupby("target"):
        print(t, "largest per-source gain drops:\n", q.sort_values("d_gain").head(6).round(4).to_string(index=False))
