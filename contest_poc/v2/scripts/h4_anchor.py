"""H4 -- Anchor (reference-point) join protocol.

Implements PREREG.md section 2, H4 ("기준점 k개로 새 출처를 합류시킬 수 있다"):
  * eligibility: datasets with >= 8 sources that have >= 8 rows (ES1, ES2, DES_RHO, DES_ETA, DES_MP, IL_CELL graded;
    DYE descriptive only)
  * leave-one-source-out RF base model, with the held-out source's copies removed (leak_mask_for_source)
  * k in {0,1,2,3,5}, 30 random anchor draws, anchor rows removed from evaluation
  * methods OFF (mean anchor residual), SHR (empirical-Bayes shrunken offset k tau^2/(k tau^2+sigma^2), tau^2/sigma^2 from
    training sources only), RET (retrain with anchors, weight 5, 5 draws; <=1000-row datasets or a 30-source subset)
  * control FAKE (offset from k rows of another random source)
  * metrics: per-source RMSE_k/RMSE_0 - 1 averaged over sources (source-bootstrap CI), fraction of sources improved,
    gap closure (RMSE_0 - RMSE_k)/(RMSE_0 - RMSE_randomCV)
  * dataset rule: (OFF or SHR k=3 mean change <= -10% AND CI upper < 0) AND FAKE k=3 mean change >= -2%;
    overall PASS if >= 4/6 datasets; secondary prediction: SHR k=1 mean change <= 0 in >= 4/6 datasets.
Exploratory extra (not graded): FAKE_SHR (fake offset with the SHR weight).
All interpretation choices are fixed in process/h4_log.md (section "Interpretations fixed BEFORE running").
FIX STAGE (after process/h4_verify.md; graded numbers unchanged): SNR diagnostic excludes zero-SD sources; deviations
reworded (single RF seed, RET RF150). Robustness (duplicates, seeds, model classes, cluster CI) is in h4_robust.py, whose
`aggregate` must run after this script's `aggregate`.

Usage (run from v2/scripts):
  python h4_anchor.py run DATASET [--budget SECONDS]   # resumable; per-source parts in results/raw/h4_parts/DATASET/
  python h4_anchor.py aggregate                         # raw CSVs, curves, summary JSON, ledger
"""
import argparse
import glob
import json
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from vrr_data import load
from vrr_common import (N_JOBS, RAW, RESULTS, LEDGER, make_model, random_folds, group_folds, rmse, boot_ci,
                        leak_mask_for_source, ledger_write)

GRADED = ["ES1", "ES2", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]
DESCRIPTIVE = ["DYE"]
ALL_DS = GRADED + DESCRIPTIVE
KS = [0, 1, 2, 3, 5]
N_DRAWS = 30
N_RET_DRAWS = 5
RET_WEIGHT = 5.0
RET_TREES = 150
MIN_ROWS = 8
MIN_SOURCES = 8
RET_MAX_ROWS = 1000
RET_N_SOURCES = 30
RET_SUBSET_SEED = 20261007
OOF_FOLDS = 10
RANDCV_SEEDS = [0, 1, 2, 3, 4]
METHODS = ["OFF", "SHR", "RET", "FAKE", "FAKE_SHR"]
PARTS = os.path.join(RAW, "h4_parts")

# prereg thresholds (do not change)
THR_MAIN = -0.10      # OFF or SHR k=3 mean change <= -10%
THR_FAKE = -0.02      # FAKE k=3 mean change >= -2%
THR_SECONDARY = 0.0   # SHR k=1 mean change <= 0
N_PASS_NEEDED = 4


def crc(s):
    return zlib.crc32(str(s).encode())


def rf_ret(seed=0):
    return RandomForestRegressor(n_estimators=RET_TREES, max_features=0.33, min_samples_leaf=2,
                                 n_jobs=N_JOBS, random_state=seed)


def eligible_sources(ds):
    g = pd.Series(ds.group).value_counts()
    return sorted(g[g >= MIN_ROWS].index.tolist())


def ret_sources(ds, elig):
    if len(ds.y) <= RET_MAX_ROWS or len(elig) <= RET_N_SOURCES:
        return list(elig), "all eligible sources (dataset <= 1000 rows)" if len(ds.y) <= RET_MAX_ROWS else "all eligible"
    pick = np.random.default_rng(RET_SUBSET_SEED).choice(len(elig), RET_N_SOURCES, replace=False)
    return sorted(elig[i] for i in pick), f"random {RET_N_SOURCES}-source subset (default_rng({RET_SUBSET_SEED}))"


# ------------------------------------------------------------------ dataset-level preparation (cached)
def prep(name, ds, outdir):
    f = os.path.join(outdir, "prep.npz")
    if os.path.exists(f):
        z = np.load(f, allow_pickle=True)
        return z["r_oof"], z["p_rand"]
    t0 = time.time()
    n = len(ds.y)
    # (a) GroupKFold(10) out-of-source residuals with per-fold leak removal (same definition as H3a)
    leak = {s: leak_mask_for_source(ds, s) for s in pd.unique(ds.group)}
    p_oof = np.full(n, np.nan)
    for tr, te in group_folds(ds.group, OOF_FOLDS, seed=0):
        te_src = pd.unique(ds.group[te])
        lk = np.zeros(n, bool)
        for s in te_src:
            lk |= leak[s]
        trm = np.ones(n, bool)
        trm[te] = False
        trm &= ~lk
        p_oof[te] = make_model("RF", 0).fit(ds.X[trm], ds.y[trm]).predict(ds.X[te])
    r_oof = ds.y - p_oof
    # (b) random 5-fold RF predictions, 5 seeds (raw data, no lineage cleaning: this is what random CV "promises")
    p_rand = np.zeros((n, len(RANDCV_SEEDS)))
    for j, sd in enumerate(RANDCV_SEEDS):
        for tr, te in random_folds(n, 5, seed=sd):
            p_rand[te, j] = make_model("RF", sd).fit(ds.X[tr], ds.y[tr]).predict(ds.X[te])
    np.savez(f, r_oof=r_oof, p_rand=p_rand)
    print(f"[{name}] prep done in {time.time() - t0:.1f}s", flush=True)
    return r_oof, p_rand


