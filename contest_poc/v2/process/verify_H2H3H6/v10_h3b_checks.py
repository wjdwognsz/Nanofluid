"""Verifier: H3b with seed-11 residuals and a different permutation stream; primary and no-copy-rows variant."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h3_offset as H
from vrr_data import load
from vrr_common import copy_mask
P = "/home/user/Nanofluid/contest_poc/v2/results/raw/h236_parts/"; V = "/home/user/Nanofluid/contest_poc/v2/process/verify_H2H3H6/"
for name in ["DES_RHO", "DES_ETA"]:
    ds = load(name); lab = H.ref_label(ds); cm = copy_mask(ds)
    print(name, "ref rows", int((lab != "").sum()), pd.Series(lab[lab != ""]).value_counts().to_dict(),
          "x values of ref rows:", sorted(pd.Series(np.where(ds.df.A == H.CHCL, ds.df.xA, ds.df.xB)[lab != ""]).round(3).unique().tolist()))
    for rlab, r in [("seed0", ds.y - pd.read_csv(P + f"oof_{name}.csv.gz").p_rm_s0.values),
                    ("seed11", ds.y - pd.read_csv(V + f"oof_{name}_s11.csv.gz").p_rm.values)]:
        for vname, keep in [("primary", np.ones(len(r), bool)), ("no_copy_rows", ~cm)]:
            t = H.ref_offsets(ds, r, lab, keep)
            rho, p2, p1, _ = H.spearman_perm(t.offset_ref.values, t.offset_other.values, name + vname + "#verify")
            print(f"   {rlab:6s} {vname:13s} S={len(t)} rho={rho:.4f} p2={p2:.4f} pass={rho >= 0.3 and p2 < 0.05}")
