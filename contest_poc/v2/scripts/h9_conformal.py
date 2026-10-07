"""H9 — Trust labels: only source-aware prediction intervals hold on NEW sources.

Implements PREREG.md §2 H9:
  * outer source GroupKFold(10) (vrr_common.group_folds), RF (make_model), 5 seeds (common protocol)
  * calibration residuals inside each outer-training part by
      (i)  random 5-fold          -> 'naive'
      (ii) source GroupKFold(10)  -> 'aware'
  * split-conformal 90% intervals, finite-sample quantile level ceil((n+1)*0.9)/n, score = |residual|
  * (iii) 'anchor': for outer-test sources with >= 8 rows, offset from k=3 random anchors (10 draws);
        q' from simulating the same k=3 anchor correction on calibration sources (>= 8 rows) using their
        out-of-source residuals (group residual minus its k=3 anchor mean, anchors excluded);
        coverage and width on the non-anchor rows
  * PASS iff (naive coverage < 0.85 in >= 4/7 datasets) AND (aware coverage >= 0.87 in >= 5/7)
        AND (anchor width <= 0.9 x aware width with anchor coverage >= 0.87 in >= 3/7)
  * EXPLORATORY: anchor offset with the un-recalibrated aware quantile ('explore_offset_q_aware')

FIX ROUND additions (2026-10-07, after the adversarial verification; see process/h1h9_log.md "## Fix round"):
  * --variant dedup: SENSITIVITY analysis on data with within-source exact duplicates collapsed (vrr_dedup.py).
    Graded by the same C1/C2/C3 rule as a separate 'H9_overall_dedup_sensitivity' row; the primary verdict is unchanged.
  * EXPLORATORY controls recorded in every new run (they do not consume RNG, so graded numbers are unchanged):
      explore_aware8_on_anchor_rows      aware quantile from calibration sources with >= 8 rows only, NO offset
                                         (is the C3 narrowing due to the offset or just to the >= 8-row restriction?)
      explore_anchor_matdisjoint         same anchor draws, evaluation (and q' simulation) restricted to non-anchor rows
                                         whose material differs from every anchor's material
      explore_aware_on_matdisjoint_rows  aware interval on those same material-disjoint rows (pairing for the ratio)
      n_rows_sharing_anchor_material     (column on 'anchor' records) evaluated rows that share a material with an anchor
  * --parts-dir: write parts elsewhere (used for a seed-0 re-run of the raw variant with the controls, which also
    checks that the modified code reproduces the original graded parts exactly).

Usage (run from scripts/):
  python h9_conformal.py run DATASET --seeds 0,1,2,3,4 [--variant raw|dedup] [--parts-dir DIR]
  python h9_conformal.py summarize
Interpretation choices are fixed in process/h1h9_log.md (written before any result was seen).
"""
import argparse
import glob
import json
import math
import os
import time

import numpy as np
import pandas as pd

from vrr_data import load
from vrr_common import make_model, random_folds, group_folds, leak_mask_for_source, ledger_write, RAW, RESULTS, LEDGER
from vrr_dedup import dedup

DATASETS = ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]
ALPHA = 0.10
K_ANCHOR = 3
N_DRAWS = 10
MIN_ROWS = 8
UNITS = {"ES1": "log10 nm", "ES2": "log10 nm", "DYE": "% exhaustion", "DES_RHO": "g/cm3", "DES_ETA": "log10 cP",
         "DES_MP": "K", "IL_CELL": "wt%"}
PARTS = os.path.join(RAW, "h9_parts")                 # primary (raw) graded runs, seeds 0-4
PARTS_DEDUP = os.path.join(RAW, "h9_parts_dedup")     # fix round: within-source dedup sensitivity, seeds 0-4
PARTS_RAWCTL = os.path.join(RAW, "h9_parts_rawctl")   # fix round: raw seed-0 re-run with exploratory controls
for _p in (PARTS, PARTS_DEDUP, PARTS_RAWCTL):
    os.makedirs(_p, exist_ok=True)
CTRL_METHODS = ["explore_aware8_on_anchor_rows", "explore_anchor_matdisjoint", "explore_aware_on_matdisjoint_rows"]


def conformal_q(scores, alpha=ALPHA):
    s = np.asarray(scores, float)
    n = len(s)
    level = min(1.0, math.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(s, level, method="higher"))


def union_leak(leak, groups_present, idx):
    """leak-mask restricted to index set idx: rows (of idx) that duplicate a row of any source in groups_present."""
    m = np.zeros(len(idx), bool)
    for s in groups_present:
        m |= leak[s][idx]
    return m