def shrink_params(ds, r_oof, s, leak_s):
    """tau^2, sigma^2 from out-of-source residuals of training sources only (rows of s and copies of s excluded)."""
    m = (ds.group != s) & ~leak_s
    d = pd.DataFrame({"g": ds.group[m], "r": r_oof[m]})
    st = d.groupby("g").r.agg(["mean", "var", "size"])
    w = st[st["size"] >= 2]
    sigma2 = float(((w["size"] - 1) * w["var"]).sum() / (w["size"] - 1).sum())
    tau2 = float(max(0.0, st["mean"].var(ddof=1) - sigma2 * np.mean(1.0 / st["size"])))
    return tau2, sigma2, int(len(st))


# ------------------------------------------------------------------ per-source protocol
def run_source(name, ds, s, r_oof, do_ret):
    n_all = len(ds.y)
    te_mask = ds.group == s
    leak_s = leak_mask_for_source(ds, s)
    tr_mask = ~te_mask & ~leak_s
    idx = np.where(te_mask)[0]
    tr_idx = np.where(tr_mask)[0]
    ns = len(idx)
    Xs, ys = ds.X[idx], ds.y[idx]
    base = make_model("RF", 0).fit(ds.X[tr_mask], ds.y[tr_mask])
    pb = base.predict(Xs)
    res = ys - pb
    tau2, sigma2, n_train_src = shrink_params(ds, r_oof, s, leak_s)
    if do_ret:
        pb150 = rf_ret(0).fit(ds.X[tr_mask], ds.y[tr_mask]).predict(Xs)
    # candidate fake sources: other sources, no copy relation with s
    gsz = pd.Series(ds.group[~te_mask & ~leak_s]).value_counts()
    leak_src = set(pd.unique(ds.group[leak_s]))
    gsz = gsz[[g not in leak_src for g in gsz.index]]
    rows_of = {g: np.where(ds.group == g)[0] for g in gsz.index}
    recs = []
    for k in KS:
        n_draws = 1 if k == 0 else N_DRAWS
        wk = (k * tau2 / (k * tau2 + sigma2)) if (k > 0 and tau2 > 0) else 0.0
        for r in range(n_draws):
            rng = np.random.default_rng([crc(name), crc(s), k, r])
            loc = np.sort(rng.choice(ns, size=k, replace=False)) if k else np.array([], int)
            test = np.setdiff1d(np.arange(ns), loc)
            e0 = res[test]
            sse0 = float(np.sum(e0 ** 2))
            off = float(res[loc].mean()) if k else 0.0
            # fake offset from another random source's out-of-source residuals
            if k:
                rng2 = np.random.default_rng([crc(name), crc(s), k, r, 7])
                cand = gsz[gsz >= k].index.values
                fsrc = cand[rng2.integers(len(cand))]
                frows = rng2.choice(rows_of[fsrc], size=k, replace=False)
                off_f = float(r_oof[frows].mean())
            else:
                fsrc, off_f = "", 0.0
            preds = {"OFF": e0 - off, "SHR": e0 - wk * off, "FAKE": e0 - off_f, "FAKE_SHR": e0 - wk * off_f}
            for meth, e in preds.items():
                ssek = float(np.sum(e ** 2))
                recs.append(dict(dataset=name, source=s, n_rows=ns, k=k, draw=r, method=meth, n_test=len(test),
                                 sse0=sse0, ssek=ssek, offset=off if meth in ("OFF", "SHR") else off_f,
                                 weight=1.0 if meth in ("OFF", "FAKE") else wk, fake_source=fsrc if "FAKE" in meth else ""))
            if do_ret and r < N_RET_DRAWS:
                e150 = ys[test] - pb150[test]
                if k == 0:
                    ssek = float(np.sum(e150 ** 2))
                else:
                    tr2 = np.concatenate([tr_idx, idx[loc]])
                    sw = np.concatenate([np.ones(len(tr_idx)), np.full(k, RET_WEIGHT)])
                    m = rf_ret(0).fit(ds.X[tr2], ds.y[tr2], sample_weight=sw)
                    ssek = float(np.sum((ys[test] - m.predict(Xs[test])) ** 2))
                recs.append(dict(dataset=name, source=s, n_rows=ns, k=k, draw=r, method="RET", n_test=len(test),
                                 sse0=float(np.sum(e150 ** 2)), ssek=ssek, offset=np.nan, weight=RET_WEIGHT,
                                 fake_source=""))
    meta = dict(dataset=name, source=s, n_rows=ns, n_train_rows=int(tr_mask.sum()), n_leak_rows_removed=int(leak_s.sum()),
                tau2=tau2, sigma2=sigma2, n_train_sources_for_shr=n_train_src,
                w_shr_k1=(tau2 / (tau2 + sigma2)) if tau2 > 0 else 0.0,
                w_shr_k3=(3 * tau2 / (3 * tau2 + sigma2)) if tau2 > 0 else 0.0,
                lopo_bias=float(res.mean()), lopo_rmse=rmse(ys, pb), lopo_resid_sd=float(res.std(ddof=1)),
                in_ret=bool(do_ret), n_fake_candidates=int(len(gsz)))
    rows = pd.DataFrame({"dataset": name, "source": s, "row": idx, "y": ys, "pred_lopo_rf300": pb, "resid_lopo": res,
                         "resid_oof_gkf10": r_oof[idx]})
    return pd.DataFrame(recs), meta, rows


