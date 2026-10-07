import json, numpy as np, pandas as pd, sys
from scipy.stats import spearmanr, norm
from sklearn.metrics import roc_auc_score
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_common import boot_ci
R = "/home/user/Nanofluid/contest_poc/v2/results"
pol = pd.read_csv(f"{R}/raw/h8_policy.csv"); sc = pd.read_csv(f"{R}/raw/h8_scores.csv")
T = pd.read_csv(f"{R}/raw/h8_targets.csv"); S = json.load(open(f"{R}/h8_summary.json"))
real = sc[~sc.is_permuted]; perm = sc[sc.is_permuted]
rho = real.groupby("target").apply(lambda d: np.nanmean([spearmanr(q.score, q.gain_if_used).correlation for _, q in d.groupby(["repeat", "fold"])]))
print("score-gain spearman mean over targets", round(rho.mean(), 4), "summary", S["diagnostics"]["mean_score_gain_spearman_over_targets"])
print("AUROC fold-level", round(roc_auc_score((real.gain_if_used < -0.01).astype(int), -real.score), 4))
print("perm frac gain>0", round((perm.gain_if_used > 0).mean(), 4), "real frac above thr", round(real.above_threshold.mean(), 4), "perm above", round(perm.above_threshold.mean(), 4))
fb = real.groupby(["target", "repeat", "fold"]).gain_if_used.max().groupby("target").mean()
print("ORACLE per fold", round(fb.mean(), 4), "fixed", round(real.groupby(["target", "source"]).gain_if_used.mean().groupby("target").max().mean(), 4),
      "RANDOM", round(real.groupby(["target", "source"]).gain_if_used.mean().groupby("target").mean().mean(), 4),
      "PERM", round(perm.groupby(["target", "source"]).gain_if_used.mean().groupby("target").mean().mean(), 4))
cl = pol[(pol.policy == "GATE") & (~pol.gate_open.astype(bool))]
print("closed folds:\n", cl[["target", "repeat", "fold", "top_source", "top_score", "threshold95"]])
print("TOP gain in closed fold", pol[(pol.policy == "TOP") & (pol.target == "p_exp_H2O") & (pol.repeat == 0) & (pol.fold == 3)].gain.values)
# c2 CI with other bootstrap seeds
g = T.set_index("target").gain_GATE
for s in [0, 1, 7, 123]:
    print("c2 CI seed", s, np.round(boot_ci(g.values, seed=s), 4))
# Multiplicity claim: family-wise gate variants (EXPLORATORY by verifier)
# (i) Bonferroni Fisher-z on |r| with m = #real sources, (ii) empirical: threshold = q-quantile of perm scores where q = 1-0.05/m (-> max)
out = []
for (t, r, f), q in sc.groupby(["target", "repeat", "fold"]):
    rq = q[~q.is_permuted]; m = len(rq)
    ntr = int(pol[(pol.target == t) & (pol.repeat == r) & (pol.fold == f) & (pol.policy == "NONE")].n_train.iloc[0])
    top = rq.loc[rq.score.idxmax()]
    thr_b = np.tanh(norm.ppf(1 - 0.05 / (2 * m)) / np.sqrt(ntr - 3))
    thr_u = np.tanh(norm.ppf(1 - 0.05 / 2) / np.sqrt(ntr - 3))
    out.append(dict(target=t, repeat=r, fold=f, ntr=ntr, top=top.score, thr_bonf=thr_b, thr_unc=thr_u,
                    perm_max=q[q.is_permuted].score.max(), top_gain=top.gain_if_used))
O = pd.DataFrame(out)
O["g_bonf"] = np.where(O.top > O.thr_bonf, O.top_gain, 0.0)
O["g_unc"] = np.where(O.top > O.thr_unc, O.top_gain, 0.0)
agg = O.groupby("target").agg(open_bonf=("top", lambda s: None), ).drop(columns="open_bonf")
agg["open_bonf"] = O.assign(o=O.top > O.thr_bonf).groupby("target").o.mean()
agg["gain_bonf"] = O.groupby("target").g_bonf.mean()
agg["open_unc"] = O.assign(o=O.top > O.thr_unc).groupby("target").o.mean()
agg["gain_unc"] = O.groupby("target").g_unc.mean()
agg["thr_bonf_mean"] = O.groupby("target").thr_bonf.mean(); agg["top_mean"] = O.groupby("target").top.mean()
agg["perm_max_mean"] = O.groupby("target").perm_max.mean()
print(agg.round(3).to_string())
print("Bonferroni gate: neg targets", int((agg.gain_bonf < -0.01).sum()), "mean", round(agg.gain_bonf.mean(), 4), "open frac", round((O.top > O.thr_bonf).mean(), 3))
print("Uncorrected parametric gate: neg", int((agg.gain_unc < -0.01).sum()), "mean", round(agg.gain_unc.mean(), 4))
# how the perm-null compares to parametric null: perm score 95th pct vs parametric thr_unc
pp = perm.groupby(["target", "repeat", "fold"]).score.apply(lambda s: np.percentile(s, 95)).rename("thr95").reset_index().merge(O, on=["target", "repeat", "fold"])
print("mean perm 95pct thr", round(pp.thr95.mean(), 3), "mean parametric 95% thr", round(pp.thr_unc.mean(), 3))
