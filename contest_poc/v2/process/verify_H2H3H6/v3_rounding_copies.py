"""Verifier: are some 'independent' H2 pairs rounding copies (one value == the other rounded to its decimals)?
Uses raw y (y_raw for DES) by reloading datasets and mapping pairs back to raw strings."""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
from decimal import Decimal
R = "/home/user/Nanofluid/contest_poc/v2/results/raw/"
C = 0.6745*np.sqrt(2)
p = pd.read_csv(R+"h2_pairs.csv")
st = pd.read_csv(R+"h2_dataset_stats.csv"); sd = st[st.pair_set=="exact_independent"].set_index("dataset").sd_y
def ndec(x):
    s = repr(float(x))
    if "e" in s: return 10
    return len(s.split(".")[1].rstrip("0")) if "." in s else 0
for ds in ["DES_RHO","DES_ETA"]:
    q = p[(p.dataset==ds)&(p.pair_set=="exact_independent")].copy()
    if ds=="DES_ETA":
        ya, yb = 10**q.y_a, 10**q.y_b
        # recover raw numbers by rounding to 6 significant digits
        ya = ya.map(lambda v: float(f"{v:.6g}")); yb = yb.map(lambda v: float(f"{v:.6g}"))
    else:
        ya, yb = q.y_a, q.y_b
    flag=[]
    for a,b,na,nb in zip(ya,yb,q.n_rows_a,q.n_rows_b):
        if na>1 or nb>1: flag.append(False); continue   # averaged values: skip
        da, db = ndec(a), ndec(b)
        if da==db: flag.append(False); continue
        lo, hi = (a,b) if da<db else (b,a)  # lo = fewer decimals
        d = min(da,db)
        flag.append(abs(round(hi, d)-lo) < 10**(-d-3) or abs(float(Decimal(str(hi)).quantize(Decimal(10)**-d, rounding="ROUND_HALF_UP"))-lo) < 10**(-d-3))
    q["round_copy"]=flag
    print(ds, "pairs", len(q), "rounding-copy pairs", int(q.round_copy.sum()), "source pairs among them", 
          (q[q.round_copy].source_a+"|"+q[q.round_copy].source_b).nunique())
    qq=q[~q.round_copy]
    med=qq.abs_delta.median()
    print("   median |d| without rounding copies:", round(med,5), ("fold %.4f"%10**med) if ds=="DES_ETA" else "", "sigma/sd %.4f"%(med/C/sd[ds]))
    print(q[q.round_copy].head(8)[["key","source_a","source_b","y_a","y_b"]].to_string())
