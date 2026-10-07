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

Usage (run from scripts/):
  python h9_conformal.py run DATASET --seeds 0,1,2,3,4
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

DATASETS = ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]
ALPHA = 0.10
K_ANCHOR = 3
N_DRAWS = 10
MIN_ROWS = 8
UNITS = {"ES1": "log10 nm", "ES2": "log10 nm", "DYE": "% exhaustion", "DES_RHO": "g/cm3", "DES_ETA": "log10 cP",
         "DES_MP": "K", "IL_CELL": "wt%"}
PARTS = os.path.join(RAW, "h9_parts")
os.makedirs(PARTS, exist_ok=True)


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


def run(name, seeds):
    ds = load(name)
    X, y, G = ds.X, ds.y, np.asarray(ds.group).astype(str)
    t0 = time.time()
    leak = {s: leak_mask_for_source(ds, s) for s in np.unique(G)}
    for seed in seeds:
        conf, persrc, rowrec = [], [], []
        outer = group_folds(G, 10, seed)
        for f, (tr, te) in enumerate(outer):
            lk = union_leak(leak, np.unique(G[te]), tr)
            n_leak_removed = int(lk.sum())
            tr = tr[~lk]
            Xtr, ytr, gtr = X[tr], y[tr], G[tr]
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
            n_cal_src = 0
            for s in sorted(np.unique(gtr)):
                idx = np.where(gtr == s)[0]
                if len(idx) < MIN_ROWS:
                    continue
                n_cal_src += 1
                r = r_aware[idx]
                for _ in range(N_DRAWS):
                    a = rng1.choice(len(idx), K_ANCHOR, replace=False)
                    na = np.ones(len(idx), bool)
                    na[a] = False
                    sc.append(np.abs(r[na] - r[a].mean()))
            q_anc = conformal_q(np.concatenate(sc)) if sc else float("nan")
            n_cal_scores = int(sum(len(x) for x in sc))
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
            acc = {"anchor": [0, 0], "aware_on_anchor_rows": [0, 0], "explore_offset_q_aware": [0, 0]}
            for s in sorted(np.unique(gte)):
                idx = np.where(gte == s)[0]
                if len(idx) < MIN_ROWS:
                    continue
                es = e[idx]
                c = {"anchor": 0, "aware_on_anchor_rows": 0, "explore_offset_q_aware": 0}
                ne = 0
                for _ in range(N_DRAWS):
                    a = rng2.choice(len(idx), K_ANCHOR, replace=False)
                    na = np.ones(len(idx), bool)
                    na[a] = False
                    off = es[a].mean()
                    c["anchor"] += int((np.abs(es[na] - off) <= q_anc).sum())
                    c["aware_on_anchor_rows"] += int((np.abs(es[na]) <= q_a).sum())
                    c["explore_offset_q_aware"] += int((np.abs(es[na] - off) <= q_a).sum())
                    ne += int(na.sum())
                for meth, q in (("anchor", q_anc), ("aware_on_anchor_rows", q_a), ("explore_offset_q_aware", q_a)):
                    persrc.append(dict(dataset=name, seed=seed, fold=f, source=s, n_rows=len(idx), method=meth,
                                       covered=c[meth], n_eval=ne, width=2 * q))
                    acc[meth][0] += c[meth]
                    acc[meth][1] += ne
            for meth, q in (("anchor", q_anc), ("aware_on_anchor_rows", q_a), ("explore_offset_q_aware", q_a)):
                cv_, ne = acc[meth]
                conf.append(dict(common, method=meth, coverage=(cv_ / ne) if ne else np.nan, width=2 * q, q=q, n=ne,
                                 n_cal=n_cal_scores if meth == "anchor" else len(tr),
                                 n_cal_sources=n_cal_src if meth == "anchor" else np.nan))
            rowrec.append(pd.DataFrame({"dataset": name, "seed": seed, "fold": f, "row": te, "source": gte, "y": y[te],
                                        "pred": p_te, "q_naive": q_n, "q_aware": q_a, "q_anchor": q_anc}))
            print(f"  {name} seed {seed} fold {f}: q_naive {q_n:.4g} q_aware {q_a:.4g} q_anchor {q_anc:.4g} "
                  f"({time.time() - t0:.0f}s)", flush=True)
        pd.DataFrame(conf).to_csv(os.path.join(PARTS, f"{name}__seed{seed}__conformal.csv"), index=False)
        pd.DataFrame(persrc).to_csv(os.path.join(PARTS, f"{name}__seed{seed}__per_source.csv"), index=False)
        pd.concat(rowrec).to_csv(os.path.join(PARTS, f"{name}__seed{seed}__rows.csv.gz"), index=False,
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


def summarize():
    conf = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*__conformal.csv")))])
    pers = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*__per_source.csv")))])
    rows = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*__rows.csv.gz")))])
    conf = conf.sort_values(["dataset", "seed", "fold", "method"]).reset_index(drop=True)
    conf.to_csv(os.path.join(RAW, "h9_conformal.csv"), index=False)
    pers["coverage"] = pers.covered / pers.n_eval
    pers = pers.sort_values(["dataset", "seed", "fold", "source", "method"]).reset_index(drop=True)
    pers.to_csv(os.path.join(RAW, "h9_per_source.csv"), index=False)
    rows.to_csv(os.path.join(RAW, "h9_rows.csv.gz"), index=False, float_format="%.6g")

    summary = {"hypothesis": "H9", "alpha": ALPHA, "datasets": {}, "notes": [
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
    ledger = []
    cond = {"C1": {}, "C2": {}, "C3": {}}
    for d in DATASETS:
        c = conf[conf.dataset == d]
        p = pers[pers.dataset == d]
        if c.empty:
            for k in cond:
                cond[k][d] = None
            ledger.append(dict(hypothesis="H9", test_id="H9_dataset", dataset=d, verdict="INCONCLUSIVE", note="not run"))
            continue
        seeds = sorted(c.seed.unique())
        yd = rows[(rows.dataset == d) & (rows.seed == seeds[0])]
        sd_y = float(yd.y.std(ddof=1))
        res = {"seeds": [int(s) for s in seeds], "n_sources": int(p.source.nunique()), "sd_y": sd_y,
               "n_sources_ge8": int(p[p.method == "anchor"].source.nunique()), "methods": {}}
        for meth in ["naive", "aware", "anchor", "aware_on_anchor_rows", "explore_offset_q_aware"]:
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
        # paired source bootstrap of the width ratio (same evaluated rows)
        jj = mx["_wn"].index.intersection(ms["_wn"].index)
        ratio_ci = boot_ratio(mx["_wn"].loc[jj].values, ms["_wn"].loc[jj].values)
        for mm in res["methods"].values():
            mm.pop("_wn"); mm.pop("_n")
        res["anchor_width_ratio_vs_aware_same_rows"] = {"value": float(ratio), "ci_source_boot": ratio_ci}
        res["naive_over_aware_width"] = float(mn["mean_width"] / ma["mean_width"])
        c1 = mn["coverage"] < 0.85
        c2 = ma["coverage"] >= 0.87
        c3 = (ratio <= 0.9) and (mx["coverage"] >= 0.87)
        cond["C1"][d], cond["C2"][d], cond["C3"][d] = c1, c2, c3
        res["conditions"] = {"naive_cov_lt_0.85": bool(c1), "aware_cov_ge_0.87": bool(c2),
                             "anchor_ratio_le_0.9_and_cov_ge_0.87": bool(c3)}
        summary["datasets"][d] = res
        ns, ns8 = res["n_sources"], res["n_sources_ge8"]
        sd = lambda m: f"seed range [{fmt(min(m['seed_coverage']))}, {fmt(max(m['seed_coverage']))}]"
        ledger += [
            dict(hypothesis="H9", test_id="H9_naive_cov", dataset=d, model="RF", metric="coverage of 90% interval, naive calib",
                 value=fmt(mn["coverage"], 4), ci_lo=fmt(mn["coverage_ci_source_boot"][0], 4),
                 ci_hi=fmt(mn["coverage_ci_source_boot"][1], 4), threshold="naive (random 5-fold) coverage on new sources < 0.85",
                 verdict="PASS" if c1 else "FAIL", n_units=ns,
                 note=f"row-pooled over 5 seeds; mean width {fmt(mn['mean_width'], 4)}; {sd(mn)}; source-avg coverage "
                      f"{fmt(mn['source_avg_coverage'])}; share of sources <0.8: {fmt(mn['share_sources_cov_lt_0.8'])}"),
            dict(hypothesis="H9", test_id="H9_aware_cov", dataset=d, model="RF", metric="coverage of 90% interval, source-aware calib",
                 value=fmt(ma["coverage"], 4), ci_lo=fmt(ma["coverage_ci_source_boot"][0], 4),
                 ci_hi=fmt(ma["coverage_ci_source_boot"][1], 4), threshold="source-aware (GroupKFold) coverage >= 0.87",
                 verdict="PASS" if c2 else "FAIL", n_units=ns,
                 note=f"row-pooled over 5 seeds; mean width {fmt(ma['mean_width'], 4)} (= {fmt(1 / res['naive_over_aware_width'], 2)}x naive); "
                      f"{sd(ma)}; source-avg coverage {fmt(ma['source_avg_coverage'])}; share of sources <0.8: "
                      f"{fmt(ma['share_sources_cov_lt_0.8'])}"),
            dict(hypothesis="H9", test_id="H9_anchor", dataset=d, model="RF", metric="anchor width / aware width (same rows)",
                 value=fmt(ratio, 4), ci_lo=fmt(ratio_ci[0], 4), ci_hi=fmt(ratio_ci[1], 4),
                 threshold="anchor-adjusted width <= 0.9 x source-aware AND anchor coverage >= 0.87",
                 verdict="PASS" if c3 else "FAIL", n_units=ns8,
                 note=f"anchor coverage {fmt(mx['coverage'], 4)} [{fmt(mx['coverage_ci_source_boot'][0])}, "
                      f"{fmt(mx['coverage_ci_source_boot'][1])}] on non-anchor rows of sources with >=8 rows (k=3, 10 draws); "
                      f"aware coverage on the same rows {fmt(ms['coverage'], 4)}; anchor source-avg coverage "
                      f"{fmt(mx['source_avg_coverage'])}"),
            dict(hypothesis="H9", test_id="H9_anchor_cov", dataset=d, model="RF", metric="coverage, anchor-adjusted interval",
                 value=fmt(mx["coverage"], 4), ci_lo=fmt(mx["coverage_ci_source_boot"][0], 4),
                 ci_hi=fmt(mx["coverage_ci_source_boot"][1], 4), threshold="component of H9_anchor (>= 0.87)",
                 verdict="DESCRIPTIVE", n_units=ns8, note=f"{sd(mx)}; mean width {fmt(mx['mean_width'], 4)}"),
            dict(hypothesis="H9", test_id="H9_desc_source_avg_cov", dataset=d, model="RF",
                 metric="source-averaged coverage naive|aware|anchor",
                 value=f"{fmt(mn['source_avg_coverage'])}|{fmt(ma['source_avg_coverage'])}|{fmt(mx['source_avg_coverage'])}",
                 threshold="descriptive (secondary estimand, fixed before results)", verdict="DESCRIPTIVE", n_units=ns,
                 note="each source weighted equally; shares of sources with coverage < 0.8: "
                      f"{fmt(mn['share_sources_cov_lt_0.8'])}|{fmt(ma['share_sources_cov_lt_0.8'])}|{fmt(mx['share_sources_cov_lt_0.8'])}"),
            dict(hypothesis="H9", test_id="H9_desc_width_over_sd", dataset=d, model="RF",
                 metric="mean interval width / SD(y): naive|aware|anchor",
                 value=f"{fmt(mn['width_over_sd_y'])}|{fmt(ma['width_over_sd_y'])}|{fmt(mx['width_over_sd_y'])}",
                 threshold="descriptive (added after results: how informative the honest interval is)",
                 verdict="DESCRIPTIVE", n_units=ns,
                 note=f"SD(y) = {sd_y:.4g} {UNITS[d]}; a 90% interval for a Gaussian with SD(y) would be 3.29 x SD"),
            dict(hypothesis="H9", test_id="H9_explore_offset_q_aware", dataset=d, model="RF",
                 metric="coverage: anchor offset + un-recalibrated aware q",
                 value=fmt(res["methods"]["explore_offset_q_aware"]["coverage"], 4),
                 threshold="exploratory, not graded", verdict="EXPLORATORY", n_units=ns8,
                 note="same non-anchor rows as H9_anchor; width = aware width"),
        ]
    for k, label, need, thr in [("C1", "naive coverage < 0.85", 4, ">= 4 of 7 datasets"),
                                ("C2", "aware coverage >= 0.87", 5, ">= 5 of 7 datasets"),
                                ("C3", "anchor width <= 0.9x aware and coverage >= 0.87", 3, ">= 3 of 7 datasets")]:
        npass = sum(bool(v) for v in cond[k].values() if v is not None)
        summary[f"condition_{k}"] = {"label": label, "n_datasets": npass, "need": need, "holds": npass >= need,
                                     "per_dataset": {d: (None if v is None else bool(v)) for d, v in cond[k].items()}}
        ledger.append(dict(hypothesis="H9", test_id=f"H9_{k}", dataset="ALL7", model="RF", metric=f"datasets with {label}",
                           value=npass, threshold=thr, verdict="PASS" if npass >= need else "FAIL", n_units=7,
                           note=", ".join(f"{d}={'yes' if v else ('n/a' if v is None else 'no')}" for d, v in cond[k].items())))
    allok = all(summary[f"condition_{k}"]["holds"] for k in cond)
    summary["overall"] = {"verdict": "PASS" if allok else "FAIL",
                          "conditions_met": int(sum(summary[f'condition_{k}']['holds'] for k in cond))}
    ledger.append(dict(hypothesis="H9", test_id="H9_overall", dataset="ALL7", model="RF", metric="conditions C1,C2,C3 met",
                       value=summary["overall"]["conditions_met"], threshold="all three conditions (no PARTIAL band in PREREG)",
                       verdict=summary["overall"]["verdict"], n_units=7,
                       note="; ".join(f"{k}={'met' if summary[f'condition_{k}']['holds'] else 'not met'} "
                                      f"({summary[f'condition_{k}']['n_datasets']}/7)" for k in cond)))
    summary["files"] = ["results/raw/h9_conformal.csv", "results/raw/h9_per_source.csv", "results/raw/h9_rows.csv.gz"]
    with open(os.path.join(RESULTS, "h9_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    ledger_write(os.path.join(LEDGER, "h9.csv"), ledger)
    for d, r in summary["datasets"].items():
        m = r["methods"]
        print(d, "naive %.3f aware %.3f anchor %.3f | widths %.4g %.4g %.4g ratio %.3f | src-avg %.3f %.3f %.3f" % (
            m["naive"]["coverage"], m["aware"]["coverage"], m["anchor"]["coverage"], m["naive"]["mean_width"],
            m["aware"]["mean_width"], m["anchor"]["mean_width"], r["anchor_width_ratio_vs_aware_same_rows"]["value"],
            m["naive"]["source_avg_coverage"], m["aware"]["source_avg_coverage"], m["anchor"]["source_avg_coverage"]))
    print({k: summary[f"condition_{k}"]["n_datasets"] for k in cond}, summary["overall"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "summarize"])
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("--seeds", default="0,1,2,3,4")
    a = ap.parse_args()
    if a.mode == "run":
        run(a.dataset, [int(s) for s in a.seeds.split(",")])
    else:
        summarize()