def cmd_run(name, budget):
    t0 = time.time()
    ds = load(name)
    outdir = os.path.join(PARTS, name)
    os.makedirs(outdir, exist_ok=True)
    elig = eligible_sources(ds)
    rsub, rnote = ret_sources(ds, elig)
    json.dump({"eligible": elig, "ret_sources": rsub, "ret_note": rnote, "n_rows": int(len(ds.y)),
               "n_sources": int(len(set(ds.group)))}, open(os.path.join(outdir, "sources.json"), "w"), indent=1)
    r_oof, p_rand = prep(name, ds, outdir)
    assert len({crc(s) for s in elig}) == len(elig), "crc32 collision between source names"
    done = 0
    for i, s in enumerate(elig):
        f = part_path(outdir, "src", s)
        if os.path.exists(f):
            done += 1
            continue
        if time.time() - t0 > budget:
            print(f"[{name}] budget reached: {done}/{len(elig)} sources done -> INCOMPLETE, re-run to resume", flush=True)
            return 1
        ts = time.time()
        recs, meta, rows = run_source(name, ds, s, r_oof, s in rsub)
        meta["seconds"] = round(time.time() - ts, 2)
        rows.to_csv(part_path(outdir, "rows", s), index=False)
        json.dump(meta, open(part_path(outdir, "meta", s, "json"), "w"))
        recs.to_csv(f + ".tmp", index=False)
        os.replace(f + ".tmp", f)  # part file appears only when complete
        done += 1
        print(f"[{name}] {done}/{len(elig)} {s[:45]:45s} n={meta['n_rows']:4d} bias={meta['lopo_bias']:+.3f} "
              f"tau2={meta['tau2']:.4g} sig2={meta['sigma2']:.4g} ret={meta['in_ret']} {meta['seconds']}s", flush=True)
    print(f"[{name}] COMPLETE {done}/{len(elig)} sources in {time.time() - t0:.1f}s", flush=True)
    return 0


# ------------------------------------------------------------------ aggregation
def per_source_table(dr):
    dr = dr.copy()
    dr["rmse0"] = np.sqrt(dr.sse0 / dr.n_test)
    dr["rmsek"] = np.sqrt(dr.ssek / dr.n_test)
    ok = dr.rmse0 > 1e-12
    dr["rel_change"] = np.where(ok, dr.rmsek / dr.rmse0.where(ok, np.nan) - 1, np.nan)
    g = dr.groupby(["dataset", "source", "n_rows", "method", "k"], sort=False)
    t = g.agg(n_draws=("draw", "size"), draw_mean_rel_change=("rel_change", "mean"),
              draw_median_rel_change=("rel_change", "median"),
              frac_draws_improved=("rel_change", lambda v: float(np.mean(v < 0))),
              rmse0=("rmse0", "mean"), rmsek=("rmsek", "mean"), sse0_mean=("sse0", "mean"), ssek_mean=("ssek", "mean"),
              n_test=("n_test", "mean"), n_draws_rmse0_zero=("rel_change", lambda v: int(np.isnan(v).sum()))).reset_index()
    t["improved"] = t.draw_mean_rel_change < 0
    return t


def curve_rows(ps, name, scope, rand_pool, rand_src):
    out = []
    for (meth, k), sub in ps.groupby(["method", "k"]):
        v = sub.draw_mean_rel_change.values
        lo, hi = boot_ci(v, seed=0)
        r0 = float(np.sqrt(sub.sse0_mean.sum() / sub.n_test.sum()))
        rk = float(np.sqrt(sub.ssek_mean.sum() / sub.n_test.sum()))
        den = r0 - rand_pool
        r0s = float(np.mean(np.sqrt(sub.sse0_mean / sub.n_test)))
        rks = float(np.mean(np.sqrt(sub.ssek_mean / sub.n_test)))
        rs = float(np.mean([rand_src[s] for s in sub.source]))
        den_s = r0s - rs
        out.append(dict(dataset=name, scope=scope, method=meth, k=int(k), n_sources=int(len(sub)),
                        mean_rel_change=float(np.nanmean(v)), ci_lo=lo, ci_hi=hi,
                        median_rel_change=float(np.nanmedian(v)), frac_improved=float(np.mean(v < 0)),
                        rmse0_pooled=r0, rmsek_pooled=rk, rmse_randcv_pooled=rand_pool,
                        gap_closure_pooled=float((r0 - rk) / den) if den > 0 else np.nan,
                        rmse0_srcmean=r0s, rmsek_srcmean=rks, rmse_randcv_srcmean=rs,
                        gap_closure_srcmean=float((r0s - rks) / den_s) if den_s > 0 else np.nan))
    return out


