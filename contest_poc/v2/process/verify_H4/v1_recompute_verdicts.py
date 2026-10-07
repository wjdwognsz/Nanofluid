"""Verifier check 1: recompute H4 dataset verdicts from the raw draw-level CSV, independently of h4_anchor.aggregate.
Also: bootstrap-seed sensitivity of the CI, alternative rule readings, jackknife (drop one source) of the k=3 mean."""
import numpy as np, pandas as pd, json, sys
RAW = "/home/user/Nanofluid/contest_poc/v2/results/raw"
D = pd.read_csv(f"{RAW}/h4_anchor_draws.csv.gz", keep_default_na=False, na_values=["", "nan", "NaN"])
D["source"] = D.source.astype(str)
# my own rel change from sse (do not trust the rel_change column)
D["rc"] = np.sqrt(D.ssek / D.n_test) / np.sqrt(D.sse0 / D.n_test) - 1
print("max |rc - rel_change| =", float(np.nanmax(np.abs(D.rc - D.rel_change))))
# draws per (dataset, source, method, k)
cnt = D.groupby(["dataset", "method", "k", "source"]).size().reset_index(name="n")
bad = cnt[((cnt.k == 0) & (cnt.n != 1)) | ((cnt.k > 0) & cnt.method.isin(["OFF", "SHR", "FAKE", "FAKE_SHR"]) & (cnt.n != 30))
          | ((cnt.k > 0) & (cnt.method == "RET") & (cnt.n != 5))]
print("bad draw counts:", len(bad))
# n_test = n_rows - k
print("n_test != n_rows-k:", int((D.n_test != D.n_rows - D.k).sum()))
# fake source never equals held-out source
print("fake==source:", int((D.fake_source == D.source).sum()))
PS = D.groupby(["dataset", "method", "k", "source"]).rc.mean().reset_index()


def boot(v, seed, n=2000):
    v = np.asarray(v, float); rs = np.random.default_rng(seed)
    bs = [v[rs.integers(0, len(v), len(v))].mean() for _ in range(n)]
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


out = []
for ds in ["ES1", "ES2", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL", "DYE"]:
    g = lambda m, k: PS[(PS.dataset == ds) & (PS.method == m) & (PS.k == k)].set_index("source").rc
    off3, shr3, fake3, shr1 = g("OFF", 3), g("SHR", 3), g("FAKE", 3), g("SHR", 1)
    rec = dict(dataset=ds, n_src=len(off3))
    for nm, v in (("OFF3", off3), ("SHR3", shr3), ("FAKE3", fake3), ("SHR1", shr1)):
        rec[nm] = v.mean()
        cis = [boot(v.values, s) for s in range(6)]  # seed 0 = original, 1..5 alternatives
        rec[nm + "_ci0"] = cis[0]
        rec[nm + "_cihi_range_seeds1to5"] = (min(c[1] for c in cis[1:]), max(c[1] for c in cis[1:]))
        rec[nm + "_median"] = v.median()
        rec[nm + "_frac_impr"] = float((v < 0).mean())
    okm = lambda nm: rec[nm] <= -0.10 and rec[nm + "_ci0"][1] < 0
    rule = (okm("OFF3") or okm("SHR3")) and rec["FAKE3"] >= -0.02
    # loose reading: (any mean <= -10%) and (any CI hi < 0) -- same here?
    loose = ((rec["OFF3"] <= -.1 or rec["SHR3"] <= -.1) and (rec["OFF3_ci0"][1] < 0 or rec["SHR3_ci0"][1] < 0)
             and rec["FAKE3"] >= -0.02)
    rec["rule"] = rule; rec["rule_loose"] = loose; rec["sec"] = rec["SHR1"] <= 0
    # jackknife: drop each source, does the rule still hold for the method that passes?
    jk = []
    for s in off3.index:
        o, h = off3.drop(s), shr3.drop(s)
        ok = ((o.mean() <= -.1 and boot(o.values, 0, 1000)[1] < 0) or (h.mean() <= -.1 and boot(h.values, 0, 1000)[1] < 0))
        jk.append(ok)
    rec["jackknife_rule_holds_frac"] = float(np.mean(jk))
    # drop the single most-improved source for SHR
    s_best = shr3.idxmin()
    rec["SHR3_without_best_source"] = shr3.drop(s_best).mean()
    rec["OFF3_without_best_source"] = off3.drop(off3.idxmin()).mean()
    out.append(rec)
    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else (tuple(round(x, 4) for x in v) if isinstance(v, tuple) else v))
                      for k, v in rec.items()}, default=str))
pd.DataFrame(out).to_csv("/home/user/Nanofluid/contest_poc/v2/process/verify_H4/v1_recomputed.csv", index=False)
