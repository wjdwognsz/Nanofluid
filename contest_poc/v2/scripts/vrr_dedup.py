"""Within-source exact-duplicate collapse (added in the H1/H9 fix round, 2026-10-07 15:45).

Why: vrr_common.copy_mask / leak_mask_for_source only handle copies BETWEEN sources. Rows that repeat inside one
source (same key = same material + same nominal condition, same value within rtol) are not handled. In the raw data
these are large in ES1 (176 / 777 rows; 161 records are identical in every column of the Cogni-e-SpinDB csv) and
DES_MP (1209 / 3390 rows; the same DES entered under IUPAC and common names with swapped components). They can
(a) let random CV memorise a test row from its twin in training and (b) feed zero-valued scores into calibration.

Definition (identical to the H1/H9 verifier's process/verify_H1H9/v9_dedup_mask.py so that before/after numbers are
comparable): within each source, rows with the same `key` whose value (y_raw if present, else y) agrees within
relative tolerance 1e-4 with an already kept row are dropped; the first occurrence (file order) is kept.
This is a SENSITIVITY variant. The pre-registered (primary) analyses use the data as loaded.
Note: H4's robustness script uses (source, X, y) twins instead of (source, key, y); counts differ slightly
(ES1 176 vs 162, DES_RHO 54 vs 45, IL_CELL 4 vs 5; identical elsewhere).
"""
import numpy as np
import pandas as pd

from vrr_common import subset


def within_source_dup_mask(ds, rtol=1e-4):
    """Boolean mask of rows to DROP (later within-source duplicates of an already kept row)."""
    yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
    d = pd.DataFrame({"g": np.asarray(ds.group).astype(str), "k": np.asarray(ds.key).astype(str),
                      "y": np.asarray(yv, float)})
    drop = np.zeros(len(d), bool)
    sizes = d.groupby(["g", "k"]).y.transform("size").values
    cand = d[sizes > 1]
    for _, sub in cand.groupby(["g", "k"], sort=False):
        kept = []
        for i, v in zip(sub.index.values, sub.y.values):
            if any(abs(v - w) <= rtol * max(abs(v), abs(w), 1e-12) for w in kept):
                drop[i] = True
            else:
                kept.append(v)
    return drop


def dedup(ds, rtol=1e-4):
    """Return (ds_dedup, info) with within-source exact duplicates collapsed to their first occurrence."""
    m = within_source_dup_mask(ds, rtol)
    info = {"n_rows_before": int(len(ds.y)), "n_dropped": int(m.sum()), "n_rows_after": int((~m).sum()),
            "n_sources_before": int(len(set(ds.group))), "n_sources_after": int(len(set(np.asarray(ds.group)[~m])))}
    return subset(ds, ~m, "_dedup"), info


if __name__ == "__main__":
    from vrr_data import load
    for n in ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]:
        ds = load(n)
        _, info = dedup(ds)
        g = pd.Series(ds.group).value_counts()
        gd = pd.Series(_.group).value_counts()
        print(n, info, "| sources>=8 rows before/after:", int((g >= 8).sum()), int((gd >= 8).sum()), flush=True)