def explore_dataset(name, ds, rows, meta, ps):
    """EXPLORATORY (post hoc, defined in process/h4_log.md 10:50 before computing; not graded).
    (a) offset signal-to-noise diagnostics; (b) material-disjoint anchors: the main run's anchor draws (same rng seeds),
    but every evaluation row sharing a material with any anchor row is dropped. OFF and SHR only; cached LOPO residuals."""
    from scipy.stats import spearmanr
    mt = meta.set_index("source")
    # FIX STAGE: sources whose within-source residual SD is 0 (one measurement repeated, e.g. 3 ES1 sources) give
    # SNR = inf; they are excluded from the SNR median / Spearman and counted.
    zero_sd = mt.lopo_resid_sd.fillna(0) <= 1e-12
    snr = (mt.lopo_bias.abs() / mt.lopo_resid_sd)[~zero_sd]
    off3 = ps[(ps.method == "OFF") & (ps.k == 3)].set_index("source").draw_mean_rel_change
    common = [s for s in off3.index if s in snr.index]
    rho, p = spearmanr(snr.loc[common].values, off3.loc[common].values)
    vb_corr = mt.lopo_bias.var(ddof=1) - (mt.lopo_resid_sd ** 2 / mt.n_rows).mean()
    vw = (mt.lopo_resid_sd ** 2).mean()
    kurt = rows.groupby("source").resid_lopo.apply(lambda v: pd.Series(v - v.mean()).kurt()).median()
    diag = dict(dataset=name, n_sources=int(len(mt)), n_zero_sd_sources_excluded_from_snr=int(zero_sd.sum()),
                median_abs_bias_over_sd=float(snr.median()),
                frac_sources_snr_gt_1=float((snr > 1).mean()), lopo_between_var=float(vb_corr), lopo_within_var=float(vw),
                lopo_between_share=float(max(vb_corr, 0) / (max(vb_corr, 0) + vw)),
                median_within_source_excess_kurtosis=float(kurt), spearman_snr_vs_OFF_k3=float(rho), spearman_p=float(p),
                tau2_oof_median=float(mt.tau2.median()), sigma2_oof_median=float(mt.sigma2.median()))
    recs = []
    n_single = 0
    for s, r in rows.groupby("source", sort=False):
        res = r.resid_lopo.values
        mat = ds.material[r.row.values.astype(int)]
        ns = len(res)
        nmat = len(set(mat))
        if nmat < 2:
            n_single += 1
            continue
        tau2, sigma2 = float(mt.loc[s, "tau2"]), float(mt.loc[s, "sigma2"])
        for k in KS[1:]:
            wk = (k * tau2 / (k * tau2 + sigma2)) if tau2 > 0 else 0.0
            for d in range(N_DRAWS):
                rng = np.random.default_rng([crc(name), crc(s), k, d])
                loc = np.sort(rng.choice(ns, size=k, replace=False))
                test = np.where(~np.isin(mat, mat[loc]))[0]
                if len(test) == 0:
                    continue
                e0 = res[test]
                r0 = float(np.sqrt(np.mean(e0 ** 2)))
                off = float(res[loc].mean())
                for meth, e in (("OFF", e0 - off), ("SHR", e0 - wk * off)):
                    rk = float(np.sqrt(np.mean(e ** 2)))
                    recs.append(dict(dataset=name, source=s, n_rows=ns, n_materials=nmat, method=meth, k=k, draw=d,
                                     n_test=len(test), rmse0=r0, rmsek=rk, rel_change=rk / r0 - 1 if r0 > 1e-12 else np.nan))
    md = pd.DataFrame(recs)
    if len(md) == 0:
        return diag, pd.DataFrame(), [], n_single
    mps = md.groupby(["dataset", "source", "n_rows", "n_materials", "method", "k"]).agg(
        n_draws_used=("draw", "size"), draw_mean_rel_change=("rel_change", "mean"), rmse0=("rmse0", "mean"),
        rmsek=("rmsek", "mean"), n_test_mean=("n_test", "mean")).reset_index()
    mps["improved"] = mps.draw_mean_rel_change < 0
    curves = []
    for (meth, k), sub in mps.groupby(["method", "k"]):
        v = sub.draw_mean_rel_change.values
        lo, hi = boot_ci(v, seed=0)
        main = ps[(ps.method == meth) & (ps.k == k) & ps.source.isin(sub.source)].draw_mean_rel_change
        curves.append(dict(dataset=name, method=meth, k=int(k), n_sources=int(len(sub)), mean_rel_change=float(np.nanmean(v)),
                           ci_lo=lo, ci_hi=hi, median_rel_change=float(np.nanmedian(v)), frac_improved=float(np.mean(v < 0)),
                           main_run_same_sources_mean=float(main.mean()), n_single_material_sources_excluded=n_single))
    return diag, mps, curves, n_single


def jdefault(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(type(o))


def part_path(outdir, kind, s, ext="csv"):
    return os.path.join(outdir, f"{kind}_{crc(s):08x}.{ext}")


def fmt(x, p=3):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.{p}f}"


