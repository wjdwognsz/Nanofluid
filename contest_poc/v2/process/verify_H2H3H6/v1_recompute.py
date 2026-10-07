"""Verifier: recompute H2/H3/H6 graded verdicts from the raw CSVs only (no script reuse)."""
import numpy as np, pandas as pd, json
from scipy.stats import spearmanr
R = "/home/user/Nanofluid/contest_poc/v2/results/raw/"
C = 0.6745*np.sqrt(2)
p = pd.read_csv(R+"h2_pairs.csv")
out = {}
for ds in ["DES_RHO","DES_ETA"]:
    q = p[(p.dataset==ds)&(p.pair_set=="exact_independent")]
    out[ds] = dict(n=len(q), med=q.abs_delta.median(), copyrel_any=bool(q.copy_relation_pair.any()),
                   n_zero=int((q.abs_delta<=1e-12).sum()))
print("H2 med", out)
print("P2a", out["DES_RHO"]["med"], out["DES_RHO"]["med"]<=0.010)
print("P2b fold", 10**out["DES_ETA"]["med"], 10**out["DES_ETA"]["med"]>=1.10)
st = pd.read_csv(R+"h2_dataset_stats.csv")
sd = st[st.pair_set=="exact_independent"].set_index("dataset").sd_y
r_rho = out["DES_RHO"]["med"]/C/sd["DES_RHO"]; r_eta = out["DES_ETA"]["med"]/C/sd["DES_ETA"]
print("P2c", r_rho, r_eta, r_rho-r_eta, r_rho<r_eta)
# H3a recompute from split file
s = pd.read_csv(R+"h3_splithalf.csv"); n = pd.read_csv(R+"h3_splithalf_null.csv")
for ds,g in s[(s.variant=="primary")].groupby(["dataset","split_mode"]):
    rbar = g.pearson_r.mean(); Rv = 2*rbar/(1+rbar)
    nn = n[(n.dataset==ds[0])&(n.variant=="primary")&(n.split_mode==ds[1])].null_R
    print("H3a", ds, round(Rv,4), "null95", round(np.percentile(nn,95),4), "pass(R>=.5 & >null95)", Rv>=0.5 and Rv>np.percentile(nn,95))
# H3b recompute
b = pd.read_csv(R+"h3b_reference.csv")
for ds in ["DES_RHO","DES_ETA"]:
    t = b[(b.dataset==ds)&(b.variant=="primary")]
    rho, pa = spearmanr(t.offset_ref, t.offset_other)
    print("H3b", ds, len(t), round(rho,4), "asymptotic p", round(pa,4), "pass", rho>=0.3 and pa<0.05)
# H6a recompute from per-source file & seeds
l = pd.read_csv(R+"h6_leak.csv"); sd_ = pd.read_csv(R+"h6_leak_seeds.csv")
for ds in ["DES_RHO","DES_ETA","DES_MP","IL_CELL","DYE"]:
    z = sd_[sd_.dataset==ds]; ch = z.rmse_keep.mean()/z.rmse_rm.mean()-1
    t = l[l.dataset==ds]
    pooled = np.sqrt(t.sse_keep.sum()/t.sse_rm.sum())-1
    rs = np.random.default_rng(12345); bs=[]
    a_, b_ = t.sse_keep.values, t.sse_rm.values
    for _ in range(4000):
        ix = rs.integers(0,len(a_),len(a_)); bs.append(np.sqrt(a_[ix].sum()/b_[ix].sum())-1)
    # alternative 'source-level' = mean over all sources of per-source change
    rs2 = np.random.default_rng(7); v=t.change.values
    bm=[v[rs2.integers(0,len(v),len(v))].mean() for _ in range(4000)]
    print("H6a", ds, "change(seed-mean)", round(ch,4), "pooled", round(pooled,4), "CI(other seed)", np.round(np.percentile(bs,[2.5,97.5]),4),
          "| mean per-source change all sources", round(v.mean(),4), np.round(np.percentile(bm,[2.5,97.5]),4),
          "| median per-source", round(np.median(v),4))
