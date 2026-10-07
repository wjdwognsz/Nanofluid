"""Verifier: H3a robustness.
 (a) residuals from new seed 11 (fold+model), split/null/boot RNG salted differently ('<DS>#verify');
 (b) leave-one-source-out influence on R (seed-0 residuals, primary material split);
 (c) Spearman (rank) instead of Pearson across sources;
 (d) ES1: exact within-paper duplicate rows collapsed before split-half."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h3_offset as H
from vrr_data import load
from scipy.stats import rankdata
P = "/home/user/Nanofluid/contest_poc/v2/results/raw/h236_parts/"; V = "/home/user/Nanofluid/contest_poc/v2/process/verify_H2H3H6/"
rows = []
for name in ["ES1", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]:
    ds = load(name)
    o0 = pd.read_csv(P + f"oof_{name}.csv.gz"); o11 = pd.read_csv(V + f"oof_{name}_s11.csv.gz")
    assert np.allclose(o11.y, ds.y)
    g = pd.Series(ds.group).value_counts(); el = g[g >= 10].index
    m = np.isin(ds.group, el)
    for lab, r_all, salt in [("seed0 (agent)", ds.y - o0.p_rm_s0.values, name),
                             ("seed0 resid, new split/null/boot RNG", ds.y - o0.p_rm_s0.values, name + "#verify"),
                             ("seed11 resid, new RNG", ds.y - o11.p_rm.values, name + "#verify")]:
        res = H.reliability(salt, r_all[m], ds.group[m], ds.material[m], "material")
        ok = res["R"] >= 0.5 and res["ci"][0] > 0 and res["R"] > res["null_p95"]
        rows.append(dict(dataset=name, variant=lab, R=res["R"], ci_lo=res["ci"][0], ci_hi=res["ci"][1], null95=res["null_p95"], n_src=res["n_sources"], pass_rule=ok))
        print(name, lab, round(res["R"], 4), np.round(res["ci"], 4), round(res["null_p95"], 4), ok, flush=True)
    # (b) LOSO influence (no null/boot)
    r = (ds.y - o0.p_rm_s0.values)[m]; src = ds.group[m]; mat = ds.material[m]
    Rs = {}
    for s in pd.unique(src):
        k = src != s
        Rs[s] = H.reliability(name, r[k], src[k], mat[k], "material", do_null=False, do_boot=False)["R"]
    Rs = pd.Series(Rs)
    print(f"   LOSO R min {Rs.min():.4f} ({Rs.idxmin()}) max {Rs.max():.4f}", flush=True)
    rows.append(dict(dataset=name, variant="LOSO min R", R=Rs.min(), n_src=len(Rs) - 1, pass_rule=Rs.min() >= 0.5))
    # (c) Spearman across sources: replicate split machinery
    us = np.array(sorted(pd.unique(src))); si = pd.Series(src).map({s: i for i, s in enumerate(us)}).values
    Lb, _ = H.make_splits(name, si, np.asarray(mat), len(us), "material")
    M = H.half_means(r, si, Lb, len(us))
    rr = [np.corrcoef(rankdata(M[b, :, 0]), rankdata(M[b, :, 1]))[0, 1] for b in range(M.shape[0])]
    Rsp = H.sb(np.mean(rr)); print(f"   Spearman-based R {Rsp:.4f}", flush=True)
    rows.append(dict(dataset=name, variant="rank (Spearman) split-half", R=Rsp, n_src=len(us), pass_rule=Rsp >= 0.5))
    if name == "ES1":
        d = ds.df.reset_index(drop=True)
        cols = ["source", "polymer(s)", "solvent(s)", "collector_type", "conc_wt", "voltage_kv", "flow_rate_ml/h", "tip_collector_distance_cm", "y"]
        keep = ~d.duplicated(subset=cols).values
        gk = pd.Series(ds.group[keep]).value_counts(); elk = gk[gk >= 10].index
        mk = keep & np.isin(ds.group, elk)
        res = H.reliability(name, (ds.y - o0.p_rm_s0.values)[mk], ds.group[mk], ds.material[mk], "material")
        ok = res["R"] >= 0.5 and res["ci"][0] > 0 and res["R"] > res["null_p95"]
        print("   ES1 dedup:", int((~keep).sum()), "dup rows dropped; sources", res["n_sources"], "R", round(res["R"], 4), np.round(res["ci"], 4), "null95", round(res["null_p95"], 4), ok)
        rows.append(dict(dataset=name, variant="within-paper duplicates collapsed", R=res["R"], ci_lo=res["ci"][0], ci_hi=res["ci"][1], null95=res["null_p95"], n_src=res["n_sources"], pass_rule=ok))
pd.DataFrame(rows).to_csv(V + "v7_h3a_checks.csv", index=False)
