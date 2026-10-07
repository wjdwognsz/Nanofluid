"""Verifier: H3b rho across residual seeds 0-4 (agent's oof file) + 11 (verifier); primary and no-copy variant."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h3_offset as H
from vrr_data import load
from vrr_common import copy_mask
from scipy.stats import spearmanr
P = "/home/user/Nanofluid/contest_poc/v2/results/raw/h236_parts/"; V = "/home/user/Nanofluid/contest_poc/v2/process/verify_H2H3H6/"
rows = []
for name in ["DES_RHO", "DES_ETA"]:
    ds = load(name); lab = H.ref_label(ds); cm = copy_mask(ds)
    o = pd.read_csv(P + f"oof_{name}.csv.gz"); o11 = pd.read_csv(V + f"oof_{name}_s11.csv.gz")
    preds = {s: o[f"p_rm_s{s}"].values for s in range(5)}; preds[11] = o11.p_rm.values
    # seed-averaged residual (mean prediction over 5 seeds) as a lower-noise variant
    preds["avg0-4"] = np.mean([o[f"p_rm_s{s}"].values for s in range(5)], axis=0)
    for sd, p in preds.items():
        r = ds.y - p
        for vname, keep in [("primary", np.ones(len(r), bool)), ("no_copy_rows", ~cm)]:
            t = H.ref_offsets(ds, r, lab, keep)
            rho, pa = spearmanr(t.offset_ref, t.offset_other)
            rows.append(dict(dataset=name, seed=sd, variant=vname, n=len(t), rho=rho, p_asym=pa))
d = pd.DataFrame(rows); d.to_csv(V + "v11_h3b_seeds.csv", index=False)
print(d.pivot_table(index=["dataset", "variant"], columns="seed", values="rho").round(3).to_string())
