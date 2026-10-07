"""Verifier: extend copy_relations with a rounding tolerance (near-copy relation) and recompute P2a-c.
near-copy pair of sources: share >= 3 keys in the H2 independent set and >= 80% of them agree within tol
(DES_RHO: |d| <= 0.0006 g/cm3 ~ rounding to 3 decimals; DES_ETA: rel raw diff <= 0.5%). Also: drop single pairs within tol."""
import numpy as np, pandas as pd
R = "/home/user/Nanofluid/contest_poc/v2/results/raw/"
C = 0.6745*np.sqrt(2)
p = pd.read_csv(R+"h2_pairs.csv")
st = pd.read_csv(R+"h2_dataset_stats.csv"); sd = st[st.pair_set=="exact_independent"].set_index("dataset").sd_y
out = {}
for ds, tolfun in [("DES_RHO", lambda q: q.abs_delta <= 0.0006),
                   ("DES_ETA", lambda q: np.abs(10**q.abs_delta - 1) <= 0.005)]:
    q = p[(p.dataset==ds)&(p.pair_set=="exact_independent")].copy()
    q["near"] = tolfun(q)
    q["sp"] = q.source_a+"||"+q.source_b
    g = q.groupby("sp").agg(n=("near","size"), f=("near","mean"))
    ncr = set(g[(g.n>=3)&(g.f>=0.8)].index)
    a = q[~q.sp.isin(ncr)]
    b = q[~q.near]
    for lab, qq in [("all", q), ("drop near-copy source pairs", a), ("drop every pair within tol", b)]:
        med = qq.abs_delta.median()
        out[(ds,lab)] = med/C/sd[ds]
        print(f"{ds:8s} {lab:30s} n={len(qq):4d} src-pairs={qq.sp.nunique():4d} median|d|={med:.5f}",
              f"fold={10**med:.4f}" if ds=="DES_ETA" else "", f"sigma/sd={med/C/sd[ds]:.4f}")
    print("   near-copy relation source pairs:", len(ncr), sorted(ncr)[:5])
for lab in ["all","drop near-copy source pairs","drop every pair within tol"]:
    print("P2c", lab, round(out[("DES_RHO",lab)]-out[("DES_ETA",lab)],4))