def cmd_aggregate():
    all_draws, all_ps, all_curves, all_rows, all_meta = [], [], [], [], []
    x_diag, x_mps, x_curves, x_ledger = [], [], [], []
    summary = {"hypothesis": "H4", "title": "Anchor (reference-point) join protocol",
               "prereg_items": ["H4 eligibility", "OFF", "SHR", "RET", "FAKE control", "k in {0,1,2,3,5}", "30 draws",
                                "per-source RMSE_k/RMSE_0-1 with source-bootstrap CI", "fraction improved",
                                "gap closure", "dataset rule", "overall >=4/6", "secondary SHR k=1 <= 0 in >=4/6"],
               "protocol": {"base_model": "RF 300 trees (vrr_common.make_model('RF',0)), leave-one-source-out, "
                                          "held-out source's copies removed (leak_mask_for_source)",
                            "ks": KS, "n_draws": N_DRAWS, "k0_draws": 1, "ret": {"weight": RET_WEIGHT, "draws": N_RET_DRAWS,
                                                                                 "trees": RET_TREES,
                                                                                 "reference": "RF150 base, same seed, no anchors"},
                            "shr_estimator": "tau2/sigma2 from GroupKFold(10, seed 0) out-of-source RF residuals (per-fold "
                                             "leak removal) of all sources except s and except copies of s; sigma2 = pooled "
                                             "within-source variance (sources with n>=2); tau2 = max(0, Var_j(mean_j) - "
                                             "sigma2*mean_j(1/n_j))",
                            "fake": "unshrunk mean of k GroupKFold out-of-source residuals from one random other source "
                                    "(no copy relation with s, >= k rows)",
                            "fake_shr": "EXPLORATORY: fake offset times the SHR weight",
                            "gap_closure": "(RMSE_0 - RMSE_k)/(RMSE_0 - RMSE_randomCV); pooled rows (primary) and "
                                           "source-mean (secondary); random CV = RF 5-fold, 5 seeds, raw data",
                            "rule": "PASS iff exists m in {OFF,SHR}: mean(k=3) <= -0.10 and CI_hi(k=3) < 0; and "
                                    "FAKE mean(k=3) >= -0.02"},
               "datasets": {}, "deviations": [], "warnings": []}
    ledger = []
    passes, sec_hold, graded_status = [], [], {}
    for name in ALL_DS:
        outdir = os.path.join(PARTS, name)
        sj = os.path.join(outdir, "sources.json")
        graded = name in GRADED
        if not os.path.exists(sj):
            summary["datasets"][name] = {"status": "not run"}
            if graded:
                ledger.append(dict(hypothesis="H4", test_id="H4_join", dataset=name, model="RF", verdict="INCONCLUSIVE",
                                   threshold="see PREREG H4", note="not run"))
                graded_status[name] = "INCONCLUSIVE"
            continue
        info = json.load(open(sj))
        elig, rsub = info["eligible"], info["ret_sources"]
        files = [part_path(outdir, "src", s) for s in elig if os.path.exists(part_path(outdir, "src", s))]
        complete = len(files) == len(elig)
        ds = load(name)
        z = np.load(os.path.join(outdir, "prep.npz"), allow_pickle=True)
        p_rand, r_oof = z["p_rand"], z["r_oof"]
        dr = pd.concat([pd.read_csv(f, keep_default_na=False, na_values=["", "nan", "NaN"]) for f in files],
                       ignore_index=True)
        dr["source"] = dr.source.astype(str)
        done_src = [s for s in elig if os.path.exists(part_path(outdir, "src", s))]
        meta = pd.DataFrame([json.load(open(part_path(outdir, "meta", s, "json"))) for s in done_src])
        meta["source"] = meta.source.astype(str)
        rows = pd.concat([pd.read_csv(part_path(outdir, "rows", s), keep_default_na=False,
                                      na_values=["", "NaN"]) for s in done_src], ignore_index=True)
        all_draws.append(dr); all_meta.append(meta); all_rows.append(rows)
        ps = per_source_table(dr)
        ps = ps.merge(meta[["source", "tau2", "sigma2", "w_shr_k1", "w_shr_k3", "lopo_bias", "lopo_rmse", "in_ret"]],
                      on="source", how="left")
        all_ps.append(ps)
        # random-CV RMSE on eligible-source rows (mean over seeds), pooled and per source
        em = np.isin(ds.group, elig)
        rand_pool = float(np.mean([rmse(ds.y[em], p_rand[em, j]) for j in range(p_rand.shape[1])]))
        rand_all = float(np.mean([rmse(ds.y, p_rand[:, j]) for j in range(p_rand.shape[1])]))
        rand_src = {s: float(np.mean([rmse(ds.y[ds.group == s], p_rand[ds.group == s, j])
                                      for j in range(p_rand.shape[1])])) for s in elig}
        oof_rmse_elig = rmse(ds.y[em], ds.y[em] - r_oof[em])
        same_scope = set(rsub) == set(elig)
        cur = curve_rows(ps[ps.method != "RET"] if not same_scope else ps, name, "all_eligible", rand_pool, rand_src)
        if not same_scope:
            pr = ps[ps.source.isin(rsub)]
            rm = np.isin(ds.group, rsub)
            rand_pool_r = float(np.mean([rmse(ds.y[rm], p_rand[rm, j]) for j in range(p_rand.shape[1])]))
            cur += curve_rows(pr, name, "ret_subset", rand_pool_r, rand_src)
        cdf = pd.DataFrame(cur)
        all_curves.append(cdf)

        def get(meth, k, scope="all_eligible"):
            r = cdf[(cdf.method == meth) & (cdf.k == k) & (cdf.scope == scope)]
            return r.iloc[0].to_dict() if len(r) else None

        dsum = {"graded": graded, "complete": complete, "n_rows": int(len(ds.y)), "n_sources": int(len(set(ds.group))),
                "n_eligible_sources": len(elig), "n_rows_eligible": int(em.sum()), "ret_scope": info["ret_note"],
                "n_ret_sources": len(rsub), "rmse_randcv_all_rows": rand_all, "rmse_randcv_eligible_rows": rand_pool,
                "rmse_gkf10_oof_eligible_rows": oof_rmse_elig,
                "rmse_lopo_eligible_rows": float(np.sqrt(np.mean(rows.resid_lopo ** 2))),
                "tau2_median_over_sources": float(meta.tau2.median()), "sigma2_median_over_sources": float(meta.sigma2.median()),
                "between_share_median": float((meta.tau2 / (meta.tau2 + meta.sigma2)).median()),
                "w_shr_k1_median": float(meta.w_shr_k1.median()), "w_shr_k3_median": float(meta.w_shr_k3.median()),
                "lopo_bias_sd_over_sources": float(meta.lopo_bias.std(ddof=1)),
                "n_draws_with_rmse0_zero": int(ps.n_draws_rmse0_zero.sum()),
                "curves_k3": {m: get(m, 3) or get(m, 3, "ret_subset") for m in METHODS},
                "curves_k1": {m: get(m, 1) or get(m, 1, "ret_subset") for m in METHODS}}
        if not same_scope:
            dsum["ret_subset_k3"] = {m: get(m, 3, "ret_subset") for m in METHODS}
        tid = "H4_join" if graded else "H4_join_descriptive"
        if len(elig) < MIN_SOURCES or not complete:
            reason = (f"only {len(elig)} sources with >= {MIN_ROWS} rows" if len(elig) < MIN_SOURCES
                      else f"incomplete: {len(files)}/{len(elig)} sources")
            v = "INCONCLUSIVE" if graded else "DESCRIPTIVE"
            dsum["verdict"] = v
            dsum["verdict_reason"] = reason
        off3, shr3, fake3, shr1 = get("OFF", 3), get("SHR", 3), get("FAKE", 3), get("SHR", 1)
        crit = {}
        for m, c in (("OFF", off3), ("SHR", shr3)):
            crit[m] = {"mean": c["mean_rel_change"], "ci_hi": c["ci_hi"],
                       "mean_ok": c["mean_rel_change"] <= THR_MAIN, "ci_ok": c["ci_hi"] < 0}
            crit[m]["both"] = crit[m]["mean_ok"] and crit[m]["ci_ok"]
        fake_ok = fake3["mean_rel_change"] >= THR_FAKE
        main_ok = crit["OFF"]["both"] or crit["SHR"]["both"]
        rule_pass = bool(main_ok and fake_ok)
        sec = shr1["mean_rel_change"] <= THR_SECONDARY
        dsum["criteria"] = {"OFF_k3": crit["OFF"], "SHR_k3": crit["SHR"],
                            "FAKE_k3": {"mean": fake3["mean_rel_change"], "ok": bool(fake_ok)},
                            "rule_pass": rule_pass, "secondary_SHR_k1": {"mean": shr1["mean_rel_change"], "holds": bool(sec)}}
        n_el = len(elig)
        thr_main = ("PASS iff [OFF or SHR k=3: mean rel. change <= -10% AND source-bootstrap CI upper < 0] AND "
                    "FAKE k=3 mean rel. change >= -2%")
        if graded and len(elig) >= MIN_SOURCES and complete:
            v = "PASS" if rule_pass else "FAIL"
            graded_status[name] = v
            passes.append(rule_pass)
            sec_hold.append(bool(sec))
            dsum["verdict"] = v
            why = []
            for m in ("OFF", "SHR"):
                c = crit[m]
                why.append(f"{m} k3 mean {c['mean']:+.3f} ({'ok' if c['mean_ok'] else 'NOT <= -0.10'}), "
                           f"CI_hi {c['ci_hi']:+.3f} ({'ok' if c['ci_ok'] else 'NOT < 0'})")
            why.append(f"FAKE k3 mean {fake3['mean_rel_change']:+.3f} ({'ok' if fake_ok else 'NOT >= -0.02'})")
            best = "SHR" if crit["SHR"]["both"] and (not crit["OFF"]["both"] or shr3["mean_rel_change"] < off3["mean_rel_change"]) else "OFF"
            bc = shr3 if best == "SHR" else off3
            ledger.append(dict(hypothesis="H4", test_id="H4_join", dataset=name, model="RF",
                               metric=f"mean rel. RMSE change k=3 (best of OFF/SHR satisfying rule: {best})" if main_ok
                               else "mean rel. RMSE change k=3 (OFF/SHR, neither satisfies rule; SHR shown)",
                               value=bc["mean_rel_change"] if main_ok else shr3["mean_rel_change"],
                               ci_lo=bc["ci_lo"] if main_ok else shr3["ci_lo"],
                               ci_hi=bc["ci_hi"] if main_ok else shr3["ci_hi"],
                               threshold=thr_main, verdict=v, n_units=n_el, note="; ".join(why)))
            ledger.append(dict(hypothesis="H4", test_id="H4_secondary_SHR_k1", dataset=name, model="RF",
                               metric="SHR k=1 mean rel. RMSE change", value=shr1["mean_rel_change"],
                               ci_lo=shr1["ci_lo"], ci_hi=shr1["ci_hi"],
                               threshold="secondary prediction: SHR k=1 mean rel. change <= 0 (holds in >= 4/6 -> PASS)",
                               verdict="PASS" if sec else "FAIL", n_units=n_el,
                               note=f"median {shr1['median_rel_change']:+.3f}; frac improved {shr1['frac_improved']:.2f}"))
        elif graded:
            graded_status[name] = dsum["verdict"]
            ledger.append(dict(hypothesis="H4", test_id="H4_join", dataset=name, model="RF", verdict="INCONCLUSIVE",
                               threshold=thr_main, n_units=n_el, note=dsum.get("verdict_reason", "")))
        else:
            dsum["verdict"] = "DESCRIPTIVE"
            ledger.append(dict(hypothesis="H4", test_id="H4_join_descriptive", dataset=name, model="RF",
                               metric="SHR k=3 mean rel. RMSE change", value=shr3["mean_rel_change"], ci_lo=shr3["ci_lo"],
                               ci_hi=shr3["ci_hi"], threshold="not graded (PREREG: DYE descriptive only; "
                                                              f"{n_el} sources with >= 8 rows < 8)",
                               verdict="DESCRIPTIVE", n_units=n_el,
                               note=f"rule would be {'met' if rule_pass else 'not met'} (not graded); OFF k3 "
                                    f"{off3['mean_rel_change']:+.3f} CI_hi {off3['ci_hi']:+.3f}; FAKE k3 "
                                    f"{fake3['mean_rel_change']:+.3f}; SHR k1 {shr1['mean_rel_change']:+.3f}"))
        # component / descriptive rows (k=3)
        for m in ["OFF", "SHR", "FAKE", "RET", "FAKE_SHR"]:
            scope = "all_eligible"
            c = get(m, 3)
            if c is None:
                c, scope = get(m, 3, "ret_subset"), "ret_subset"
            if c is None:
                continue
            if m == "FAKE":
                met = c["mean_rel_change"] >= THR_FAKE
                thr = "component of H4_join: FAKE k=3 mean rel. change >= -2%"
            elif m in ("OFF", "SHR"):
                met = c["mean_rel_change"] <= THR_MAIN and c["ci_hi"] < 0
                thr = "component of H4_join: k=3 mean rel. change <= -10% and CI upper < 0"
            else:
                met = None
                thr = "not part of pass rule"
            note = (f"scope={scope}; median {c['median_rel_change']:+.3f}; frac sources improved {c['frac_improved']:.2f}; "
                    f"gap closure pooled {fmt(c['gap_closure_pooled'])}, source-mean {fmt(c['gap_closure_srcmean'])}")
            if met is not None:
                note = f"sub-criterion {'met' if met else 'NOT met'}; " + note
            if m == "RET":
                note += f"; RF{RET_TREES}, weight {RET_WEIGHT:g}, {N_RET_DRAWS} draws; reference = RF{RET_TREES} base"
            if m == "FAKE_SHR":
                note += "; EXPLORATORY stricter control (not preregistered)"
            ledger.append(dict(hypothesis="H4", test_id=f"H4_{m}_k3", dataset=name, model="RF" if m != "RET" else f"RF{RET_TREES}",
                               metric="mean rel. RMSE change k=3 (source mean of draw means)",
                               value=c["mean_rel_change"], ci_lo=c["ci_lo"], ci_hi=c["ci_hi"], threshold=thr,
                               verdict="EXPLORATORY" if m == "FAKE_SHR" else "DESCRIPTIVE", n_units=c["n_sources"], note=note))
        if not same_scope:
            for m in ["OFF", "SHR", "RET"]:
                c = get(m, 3, "ret_subset")
                ledger.append(dict(hypothesis="H4", test_id=f"H4_{m}_k3_retsubset", dataset=name,
                                   model="RF" if m != "RET" else f"RF{RET_TREES}",
                                   metric="mean rel. RMSE change k=3 on the 30-source RET subset",
                                   value=c["mean_rel_change"], ci_lo=c["ci_lo"], ci_hi=c["ci_hi"],
                                   threshold="not part of pass rule (like-for-like comparison with RET)",
                                   verdict="DESCRIPTIVE", n_units=c["n_sources"],
                                   note=f"median {c['median_rel_change']:+.3f}; frac improved {c['frac_improved']:.2f}; "
                                        f"gap closure pooled {fmt(c['gap_closure_pooled'])}"))
        summary["datasets"][name] = dsum
        # ---------------- EXPLORATORY (not graded)
        diag, mps, xc, n_single = explore_dataset(name, ds, rows, meta, ps)
        x_diag.append(diag); x_mps.append(mps); x_curves += xc
        x_ledger.append(dict(hypothesis="H4", test_id="H4X_offset_snr", dataset=name, model="RF",
                             metric="median over sources of |LOPO mean residual| / within-source residual SD",
                             value=diag["median_abs_bias_over_sd"], threshold="none (post hoc diagnostic)",
                             verdict="EXPLORATORY", n_units=diag["n_sources"],
                             note=(f"post hoc after DES_RHO FAIL; {diag['n_zero_sd_sources_excluded_from_snr']} source(s) with "
                                   f"zero within-source SD (SNR=inf) excluded; "
                                   f"LOPO between-source share {diag['lopo_between_share']:.2f}; "
                                   f"median within-source excess kurtosis {diag['median_within_source_excess_kurtosis']:+.2f}; "
                                   f"Spearman(SNR, OFF k3 change) {diag['spearman_snr_vs_OFF_k3']:+.2f} (largely mechanical)")))
        for c in xc:
            if c["k"] != 3:
                continue
            x_ledger.append(dict(hypothesis="H4", test_id=f"H4X_matdisjoint_{c['method']}_k3", dataset=name, model="RF",
                                 metric="mean rel. RMSE change k=3, evaluation rows restricted to materials not among anchors",
                                 value=c["mean_rel_change"], ci_lo=c["ci_lo"], ci_hi=c["ci_hi"],
                                 threshold="none (post hoc robustness check; same draws as main run)",
                                 verdict="EXPLORATORY", n_units=c["n_sources"],
                                 note=(f"main run on the same {c['n_sources']} sources: {c['main_run_same_sources_mean']:+.3f}; "
                                       f"median {c['median_rel_change']:+.3f}; frac improved {c['frac_improved']:.2f}; "
                                       f"{n_single} single-material sources excluded")))
        dsum["exploratory"] = {"offset_snr": diag,
                               "material_disjoint_k3": {c["method"]: c for c in xc if c["k"] == 3},
                               "material_disjoint_k1": {c["method"]: c for c in xc if c["k"] == 1}}
        print(f"{name:8s} verdict={dsum['verdict']:12s} OFF3 {off3['mean_rel_change']:+.3f} [{off3['ci_lo']:+.3f},{off3['ci_hi']:+.3f}] "
              f"SHR3 {shr3['mean_rel_change']:+.3f} [{shr3['ci_lo']:+.3f},{shr3['ci_hi']:+.3f}] FAKE3 {fake3['mean_rel_change']:+.3f} "
              f"SHR1 {shr1['mean_rel_change']:+.3f}", flush=True)
    n_pass, n_sec = int(sum(passes)), int(sum(sec_hold))
    overall = "PASS" if n_pass >= N_PASS_NEEDED else "FAIL"
    overall_sec = "PASS" if n_sec >= N_PASS_NEEDED else "FAIL"
    n_grad = len(passes)
    summary["overall"] = {"verdict": overall, "n_datasets_pass": n_pass, "n_datasets_graded": n_grad,
                          "per_dataset": graded_status, "rule": ">= 4 of 6 graded datasets PASS (no PARTIAL band in PREREG)",
                          "secondary_verdict": overall_sec, "secondary_n_hold": n_sec,
                          "secondary_rule": "SHR k=1 mean rel. change <= 0 in >= 4 of 6"}
    ledger.append(dict(hypothesis="H4", test_id="H4_overall", dataset="ALL(6 graded)", model="RF",
                       metric="number of datasets passing H4_join", value=n_pass, threshold=">= 4 of 6 datasets PASS",
                       verdict=overall, n_units=n_grad,
                       note="; ".join(f"{k}={v}" for k, v in graded_status.items()) + "; PREREG defines no PARTIAL band for H4"))
    ledger.append(dict(hypothesis="H4", test_id="H4_secondary_overall", dataset="ALL(6 graded)", model="RF",
                       metric="number of datasets where SHR k=1 mean change <= 0", value=n_sec,
                       threshold="secondary prediction holds in >= 4 of 6", verdict=overall_sec, n_units=n_grad, note=""))
    ledger += x_ledger
    pd.DataFrame(x_diag).to_csv(os.path.join(RAW, "h4_explore_offset_snr.csv"), index=False, float_format="%.6g")
    pd.concat([m for m in x_mps if len(m)], ignore_index=True).to_csv(
        os.path.join(RAW, "h4_explore_matdisjoint_per_source.csv"), index=False, float_format="%.6g")
    pd.DataFrame(x_curves).to_csv(os.path.join(RAW, "h4_explore_matdisjoint_curves.csv"), index=False, float_format="%.6g")
    # write outputs
    D = pd.concat(all_draws, ignore_index=True)
    D["rmse0"] = np.sqrt(D.sse0 / D.n_test)
    D["rmsek"] = np.sqrt(D.ssek / D.n_test)
    D["rel_change"] = D.rmsek / D.rmse0 - 1
    D.to_csv(os.path.join(RAW, "h4_anchor_draws.csv.gz"), index=False, compression="gzip", float_format="%.6g")
    PS = pd.concat(all_ps, ignore_index=True)
    cols = ["dataset", "source", "n_rows", "method", "k", "draw_mean_rel_change", "rmse0", "rmsek", "improved",
            "n_draws", "draw_median_rel_change", "frac_draws_improved", "sse0_mean", "ssek_mean", "n_test",
            "n_draws_rmse0_zero", "tau2", "sigma2", "w_shr_k1", "w_shr_k3", "lopo_bias", "lopo_rmse", "in_ret"]
    PS[cols].to_csv(os.path.join(RAW, "h4_anchor_per_source.csv"), index=False, float_format="%.6g")
    pd.concat(all_curves, ignore_index=True).to_csv(os.path.join(RAW, "h4_curves.csv"), index=False, float_format="%.6g")
    pd.concat(all_meta, ignore_index=True).to_csv(os.path.join(RAW, "h4_source_meta.csv"), index=False, float_format="%.6g")
    pd.concat(all_rows, ignore_index=True).to_csv(os.path.join(RAW, "h4_base_rows.csv"), index=False, float_format="%.6g")
    summary["files"] = {"per_source": "results/raw/h4_anchor_per_source.csv", "curves": "results/raw/h4_curves.csv",
                        "draws": "results/raw/h4_anchor_draws.csv.gz", "source_meta": "results/raw/h4_source_meta.csv",
                        "base_rows": "results/raw/h4_base_rows.csv", "ledger": "ledger/h4.csv", "log": "process/h4_log.md",
                        "exploratory": ["results/raw/h4_explore_offset_snr.csv",
                                        "results/raw/h4_explore_matdisjoint_per_source.csv",
                                        "results/raw/h4_explore_matdisjoint_curves.csv"]}
    summary["deviations"] = [
        "DEVIATION 1 (logged in the FIX STAGE; the original text wrongly said 'No deviation'): the graded run uses a "
        "single base model, RF seed 0, whereas the PREREG common protocol lists 5 seeds and HistGB/kNN as robustness "
        "models. The graded verdicts stay those of RF seed 0 (fixed before results); RF seeds 1-4, HistGB and kNN were "
        "run afterwards as EXPLORATORY robustness (scripts/h4_robust.py, summary['robustness']).",
        "DEVIATION 2: RET uses RF150 (not the shared RF300 configuration) with an RF150 no-anchor reference, for compute "
        "(RET is descriptive, not part of the pass rule).",
        "Interpretation choices (fixed before any H4 result, see process/h4_log.md 09:50): k=0 evaluated once "
        "(deterministic); FAKE uses out-of-source GroupKFold residuals of the other source; RET on all eligible sources "
        "for <=1000-row datasets and on a 30-source random subset for DES_RHO/DES_ETA/DES_MP (as PREREG allows).",
        "Added (not preregistered, labelled EXPLORATORY): FAKE_SHR control; offset signal-to-noise diagnostic; "
        "material-disjoint anchors. Defined after seeing the DES_RHO FAIL; they do not change any verdict."]
    cav = []
    for nm in GRADED:
        dd = summary["datasets"].get(nm, {})
        if "curves_k3" not in dd:
            continue
        o, h, f = dd["curves_k3"]["OFF"], dd["curves_k3"]["SHR"], dd["curves_k3"]["FAKE"]
        x = dd.get("exploratory", {}).get("material_disjoint_k3", {})
        xs = x.get("SHR")
        cav.append(f"{nm} ({dd['verdict']}): OFF k3 mean {o['mean_rel_change']:+.3f} / median~ {o['median_rel_change']:+.3f} / "
                   f"{o['frac_improved']:.0%} sources improved; SHR k3 mean {h['mean_rel_change']:+.3f} / median~ "
                   f"{h['median_rel_change']:+.3f} / {h['frac_improved']:.0%} improved; FAKE k3 {f['mean_rel_change']:+.3f}; "
                   f"pooled gap closure SHR {h['gap_closure_pooled']:+.2f}"
                   + (f"; EXPLORATORY material-disjoint SHR k3 {xs['mean_rel_change']:+.3f} [{xs['ci_lo']:+.3f}, "
                      f"{xs['ci_hi']:+.3f}] on {xs['n_sources']} multi-material sources (main run same sources "
                      f"{xs['main_run_same_sources_mean']:+.3f})" if xs else ""))
    fk = [summary["datasets"][nm]["curves_k3"]["FAKE"]["mean_rel_change"] for nm in GRADED if "curves_k3" in summary["datasets"].get(nm, {})]
    cav.append(f"FAKE control (unshrunk) hurts in every graded dataset (k3 mean {min(fk):+.3f} to {max(fk):+.3f}); the "
               f"'>= -2%' criterion was never close to binding, so it is a weak discriminator.")
    summary["caveats"] = cav
    json.dump(summary, open(os.path.join(RESULTS, "h4_summary.json"), "w"), indent=1, default=jdefault)
    ledger_write(os.path.join(LEDGER, "h4.csv"), ledger)
    print(f"OVERALL H4 {overall} ({n_pass}/{n_grad}); secondary {overall_sec} ({n_sec}/{n_grad})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "aggregate"])
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("--budget", type=float, default=480.0)
    a = ap.parse_args()
    if a.cmd == "run":
        sys.exit(cmd_run(a.dataset, a.budget))
    cmd_aggregate()
