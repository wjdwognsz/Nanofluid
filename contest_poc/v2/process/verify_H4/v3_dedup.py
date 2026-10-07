"""Verifier check 3: within-source exact duplicates (same source, identical feature vector X and identical y).
In ES1 (Cogni-e-SpinDB has fully identical repeated rows) and DES_MP (each DES listed twice with swapped component
order, which the loader canonicalises into identical rows) an anchor row frequently has an exact twin that stays in the
evaluation set, so 'anchor rows removed from evaluation' is not effectively true.
(A) exact-twin-disjoint: main-run draws (same rng), drop evaluation rows whose (X,y) equals an anchor's (X,y).
(B) dedup: collapse exact duplicates inside each source, then fresh draws with the same rng scheme on the unique rows;
    sources with >= 8 unique rows (and, as a sensitivity, >= 4 unique rows).
Uses the cached LOPO residuals (results/raw/h4_base_rows.csv) and tau2/sigma2 of h4_source_meta.csv (unchanged).
Usage: python v3_dedup.py DATASET [DATASET ...]"""
import sys, zlib
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load

RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
OUT = "/home/user/Nanofluid/contest_poc/v2/process/verify_H4"
crc = lambda s: zlib.crc32(str(s).encode())
meta_all = pd.read_csv(f"{RAW}/h4_source_meta.csv", keep_default_na=False, na_values=["", "NaN"])
rows_all = pd.read_csv(f"{RAW}/h4_base_rows.csv", keep_default_na=False, na_values=["", "NaN"])


def boot(v, seed=0, n=2000):
    v = np.asarray(v, float); rs = np.random.default_rng(seed)
    bs = [v[rs.integers(0, len(v), len(v))].mean() for _ in range(n)]
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


summ = []
for name in sys.argv[1:]:
    ds = load(name)
    xh = pd.util.hash_pandas_object(pd.DataFrame(np.round(ds.X, 9)), index=False).values
    meta = meta_all[meta_all.dataset == name].copy(); meta["source"] = meta.source.astype(str); meta = meta.set_index("source")
    rows = rows_all[rows_all.dataset == name].copy(); rows["source"] = rows.source.astype(str)
    recs = []
    for s, r in rows.groupby("source", sort=False):
        idx = r.row.values.astype(int); e = r.resid_lopo.values; ns = len(e)
        twin = np.array([f"{a}|{b:.9g}" for a, b in zip(xh[idx], ds.y[idx])])
        tau2, sig2 = float(meta.loc[s, "tau2"]), float(meta.loc[s, "sigma2"])
        _, first = np.unique(twin, return_index=True)
        u = np.sort(first); nu = len(u)
        for k in (1, 3, 5):
            wk = k * tau2 / (k * tau2 + sig2) if tau2 > 0 else 0.0
            for d in range(30):
                # (A) main-run draw, twin-disjoint evaluation
                rng = np.random.default_rng([crc(name), crc(s), k, d])
                loc = np.sort(rng.choice(ns, size=k, replace=False))
                test = np.setdiff1d(np.arange(ns), loc)
                test = test[~np.isin(twin[test], twin[loc])]
                off = e[loc].mean()
                if len(test):
                    r0 = np.sqrt(np.mean(e[test] ** 2))
                    for meth, w in (("OFF", 1.0), ("SHR", wk)):
                        recs.append((name, s, ns, nu, "twin_disjoint", meth, k, d, len(test),
                                     np.sqrt(np.mean((e[test] - w * off) ** 2)) / r0 - 1))
                # (B) dedup within source, fresh draw on unique rows (same rng scheme, tag 99)
                if nu > k:
                    rng = np.random.default_rng([crc(name), crc(s), k, d, 99])
                    locu = np.sort(rng.choice(nu, size=k, replace=False))
                    testu = np.setdiff1d(np.arange(nu), locu)
                    eu = e[u]
                    offu = eu[locu].mean()
                    r0 = np.sqrt(np.mean(eu[testu] ** 2))
                    for meth, w in (("OFF", 1.0), ("SHR", wk)):
                        recs.append((name, s, ns, nu, "dedup", meth, k, d, len(testu),
                                     np.sqrt(np.mean((eu[testu] - w * offu) ** 2)) / r0 - 1))
    R = pd.DataFrame(recs, columns=["dataset", "source", "n_rows", "n_unique", "scope", "method", "k", "draw", "n_test", "rel_change"])
    R.to_csv(f"{OUT}/v3_dedup_{name}.csv.gz", index=False, compression="gzip")
    P = R.groupby(["scope", "method", "k", "source", "n_rows", "n_unique"]).rel_change.mean().reset_index()
    for (sc, me, k), v in P.groupby(["scope", "method", "k"]):
        for minu in ((None,) if sc == "twin_disjoint" else (8, 4)):
            vv = v if minu is None else v[v.n_unique >= minu]
            lo, hi = boot(vv.rel_change.values)
            m = vv.rel_change.mean()
            summ.append(dict(dataset=name, scope=sc + ("" if minu is None else f"_minunique{minu}"), method=me, k=k,
                             n_sources=len(vv), mean=m, ci_lo=lo, ci_hi=hi, median=vv.rel_change.median(),
                             frac_improved=float((vv.rel_change < 0).mean()),
                             meets_main_criterion=bool(m <= -0.10 and hi < 0)))
    S = pd.DataFrame([x for x in summ if x["dataset"] == name])
    print(name, "rows", len(rows), "unique within source", int(rows.groupby("source").size().sum()),
          "| unique rows:", int(R.drop_duplicates("source").n_unique.sum()))
    print(S[S.k.isin([1, 3])].to_string(index=False, float_format=lambda x: f"{x:+.4f}"))
pd.DataFrame(summ).to_csv(f"{OUT}/v3_dedup_summary_{'_'.join(sys.argv[1:])}.csv", index=False)