def run(name, seeds, variant="raw", parts_dir=None):
    ds = load(name)
    if variant == "dedup":
        ds, info = dedup(ds)
        print(f"{name}: within-source dedup {info}", flush=True)
    parts_dir = parts_dir or (PARTS if variant == "raw" else PARTS_DEDUP)
    os.makedirs(parts_dir, exist_ok=True)
    X, y, G = ds.X, ds.y, np.asarray(ds.group).astype(str)
    M = np.asarray(ds.material).astype(str)
    t0 = time.time()
    leak = {s: leak_mask_for_source(ds, s) for s in np.unique(G)}
    for seed in seeds:
        conf, persrc, rowrec = [], [], []
        outer = group_folds(G, 10, seed)
        for f, (tr, te) in enumerate(outer):
            lk = union_leak(leak, np.unique(G[te]), tr)
            n_leak_removed = int(lk.sum())
            tr = tr[~lk]
            Xtr, ytr, gtr, mtr = X[tr], y[tr], G[tr], M[tr]
            p_te = make_model("RF", seed).fit(Xtr, ytr).predict(X[te])
            e = y[te] - p_te
            # (i) naive: random 5-fold residuals in the outer-training part
            r_naive = np.full(len(tr), np.nan)
            for itr, ite in random_folds(len(tr), 5, seed):
                r_naive[ite] = ytr[ite] - make_model("RF", seed).fit(Xtr[itr], ytr[itr]).predict(Xtr[ite])
            # (ii) aware: source GroupKFold residuals in the outer-training part (leak removal inside)
            r_aware = np.full(len(tr), np.nan)
            inner = group_folds(gtr, 10, seed)
            for itr, ite in inner:
                lk_in = union_leak(leak, np.unique(gtr[ite]), tr[itr])
                itr = itr[~lk_in]
                r_aware[ite] = ytr[ite] - make_model("RF", seed).fit(Xtr[itr], ytr[itr]).predict(Xtr[ite])
            assert not np.isnan(r_naive).any() and not np.isnan(r_aware).any()
            q_n, q_a = conformal_q(np.abs(r_naive)), conformal_q(np.abs(r_aware))
            # (iii) anchor recalibration: simulate k=3 anchor correction on calibration sources
            rng1 = np.random.default_rng([seed, f, 1])
            sc = []
            sc_md, big = [], []  # exploratory controls (no extra RNG draws)
            n_cal_src = 0
            for s in sorted(np.unique(gtr)):
                idx = np.where(gtr == s)[0]
                if len(idx) < MIN_ROWS:
                    continue
                n_cal_src += 1
                r = r_aware[idx]
                ms = mtr[idx]
                big.append(np.abs(r))
                for _ in range(N_DRAWS):
                    a = rng1.choice(len(idx), K_ANCHOR, replace=False)
                    na = np.ones(len(idx), bool)
                    na[a] = False
                    sc.append(np.abs(r[na] - r[a].mean()))
                    md = na & ~np.isin(ms, ms[a])
                    sc_md.append(np.abs(r[md] - r[a].mean()))
            q_anc = conformal_q(np.concatenate(sc)) if sc else float("nan")
            n_cal_scores = int(sum(len(x) for x in sc))
            q_8 = conformal_q(np.concatenate(big)) if big else float("nan")
            smd = np.concatenate(sc_md) if sc_md else np.zeros(0)
            q_md = conformal_q(smd) if len(smd) >= 20 else float("nan")  # >= 20 scores needed for a 90% quantile
            gte = G[te]
            cov_n, cov_a = np.abs(e) <= q_n, np.abs(e) <= q_a
            common = dict(dataset=name, seed=seed, fold=f, n_test_sources=len(np.unique(gte)), n_train=len(tr),
                          n_leak_removed=n_leak_removed)
            conf.append(dict(common, method="naive", coverage=cov_n.mean(), width=2 * q_n, q=q_n, n=len(te),
                             n_cal=len(tr)))
            conf.append(dict(common, method="aware", coverage=cov_a.mean(), width=2 * q_a, q=q_a, n=len(te),
                             n_cal=len(tr)))
            for s in sorted(np.unique(gte)):
                m = gte == s
                for meth, cv_, q in (("naive", cov_n, q_n), ("aware", cov_a, q_a)):
                    persrc.append(dict(dataset=name, seed=seed, fold=f, source=s, n_rows=int(m.sum()), method=meth,
                                       covered=int(cv_[m].sum()), n_eval=int(m.sum()), width=2 * q))
            # anchors on outer-test sources with >= 8 rows
            rng2 = np.random.default_rng([seed, f, 2])
            meths = [("anchor", q_anc), ("aware_on_anchor_rows", q_a), ("explore_offset_q_aware", q_a),
                     ("explore_aware8_on_anchor_rows", q_8), ("explore_anchor_matdisjoint", q_md),
                     ("explore_aware_on_matdisjoint_rows", q_a)]
            acc = {m_: [0, 0] for m_, _ in meths}
            n_share_fold = 0
            mte = M[te]
            for s in sorted(np.unique(gte)):
                idx = np.where(gte == s)[0]
                if len(idx) < MIN_ROWS:
                    continue
                es = e[idx]
                ms = mte[idx]
                c = {m_: 0 for m_, _ in meths}
                ne, nmd, nsh = 0, 0, 0
                for _ in range(N_DRAWS):
                    a = rng2.choice(len(idx), K_ANCHOR, replace=False)
                    na = np.ones(len(idx), bool)
                    na[a] = False
                    off = es[a].mean()
                    c["anchor"] += int((np.abs(es[na] - off) <= q_anc).sum())
                    c["aware_on_anchor_rows"] += int((np.abs(es[na]) <= q_a).sum())
                    c["explore_offset_q_aware"] += int((np.abs(es[na] - off) <= q_a).sum())
                    ne += int(na.sum())
                    # exploratory controls (same draws)
                    c["explore_aware8_on_anchor_rows"] += int((np.abs(es[na]) <= q_8).sum())
                    md = na & ~np.isin(ms, ms[a])
                    nsh += int(na.sum() - md.sum())
                    if np.isfinite(q_md):
                        c["explore_anchor_matdisjoint"] += int((np.abs(es[md] - off) <= q_md).sum())
                        c["explore_aware_on_matdisjoint_rows"] += int((np.abs(es[md]) <= q_a).sum())
                        nmd += int(md.sum())
                n_share_fold += nsh
                for meth, q in meths:
                    nev = nmd if meth in ("explore_anchor_matdisjoint", "explore_aware_on_matdisjoint_rows") else ne
                    persrc.append(dict(dataset=name, seed=seed, fold=f, source=s, n_rows=len(idx), method=meth,
                                       covered=c[meth], n_eval=nev, width=2 * q,
                                       n_rows_sharing_anchor_material=nsh if meth == "anchor" else np.nan))
                    acc[meth][0] += c[meth]
                    acc[meth][1] += nev
            for meth, q in meths:
                cv_, ne = acc[meth]
                conf.append(dict(common, method=meth, coverage=(cv_ / ne) if ne else np.nan, width=2 * q, q=q, n=ne,
                                 n_cal=(n_cal_scores if meth == "anchor" else
                                        (len(smd) if meth == "explore_anchor_matdisjoint" else len(tr))),
                                 n_cal_sources=n_cal_src if meth in ("anchor", "explore_aware8_on_anchor_rows",
                                                                    "explore_anchor_matdisjoint") else np.nan,
                                 n_rows_sharing_anchor_material=n_share_fold if meth == "anchor" else np.nan))
            rowrec.append(pd.DataFrame({"dataset": name, "seed": seed, "fold": f, "row": te, "source": gte, "y": y[te],
                                        "pred": p_te, "q_naive": q_n, "q_aware": q_a, "q_anchor": q_anc}))
            print(f"  {name} seed {seed} fold {f}: q_naive {q_n:.4g} q_aware {q_a:.4g} q_anchor {q_anc:.4g} "
                  f"({time.time() - t0:.0f}s)", flush=True)
        pd.DataFrame(conf).to_csv(os.path.join(parts_dir, f"{name}__seed{seed}__conformal.csv"), index=False)
        pd.DataFrame(persrc).to_csv(os.path.join(parts_dir, f"{name}__seed{seed}__per_source.csv"), index=False)
        pd.concat(rowrec).to_csv(os.path.join(parts_dir, f"{name}__seed{seed}__rows.csv.gz"), index=False,
                                 float_format="%.6g")
        print(f"{name} seed {seed} done ({time.time() - t0:.0f}s)", flush=True)


