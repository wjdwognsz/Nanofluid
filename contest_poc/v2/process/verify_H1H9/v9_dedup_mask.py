"""Verifier helper: mask that keeps one row per within-source exact duplicate (same source, same key, |rel dy|<1e-4)."""
import numpy as np, pandas as pd

def within_source_dup_mask(ds, rtol=1e-4):
    yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
    d = pd.DataFrame({"g": np.asarray(ds.group).astype(str), "k": ds.key, "y": yv})
    drop = np.zeros(len(d), bool)
    for (g, k), sub in d.groupby(["g", "k"]):
        if len(sub) < 2:
            continue
        idx = sub.index.values
        kept = []
        for i in idx:
            if any(abs(d.y[i] - d.y[j]) <= rtol * max(abs(d.y[i]), abs(d.y[j]), 1e-12) for j in kept):
                drop[i] = True
            else:
                kept.append(i)
    return drop

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
    from vrr_data import load
    for n in ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]:
        ds = load(n)
        m = within_source_dup_mask(ds)
        print(f"{n:8s} rows {len(m):5d} within-source exact (key,y) duplicates to drop: {m.sum():5d} ({m.mean():.3f})")
