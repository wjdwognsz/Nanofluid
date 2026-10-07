"""Verifier check 4: independent re-implementation of the H4 core (OFF / SHR / FAKE, k in {0,1,3,5}) with DIFFERENT seeds:
RF seed 1 (base LOPO model and GroupKFold residual model), GroupKFold relabel seed 1, anchor rng seeded with tag 4242,
own leak-removal code (merge on key, |rel diff| <= 1e-4 of y_raw), own tau2/sigma2 estimator (same formula as prereg/
log 09:50). Not RET. Optionally a different base model (--model GB) as a robustness class.
Usage: python v4_rerun_seed.py DATASET [--model RF|GB] [--seed 1]"""
import sys, zlib, time, argparse, os
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load
from vrr_common import make_model, group_folds

OUT = "/home/user/Nanofluid/contest_poc/v2/process/verify_H4"
ap = argparse.ArgumentParser(); ap.add_argument("dataset"); ap.add_argument("--model", default="RF"); ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args()
name, MODEL, SEED = a.dataset, a.model, a.seed
t0 = time.time()
ds = load(name)
n = len(ds.y)
yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
G = ds.group.astype(str)
df = pd.DataFrame({"g": G, "k": ds.key, "y": yv, "i": np.arange(n)})


def leak_of(s):
    own = df[df.g == s][["k", "y"]].rename(columns={"y": "ys"})
    mm = df[df.g != s].merge(own, on="k")
    rel = (mm.y - mm.ys).abs() / np.maximum(np.maximum(mm.y.abs(), mm.ys.abs()), 1e-12)
    m = np.zeros(n, bool); m[mm.i[rel <= 1e-4].values] = True
    return m


srcs = pd.unique(G)
LEAK = {s: leak_of(s) for s in srcs}
# GroupKFold(10) out-of-source residuals, different seed
p = np.full(n, np.nan)
for tr, te in group_folds(G, 10, seed=SEED):
    trm = np.ones(n, bool); trm[te] = False
    for s in pd.unique(G[te]):
        trm &= ~LEAK[s]
    p[te] = make_model(MODEL, SEED).fit(ds.X[trm], ds.y[trm]).predict(ds.X[te])
r_oof = ds.y - p
print(f"[{name}] oof done {time.time() - t0:.0f}s", flush=True)
vc = pd.Series(G).value_counts()
elig = sorted(vc[vc >= 8].index)
crc = lambda s: zlib.crc32(str(s).encode())
recs = []
for s in elig:
    te = G == s; lk = LEAK[s]; trm = ~te & ~lk
    idx = np.where(te)[0]; ns = len(idx)
    e = ds.y[idx] - make_model(MODEL, SEED).fit(ds.X[trm], ds.y[trm]).predict(ds.X[idx])
    d = pd.DataFrame({"g": G[trm], "r": r_oof[trm]})
    st = d.groupby("g").r.agg(["mean", "var", "size"]); w = st[st["size"] >= 2]
    sig2 = float(((w["size"] - 1) * w["var"]).sum() / (w["size"] - 1).sum())
    tau2 = max(0.0, float(st["mean"].var(ddof=1) - sig2 * np.mean(1.0 / st["size"])))
    leak_src = set(G[lk])
    cand_all = [g for g in vc.index if g != s and g not in leak_src]
    for k in (0, 1, 3, 5):
        wk = k * tau2 / (k * tau2 + sig2) if (k and tau2 > 0) else 0.0
        for dr in range(1 if k == 0 else 30):
            rng = np.random.default_rng([4242, crc(name), crc(s), k, dr, SEED])
            loc = np.sort(rng.choice(ns, size=k, replace=False)) if k else np.array([], int)
            test = np.setdiff1d(np.arange(ns), loc)
            off = e[loc].mean() if k else 0.0
            if k:
                cand = [g for g in cand_all if vc[g] >= k]
                fs = cand[rng.integers(len(cand))]
                fr = rng.choice(np.where(G == fs)[0], size=k, replace=False)
                offf = r_oof[fr].mean()
            else:
                offf = 0.0
            r0 = np.sqrt(np.mean(e[test] ** 2))
            for meth, sh in (("OFF", off), ("SHR", wk * off), ("FAKE", offf)):
                recs.append((name, MODEL, SEED, s, ns, k, dr, meth, np.sqrt(np.mean((e[test] - sh) ** 2)) / r0 - 1, tau2, sig2))
R = pd.DataFrame(recs, columns=["dataset", "model", "seed", "source", "n_rows", "k", "draw", "method", "rel_change", "tau2", "sigma2"])
R.to_csv(f"{OUT}/v4_rerun_{name}_{MODEL}_s{SEED}.csv.gz", index=False, compression="gzip")
P = R.groupby(["method", "k", "source"]).rel_change.mean().reset_index()
lines = []
for (me, k), v in P.groupby(["method", "k"]):
    vv = v.rel_change.values; rs = np.random.default_rng(SEED)
    bs = [vv[rs.integers(0, len(vv), len(vv))].mean() for _ in range(2000)]
    lines.append(dict(dataset=name, model=MODEL, seed=SEED, method=me, k=k, n_sources=len(vv), mean=vv.mean(),
                      ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5), median=np.median(vv), frac_improved=np.mean(vv < 0)))
L = pd.DataFrame(lines)
L.to_csv(f"{OUT}/v4_rerun_summary_{name}_{MODEL}_s{SEED}.csv", index=False)
g = lambda m, k: L[(L.method == m) & (L.k == k)].iloc[0]
ok = lambda m: g(m, 3)["mean"] <= -0.10 and g(m, 3)["ci_hi"] < 0
rule = (ok("OFF") or ok("SHR")) and g("FAKE", 3)["mean"] >= -0.02
print(L[L.k.isin([1, 3])].to_string(index=False, float_format=lambda x: f"{x:+.4f}"))
print(f"[{name}] {MODEL} seed {SEED}: rule {'PASS' if rule else 'FAIL'}; secondary SHR k1 {'holds' if g('SHR', 1)['mean'] <= 0 else 'fails'}; "
      f"median tau2 {R.tau2.median():.4g} sigma2 {R.sigma2.median():.4g}; {time.time() - t0:.0f}s", flush=True)