# ------------------------------------------------------------------------------------------- summary
def boot_cov(ps, n=2000, seed=0):
    """Source bootstrap of pooled coverage; ps = per-source frame with covered, n_eval (summed over seeds)."""
    C, N = ps.covered.values.astype(float), ps.n_eval.values.astype(float)
    if len(C) < 2:
        return float("nan"), float("nan")
    idx = np.random.default_rng(seed).integers(0, len(C), (n, len(C)))
    b = C[idx].sum(1) / N[idx].sum(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def boot_ratio(num, den, n=2000, seed=0):
    num, den = np.asarray(num, float), np.asarray(den, float)
    if len(num) < 2:
        return float("nan"), float("nan")
    idx = np.random.default_rng(seed).integers(0, len(num), (n, len(num)))
    b = num[idx].sum(1) / den[idx].sum(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def fmt(x, d=3):
    return "nan" if x is None or not np.isfinite(x) else f"{x:.{d}f}"


GRADED = ["naive", "aware", "anchor", "aware_on_anchor_rows", "explore_offset_q_aware"]


def _read_parts(parts_dir):
    fc = sorted(glob.glob(os.path.join(parts_dir, "*__conformal.csv")))
    if not fc:
        return None, None, None
    conf = pd.concat([pd.read_csv(f) for f in fc])
    pers = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(parts_dir, "*__per_source.csv")))])
    rows = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(parts_dir, "*__rows.csv.gz")))])
    conf = conf.sort_values(["dataset", "seed", "fold", "method"]).reset_index(drop=True)
    pers["coverage"] = pers.covered / pers.n_eval
    pers = pers.sort_values(["dataset", "seed", "fold", "source", "method"]).reset_index(drop=True)
    return conf, pers, rows


