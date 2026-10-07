"""H5 audit rules: H5a artificial error injection and H5b predictive value of the audit on real data (PREREG section 2, H5).

Implements
  * H5a: lineage-cleaned DES_RHO, DES_ETA and ES1; UNIT / TEMP / COPY / DEFAULT injected separately into 5 % of rows,
    10 seeds; per-type recall/precision of the designated rules (UNIT, TEMP -> R1|R2; COPY -> R3; DEFAULT -> R4);
    model harm = source GroupKFold RMSE on clean (non-injected) rows for clean / injected / injected-then-filtered training;
    recovery = (inj - filt) / (inj - orig). ES1 TEMP = Fahrenheit written into the degC column (PREREG has no K column for
    ES1 -> deviation, see process/h5h7_log.md); exploratory ES1 TEMP_K = Kelvin written into the degC column.
  * H5b: 7 raw datasets, train-all vs train-unflagged (any rule), evaluated on unflagged rows of held-out sources,
    source GroupKFold(10), 5 seeds, leak copies of held-out sources removed (common protocol), source-bootstrap CI.

Usage (run from scripts/):
  python h5_audit.py base DATASET              # clean-base audit + cached clean-base predictions (DES_RHO|DES_ETA|ES1)
  python h5_audit.py inject DATASET ETYPE [--seeds 0-9]
  python h5_audit.py real DATASET              # H5b, one raw dataset
  python h5_audit.py summarize
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd

from vrr_data import load, DS
from vrr_common import (make_model, group_folds, rmse, boot_ci, copy_mask, subset, leak_mask_for_source,
                        ledger_write, RAW, RESULTS, LEDGER)
from vrr_audit import audit, family

PARTS = os.path.join(RAW, "h5_parts")
os.makedirs(PARTS, exist_ok=True)
H5A_SETS = ["DES_RHO", "DES_ETA", "ES1"]
ETYPES = ["UNIT", "TEMP", "COPY", "DEFAULT"]
DESIGNATED = {"UNIT": "R12", "TEMP": "R12", "TEMP_K": "R12", "COPY": "R3", "DEFAULT": "R4"}
REAL_SETS = ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]
FRAC = 0.05
FLAG_COLS = ["R1", "R1_y", "R1_T", "R2", "R2a", "R2b", "R3", "R4", "R12", "any"]


# ------------------------------------------------------------------ helpers
def base_ds(name):
    ds = load(name)
    if name in ("DES_RHO", "DES_ETA"):
        ds = subset(ds, ~copy_mask(ds), "_lineage")
    return ds


def clone(ds, df, X, y, group, key, material, suffix="_inj"):
    return DS(name=ds.name + suffix, y_name=ds.y_name, y_unit=ds.y_unit, df=df.reset_index(drop=True), X=X,
              feats=ds.feats, y=y, group=np.asarray(group), key=np.asarray(key), material=np.asarray(material),
              audit=ds.audit)


def fold_map(ds):
    """source -> fold id, fixed from the clean base (group_folds seed 0, 10 folds)."""
    m = {}
    for f, (_, te) in enumerate(group_folds(ds.group, 10, 0)):
        for s in np.unique(ds.group[te]):
            m[s] = f
    return m


def folds_from_map(group, fmap):
    fid = np.array([fmap[g] for g in group])
    return [(np.where(fid != f)[0], np.where(fid == f)[0]) for f in sorted(set(fid))]


def cv_pred(X, y, folds, train_mask=None, seed=0):
    pred = np.full(len(y), np.nan)
    for tr, te in folds:
        if train_mask is not None:
            tr = tr[train_mask[tr]]
        pred[te] = make_model("RF", seed).fit(X[tr], y[tr]).predict(X[te])
    return pred


def mean_source_rmse(y, p, g, mask):
    vals = [rmse(y[(g == s) & mask], p[(g == s) & mask]) for s in np.unique(g[mask])]
    return float(np.mean(vals))


# ------------------------------------------------------------------ injection
def inject(ds, etype, seed):
    rs = np.random.default_rng(10_000 + seed)
    fam = family(ds.name)
    n = len(ds.y)
    m = int(round(FRAC * n))
    df, X, y = ds.df.copy(), ds.X.copy(), ds.y.copy()
    group, key, material = ds.group.copy(), ds.key.copy(), ds.material.copy()
    note = ""
    if etype == "COPY":
        src = rs.choice(n, m, replace=False)
        srcs = np.unique(ds.group)
        newg = np.array([rs.choice(srcs[srcs != ds.group[i]]) for i in src])
        add = df.iloc[src].copy()
        add["source"] = newg
        df = pd.concat([df, add], ignore_index=True)
        X = np.vstack([X, X[src]])
        y = np.r_[y, y[src]]
        group = np.r_[group, newg]
        key = np.r_[key, key[src]]
        material = np.r_[material, material[src]]
        inj = np.r_[np.zeros(n, bool), np.ones(m, bool)]
        return clone(ds, df, X, y, group, key, material), inj, note
    # in-place types: candidate rows = rows where the injection changes the value
    if etype == "UNIT":
        cand = np.arange(n)
    elif etype in ("TEMP", "TEMP_K"):
        cand = np.arange(n) if fam.startswith("DES") else np.where(df.temperature_c_missing.values == 0)[0]
    elif etype == "DEFAULT":
        if fam.startswith("DES"):
            cand = np.where(~np.isclose(df["T"].values, 298.15))[0]
        else:
            cand = np.where(~((df.rh.values == 45) & (df.rh_missing.values == 0)))[0]
    else:
        raise ValueError(etype)
    idx = rs.choice(cand, m, replace=False)
    inj = np.zeros(n, bool)
    inj[idx] = True
    fi = {f: i for i, f in enumerate(ds.feats)}
    if etype == "UNIT":
        if fam == "DES_RHO":
            df.loc[idx, "y_raw"] = df.loc[idx, "y_raw"] * 1000.0
            y[idx] = df.loc[idx, "y_raw"].values
        elif fam == "DES_ETA":
            df.loc[idx, "y_raw"] = df.loc[idx, "y_raw"] * 0.001
            y[idx] = np.log10(df.loc[idx, "y_raw"].values)
        elif fam == "ES1":
            df.loc[idx, "fiber_diameter_nm"] = df.loc[idx, "fiber_diameter_nm"] * 0.001
            y[idx] = np.log10(df.loc[idx, "fiber_diameter_nm"].values)
        df.loc[idx, "y"] = y[idx]
    elif etype in ("TEMP", "TEMP_K", "DEFAULT") and fam.startswith("DES"):
        if etype == "TEMP":
            df.loc[idx, "T"] = df.loc[idx, "T"] - 273.15
        elif etype == "DEFAULT":
            df.loc[idx, "T"] = 298.15
        else:
            raise ValueError("TEMP_K is defined for ES1 only")
        X[idx, fi["T"]] = df.loc[idx, "T"].values
        newkey = (df.loc[idx, "material"] + " | T=" + df.loc[idx, "T"].round(1).astype(str)).values
        key[idx] = newkey
    elif etype in ("TEMP", "TEMP_K") and fam == "ES1":
        t = df.loc[idx, "temperature_c"].values
        df.loc[idx, "temperature_c"] = t * 9 / 5 + 32 if etype == "TEMP" else t + 273.15
        X[idx, fi["temperature_c"]] = df.loc[idx, "temperature_c"].values
        note = "ES1 TEMP = degF written as degC" if etype == "TEMP" else "ES1 TEMP_K = K written as degC"
    elif etype == "DEFAULT" and fam == "ES1":
        df.loc[idx, "rh"] = 45.0
        df.loc[idx, "rh_missing"] = 0.0
        X[idx, fi["rh"]] = 45.0
        X[idx, fi["rh_missing"]] = 0.0
    else:
        raise ValueError((etype, fam))
    return clone(ds, df, X, y, group, key, material), inj, note


# ------------------------------------------------------------------ modes
def run_base(name):
    t0 = time.time()
    ds = base_ds(name)
    fl = audit(ds)
    fmap = fold_map(ds)
    folds = folds_from_map(ds.group, fmap)
    pred = cv_pred(ds.X, ds.y, folds, seed=0)
    np.save(os.path.join(PARTS, f"orig_pred_{name}.npy"), pred)
    out = fl.copy()
    out.insert(0, "row", np.arange(len(ds.y)))
    out.insert(1, "source", ds.group)
    out.insert(2, "y", ds.y)
    out.to_csv(os.path.join(PARTS, f"base_flags_{name}.csv.gz"), index=False)
    print(name, ds, "base flags:", {c: int(fl[c].sum()) for c in FLAG_COLS},
          "orig RMSE", round(rmse(ds.y, pred), 5), f"{time.time() - t0:.0f}s", flush=True)


def run_inject(name, etype, seeds):
    ds = base_ds(name)
    orig = np.load(os.path.join(PARTS, f"orig_pred_{name}.npy"))
    fmap = fold_map(ds)
    n = len(ds.y)
    out_path = os.path.join(PARTS, f"inj_{name}_{etype}.csv")
    rows = []
    if os.path.exists(out_path):
        rows = pd.read_csv(out_path).to_dict("records")
    done = {r["seed"] for r in rows}
    for seed in seeds:
        if seed in done:
            continue
        t0 = time.time()
        di, inj, note = inject(ds, etype, seed)
        fl = audit(di)
        folds = folds_from_map(di.group, fmap)
        p_inj = cv_pred(di.X, di.y, folds, seed=0)
        keep_any = ~fl["any"].values
        keep_12 = ~fl["R12"].values
        p_filt = cv_pred(di.X, di.y, folds, train_mask=keep_any, seed=0)
        if np.array_equal(keep_any, keep_12):
            p_f12 = p_filt
        else:
            p_f12 = cv_pred(di.X, di.y, folds, train_mask=keep_12, seed=0)
        clean = ~inj[:n]                       # evaluation rows = base rows not injected
        yb, gb = ds.y, ds.group
        r = dict(dataset=name, etype=etype, seed=seed, n_rows=len(di.y), n_injected=int(inj.sum()),
                 n_eval=int(clean.sum()), note=note)
        for c in FLAG_COLS:
            f = fl[c].values
            r[f"flag_{c}"] = int(f.sum())
            r[f"tp_{c}"] = int((f & inj).sum())
        des = DESIGNATED[etype]
        tp, nf = r[f"tp_{des}"], r[f"flag_{des}"]
        r["designated"] = des
        r["recall"] = tp / r["n_injected"]
        r["precision"] = tp / nf if nf > 0 else np.nan
        r["recall_any"] = r["tp_any"] / r["n_injected"]
        r["precision_any"] = r["tp_any"] / r["flag_any"] if r["flag_any"] > 0 else np.nan
        r["rmse_orig"] = rmse(yb[clean], orig[clean])
        r["rmse_inj"] = rmse(yb[clean], p_inj[:n][clean])
        r["rmse_filt"] = rmse(yb[clean], p_filt[:n][clean])
        r["rmse_filt_R12"] = rmse(yb[clean], p_f12[:n][clean])
        r["msrc_orig"] = mean_source_rmse(yb, orig, gb, clean)
        r["msrc_inj"] = mean_source_rmse(yb, p_inj[:n], gb, clean)
        r["msrc_filt"] = mean_source_rmse(yb, p_filt[:n], gb, clean)
        r["msrc_filt_R12"] = mean_source_rmse(yb, p_f12[:n], gb, clean)
        r["n_train_removed_any"] = int((~keep_any).sum())
        r["n_train_removed_R12"] = int((~keep_12).sum())
        r["sec"] = round(time.time() - t0, 1)
        rows.append(r)
        pd.DataFrame(rows).to_csv(out_path, index=False)
        print(name, etype, seed, f"recall={r['recall']:.3f} prec={r['precision']:.3f} "
              f"rmse orig/inj/filt/f12 = {r['rmse_orig']:.5f}/{r['rmse_inj']:.5f}/{r['rmse_filt']:.5f}/{r['rmse_filt_R12']:.5f}"
              f" ({r['sec']}s)", flush=True)


def run_real(name, seeds=range(5)):
    t0 = time.time()
    ds = load(name)
    fl, det = audit(ds, return_detail=True)
    flag = fl["any"].values
    fo = fl.copy()
    fo.insert(0, "dataset", name)
    fo.insert(1, "row", np.arange(len(ds.y)))
    fo.insert(2, "source", ds.group)
    fo.insert(3, "y", ds.y)
    fo.to_csv(os.path.join(PARTS, f"real_flags_{name}.csv.gz"), index=False)
    srcs = np.unique(ds.group)
    leak = {s: leak_mask_for_source(ds, s) for s in srcs}
    rows = []
    for seed in seeds:
        p_all = np.full(len(ds.y), np.nan)
        p_unf = np.full(len(ds.y), np.nan)
        for tr, te in group_folds(ds.group, 10, seed):
            lk = np.zeros(len(ds.y), bool)
            for s in np.unique(ds.group[te]):
                lk |= leak[s]
            tr_all = tr[~lk[tr]]
            p_all[te] = make_model("RF", seed).fit(ds.X[tr_all], ds.y[tr_all]).predict(ds.X[te])
            if flag.any():
                tr_unf = tr_all[~flag[tr_all]]
                p_unf[te] = make_model("RF", seed).fit(ds.X[tr_unf], ds.y[tr_unf]).predict(ds.X[te])
            else:
                p_unf[te] = p_all[te]
        ev = ~flag
        for s in srcs:
            msk = (ds.group == s) & ev
            if msk.sum() == 0:
                rows.append(dict(dataset=name, seed=seed, source=s, n_rows=int((ds.group == s).sum()), n_eval=0,
                                 n_flagged=int(((ds.group == s) & flag).sum()), rmse_all=np.nan, rmse_unflagged=np.nan))
                continue
            rows.append(dict(dataset=name, seed=seed, source=s, n_rows=int((ds.group == s).sum()), n_eval=int(msk.sum()),
                             n_flagged=int(((ds.group == s) & flag).sum()),
                             rmse_all=rmse(ds.y[msk], p_all[msk]), rmse_unflagged=rmse(ds.y[msk], p_unf[msk])))
        print(name, "seed", seed, "pooled RMSE all/unflagged on unflagged rows:",
              round(rmse(ds.y[ev], p_all[ev]), 5), round(rmse(ds.y[ev], p_unf[ev]), 5), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(PARTS, f"real_{name}.csv"), index=False)
    meta = {"dataset": name, "n": int(len(ds.y)), "n_sources": int(len(srcs)),
            "flags": {c: int(fl[c].sum()) for c in FLAG_COLS}, "detail": json.loads(json.dumps(det, default=str)),
            "leak_rows_total": int(np.sum([leak[s].sum() for s in srcs])), "sec": round(time.time() - t0, 1)}
    with open(os.path.join(PARTS, f"real_meta_{name}.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(name, json.dumps(meta)[:500], flush=True)


# ------------------------------------------------------------------ summarize
def seed_ci(v, seed=0):
    return boot_ci(np.asarray(v, float), n=2000, seed=seed)


def ratio_boot(inj, filt, orig, n=2000, seed=0):
    inj, filt, orig = map(lambda a: np.asarray(a, float), (inj, filt, orig))
    rs = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        i = rs.integers(0, len(inj), len(inj))
        den = inj[i].mean() - orig[i].mean()
        out.append((inj[i].mean() - filt[i].mean()) / den if den > 0 else np.nan)
    out = np.asarray(out)
    out = out[~np.isnan(out)]
    if len(out) < 100:
        return (np.nan, np.nan)
    return (float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5)))


def summarize():
    L, S = [], {"H5a": {}, "H5b": {}}
    # ---------------- H5a
    parts = [pd.read_csv(os.path.join(PARTS, f)) for f in sorted(os.listdir(PARTS)) if f.startswith("inj_")]
    inj = pd.concat(parts, ignore_index=True)
    inj.to_csv(os.path.join(RAW, "h5_injection.csv"), index=False)
    base_rows = []
    for name in H5A_SETS:
        p = os.path.join(PARTS, f"base_flags_{name}.csv.gz")
        if os.path.exists(p):
            b = pd.read_csv(p)
            base_rows.append({"dataset": name, "n": len(b), **{f"flag_{c}": int(b[c].sum()) for c in FLAG_COLS}})
    pd.DataFrame(base_rows).to_csv(os.path.join(RAW, "h5_base_flags.csv"), index=False)
    for b in base_rows:
        L.append(dict(hypothesis="H5", test_id="H5a_base_flag_rate", dataset=b["dataset"] + ("_lineage" if b["dataset"] != "ES1" else ""),
                      model="audit R1-R4", metric="rows flagged by any rule on the clean base (no injection)",
                      value=b["flag_any"], threshold="descriptive (background flags = false positives in H5a)",
                      verdict="DESCRIPTIVE", n_units=b["n"],
                      note="per rule: " + ", ".join(f"{c}={b['flag_' + c]}" for c in ["R1", "R2a", "R2b", "R3", "R4"])))
    graded = []   # (dataset, check, verdict)
    for name in H5A_SETS:
        dname = name + ("_lineage" if name != "ES1" else "")
        S["H5a"][dname] = {}
        for et in ["UNIT", "TEMP", "COPY", "DEFAULT", "TEMP_K"]:
            sub = inj[(inj.dataset == name) & (inj.etype == et)].sort_values("seed")
            if len(sub) == 0:
                continue
            nseed = len(sub)
            rec, prec = sub.recall.values, sub.precision.values
            rec_m, prec_m = float(np.mean(rec)), float(np.nanmean(prec)) if np.any(~np.isnan(prec)) else np.nan
            rec_ci, prec_ci = seed_ci(rec), seed_ci(prec)
            harm = sub.rmse_inj.values - sub.rmse_orig.values
            harm_m, harm_ci = float(np.mean(harm)), seed_ci(harm)
            den = sub.rmse_inj.mean() - sub.rmse_orig.mean()
            recov = float((sub.rmse_inj.mean() - sub.rmse_filt.mean()) / den) if den > 0 else np.nan
            recov12 = float((sub.rmse_inj.mean() - sub.rmse_filt_R12.mean()) / den) if den > 0 else np.nan
            recov_ci = ratio_boot(sub.rmse_inj, sub.rmse_filt, sub.rmse_orig)
            recov12_ci = ratio_boot(sub.rmse_inj, sub.rmse_filt_R12, sub.rmse_orig)
            harm_ok = harm_m > 0 and harm_ci[0] > 0
            if not harm_ok:   # ratio with a ~0 or negative denominator is not interpretable -> no CI reported
                recov_ci = recov12_ci = (np.nan, np.nan)
            per_rule = {c: float((sub[f"tp_{c}"] / sub.n_injected).mean()) for c in FLAG_COLS}
            S["H5a"][dname][et] = dict(n_seeds=nseed, n_injected=int(sub.n_injected.iloc[0]), designated=DESIGNATED[et],
                                      recall=rec_m, recall_ci=rec_ci, precision=prec_m, precision_ci=prec_ci,
                                      recall_any=float(sub.recall_any.mean()), precision_any=float(sub.precision_any.mean()),
                                      recall_by_rule=per_rule,
                                      rmse_orig=float(sub.rmse_orig.mean()), rmse_inj=float(sub.rmse_inj.mean()),
                                      rmse_filt=float(sub.rmse_filt.mean()), rmse_filt_R12=float(sub.rmse_filt_R12.mean()),
                                      harm=harm_m, harm_ci=harm_ci, harm_measurable=bool(harm_ok),
                                      recovery=recov, recovery_ci=recov_ci, recovery_R12=recov12, recovery_R12_ci=recov12_ci,
                                      train_rows_removed_any=float(sub.n_train_removed_any.mean()),
                                      train_rows_removed_R12=float(sub.n_train_removed_R12.mean()))
            tag = f"{nseed} seeds; designated rules {DESIGNATED[et]}; per-rule recall " + \
                  ", ".join(f"{c}={per_rule[c]:.2f}" for c in ["R1", "R2a", "R2b", "R3", "R4"])
            ci_note = "CI = 95% bootstrap over seeds"
            explo = et in ("DEFAULT", "TEMP_K")
            es1temp = (name == "ES1" and et == "TEMP")
            dev = (" | PROTOCOL DEVIATION: ES1 has no Kelvin column; TEMP = degF value written into the degC column "
                   "(realistic unit confusion, not what R1 is designed to catch)") if es1temp else ""
            if et == "TEMP_K":
                dev = " | EXPLORATORY variant: K value written into the ES1 degC column (+273.15)"
            # recall
            if et in ("UNIT", "TEMP"):
                v = "PASS" if rec_m >= 0.8 else "FAIL"
                graded.append((dname, f"{et}_recall", v))
                L.append(dict(hypothesis="H5", test_id=f"H5a_{et}_recall", dataset=dname, model="audit R1|R2",
                              metric="recall of injected rows (seed mean)", value=round(rec_m, 4), ci_lo=round(rec_ci[0], 4),
                              ci_hi=round(rec_ci[1], 4), threshold="recall >= 0.8 (UNIT and TEMP, each dataset)",
                              verdict=v, n_units=nseed, note=tag + "; " + ci_note + dev))
                v = "PASS" if (not np.isnan(prec_m)) and prec_m >= 0.8 else "FAIL"
                graded.append((dname, f"{et}_precision", v))
                L.append(dict(hypothesis="H5", test_id=f"H5a_{et}_precision", dataset=dname, model="audit R1|R2",
                              metric="precision = injected flagged / all rows flagged by R1|R2 (seed mean)",
                              value=round(prec_m, 4), ci_lo=round(prec_ci[0], 4), ci_hi=round(prec_ci[1], 4),
                              threshold="precision >= 0.8 (UNIT and TEMP, each dataset)", verdict=v, n_units=nseed,
                              note=f"mean rows flagged by R1|R2 = {sub.flag_R12.mean():.1f} for {int(sub.n_injected.iloc[0])} injected; "
                                   f"non-injected flags count as false positives; {ci_note}" + dev))
            elif et == "COPY":
                v = "PASS" if rec_m >= 0.9 else "FAIL"
                graded.append((dname, "COPY_recall", v))
                L.append(dict(hypothesis="H5", test_id="H5a_COPY_recall", dataset=dname, model="audit R3",
                              metric="recall of injected copy rows (seed mean)", value=round(rec_m, 4),
                              ci_lo=round(rec_ci[0], 4), ci_hi=round(rec_ci[1], 4), threshold="recall >= 0.9",
                              verdict=v, n_units=nseed, note=tag + "; " + ci_note +
                              " | circular by design: R3 tests exactly the property that the injection creates"))
                L.append(dict(hypothesis="H5", test_id="H5a_COPY_precision", dataset=dname, model="audit R3",
                              metric="precision (seed mean)", value=round(prec_m, 4), ci_lo=round(prec_ci[0], 4),
                              ci_hi=round(prec_ci[1], 4), threshold="descriptive (not graded in PREREG)",
                              verdict="DESCRIPTIVE", n_units=nseed,
                              note="R3 flags BOTH members of a copy pair (the injected copy and its original), so precision <= ~0.5 by construction"))
            else:
                for met, val, ci in [("recall", rec_m, rec_ci), ("precision", prec_m, prec_ci)]:
                    L.append(dict(hypothesis="H5", test_id=f"H5a_{et}_{met}", dataset=dname,
                                  model="audit " + DESIGNATED[et].replace("R12", "R1|R2"),
                                  metric=f"{met} (seed mean)", value=round(val, 4), ci_lo=round(ci[0], 4),
                                  ci_hi=round(ci[1], 4),
                                  threshold="exploratory (PREREG predicts low DEFAULT recall)" if et == "DEFAULT"
                                  else "exploratory variant (not graded)",
                                  verdict="EXPLORATORY", n_units=nseed, note=tag + "; " + ci_note + dev))
            # any-rule sensitivity
            for met, col in [("recall", "recall_any"), ("precision", "precision_any")]:
                vv = sub[col].values.astype(float)
                cc = seed_ci(vv)
                L.append(dict(hypothesis="H5", test_id=f"H5a_{et}_anyrule_{met}", dataset=dname, model="audit R1-R4",
                              metric=f"{met} when ALL rules (R1|R2|R3|R4) count (seed mean)",
                              value=round(float(np.nanmean(vv)), 4), ci_lo=round(cc[0], 4), ci_hi=round(cc[1], 4),
                              threshold="sensitivity (not graded): any-rule union instead of designated rules",
                              verdict="EXPLORATORY", n_units=nseed,
                              note=f"mean rows flagged by any rule = {sub.flag_any.mean():.1f} for {int(sub.n_injected.iloc[0])} injected; {ci_note}"))
            # recovery
            rec_note = (f"RMSE on clean rows (source GroupKFold 10, RF seed 0): orig {sub.rmse_orig.mean():.5g}, inj {sub.rmse_inj.mean():.5g}, "
                        f"filt(any rule) {sub.rmse_filt.mean():.5g}, filt(R1|R2) {sub.rmse_filt_R12.mean():.5g}; harm inj-orig "
                        f"{harm_m:.3g} CI [{harm_ci[0]:.3g}, {harm_ci[1]:.3g}]; training rows removed by filter: any {sub.n_train_removed_any.mean():.0f}, "
                        f"R1|R2 {sub.n_train_removed_R12.mean():.0f}; recovery with R1|R2-only filter {recov12:.3f} "
                        f"CI [{recov12_ci[0]:.3f}, {recov12_ci[1]:.3f}]")
            if et in ("UNIT", "TEMP"):
                if not harm_ok:
                    v = "INCONCLUSIVE"
                    extra = " | harm not measurable (seed-mean <= 0 or CI lower <= 0): nothing to recover"
                else:
                    v = "PASS" if recov >= 0.5 else "FAIL"
                    extra = ""
                graded.append((dname, f"{et}_recovery", v))
                L.append(dict(hypothesis="H5", test_id=f"H5a_{et}_recovery", dataset=dname, model="RF",
                              metric="recovery = (RMSE_inj - RMSE_filt)/(RMSE_inj - RMSE_orig), filter = any rule",
                              value=round(recov, 4) if not np.isnan(recov) else "", ci_lo=round(recov_ci[0], 4),
                              ci_hi=round(recov_ci[1], 4), threshold="recovery >= 0.5 (UNIT and TEMP, all 3 datasets)",
                              verdict=v, n_units=nseed, note=rec_note + extra + dev))
            else:
                L.append(dict(hypothesis="H5", test_id=f"H5a_{et}_recovery", dataset=dname, model="RF",
                              metric="recovery = (RMSE_inj - RMSE_filt)/(RMSE_inj - RMSE_orig), filter = any rule",
                              value=round(recov, 4) if not np.isnan(recov) else "", ci_lo=round(recov_ci[0], 4),
                              ci_hi=round(recov_ci[1], 4), threshold="descriptive / exploratory (not graded)",
                              verdict="EXPLORATORY" if explo else "DESCRIPTIVE", n_units=nseed,
                              note=rec_note + ("" if harm_ok else " | harm not measurable") + dev))
            L.append(dict(hypothesis="H5", test_id=f"H5a_{et}_recovery_R12filter", dataset=dname, model="RF",
                          metric="recovery when only R1|R2 flags are filtered", value=round(recov12, 4) if not np.isnan(recov12) else "",
                          ci_lo=round(recov12_ci[0], 4), ci_hi=round(recov12_ci[1], 4),
                          threshold="sensitivity (not graded)", verdict="EXPLORATORY", n_units=nseed,
                          note="filter policy alternative fixed before running (process log)" + ("" if harm_ok else " | harm not measurable")))
    nfail = sum(v == "FAIL" for _, _, v in graded)
    ninc = sum(v == "INCONCLUSIVE" for _, _, v in graded)
    npass = sum(v == "PASS" for _, _, v in graded)
    ov = "FAIL" if nfail else ("PARTIAL" if ninc else "PASS")
    failed = [f"{d}:{c}" for d, c, v in graded if v == "FAIL"]
    incon = [f"{d}:{c}" for d, c, v in graded if v == "INCONCLUSIVE"]
    S["H5a"]["graded_cells"] = [dict(dataset=d, check=c, verdict=v) for d, c, v in graded]
    S["H5a"]["overall"] = dict(verdict=ov, n_pass=npass, n_fail=nfail, n_inconclusive=ninc, failed=failed, inconclusive=incon)
    L.append(dict(hypothesis="H5", test_id="H5a_overall", dataset="DES_RHO_lineage+DES_ETA_lineage+ES1", model="audit + RF",
                  metric="graded cells passed", value=npass, threshold="all of: UNIT/TEMP recall>=0.8 & precision>=0.8; COPY recall>=0.9; "
                  "UNIT/TEMP recovery>=0.5 on all 3 datasets", verdict=ov, n_units=len(graded),
                  note=f"{npass} PASS, {nfail} FAIL, {ninc} INCONCLUSIVE of {len(graded)} graded cells; FAIL: {failed}; INCONCLUSIVE: {incon}"))
    g2 = [(d, c, v) for d, c, v in graded if not (d == "ES1" and c.startswith("TEMP"))]
    nf2 = sum(v == "FAIL" for _, _, v in g2)
    ni2 = sum(v == "INCONCLUSIVE" for _, _, v in g2)
    ov2 = "FAIL" if nf2 else ("PARTIAL" if ni2 else "PASS")
    S["H5a"]["overall_sens_ES1_TEMP_NA"] = dict(verdict=ov2, n_cells=len(g2), n_fail=nf2, n_inconclusive=ni2)
    L.append(dict(hypothesis="H5", test_id="H5a_overall_sens_ES1TEMP_not_applicable", dataset="DES_RHO_lineage+DES_ETA_lineage+ES1",
                  model="audit + RF", metric="graded cells passed (ES1 TEMP cells dropped)", value=sum(v == "PASS" for _, _, v in g2),
                  threshold="same rule; ES1 TEMP treated as not applicable (no Kelvin column)", verdict="EXPLORATORY",
                  n_units=len(g2), note=f"verdict under this alternative = {ov2}; primary verdict is H5a_overall"))
    # ---------------- H5b
    rparts = [pd.read_csv(os.path.join(PARTS, f"real_{n}.csv")) for n in REAL_SETS if os.path.exists(os.path.join(PARTS, f"real_{n}.csv"))]
    real = pd.concat(rparts, ignore_index=True)
    real.to_csv(os.path.join(RAW, "h5b_real.csv"), index=False)
    flags = []
    for n in REAL_SETS:
        p = os.path.join(PARTS, f"real_flags_{n}.csv.gz")
        if os.path.exists(p):
            flags.append(pd.read_csv(p))
    pd.concat(flags, ignore_index=True).to_csv(os.path.join(RAW, "h5b_flags.csv.gz"), index=False)
    nimp = 0
    for n in REAL_SETS:
        meta_p = os.path.join(PARTS, f"real_meta_{n}.json")
        sub = real[real.dataset == n]
        if len(sub) == 0 or not os.path.exists(meta_p):
            L.append(dict(hypothesis="H5", test_id="H5b_real", dataset=n, verdict="INCONCLUSIVE", note="not run"))
            continue
        meta = json.load(open(meta_p))
        ps = sub.groupby("source")[["rmse_all", "rmse_unflagged"]].mean().dropna()
        ps = ps[ps.rmse_all > 0]
        rel = (ps.rmse_unflagged / ps.rmse_all - 1).values
        m = float(np.mean(rel))
        ci = boot_ci(rel)
        frac_impr = float(np.mean(rel < 0))
        # pooled RMSE on unflagged rows per seed
        pooled = []
        for sd, g in sub.groupby("seed"):
            g = g[g.n_eval > 0]
            a = np.sqrt((g.rmse_all ** 2 * g.n_eval).sum() / g.n_eval.sum())
            u = np.sqrt((g.rmse_unflagged ** 2 * g.n_eval).sum() / g.n_eval.sum())
            pooled.append(u / a - 1)
        nfl = meta["flags"]["any"]
        v = "PASS" if (not np.isnan(ci[1])) and ci[1] < 0 else "FAIL"
        nimp += v == "PASS"
        S["H5b"][n] = dict(n_rows=meta["n"], n_flagged_any=nfl, flags=meta["flags"], r4_detail=meta["detail"]["r4"],
                           n_sources_eval=int(len(ps)), mean_rel_change=m, ci=ci, frac_sources_improved=frac_impr,
                           pooled_rel_change_per_seed=[float(x) for x in pooled], verdict=v)
        L.append(dict(hypothesis="H5", test_id="H5b_real", dataset=n, model="RF",
                      metric="mean over sources of RMSE_unflaggedTrain/RMSE_allTrain - 1 (unflagged eval rows, source GroupKFold 10, 5 seeds)",
                      value=round(m, 4), ci_lo=round(ci[0], 4), ci_hi=round(ci[1], 4),
                      threshold="CI upper < 0 (>= 2 of 7 datasets)", verdict=v, n_units=int(len(ps)),
                      note=f"rows flagged (any rule) {nfl}/{meta['n']} (R1 {meta['flags']['R1']}, R2a {meta['flags']['R2a']}, "
                           f"R2b {meta['flags']['R2b']}, R3 {meta['flags']['R3']}, R4 {meta['flags']['R4']}); sources improved {frac_impr:.2f}; "
                           f"pooled change per seed {min(pooled):+.4f}..{max(pooled):+.4f}; leak rows of held-out sources removed in both arms"
                           + ("; NO rows flagged -> arms identical" if nfl == 0 else "")))
        L.append(dict(hypothesis="H5", test_id="H5b_flag_rate", dataset=n, model="audit R1-R4",
                      metric="share of rows flagged by any rule", value=round(nfl / meta["n"], 4),
                      threshold="descriptive", verdict="DESCRIPTIVE", n_units=meta["n"],
                      note=json.dumps(meta["flags"]) + " R4 detail: " + json.dumps(meta["detail"]["r4"])))
    ov_b = "PASS" if nimp >= 2 else "FAIL"
    S["H5b"]["overall"] = dict(verdict=ov_b, n_improved=nimp, n_datasets=len(REAL_SETS))
    L.append(dict(hypothesis="H5", test_id="H5b_overall", dataset="7 datasets", model="RF", metric="datasets with CI upper < 0",
                  value=nimp, threshold=">= 2 of 7 datasets (PREREG predicts FAIL)", verdict=ov_b, n_units=len(REAL_SETS),
                  note="PREREG prior prediction: FAIL likely; value of the audit expected in trust labelling, not accuracy"))
    ov5 = "PASS" if (ov == "PASS" and ov_b == "PASS") else ("FAIL" if (ov == "FAIL" and ov_b == "FAIL") else "PARTIAL")
    S["H5_overall"] = dict(verdict=ov5, H5a=ov, H5b=ov_b)
    L.append(dict(hypothesis="H5", test_id="H5_overall", dataset="all", metric="H5a and H5b verdicts", value=f"H5a={ov}; H5b={ov_b}",
                  threshold="aggregation not defined in PREREG; rule used: PASS if both PASS, FAIL if both FAIL, else PARTIAL",
                  verdict=ov5, n_units=2, note="module verdict; see H5a_overall and H5b_overall"))
    for r in L:   # NaN -> empty cell in the ledger
        for k, v in list(r.items()):
            if isinstance(v, float) and np.isnan(v):
                r[k] = ""
    ledger_write(os.path.join(LEDGER, "h5.csv"), L)
    with open(os.path.join(RESULTS, "h5_summary.json"), "w") as f:
        json.dump(S, f, indent=1, default=float)
    print(json.dumps({"H5a": S["H5a"]["overall"], "H5b": S["H5b"]["overall"], "H5": S["H5_overall"]}, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["base", "inject", "real", "summarize"])
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("etype", nargs="?")
    ap.add_argument("--seeds", default="0-9")
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split("-")) if "-" in a.seeds else (int(a.seeds), int(a.seeds))
    if a.mode == "base":
        run_base(a.dataset)
    elif a.mode == "inject":
        run_inject(a.dataset, a.etype, range(lo, hi + 1))
    elif a.mode == "real":
        run_real(a.dataset)
    else:
        summarize()
