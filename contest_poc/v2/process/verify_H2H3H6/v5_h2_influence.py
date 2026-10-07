"""Verifier: H2 leave-one-source-out influence on P2a/P2b/P2c medians (pairs involving source s dropped)."""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
R = "/home/user/Nanofluid/contest_poc/v2/results/raw/"
C = 0.6745*np.sqrt(2)
p = pd.read_csv(R+"h2_pairs.csv")
st = pd.read_csv(R+"h2_dataset_stats.csv"); sd = st[st.pair_set=="exact_independent"].set_index("dataset").sd_y
Q = {ds: p[(p.dataset==ds)&(p.pair_set=="exact_independent")] for ds in ["DES_RHO","DES_ETA"]}
for ds,q in Q.items():
    srcs = sorted(set(q.source_a)|set(q.source_b))
    meds = {s: q[(q.source_a!=s)&(q.source_b!=s)].abs_delta.median() for s in srcs}
    m = pd.Series(meds)
    print(ds, "LOSO median range", round(m.min(),5), round(m.max(),5), "argmin", m.idxmin(), "argmax", m.idxmax())
    if ds=="DES_ETA": print("   fold range", round(10**m.min(),4), round(10**m.max(),4))
    print("   sigma/sd range", round(m.min()/C/sd[ds],4), round(m.max()/C/sd[ds],4))
# top non-DOI / compilation sources
for ds in ["DES_RHO","DES_ETA"]:
    q=Q[ds]; s=pd.concat([q.source_a,q.source_b]).value_counts()
    print(ds, "pairs involving non-DOI sources:", int(sum(v for k,v in s.items() if not str(k).startswith("10."))), s[[k for k in s.index if not str(k).startswith("10.")]].to_dict())
# raw source sizes
from vrr_data import load
for ds in ["DES_ETA"]:
    d=load(ds); g=pd.Series(d.group).value_counts()
    print(ds, "size of 'http://pubs.acs.org/journal/acscii':", g.get("http://pubs.acs.org/journal/acscii"), "| top 5 sources:", g.head(5).to_dict())