def grade_variant(conf, pers, rows, variant, dedup_info=None):
    """PREREG H9 rule applied to one data variant. variant 'raw' = primary graded; 'dedup' = fix-round sensitivity."""
    sfx = "" if variant == "raw" else "_dedup"
    vnote = "" if variant == "raw" else \
        "FIX-ROUND SENSITIVITY (within-source exact duplicates collapsed, vrr_dedup.py); not the primary verdict. "
    datasets, ledger = {}, []
    cond = {"C1": {}, "C2": {}, "C3": {}}
    for d in DATASETS:
        dn = d + sfx
        c = conf[conf.dataset == d] if conf is not None else pd.DataFrame()
        p = pers[pers.dataset == d] if pers is not None else pd.DataFrame()
        if c.empty:
            for k in cond:
                cond[k][d] = None
            ledger.append(dict(hypothesis="H9", test_id="H9_dataset", dataset=dn, verdict="INCONCLUSIVE",
                               threshold="H9 conditions C1-C3", note=vnote + "not run"))
            continue
        seeds = sorted(c.seed.unique())
        yd = rows[(rows.dataset == d) & (rows.seed == seeds[0])]
        sd_y = float(yd.y.std(ddof=1))
        res = {"seeds": [int(s) for s in seeds], "n_rows": int(len(yd)), "n_sources": int(p.source.nunique()),
               "sd_y": sd_y, "n_sources_ge8": int(p[p.method == "anchor"].source.nunique()), "methods": {}}
        if dedup_info and d in dedup_info:
            res["dedup_info"] = dedup_info[d]
        for meth in GRADED:
            cm = c[c.method == meth]
            pm = p[p.method == meth]
            cov = cm.coverage.mul(cm.n).sum() / cm.n.sum()
            width = cm.width.mul(cm.n).sum() / cm.n.sum()
            seed_cov = cm.groupby("seed").apply(lambda z: z.coverage.mul(z.n).sum() / z.n.sum(), include_groups=False)
            ps = pm.groupby("source")[["covered", "n_eval"]].sum()
            ps["coverage"] = ps.covered / ps.n_eval
            pw = pm.assign(wn=pm.width * pm.n_eval).groupby("source")[["wn", "n_eval"]].sum()
            res["methods"][meth] = {
                "coverage": float(cov), "coverage_ci_source_boot": boot_cov(ps),
                "mean_width": float(width), "seed_coverage": [float(x) for x in seed_cov.values],
                "source_avg_coverage": float(ps.coverage.mean()),
                "share_sources_cov_lt_0.8": float((ps.coverage < 0.8).mean()),
                "share_sources_cov_lt_0.5": float((ps.coverage < 0.5).mean()),
                "n_sources": int(len(ps)), "n_evals_all_seeds": int(cm.n.sum()), "width_over_sd_y": float(width / sd_y),
                "_wn": pw.wn, "_n": pw.n_eval}
        mn, ma, mx = res["methods"]["naive"], res["methods"]["aware"], res["methods"]["anchor"]
        ms = res["methods"]["aware_on_anchor_rows"]
        ratio = mx["mean_width"] / ms["mean_width"]
        jj = mx["_wn"].index.intersection(ms["_wn"].index)
        ratio_ci = boot_ratio(mx["_wn"].loc[jj].values, ms["_wn"].loc[jj].values)
        # per-seed ratio (fix round, descriptive): is C3 met in every seed?
        cx = c[c.method == "anchor"].assign(wn=lambda z: z.width * z.n).groupby("seed")[["wn", "n"]].sum()
        cs = c[c.method == "aware_on_anchor_rows"].assign(wn=lambda z: z.width * z.n).groupby("seed")[["wn", "n"]].sum()
        seed_ratio = (cx.wn / cx.n) / (cs.wn / cs.n)
        for mm in res["methods"].values():
            mm.pop("_wn"); mm.pop("_n")
        res["anchor_width_ratio_vs_aware_same_rows"] = {"value": float(ratio), "ci_source_boot": ratio_ci,
                                                        "per_seed": [float(x) for x in seed_ratio.values]}
        res["naive_over_aware_width"] = float(mn["mean_width"] / ma["mean_width"])
        c1 = mn["coverage"] < 0.85
        c2 = ma["coverage"] >= 0.87
        c3 = (ratio <= 0.9) and (mx["coverage"] >= 0.87)
        cond["C1"][d], cond["C2"][d], cond["C3"][d] = c1, c2, c3
        res["conditions"] = {"naive_cov_lt_0.85": bool(c1), "aware_cov_ge_0.87": bool(c2),
                             "anchor_ratio_le_0.9_and_cov_ge_0.87": bool(c3)}
        datasets[d] = res
        ns, ns8 = res["n_sources"], res["n_sources_ge8"]
        nseed = len(seeds)
        sd = lambda m: f"seed range [{fmt(min(m['seed_coverage']))}, {fmt(max(m['seed_coverage']))}]"
        dnote = "" if variant == "raw" else (f"{res.get('dedup_info', {}).get('n_dropped', '?')} duplicate rows dropped "
                                             f"({res['n_rows']} rows left, {ns8} sources with >= 8 rows); ")
        ledger += [
            dict(hypothesis="H9", test_id="H9_naive_cov", dataset=dn, model="RF", metric="coverage of 90% interval, naive calib",
                 value=fmt(mn["coverage"], 4), ci_lo=fmt(mn["coverage_ci_source_boot"][0], 4),
                 ci_hi=fmt(mn["coverage_ci_source_boot"][1], 4), threshold="naive (random 5-fold) coverage on new sources < 0.85",
                 verdict="PASS" if c1 else "FAIL", n_units=ns,
                 note=vnote + dnote + f"row-pooled over {nseed} seeds; mean width {fmt(mn['mean_width'], 4)}; {sd(mn)}; source-avg coverage "
                      f"{fmt(mn['source_avg_coverage'])}; share of sources <0.8: {fmt(mn['share_sources_cov_lt_0.8'])}"),
            dict(hypothesis="H9", test_id="H9_aware_cov", dataset=dn, model="RF", metric="coverage of 90% interval, source-aware calib",
                 value=fmt(ma["coverage"], 4), ci_lo=fmt(ma["coverage_ci_source_boot"][0], 4),
                 ci_hi=fmt(ma["coverage_ci_source_boot"][1], 4), threshold="source-aware (GroupKFold) coverage >= 0.87",
                 verdict="PASS" if c2 else "FAIL", n_units=ns,
                 note=vnote + f"row-pooled over {nseed} seeds; mean width {fmt(ma['mean_width'], 4)} (= {fmt(1 / res['naive_over_aware_width'], 2)}x naive); "
                      f"{sd(ma)}; source-avg coverage {fmt(ma['source_avg_coverage'])}; share of sources <0.8: "
                      f"{fmt(ma['share_sources_cov_lt_0.8'])}"),
            dict(hypothesis="H9", test_id="H9_anchor", dataset=dn, model="RF", metric="anchor width / aware width (same rows)",
                 value=fmt(ratio, 4), ci_lo=fmt(ratio_ci[0], 4), ci_hi=fmt(ratio_ci[1], 4),
                 threshold="anchor-adjusted width <= 0.9 x source-aware AND anchor coverage >= 0.87",
                 verdict="PASS" if c3 else "FAIL", n_units=ns8,
                 note=vnote + f"anchor coverage {fmt(mx['coverage'], 4)} [{fmt(mx['coverage_ci_source_boot'][0])}, "
                      f"{fmt(mx['coverage_ci_source_boot'][1])}] on non-anchor rows of sources with >=8 rows (k=3, 10 draws); "
                      f"aware coverage on the same rows {fmt(ms['coverage'], 4)}; anchor source-avg coverage "
                      f"{fmt(mx['source_avg_coverage'])}; per-seed ratio "
                      f"[{', '.join(fmt(x) for x in res['anchor_width_ratio_vs_aware_same_rows']['per_seed'])}]"),
            dict(hypothesis="H9", test_id="H9_anchor_cov", dataset=dn, model="RF", metric="coverage, anchor-adjusted interval",
                 value=fmt(mx["coverage"], 4), ci_lo=fmt(mx["coverage_ci_source_boot"][0], 4),
                 ci_hi=fmt(mx["coverage_ci_source_boot"][1], 4), threshold="component of H9_anchor (>= 0.87)",
                 verdict="DESCRIPTIVE", n_units=ns8, note=vnote + f"{sd(mx)}; mean width {fmt(mx['mean_width'], 4)}"),
            dict(hypothesis="H9", test_id="H9_desc_source_avg_cov", dataset=dn, model="RF",
                 metric="source-averaged coverage naive|aware|anchor",
                 value=f"{fmt(mn['source_avg_coverage'])}|{fmt(ma['source_avg_coverage'])}|{fmt(mx['source_avg_coverage'])}",
                 threshold="descriptive (secondary estimand, fixed before results)", verdict="DESCRIPTIVE", n_units=ns,
                 note=vnote + "each source weighted equally; shares of sources with coverage < 0.8: "
                      f"{fmt(mn['share_sources_cov_lt_0.8'])}|{fmt(ma['share_sources_cov_lt_0.8'])}|{fmt(mx['share_sources_cov_lt_0.8'])}"),
            dict(hypothesis="H9", test_id="H9_desc_width_over_sd", dataset=dn, model="RF",
                 metric="mean interval width / SD(y): naive|aware|anchor",
                 value=f"{fmt(mn['width_over_sd_y'])}|{fmt(ma['width_over_sd_y'])}|{fmt(mx['width_over_sd_y'])}",
                 threshold="descriptive (added after results: how informative the honest interval is)",
                 verdict="DESCRIPTIVE", n_units=ns,
                 note=vnote + f"SD(y) = {sd_y:.4g} {UNITS[d]}; a 90% interval for a Gaussian with SD(y) would be 3.29 x SD"),
            dict(hypothesis="H9", test_id="H9_explore_offset_q_aware", dataset=dn, model="RF",
                 metric="coverage: anchor offset + un-recalibrated aware q",
                 value=fmt(res["methods"]["explore_offset_q_aware"]["coverage"], 4),
                 threshold="exploratory, not graded", verdict="EXPLORATORY", n_units=ns8,
                 note=vnote + "same non-anchor rows as H9_anchor; width = aware width"),
        ]
    out = {"datasets": datasets}
    tsfx = "" if variant == "raw" else "_dedup_sensitivity"
    for k, label, need, thr in [("C1", "naive coverage < 0.85", 4, ">= 4 of 7 datasets"),
                                ("C2", "aware coverage >= 0.87", 5, ">= 5 of 7 datasets"),
                                ("C3", "anchor width <= 0.9x aware and coverage >= 0.87", 3, ">= 3 of 7 datasets")]:
        npass = sum(bool(v) for v in cond[k].values() if v is not None)
        out[f"condition_{k}"] = {"label": label, "n_datasets": npass, "need": need, "holds": npass >= need,
                                 "per_dataset": {d: (None if v is None else bool(v)) for d, v in cond[k].items()}}
        ledger.append(dict(hypothesis="H9", test_id=f"H9_{k}{tsfx}", dataset="ALL7", model="RF", metric=f"datasets with {label}",
                           value=npass, threshold=thr, verdict="PASS" if npass >= need else "FAIL", n_units=7,
                           note=vnote + ", ".join(f"{d}={'yes' if v else ('n/a' if v is None else 'no')}" for d, v in cond[k].items())))
    allok = all(out[f"condition_{k}"]["holds"] for k in cond)
    n_run = sum(v is not None for v in cond["C1"].values())
    verdict = ("PASS" if allok else "FAIL") if n_run == 7 else "INCONCLUSIVE"
    out["overall"] = {"verdict": verdict, "conditions_met": int(sum(out[f'condition_{k}']['holds'] for k in cond)),
                      "n_datasets_run": n_run}
    ledger.append(dict(hypothesis="H9", test_id=f"H9_overall{tsfx}", dataset="ALL7", model="RF", metric="conditions C1,C2,C3 met",
                       value=out["overall"]["conditions_met"], threshold="all three conditions (no PARTIAL band in PREREG)",
                       verdict=verdict, n_units=7,
                       note=vnote + "; ".join(f"{k}={'met' if out[f'condition_{k}']['holds'] else 'not met'} "
                                              f"({out[f'condition_{k}']['n_datasets']}/7)" for k in cond)
                            + ("" if n_run == 7 else f"; only {n_run}/7 datasets run")))
    return out, ledger


