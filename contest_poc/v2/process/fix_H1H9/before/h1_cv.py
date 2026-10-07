"""H1 — Evaluation inflation: random CV over-estimates performance on NEW sources.

Implements PREREG.md §2 H1 exactly:
  * random 5-fold vs source GroupKFold(min(10, n_sources)); 5 seeds; models RF, GB, KNN (vrr_common.make_model)
  * negative control: pseudo_groups (rows randomly partitioned into fake sources with the real size distribution),
    GroupKFold on them, 20 seeds, RF only
  * DES_RHO and DES_ETA: raw AND lineage-cleaned (subset(ds, ~copy_mask(ds))) variants
  * metric gap = RMSE_group / RMSE_random - 1
  * dataset PASS iff RF gap >= 0.20 AND RF gap > pseudo-gap 95th percentile AND (GB or KNN gap >= 0.10)
  * overall: >= 5/7 PASS -> PASS, <= 3/7 -> FAIL, else PARTIAL
  * diagnostic (not graded): leave-material-out (GroupKFold on ds.material)
  * EXPLORATORY (not graded): RF 'group_leakfree' (same group folds, copies of test-fold rows removed from training)

Usage (run from scripts/):
  python h1_cv.py cv DATASET [--variant raw|lineage] [--models RF,GB,KNN]
  python h1_cv.py pseudo DATASET [--variant raw|lineage]
  python h1_cv.py summarize
Interpretation choices are fixed in process/h1h9_log.md (written before any result was seen).
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

from vrr_data import load
from vrr_common import (make_model, random_folds, group_folds, pseudo_groups, rmse, r2, copy_mask,
                        leak_mask_for_source, subset, ledger_write, RAW, RESULTS, LEDGER)

DATASETS = ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]
LINEAGE = ["DES_RHO", "DES_ETA"]
SEEDS = range(5)
PSEUDO_SEEDS = range(20)
PARTS = os.path.join(RAW, "h1_parts")
os.makedirs(PARTS, exist_ok=True)


def get_ds(name, variant):
    ds = load(name)
    if variant == "lineage":
        ds = subset(ds, ~copy_mask(ds), "_lineage")
    return ds


def leak_union(ds, te, cache):
    """Rows of other sources that duplicate (key+value) a row of any source present in test indices te."""
    m = np.zeros(len(ds.y), bool)
    for s in np.unique(ds.group[te]):
        if s not in cache:
            cache[s] = leak_mask_for_source(ds, s)
        m |= cache[s]
    return m


def oof(ds, folds, model, seed, leakfree=False, cache=None):
    pred = np.full(len(ds.y), np.nan)
    for tr, te in folds:
        if leakfree:
            lk = leak_union(ds, te, cache)
            tr = tr[~lk[tr]]
        pred[te] = make_model(model, seed).fit(ds.X[tr], ds.y[tr]).predict(ds.X[te])
    assert not np.isnan(pred).any()
    return pred


def part_name(ds_name, variant, part):
    return os.path.join(PARTS, f"{ds_name}__{variant}__{part}")


def run_cv(name, variant, models):
    ds = get_ds(name, variant)
    n = len(ds.y)
    t0 = time.time()
    rows, preds = [], []
    cache = {}
    meta = pd.DataFrame({"dataset": name, "variant": variant, "row": np.arange(n), "source": ds.group,
                         "material": ds.material, "y": ds.y})
    meta.to_csv(part_name(name, variant, "meta.csv.gz"), index=False)
    for model in models:
        for seed in SEEDS:
            schemes = {"random": random_folds(n, 5, seed), "group": group_folds(ds.group, 10, seed),
                       "material": group_folds(ds.material, 10, seed)}
            for scheme, folds in schemes.items():
                p = oof(ds, folds, model, seed)
                rows.append(dict(dataset=name, variant=variant, model=model, seed=seed, scheme=scheme,
                                 rmse=rmse(ds.y, p), r2=r2(ds.y, p), n_rows=n, n_folds=len(folds)))
                preds.append(pd.DataFrame({"model": model, "seed": seed, "scheme": scheme, "row": np.arange(n),
                                           "pred": p}))
            if model == "RF":  # EXPLORATORY leak-free group CV
                folds = schemes["group"]
                p = oof(ds, folds, model, seed, leakfree=True, cache=cache)
                rows.append(dict(dataset=name, variant=variant, model=model, seed=seed, scheme="group_leakfree",
                                 rmse=rmse(ds.y, p), r2=r2(ds.y, p), n_rows=n, n_folds=len(folds)))
                preds.append(pd.DataFrame({"model": model, "seed": seed, "scheme": "group_leakfree",
                                           "row": np.arange(n), "pred": p}))
            print(f"  {name}/{variant} {model} seed {seed} done ({time.time() - t0:.0f}s)", flush=True)
    tag = "-".join(models)
    pd.DataFrame(rows).to_csv(part_name(name, variant, f"cv_{tag}.csv"), index=False)
    pr = pd.concat(preds)
    pr.insert(0, "variant", variant)
    pr.insert(0, "dataset", name)
    pr.to_csv(part_name(name, variant, f"pred_{tag}.csv.gz"), index=False, float_format="%.6g")
    print(f"cv {name}/{variant} {models}: {time.time() - t0:.0f}s")


def run_pseudo(name, variant):
    ds = get_ds(name, variant)
    t0 = time.time()
    rows = []
    for j in PSEUDO_SEEDS:
        pg = pseudo_groups(ds.group, seed=j)
        folds = group_folds(pg, 10, seed=j)
        p = oof(ds, folds, "RF", j)
        rows.append(dict(dataset=name, variant=variant, model="RF", pseudo_seed=j, n_folds=len(folds),
                         rmse=rmse(ds.y, p), r2=r2(ds.y, p), n_rows=len(ds.y)))
        print(f"  pseudo {name}/{variant} seed {j}: rmse {rows[-1]['rmse']:.4f} ({time.time() - t0:.0f}s)", flush=True)
    pd.DataFrame(rows).to_csv(part_name(name, variant, "pseudo.csv"), index=False)
    print(f"pseudo {name}/{variant}: {time.time() - t0:.0f}s")


# ------------------------------------------------------------------------------------------- summary
def boot_gap(se_g, se_r, src, n=2000, seed=0):
    """Source bootstrap of sqrt(sum SE_g / sum SE_r) - 1 (SE = per-row squared error averaged over seeds)."""
    d = pd.DataFrame({"g": se_g, "r": se_r, "s": src}).groupby("s")[["g", "r"]].sum()
    G, R = d.g.values, d.r.values
    rs = np.random.default_rng(seed)
    idx = rs.integers(0, len(G), (n, len(G)))
    b = np.sqrt(G[idx].sum(1) / R[idx].sum(1)) - 1
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def fmt(x, d=3):
    return "nan" if x is None or not np.isfinite(x) else f"{x:.{d}f}"


def summarize():
    cv = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*__cv_*.csv")))])
    ps = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*__pseudo.csv")))])
    meta = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*__meta.csv.gz")))])
    pred = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*__pred_*.csv.gz")))])
    cv = cv.sort_values(["dataset", "variant", "model", "seed", "scheme"]).reset_index(drop=True)
    cv.to_csv(os.path.join(RAW, "h1_cv.csv"), index=False)

    # mean RF random RMSE per (dataset, variant) -> pseudo gaps
    rf_rand = cv[(cv.model == "RF") & (cv.scheme == "random")].groupby(["dataset", "variant"]).rmse.mean()
    ps["rf_random_rmse_mean"] = [rf_rand[(d, v)] for d, v in zip(ps.dataset, ps.variant)]
    ps["gap"] = ps.rmse / ps.rf_random_rmse_mean - 1
    ps = ps.sort_values(["dataset", "variant", "pseudo_seed"]).reset_index(drop=True)
    ps.to_csv(os.path.join(RAW, "h1_pseudo.csv"), index=False)

    # per-seed gaps (raw, for figures)
    pv = cv.pivot_table(index=["dataset", "variant", "model", "seed"], columns="scheme", values="rmse").reset_index()
    for sch in ["group", "material", "group_leakfree"]:
        if sch in pv:
            pv[f"gap_{sch}"] = pv[sch] / pv["random"] - 1
    pv.to_csv(os.path.join(RAW, "h1_seed_gaps.csv"), index=False)

    # row-level: seed-mean squared errors, per-source RMSE (raw, for figures)
    pred = pred.merge(meta[["dataset", "variant", "row", "source", "y"]], on=["dataset", "variant", "row"])
    pred["se"] = (pred.pred - pred.y) ** 2
    rowse = pred.groupby(["dataset", "variant", "model", "scheme", "row", "source"]).se.mean().reset_index()
    psrc = rowse.groupby(["dataset", "variant", "model", "scheme", "source"]).se.agg(["mean", "size"]).reset_index()
    psrc["rmse"] = np.sqrt(psrc["mean"])
    psrc = psrc.rename(columns={"size": "n_rows"}).drop(columns="mean")
    pss = psrc.pivot_table(index=["dataset", "variant", "model", "source", "n_rows"], columns="scheme",
                           values="rmse").reset_index()
    pss.columns.name = None
    pss = pss.rename(columns={c: f"rmse_{c}" for c in ["random", "group", "material", "group_leakfree"]})
    pss["ratio_group_random"] = pss.rmse_group / pss.rmse_random
    pss.to_csv(os.path.join(RAW, "h1_per_source.csv"), index=False)
    # row-level seed-mean predictions for figures
    rowp = pred.groupby(["dataset", "variant", "model", "scheme", "row", "source", "y"]).pred.mean().reset_index()
    rowp.to_csv(os.path.join(RAW, "h1_rows.csv.gz"), index=False, float_format="%.6g")

    summary = {"hypothesis": "H1", "datasets": {}, "notes": [
        "Primary overall uses raw variants; DES_RHO_lineage and DES_ETA_lineage are separate graded rows + a sensitivity overall.",
        "gap point estimate = mean_seed(RMSE_group)/mean_seed(RMSE_random)-1; CI = source bootstrap of seed-mean squared errors.",
        "Pseudo-source control only rules out fold-mechanics artefacts (10 vs 5 folds, uneven fold sizes); it does not separate "
        "source effects from material novelty - see gap_material (diagnostic) and the process log.",
        "Pooled gaps are influenced by a subset of sources; see rf_source_avg_gap, rf_median_source_ratio_group_random, "
        "rf_top1_source_share_of_group_SE and rf_gap_without_top1_source (descriptive).",
        "group_leakfree (RF) is EXPLORATORY: same group folds with copies of test-fold rows removed from training."]}
    ledger = []
    units = [(d, "raw") for d in DATASETS] + [(d, "lineage") for d in LINEAGE]
    dataset_verdict = {}
    for d, v in units:
        dname = d if v == "raw" else f"{d}_lineage"
        sub = cv[(cv.dataset == d) & (cv.variant == v)]
        if sub.empty:
            ledger.append(dict(hypothesis="H1", test_id="H1_dataset", dataset=dname, verdict="INCONCLUSIVE",
                               threshold="all three H1 conditions", note="not run"))
            dataset_verdict[(d, v)] = "INCONCLUSIVE"
            continue
        n_src = meta[(meta.dataset == d) & (meta.variant == v)].source.nunique()
        res = {"n_rows": int(sub.n_rows.iloc[0]), "n_sources": int(n_src), "models": {}}
        gaps = {}
        for m in ["RF", "GB", "KNN"]:
            s = sub[sub.model == m]
            mr = s.groupby("scheme").rmse.mean()
            r2m = s.groupby("scheme").r2.mean()
            rs = rowse[(rowse.dataset == d) & (rowse.variant == v) & (rowse.model == m)]
            rr = rs[rs.scheme == "random"].sort_values("row")
            out = {"rmse_mean": mr.to_dict(), "r2_mean": r2m.to_dict(),
                   "n_folds": s.groupby("scheme").n_folds.first().to_dict()}
            for sch in ["group", "material", "group_leakfree"]:
                if sch not in mr:
                    continue
                g = mr[sch] / mr["random"] - 1
                rg = rs[rs.scheme == sch].sort_values("row")
                ci = boot_gap(rg.se.values, rr.se.values, rr.source.values)
                sg = pv[(pv.dataset == d) & (pv.variant == v) & (pv.model == m)][f"gap_{sch}"]
                out[f"gap_{sch}"] = {"value": float(g), "ci_source_boot": ci, "seed_min": float(sg.min()),
                                     "seed_max": float(sg.max())}
            gaps[m] = out["gap_group"]["value"]
            res["models"][m] = out
        pss_d = ps[(ps.dataset == d) & (ps.variant == v)]
        p95 = float(np.percentile(pss_d.gap, 95)) if len(pss_d) else float("nan")
        res["pseudo"] = {"n_seeds": int(len(pss_d)), "gaps": pss_d.gap.round(5).tolist(), "p95": p95,
                         "mean": float(pss_d.gap.mean()) if len(pss_d) else float("nan"),
                         "max": float(pss_d.gap.max()) if len(pss_d) else float("nan")}
        c1 = gaps["RF"] >= 0.20
        c2 = len(pss_d) == 20 and gaps["RF"] > p95
        other = max(gaps["GB"], gaps["KNN"])
        c3 = other >= 0.10
        verdict = "PASS" if (c1 and c2 and c3) else "FAIL"
        res["conditions"] = {"rf_gap_ge_0.20": bool(c1), "rf_gap_gt_pseudo_p95": bool(c2),
                             "other_model_gap_ge_0.10": bool(c3)}
        res["verdict"] = verdict
        # source-averaged view (pre-declared as descriptive in the log; dominated-by-few-sources check)
        pr = pss[(pss.dataset == d) & (pss.variant == v) & (pss.model == "RF")]
        res["rf_share_sources_worse_under_group"] = float((pr.ratio_group_random > 1).mean())
        res["rf_median_source_ratio_group_random"] = float(pr.ratio_group_random.median())
        res["rf_source_avg_gap"] = float(pr.rmse_group.mean() / pr.rmse_random.mean() - 1)
        seg = pr.rmse_group ** 2 * pr.n_rows
        res["rf_top1_source_share_of_group_SE"] = float(seg.max() / seg.sum())
        top = seg.idxmax()
        rest = pr.drop(index=top)
        res["rf_gap_without_top1_source"] = float(np.sqrt((rest.rmse_group ** 2 * rest.n_rows).sum() /
                                                          (rest.rmse_random ** 2 * rest.n_rows).sum()) - 1)
        res["rf_top1_source_n_rows"] = int(pr.n_rows.loc[top])
        summary["datasets"][dname] = res
        dataset_verdict[(d, v)] = verdict
        rf = res["models"]["RF"]
        nsrc = res["n_sources"]
        vnote = "" if v == "raw" else "lineage-cleaned variant (copies removed by copy_mask); separate graded row, " \
                                      "not counted in the primary 7-dataset overall. "
        ledger += [
            dict(hypothesis="H1", test_id="H1_rf_gap", dataset=dname, model="RF", metric="gap=RMSE_group/RMSE_random-1",
                 value=fmt(gaps["RF"], 4), ci_lo=fmt(rf["gap_group"]["ci_source_boot"][0], 4),
                 ci_hi=fmt(rf["gap_group"]["ci_source_boot"][1], 4), threshold="RF gap >= 0.20",
                 verdict="PASS" if c1 else "FAIL", n_units=nsrc,
                 note=vnote + f"RMSE random {fmt(rf['rmse_mean']['random'], 4)}, group {fmt(rf['rmse_mean']['group'], 4)} "
                              f"(mean of 5 seeds); per-seed gap range [{fmt(rf['gap_group']['seed_min'])}, "
                              f"{fmt(rf['gap_group']['seed_max'])}]; CI = source bootstrap of seed-mean squared errors"),
            dict(hypothesis="H1", test_id="H1_vs_pseudo", dataset=dname, model="RF", metric="RF gap - pseudo-source gap p95",
                 value=fmt(gaps["RF"] - p95, 4), threshold="real RF gap > 95th percentile of 20 pseudo-source gaps",
                 verdict="PASS" if c2 else "FAIL", n_units=len(pss_d),
                 note=vnote + f"real gap {fmt(gaps['RF'], 4)}; pseudo gaps mean {fmt(res['pseudo']['mean'], 4)}, "
                              f"p95 {fmt(p95, 4)}, max {fmt(res['pseudo']['max'], 4)}"),
            dict(hypothesis="H1", test_id="H1_other_model", dataset=dname, model="GB|KNN", metric="max(GB gap, KNN gap)",
                 value=fmt(other, 4), threshold="gap >= 0.10 in at least one other model (GB or KNN)",
                 verdict="PASS" if c3 else "FAIL", n_units=nsrc,
                 note=vnote + f"GB gap {fmt(gaps['GB'], 4)} CI [{fmt(res['models']['GB']['gap_group']['ci_source_boot'][0])}, "
                              f"{fmt(res['models']['GB']['gap_group']['ci_source_boot'][1])}]; KNN gap {fmt(gaps['KNN'], 4)} CI "
                              f"[{fmt(res['models']['KNN']['gap_group']['ci_source_boot'][0])}, "
                              f"{fmt(res['models']['KNN']['gap_group']['ci_source_boot'][1])}]"),
            dict(hypothesis="H1", test_id="H1_dataset", dataset=dname, model="RF+GB+KNN", metric="all three conditions",
                 value=int(c1) + int(c2) + int(c3), threshold="RF gap>=0.20 AND RF gap>pseudo p95 AND (GB or KNN gap>=0.10)",
                 verdict=verdict, n_units=nsrc, note=vnote + f"conditions met {int(c1) + int(c2) + int(c3)}/3"),
        ]
        ledger.append(dict(hypothesis="H1", test_id="H1_desc_source_avg", dataset=dname, model="RF",
                           metric="mean_s RMSE_group,s / mean_s RMSE_random,s - 1", value=fmt(res["rf_source_avg_gap"], 4),
                           threshold="descriptive (each source weighted equally), not graded", verdict="DESCRIPTIVE",
                           n_units=nsrc,
                           note=vnote + f"median per-source RMSE ratio group/random {fmt(res['rf_median_source_ratio_group_random'])}; "
                                        f"share of sources worse under group CV {fmt(res['rf_share_sources_worse_under_group'], 2)}; "
                                        f"largest contributor to group SE: {fmt(res['rf_top1_source_share_of_group_SE'], 2)} of total "
                                        f"(n={res['rf_top1_source_n_rows']} rows); pooled gap without it "
                                        f"{fmt(res['rf_gap_without_top1_source'])}"))
        for m in ["RF", "GB", "KNN"]:
            mg = res["models"][m]["gap_material"]
            ledger.append(dict(hypothesis="H1", test_id="H1_diag_material_gap", dataset=dname, model=m,
                               metric="RMSE_leave-material-out/RMSE_random-1", value=fmt(mg["value"], 4),
                               ci_lo=fmt(mg["ci_source_boot"][0], 4), ci_hi=fmt(mg["ci_source_boot"][1], 4),
                               threshold="diagnostic, not graded", verdict="DESCRIPTIVE", n_units=nsrc,
                               note=vnote + "GroupKFold(10) on ds.material; CI = source bootstrap"))
        lf = rf.get("gap_group_leakfree")
        if lf:
            ledger.append(dict(hypothesis="H1", test_id="H1_explore_group_leakfree", dataset=dname, model="RF",
                               metric="RMSE_group_leakfree/RMSE_random-1", value=fmt(lf["value"], 4),
                               ci_lo=fmt(lf["ci_source_boot"][0], 4), ci_hi=fmt(lf["ci_source_boot"][1], 4),
                               threshold="exploratory, not graded", verdict="EXPLORATORY", n_units=nsrc,
                               note=vnote + "same group folds; training rows duplicating key+value of a test-fold row removed"))

    def overall(units_used, test_id, note):
        vs = [dataset_verdict[u] for u in units_used]
        npass = sum(x == "PASS" for x in vs)
        ov = "PASS" if npass >= 5 else ("FAIL" if npass <= 3 else "PARTIAL")
        names = [u[0] if u[1] == "raw" else u[0] + "_lineage" for u in units_used]
        ledger.append(dict(hypothesis="H1", test_id=test_id, dataset="ALL7", model="RF+GB+KNN",
                           metric="datasets passing", value=npass,
                           threshold=">=5/7 PASS -> PASS; <=3/7 -> FAIL; else PARTIAL", verdict=ov, n_units=7,
                           note=note + "; " + ", ".join(f"{n}={x}" for n, x in zip(names, vs))))
        return ov, npass

    ov, npass = overall([(d, "raw") for d in DATASETS], "H1_overall", "primary (raw variants)")
    sens_units = [(d, "lineage" if d in LINEAGE else "raw") for d in DATASETS]
    ov2, npass2 = overall(sens_units, "H1_overall_lineage_sensitivity",
                          "sensitivity: DES_RHO and DES_ETA replaced by lineage-cleaned variants; primary verdict is H1_overall")
    summary["overall"] = {"verdict": ov, "n_pass": npass, "per_dataset": {d: dataset_verdict[(d, "raw")] for d in DATASETS}}
    summary["overall_lineage_sensitivity"] = {"verdict": ov2, "n_pass": npass2}
    summary["files"] = ["results/raw/h1_cv.csv", "results/raw/h1_pseudo.csv", "results/raw/h1_seed_gaps.csv",
                        "results/raw/h1_per_source.csv", "results/raw/h1_rows.csv.gz"]
    with open(os.path.join(RESULTS, "h1_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    ledger_write(os.path.join(LEDGER, "h1.csv"), ledger)
    print(json.dumps({k: (v["verdict"], round(v["models"]["RF"]["gap_group"]["value"], 3), round(v["pseudo"]["p95"], 3),
                          round(v["models"]["GB"]["gap_group"]["value"], 3), round(v["models"]["KNN"]["gap_group"]["value"], 3))
                      for k, v in summary["datasets"].items()}, indent=0))
    print("overall", ov, npass, "| sensitivity", ov2, npass2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["cv", "pseudo", "summarize"])
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("--variant", default="raw", choices=["raw", "lineage"])
    ap.add_argument("--models", default="RF,GB,KNN")
    a = ap.parse_args()
    if a.mode == "cv":
        run_cv(a.dataset, a.variant, a.models.split(","))
    elif a.mode == "pseudo":
        run_pseudo(a.dataset, a.variant)
    else:
        summarize()
