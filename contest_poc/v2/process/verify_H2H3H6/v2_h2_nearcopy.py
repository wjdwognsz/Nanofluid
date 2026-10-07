"""Verifier: H2 sensitivity -- near-copies (rounded re-reports) among 'independent' pairs, key concentration,
and source-level (not source-pair) bootstrap for P2a/P2b/P2c."""
import numpy as np, pandas as pd, zlib
R = "/home/user/Nanofluid/contest_poc/v2/results/raw/"
C = 0.6745*np.sqrt(2)
p = pd.read_csv(R+"h2_pairs.csv")
st = pd.read_csv(R+"h2_dataset_stats.csv"); sd = st[st.pair_set=="exact_independent"].set_index("dataset").sd_y
res = {}
for ds in ["DES_RHO","DES_ETA","DES_MP"]:
    q = p[(p.dataset==ds)&(p.pair_set=="exact_independent")].copy()
    if ds=="DES_ETA":
        rel = np.abs(10**q.y_a-10**q.y_b)/np.maximum(10**q.y_a,10**q.y_b)
    else:
        rel = q.abs_delta/np.maximum(q.y_a.abs(),q.y_b.abs())
    q["rel"]=rel
    print(ds, "n pairs", len(q), "quantiles |d|:", np.round(np.percentile(q.abs_delta,[5,10,25,50,75,90]),5))
    for thr in [1e-3, 5e-3]:
        print(f"   share rel diff <= {thr}:", round((rel<=thr).mean(),3), int((rel<=thr).sum()))
    # key concentration: pairs per key
    kc = q.groupby("key").size().sort_values(ascending=False)
    print("   top keys:", kc.head(3).to_dict())
    # sources appearing most
    sc = pd.concat([q.source_a,q.source_b]).value_counts()
    print("   top sources (#pairs):", sc.head(3).to_dict())
    for thr in [1e-3, 5e-3]:
        qq = q[q.rel>thr]
        print(f"   drop near-copies rel<={thr}: n={len(qq)} median |d|={qq.abs_delta.median():.5f}",
              ("fold=%.4f"%10**qq.abs_delta.median()) if ds=="DES_ETA" else "",
              "sigma/sd=%.4f"%(qq.abs_delta.median()/C/sd[ds]))
    res[ds]=q
# key-balanced median (one value per key: median within key), source-balanced
for ds,q in res.items():
    kb = q.groupby("key").abs_delta.median().median()
    print(ds, "key-balanced median", round(kb,5), ("fold %.4f"%10**kb) if ds=="DES_ETA" else "")
# source-level bootstrap: resample sources; keep pairs whose both sources drawn, weight by multiplicity product
def src_boot(q, n=2000, seed=0):
    srcs = np.array(sorted(set(q.source_a)|set(q.source_b)))
    idx = {s:i for i,s in enumerate(srcs)}
    ia = q.source_a.map(idx).values; ib = q.source_b.map(idx).values; v=q.abs_delta.values
    rs = np.random.default_rng(seed); out=np.empty(n)
    for b in range(n):
        cnt = np.bincount(rs.integers(0,len(srcs),len(srcs)), minlength=len(srcs))
        w = cnt[ia]*cnt[ib]
        m = w>0
        if m.sum()==0: out[b]=np.nan; continue
        vv = np.repeat(v[m], w[m]); out[b]=np.median(vv)
    return out
bR = src_boot(res["DES_RHO"], seed=1); bE = src_boot(res["DES_ETA"], seed=2)
print("P2a source-boot CI", np.nanpercentile(bR,[2.5,97.5]))
print("P2b source-boot fold CI", 10**np.nanpercentile(bE,[2.5,97.5]))
d = bR/C/sd["DES_RHO"] - bE/C/sd["DES_ETA"]
print("P2c source-boot diff CI", np.nanpercentile(d,[2.5,97.5]), "share >=0:", np.nanmean(d>=0))
# Bootstrap-seed rerun of the agent's own cluster (source-pair) bootstrap with different seeds
def clus(q, seed, n=2000):
    cl=(q.source_a+"||"+q.source_b).values; arrs=[g.values for _,g in q.abs_delta.groupby(cl)]
    rs=np.random.default_rng(seed); out=np.empty(n)
    for b in range(n):
        ix=rs.integers(0,len(arrs),len(arrs)); out[b]=np.median(np.concatenate([arrs[i] for i in ix]))
    return out
for sdd in [101, 202]:
    a=clus(res["DES_RHO"],sdd); e=clus(res["DES_ETA"],sdd+1)
    print("seed",sdd,"P2a CI",np.round(np.percentile(a,[2.5,97.5]),5),"P2b fold CI",np.round(10**np.percentile(e,[2.5,97.5]),4),
          "P2c CI",np.round(np.percentile(a/C/sd['DES_RHO']-e/C/sd['DES_ETA'],[2.5,97.5]),4))