def controls(conf, pers, variant):
    """EXPLORATORY C3 construct checks (fix round). Pooled over the seeds present in `conf`."""
    out = {}
    for d in DATASETS:
        c = conf[conf.dataset == d]
        if c.empty or "explore_aware8_on_anchor_rows" not in set(c.method):
            continue
        p = pers[pers.dataset == d]

        def pooled(m):
            z = c[c.method == m]
            n = z.n.sum()
            return (float(z.coverage.mul(z.n).sum() / n) if n else float("nan"),
                    float(z.width.mul(z.n).sum() / n) if n else float("nan"), int(n))
        cov_x, w_x, n_x = pooled("anchor")
        cov_s, w_s, _ = pooled("aware_on_anchor_rows")
        cov_8, w_8, _ = pooled("explore_aware8_on_anchor_rows")
        cov_md, w_md, n_md = pooled("explore_anchor_matdisjoint")
        cov_amd, w_amd, _ = pooled("explore_aware_on_matdisjoint_rows")
        za = c[c.method == "anchor"]
        share = float(za.n_rows_sharing_anchor_material.sum() / za.n.sum()) if za.n.sum() else float("nan")
        pmd = p[(p.method == "explore_anchor_matdisjoint") & (p.n_eval > 0)]
        r_md = w_md / w_amd if n_md else float("nan")
        out[d] = {"variant": variant, "seeds": sorted(int(s) for s in c.seed.unique()),
                  "anchor_coverage": cov_x, "anchor_ratio_vs_aware": w_x / w_s,
                  "aware8_coverage": cov_8, "aware8_ratio_vs_aware": w_8 / w_s,
                  "offset_only_ratio_anchor_vs_aware8": w_x / w_8,
                  "share_eval_rows_sharing_anchor_material": share,
                  "matdisjoint_n_evals": n_md, "matdisjoint_n_sources": int(pmd.source.nunique()),
                  "matdisjoint_coverage": cov_md, "matdisjoint_aware_coverage_same_rows": cov_amd,
                  "matdisjoint_ratio_vs_aware_same_rows": r_md,
                  "matdisjoint_c3_like_holds": bool(n_md > 0 and r_md <= 0.9 and cov_md >= 0.87)}
    return out


