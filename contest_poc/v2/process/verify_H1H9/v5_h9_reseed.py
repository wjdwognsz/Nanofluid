"""Verifier: re-run the family's H9 run() with NEW seeds, writing parts into the verifier folder (not the family's).
Usage: python v5_h9_reseed.py DATASET 5,6,7"""
import os, sys, glob
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h9_conformal as H
OUT = "/home/user/Nanofluid/contest_poc/v2/process/verify_H1H9/h9_reseed_parts"
os.makedirs(OUT, exist_ok=True)
H.PARTS = OUT
name, seeds = sys.argv[1], [int(s) for s in sys.argv[2].split(",")]
if len(sys.argv) < 4 or sys.argv[3] != "--summ-only":
    H.run(name, seeds)
conf = pd.concat([pd.read_csv(f) for f in glob.glob(f"{OUT}/{name}__seed*__conformal.csv")])
def pooled(m):
    c = conf[conf.method == m]
    return (c.coverage * c.n).sum() / c.n.sum(), (c.width * c.n).sum() / c.n.sum()
res = {m: pooled(m) for m in ["naive", "aware", "anchor", "aware_on_anchor_rows"]}
ratio = res["anchor"][1] / res["aware_on_anchor_rows"][1]
print(name, "seeds", sorted(conf.seed.unique()))
for m, (c, w) in res.items():
    print(f"  {m:22s} coverage {c:.4f} width {w:.4g}")
print(f"  ratio anchor/aware(same rows) {ratio:.4f}; C1 {res['naive'][0] < 0.85} C2 {res['aware'][0] >= 0.87} "
      f"C3 {ratio <= 0.9 and res['anchor'][0] >= 0.87}")
