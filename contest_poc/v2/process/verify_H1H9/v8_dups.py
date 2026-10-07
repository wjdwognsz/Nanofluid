"""Verifier: count exact feature-vector duplicates within a source and across sources (could inflate random CV)."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
for d in ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]:
    ds = load(d)
    Xr = pd.DataFrame(np.round(ds.X, 8)).astype(str).agg("|".join, axis=1)
    df = pd.DataFrame({"x": Xr, "g": np.asarray(ds.group).astype(str), "y": ds.y})
    n_in = df.groupby(["g", "x"]).x.transform("size")
    n_all = df.groupby("x").x.transform("size")
    n_src = df.groupby("x").g.transform("nunique")
    within = (n_in > 1).mean()
    across = (n_src > 1).mean()
    # y spread among within-source X-duplicates
    wd = df[n_in > 1].groupby(["g", "x"]).y.std().mean() if within > 0 else np.nan
    print(f"{d:8s} rows {len(df):5d}  share rows w/ exact-X dup in SAME source {within:.3f} (mean within-dup y SD {wd:.4g}); "
          f"share rows whose X appears in >1 source {across:.3f}; n features {ds.X.shape[1]}")