def summarize():
    conf, pers, rows = _read_parts(PARTS)
    conf.to_csv(os.path.join(RAW, "h9_conformal.csv"), index=False)
    pers.to_csv(os.path.join(RAW, "h9_per_source.csv"), index=False)
    rows.to_csv(os.path.join(RAW, "h9_rows.csv.gz"), index=False, float_format="%.6g")
    prim, ledger = grade_variant(conf, pers, rows, "raw")

    summary = {"hypothesis": "H9", "alpha": ALPHA, "datasets": prim["datasets"], "notes": [
        "Graded coverage = row-pooled over outer-test rows and 5 seeds; source-averaged coverage is descriptive.",
        "Conformal quantile = np.quantile(|r|, ceil((n+1)*0.9)/n, method='higher') (the common reference implementation); "
        "this picks one order statistic above the textbook ceil((n+1)*0.9)-th smallest, i.e. it is very slightly conservative.",
        "Outer and inner (source-aware) folds drop training rows that copy (key+value) a held-out source's rows; naive inner "
        "random folds do not (by definition).",
        "anchor = k=3 random anchors (10 draws) on outer-test sources with >=8 rows; q' recalibrated by simulating the same "
        "correction on calibration sources with >=8 rows using their out-of-source residuals; width ratio is paired on the "
        "same non-anchor rows (aware_on_anchor_rows).",
        "width_over_sd_y is a descriptive add-on chosen after seeing results.",
        "Coverage guarantees are marginal over rows; per-source coverage still varies (share_sources_cov_lt_0.8)."]}
    for k in ("condition_C1", "condition_C2", "condition_C3", "overall"):
        summary[k] = prim[k]

    # ---------------- fix round: within-source dedup sensitivity (all 7 datasets x 5 seeds)
    conf_d, pers_d, rows_d = _read_parts(PARTS_DEDUP)
    dinfo = {}
    if conf_d is not None:
        conf_d.to_csv(os.path.join(RAW, "h9_dedup_conformal.csv"), index=False)
        pers_d.to_csv(os.path.join(RAW, "h9_dedup_per_source.csv"), index=False)
        rows_d.to_csv(os.path.join(RAW, "h9_dedup_rows.csv.gz"), index=False, float_format="%.6g")
        for d in conf_d.dataset.unique():
            n_raw = int(len(rows[(rows.dataset == d) & (rows.seed == 0)]))
            n_dd = int(len(rows_d[(rows_d.dataset == d) & (rows_d.seed == rows_d[rows_d.dataset == d].seed.min())]))
            dinfo[d] = {"n_rows_raw": n_raw, "n_rows_dedup": n_dd, "n_dropped": n_raw - n_dd}
    sens, led_s = grade_variant(conf_d, pers_d, rows_d, "dedup", dinfo)
    ledger += led_s
    summary["dedup_sensitivity"] = sens

    # ---------------- fix round: exploratory C3 construct controls
    ctl = {}
    conf_c, pers_c, rows_c = _read_parts(PARTS_RAWCTL)
    regression = {}
    if conf_c is not None:
        ctl["raw_seed0"] = controls(conf_c, pers_c, "raw (seed 0 re-run)")
        # regression check: the modified run() must reproduce the original graded seed-0 parts
        for d in conf_c.dataset.unique():
            a = conf[(conf.dataset == d) & (conf.seed == 0) & conf.method.isin(GRADED)].sort_values(["fold", "method"])
            b = conf_c[(conf_c.dataset == d) & conf_c.method.isin(GRADED)].sort_values(["fold", "method"])
            regression[d] = {k: float(np.nanmax(np.abs(a[k].values - b[k].values))) for k in ["coverage", "q", "n"]} \
                if len(a) == len(b) else "row count mismatch"
    if conf_d is not None:
        ctl["dedup_all_seeds"] = controls(conf_d, pers_d, "dedup")
    summary["explore_controls"] = ctl
    summary["regression_check_rawctl_vs_original_seed0"] = regression
    cframes = []
    for tag, cf, pf in (("raw_seed0", conf_c, pers_c), ("dedup", conf_d, pers_d)):
        if cf is not None:
            cframes.append(cf[cf.method.isin(["anchor", "aware_on_anchor_rows"] + CTRL_METHODS)].assign(variant=tag))
    if cframes:
        pd.concat(cframes).to_csv(os.path.join(RAW, "h9_controls.csv"), index=False)
        pd.concat([pf[pf.method.isin(["anchor", "aware_on_anchor_rows"] + CTRL_METHODS)].assign(variant=tag)
                   for tag, cf, pf in (("raw_seed0", conf_c, pers_c), ("dedup", conf_d, pers_d)) if pf is not None]) \
            .to_csv(os.path.join(RAW, "h9_controls_per_source.csv"), index=False)
    for tag, cc in ctl.items():
        for d, r in cc.items():
            dn = d if tag == "raw_seed0" else d + "_dedup"
            sn = f"{tag}: seeds {r['seeds']}"
            ledger += [
                dict(hypothesis="H9", test_id="H9_explore_ctrl_aware8", dataset=dn, model="RF",
                     metric="width ratio: aware q from >=8-row calibration sources (no offset) / aware, same rows",
                     value=fmt(r["aware8_ratio_vs_aware"], 4), threshold="exploratory, not graded (fix round)",
                     verdict="EXPLORATORY", n_units=prim["datasets"].get(d, {}).get("n_sources_ge8", ""),
                     note=f"{sn}; aware8 coverage {fmt(r['aware8_coverage'])}; anchor ratio on the same seeds "
                          f"{fmt(r['anchor_ratio_vs_aware'])} (coverage {fmt(r['anchor_coverage'])}); narrowing due to the "
                          f"offset itself = anchor/aware8 width {fmt(r['offset_only_ratio_anchor_vs_aware8'])}"),
                dict(hypothesis="H9", test_id="H9_explore_ctrl_material_overlap", dataset=dn, model="RF",
                     metric="share of evaluated non-anchor rows that share a material with an anchor",
                     value=fmt(r["share_eval_rows_sharing_anchor_material"], 4), threshold="exploratory, not graded (fix round)",
                     verdict="EXPLORATORY", n_units="",
                     note=f"{sn}; high share = the anchor gain cannot be separated from same-material calibration"),
                dict(hypothesis="H9", test_id="H9_explore_ctrl_matdisjoint", dataset=dn, model="RF",
                     metric="coverage, anchor interval on material-disjoint rows (q' re-simulated material-disjoint)",
                     value=fmt(r["matdisjoint_coverage"], 4), threshold="exploratory; C3-like = ratio <= 0.9 and coverage >= 0.87",
                     verdict="EXPLORATORY", n_units=r["matdisjoint_n_sources"],
                     note=f"{sn}; width ratio vs aware on the same rows {fmt(r['matdisjoint_ratio_vs_aware_same_rows'])}; "
                          f"aware coverage on those rows {fmt(r['matdisjoint_aware_coverage_same_rows'])}; "
                          f"{r['matdisjoint_n_evals']} evaluations from {r['matdisjoint_n_sources']} sources; C3-like holds: "
                          f"{'yes' if r['matdisjoint_c3_like_holds'] else 'no'}"),
            ]

    # ---------------- robustness statement (computed, not hand-written)
    c3_raw = [d for d, v in prim["condition_C3"]["per_dataset"].items() if v]
    c3_dd = [d for d, v in sens["condition_C3"]["per_dataset"].items() if v] if conf_d is not None else []
    md_raw = [d for d, r in ctl.get("raw_seed0", {}).items() if r["matdisjoint_c3_like_holds"]]
    md_dd = [d for d, r in ctl.get("dedup_all_seeds", {}).items() if r["matdisjoint_c3_like_holds"]]
    robust = [d for d in c3_raw if d in c3_dd and d in md_raw and d in md_dd]
    summary["robustness"] = {
        "primary_verdict": prim["overall"]["verdict"],
        "dedup_sensitivity_verdict": sens["overall"]["verdict"],
        "C3_pass_raw": c3_raw, "C3_pass_dedup": c3_dd,
        "C3_like_matdisjoint_raw_seed0": md_raw, "C3_like_matdisjoint_dedup": md_dd,
        "C3_robust_datasets(raw & dedup & material-disjoint)": robust,
        "statement": (f"H9 primary (pre-registered) verdict {prim['overall']['verdict']} "
                      f"(C1 {prim['condition_C1']['n_datasets']}/7, C2 {prim['condition_C2']['n_datasets']}/7, "
                      f"C3 {prim['condition_C3']['n_datasets']}/7). Under within-source dedup: {sens['overall']['verdict']} "
                      f"(C1 {sens['condition_C1']['n_datasets']}/7, C2 {sens['condition_C2']['n_datasets']}/7, "
                      f"C3 {sens['condition_C3']['n_datasets']}/7). "
                      + ("The PASS is NOT robust. " if prim["overall"]["verdict"] == "PASS" and sens["overall"]["verdict"] == "FAIL"
                         else ("Dedup sensitivity incomplete. " if sens["overall"]["verdict"] == "INCONCLUSIVE" else ""))
                      + f"The anchor-interval claim (C3) survives dedup and material-disjoint anchors only in: {robust}.")}
    summary["notes"] += [
        "FIX ROUND (after adversarial verification): within-source exact duplicates (same source, key and value; ES1 176, "
        "DES_MP 1209 rows) are not handled by copy_mask/leak_mask_for_source. They give zero-valued anchor-calibration "
        "scores (shrinking q') and trivially covered test rows. A dedup sensitivity re-run of the full H9 protocol "
        "(all 7 datasets x 5 seeds) is in dedup_sensitivity and ledger rows *_dedup / *_dedup_sensitivity.",
        "FIX ROUND: anchors are random rows of the new source; in datasets where a source studies one material system the "
        "anchor offset is same-material calibration, not a reference-sample effect. explore_controls quantifies this "
        "(material overlap share, material-disjoint anchors with re-simulated q', and the >=8-row calibration restriction "
        "without offset). Raw controls come from a seed-0 re-run (regression check vs the original parts included)."]
    for row in ledger:
        if row.get("test_id") == "H9_overall":
            row["note"] += f"; FIX ROUND: {summary['robustness']['statement']}"
    summary["files"] = ["results/raw/h9_conformal.csv", "results/raw/h9_per_source.csv", "results/raw/h9_rows.csv.gz",
                        "results/raw/h9_dedup_conformal.csv", "results/raw/h9_dedup_per_source.csv",
                        "results/raw/h9_dedup_rows.csv.gz", "results/raw/h9_controls.csv",
                        "results/raw/h9_controls_per_source.csv"]
    with open(os.path.join(RESULTS, "h9_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    ledger_write(os.path.join(LEDGER, "h9.csv"), ledger)
    for tag, block in (("raw", prim), ("dedup", sens)):
        for d, r in block["datasets"].items():
            m = r["methods"]
            print(tag, d, "naive %.3f aware %.3f anchor %.3f | widths %.4g %.4g %.4g ratio %.3f | src-avg %.3f %.3f %.3f" % (
                m["naive"]["coverage"], m["aware"]["coverage"], m["anchor"]["coverage"], m["naive"]["mean_width"],
                m["aware"]["mean_width"], m["anchor"]["mean_width"], r["anchor_width_ratio_vs_aware_same_rows"]["value"],
                m["naive"]["source_avg_coverage"], m["aware"]["source_avg_coverage"], m["anchor"]["source_avg_coverage"]))
        print(tag, {k: block[f"condition_{k}"]["n_datasets"] for k in ("C1", "C2", "C3")}, block["overall"])
    print(json.dumps(ctl, indent=0, default=str)[:3000])
    print("regression", regression)
    print(summary["robustness"]["statement"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "summarize"])
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--variant", default="raw", choices=["raw", "dedup"])
    ap.add_argument("--parts-dir", default=None)
    a = ap.parse_args()
    if a.mode == "run":
        run(a.dataset, [int(s) for s in a.seeds.split(",")], a.variant, a.parts_dir)
    else:
        summarize()
