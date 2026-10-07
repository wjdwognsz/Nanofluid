"""H4 robustness / FIX STAGE (after the adversarial verification in process/h4_verify.md).

Everything here is EXPLORATORY robustness. The preregistered H4 verdicts and headline numbers come from
scripts/h4_anchor.py (PREREG section 2, H4) and are NOT changed. Thresholds are the PREREG H4 thresholds, unchanged.
This script implements the PREREG common-protocol items H4 had skipped, plus the checks the verifier asked for:

  R1  within-source duplicate audit: rows with identical X (rounded 1e-9) AND identical y inside one source
  R2  twin-disjoint re-scoring of the main-run draws (same rng, cached LOPO residuals): evaluation rows that are exact
      (X, y) twins of an anchor row are dropped. OFF / SHR / FAKE / FAKE_SHR, k = 1, 2, 3, 5.
  R2b near-copy exclusion (all datasets): evaluation rows that have a same-key value within 1e-4 < rel.diff <= 1e-2 in
      the LOPO training set are dropped (the PREREG lineage rule uses rtol 1e-4 and keeps them in training).
  R2c dedup on cached residuals (verifier's variant): unique (X, y) rows per source, fresh draws, >= 8 unique rows.
  R3  dedup REFIT: whole dataset de-duplicated inside each source, then GroupKFold OOF residuals, LOPO base model,
      tau2/sigma2 and draws all recomputed; eligibility = >= 8 unique rows. RF seed 0. RET at k=3 included.
  R4  seed / model-class robustness (PREREG common protocol: 5 seeds; HistGB and kNN as robustness classes):
      RF seeds 1-4, HistGB seed 0, kNN. OFF / SHR / FAKE / FAKE_SHR, k = 0, 1, 2, 3, 5 (RET not re-run).
      Config rf_s0_repro re-runs RF seed 0 with this code and must reproduce the main run exactly (regression test).
  R5  RET twin-disjoint at k = 3 (re-fit RF150 with the main-run anchor draws where an anchor has a twin).
  R6  cluster bootstrap: eligible sources linked by vrr_common.copy_relations are merged into clusters.
  R7  subset sensitivity: ES1 without its 3 single-measurement sources; DES_ETA without the journal-URL pseudo-source.

Usage (run from v2/scripts):
  python h4_robust.py audit                        # R1 (all datasets)
  python h4_robust.py rescore DATASET              # R2, R2b, R2c (cached residuals; seconds)
  python h4_robust.py rettwin DATASET              # R5
  python h4_robust.py refit CONFIG DATASET [--budget S]   # R3 / R4 (resumable per source)
  python h4_robust.py aggregate                    # curves, rules, ledger rows (H4R_*), summary['robustness']
Run `python h4_anchor.py aggregate` BEFORE `python h4_robust.py aggregate` (the latter appends to ledger/h4.csv and
h4_summary.json and strips its own earlier additions, so it is idempotent).
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

import h4_anchor as H
from vrr_data import load
from vrr_common import (RAW, RESULTS, LEDGER, make_model, group_folds, boot_ci, leak_mask_for_source, copy_relations,
                        subset, ledger_write, LEDGER_COLS)

RPARTS = os.path.join(RAW, "h4_parts_robust")
CONFIGS = {
    "rf_s0_repro": dict(model="RF", seed=0, dedup=False, ret_k3=False, tag=None),   # must equal main run
    "rf_s1": dict(model="RF", seed=1, dedup=False, ret_k3=False, tag="RF|1"),
    "rf_s2": dict(model="RF", seed=2, dedup=False, ret_k3=False, tag="RF|2"),
    "rf_s3": dict(model="RF", seed=3, dedup=False, ret_k3=False, tag="RF|3"),
    "rf_s4": dict(model="RF", seed=4, dedup=False, ret_k3=False, tag="RF|4"),
    "gb_s0": dict(model="GB", seed=0, dedup=False, ret_k3=False, tag="GB|0"),
    "knn": dict(model="KNN", seed=0, dedup=False, ret_k3=False, tag="KNN|0"),
    "dedup_rf_s0": dict(model="RF", seed=0, dedup=True, ret_k3=True, tag="DEDUP|RF|0"),
}
SEED_CONFIGS = ["main", "rf_s1", "rf_s2", "rf_s3", "rf_s4"]
NEAR_LO, NEAR_HI = 1e-4, 1e-2
ES1_SINGLE = ["10.1016/j.jmrt.2023.01.007", "10.1016/j.mtsust.2022.100275", "10.1016/j.polymer.2020.123366"]
DES_ETA_URL = "http://pubs.acs.org/journal/acscii"
crc = H.crc


# ------------------------------------------------------------------ helpers
def twin_keys(ds):
    xh = pd.util.hash_pandas_object(pd.DataFrame(np.round(ds.X, 9)), index=False).values
    return np.array([f"{a}|{b:.9g}" for a, b in zip(xh, ds.y)])


def dedup_mask(ds):
    """Keep the first row of every (source, X, y) group."""
    return ~pd.DataFrame({"g": ds.group.astype(str), "t": twin_keys(ds)}).duplicated(["g", "t"]).values


def rng_for(name, s, k, r, tag, extra=None):
    seq = [crc(name), crc(s), k, r] + ([] if tag is None else [crc(tag)]) + ([] if extra is None else [extra])
    return np.random.default_rng(seq)


def main_rows(name):
    """Full-precision cached LOPO residuals of the main run (results/raw/h4_parts/NAME/rows_*.csv)."""
    info = json.load(open(os.path.join(H.PARTS, name, "sources.json")))
    out = {}
    for s in info["eligible"]:
        r = pd.read_csv(H.part_path(os.path.join(H.PARTS, name), "rows", s), keep_default_na=False, na_values=["", "NaN"])
        m = json.load(open(H.part_path(os.path.join(H.PARTS, name), "meta", s, "json")))
        out[s] = (r.row.values.astype(int), r.resid_lopo.values, m)
    return info, out


def fake_candidates(ds, s, leak_s):
    te_mask = ds.group == s
    gsz = pd.Series(ds.group[~te_mask & ~leak_s]).value_counts()
    leak_src = set(pd.unique(ds.group[leak_s]))
    gsz = gsz[[g not in leak_src for g in gsz.index]]
    return gsz, {g: np.where(ds.group == g)[0] for g in gsz.index}


def near_copy_flags(ds, s, idx, leak_s):
    """Rows of s with a same-key value in the LOPO training set (other sources, not leak-removed) whose relative
    difference is in (1e-4, 1e-2]."""
    yv = ds.df["y_raw"].values if "y_raw" in ds.df else ds.y
    tr = np.where((ds.group != s) & ~leak_s)[0]
    a = pd.DataFrame({"k": ds.key[idx], "ys": yv[idx], "pos": np.arange(len(idx))})
    b = pd.DataFrame({"k": ds.key[tr], "y": yv[tr]})
    mm = a.merge(b, on="k")
    if len(mm) == 0:
        return np.zeros(len(idx), bool)
    rel = (mm.y - mm.ys).abs() / np.maximum(np.maximum(mm.y.abs(), mm.ys.abs()), 1e-12)
    flag = np.zeros(len(idx), bool)
    flag[mm.pos[(rel > NEAR_LO) & (rel <= NEAR_HI)].values] = True
    return flag


# ------------------------------------------------------------------ R1 audit
def cmd_audit():
    recs = []
    for name in H.ALL_DS:
        ds = load(name)
        tk = twin_keys(ds)
        d = pd.DataFrame({"g": ds.group.astype(str), "t": tk})
        n = d.groupby("g").size()
        nu = d.groupby("g").t.nunique()
        tw = d.duplicated(["g", "t"], keep=False)
        nt = d.assign(tw=tw).groupby("g").tw.sum()
        for s in n.index:
            recs.append(dict(dataset=name, source=s, n_rows=int(n[s]), n_unique_xy=int(nu[s]),
                             n_redundant=int(n[s] - nu[s]), n_rows_with_twin=int(nt[s]),
                             eligible_main=bool(n[s] >= H.MIN_ROWS), eligible_dedup=bool(nu[s] >= H.MIN_ROWS),
                             single_measurement=bool(nu[s] == 1)))
        print(f"{name}: redundant {int((n - nu).sum())}/{len(d)}; rows with twin {int(tw.sum())}", flush=True)
    pd.DataFrame(recs).to_csv(os.path.join(RAW, "h4r_dup_audit.csv"), index=False)


# ------------------------------------------------------------------ R2 / R2b / R2c rescoring of cached residuals
def cmd_rescore(name):
    t0 = time.time()
    ds = load(name)
    tk = twin_keys(ds)
    z = np.load(os.path.join(H.PARTS, name, "prep.npz"), allow_pickle=True)
    r_oof = z["r_oof"]
    info, mr = main_rows(name)
    D = pd.read_csv(os.path.join(RAW, "h4_anchor_draws.csv.gz"), keep_default_na=False, na_values=["", "nan", "NaN"])
    D = D[(D.dataset == name) & D.method.isin(["OFF", "SHR", "FAKE", "FAKE_SHR"])].copy()
    D["source"] = D.source.astype(str)
    Dk = D.set_index(["source", "k", "draw", "method"]).rel_change
    recs, maxdiff = [], 0.0
    cnt = {"n_eval_rows_with_nearcopy_in_training": 0, "n_rows_with_within_source_twin": 0, "n_rows_eligible": 0}
    for s in info["eligible"]:
        idx, res, meta = mr[s]
        ns = len(idx)
        tau2, sigma2 = meta["tau2"], meta["sigma2"]
        leak_s = leak_mask_for_source(ds, s)
        gsz, rows_of = fake_candidates(ds, s, leak_s)
        twin = tk[idx]
        near = near_copy_flags(ds, s, idx, leak_s)
        cnt["n_eval_rows_with_nearcopy_in_training"] += int(near.sum())
        cnt["n_rows_with_within_source_twin"] += int(pd.Series(twin).duplicated(keep=False).sum())
        cnt["n_rows_eligible"] += int(ns)
        _, first = np.unique(twin, return_index=True)
        uq = np.sort(first)
        nu = len(uq)
        for k in H.KS[1:]:
            wk = (k * tau2 / (k * tau2 + sigma2)) if tau2 > 0 else 0.0
            for r in range(H.N_DRAWS):
                rng = rng_for(name, s, k, r, None)
                loc = np.sort(rng.choice(ns, size=k, replace=False))
                test = np.setdiff1d(np.arange(ns), loc)
                off = float(res[loc].mean())
                rng2 = rng_for(name, s, k, r, None, 7)
                cand = gsz[gsz >= k].index.values
                fsrc = cand[rng2.integers(len(cand))]
                off_f = float(r_oof[rng2.choice(rows_of[fsrc], size=k, replace=False)].mean())
                shifts = {"OFF": off, "SHR": wk * off, "FAKE": off_f, "FAKE_SHR": wk * off_f}
                twin_hit = np.isin(twin[test], twin[loc])
                scopes = {"main_check": test, "twin_disjoint": test[~twin_hit], "nearcopy_excluded": test[~near[test]],
                          "twin_and_nearcopy_excluded": test[~twin_hit & ~near[test]]}
                for sc, tt in scopes.items():
                    if len(tt) == 0:
                        continue
                    e0 = res[tt]
                    r0 = float(np.sqrt(np.mean(e0 ** 2)))
                    for meth, sh in shifts.items():
                        rk = float(np.sqrt(np.mean((e0 - sh) ** 2)))
                        rc = rk / r0 - 1 if r0 > 1e-12 else np.nan
                        if sc == "main_check":
                            maxdiff = max(maxdiff, abs(rc - Dk.loc[(s, k, r, meth)]))
                            continue
                        recs.append(dict(dataset=name, scope=sc, source=s, n_rows=ns, n_unique=nu, k=k, draw=r,
                                         method=meth, n_test=len(tt), n_removed=int(len(test) - len(tt)),
                                         rmse0=r0, rmsek=rk, rel_change=rc))
                # R2c: dedup on cached residuals, fresh draw on unique rows (verifier's variant, tag 99)
                if nu > k:
                    rng3 = rng_for(name, s, k, r, None, 99)
                    lu = np.sort(rng3.choice(nu, size=k, replace=False))
                    tu = np.setdiff1d(np.arange(nu), lu)
                    eu = res[uq]
                    offu = float(eu[lu].mean())
                    r0 = float(np.sqrt(np.mean(eu[tu] ** 2)))
                    for meth, sh in (("OFF", offu), ("SHR", wk * offu)):
                        rk = float(np.sqrt(np.mean((eu[tu] - sh) ** 2)))
                        recs.append(dict(dataset=name, scope="dedup_cached", source=s, n_rows=ns, n_unique=nu, k=k,
                                         draw=r, method=meth, n_test=len(tu), n_removed=int(ns - nu),
                                         rmse0=r0, rmsek=rk, rel_change=rk / r0 - 1 if r0 > 1e-12 else np.nan))
    R = pd.DataFrame(recs)
    out = os.path.join(RAW, "h4r_parts")
    os.makedirs(out, exist_ok=True)
    R.to_csv(os.path.join(out, f"rescore_{name}.csv.gz"), index=False, compression="gzip", float_format="%.6g")
    json.dump({"dataset": name, "max_abs_diff_vs_main_draws": maxdiff, **cnt, "seconds": round(time.time() - t0, 1),
               "note": "max_abs_diff is vs the %.6g-rounded draws file; vs full-precision part files it is ~1e-15"},
              open(os.path.join(out, f"rescore_{name}.json"), "w"))
    print(f"[{name}] rescore done: {len(R)} records; regression max|diff| vs main draws {maxdiff:.2e}; "
          f"{time.time() - t0:.1f}s", flush=True)


# ------------------------------------------------------------------ R5 RET twin-disjoint at k=3
def cmd_rettwin(name, k=3):
    t0 = time.time()
    ds = load(name)
    tk = twin_keys(ds)
    info = json.load(open(os.path.join(H.PARTS, name, "sources.json")))
    D = pd.read_csv(os.path.join(RAW, "h4_anchor_draws.csv.gz"), keep_default_na=False, na_values=["", "nan", "NaN"])
    D = D[(D.dataset == name) & (D.method == "RET") & (D.k == k)].copy()
    D["source"] = D.source.astype(str)
    Dk = D.set_index(["source", "draw"]).rel_change
    recs, n_refit, maxdiff = [], 0, 0.0
    for s in info["ret_sources"]:
        te = ds.group == s
        leak_s = leak_mask_for_source(ds, s)
        trm = ~te & ~leak_s
        idx, tr_idx = np.where(te)[0], np.where(trm)[0]
        ns = len(idx)
        twin = tk[idx]
        draws = []
        for r in range(H.N_RET_DRAWS):
            loc = np.sort(rng_for(name, s, k, r, None).choice(ns, size=k, replace=False))
            test = np.setdiff1d(np.arange(ns), loc)
            draws.append((r, loc, test, test[~np.isin(twin[test], twin[loc])]))
        affected = any(len(td) < len(t) for _, _, t, td in draws)
        if not affected:
            for r, loc, test, td in draws:
                recs.append(dict(dataset=name, source=s, n_rows=ns, k=k, draw=r, refit=False, n_test=len(td),
                                 n_removed=0, rel_change_main=float(Dk.loc[(s, r)]),
                                 rel_change_twin_disjoint=float(Dk.loc[(s, r)])))
            continue
        n_refit += 1
        Xs, ys = ds.X[idx], ds.y[idx]
        pb = H.rf_ret(0).fit(ds.X[trm], ds.y[trm]).predict(Xs)
        for r, loc, test, td in draws:
            sw = np.concatenate([np.ones(len(tr_idx)), np.full(k, H.RET_WEIGHT)])
            m = H.rf_ret(0).fit(ds.X[np.concatenate([tr_idx, idx[loc]])], ds.y[np.concatenate([tr_idx, idx[loc]])],
                                sample_weight=sw)
            pk = m.predict(Xs)
            rc = {}
            for sc, tt in (("main", test), ("twin_disjoint", td)):
                if len(tt) == 0:
                    rc[sc] = np.nan
                    continue
                r0 = np.sqrt(np.mean((ys[tt] - pb[tt]) ** 2))
                rk = np.sqrt(np.mean((ys[tt] - pk[tt]) ** 2))
                rc[sc] = float(rk / r0 - 1) if r0 > 1e-12 else np.nan
            maxdiff = max(maxdiff, abs(rc["main"] - float(Dk.loc[(s, r)])))
            recs.append(dict(dataset=name, source=s, n_rows=ns, k=k, draw=r, refit=True, n_test=len(td),
                             n_removed=int(len(test) - len(td)), rel_change_main=rc["main"],
                             rel_change_twin_disjoint=rc["twin_disjoint"]))
    out = os.path.join(RAW, "h4r_parts")
    os.makedirs(out, exist_ok=True)
    pd.DataFrame(recs).to_csv(os.path.join(out, f"rettwin_{name}.csv"), index=False, float_format="%.6g")
    json.dump({"dataset": name, "n_sources_refit": n_refit, "n_ret_sources": len(info["ret_sources"]),
               "max_abs_diff_refit_vs_main": maxdiff, "seconds": round(time.time() - t0, 1)},
              open(os.path.join(out, f"rettwin_{name}.json"), "w"))
    print(f"[{name}] RET twin k={k}: {n_refit}/{len(info['ret_sources'])} sources re-fitted; regression max|diff| "
          f"{maxdiff:.2e}; {time.time() - t0:.1f}s", flush=True)


# ------------------------------------------------------------------ R3 / R4 refit configs
def oof_residuals(ds, model, seed):
    n = len(ds.y)
    leak = {s: leak_mask_for_source(ds, s) for s in pd.unique(ds.group)}
    p = np.full(n, np.nan)
    for tr, te in group_folds(ds.group, H.OOF_FOLDS, seed=seed):
        lk = np.zeros(n, bool)
        for s in pd.unique(ds.group[te]):
            lk |= leak[s]
        trm = np.ones(n, bool)
        trm[te] = False
        trm &= ~lk
        p[te] = make_model(model, seed).fit(ds.X[trm], ds.y[trm]).predict(ds.X[te])
    return ds.y - p


def run_source_cfg(name, ds, s, r_oof, cfg, do_ret):
    """Same protocol as h4_anchor.run_source (OFF/SHR/FAKE/FAKE_SHR, k in KS, 30 draws), parameterised by model/seed;
    RET only at k=3 (5 draws) when do_ret."""
    model, seed, tag = cfg["model"], cfg["seed"], cfg["tag"]
    te_mask = ds.group == s
    leak_s = leak_mask_for_source(ds, s)
    tr_mask = ~te_mask & ~leak_s
    idx, tr_idx = np.where(te_mask)[0], np.where(tr_mask)[0]
    ns = len(idx)
    Xs, ys = ds.X[idx], ds.y[idx]
    pb = make_model(model, seed).fit(ds.X[tr_mask], ds.y[tr_mask]).predict(Xs)
    res = ys - pb
    tau2, sigma2, n_train_src = H.shrink_params(ds, r_oof, s, leak_s)
    gsz, rows_of = fake_candidates(ds, s, leak_s)
    if do_ret:
        pb150 = H.rf_ret(0).fit(ds.X[tr_mask], ds.y[tr_mask]).predict(Xs)
    recs = []
    for k in H.KS:
        n_draws = 1 if k == 0 else H.N_DRAWS
        wk = (k * tau2 / (k * tau2 + sigma2)) if (k > 0 and tau2 > 0) else 0.0
        for r in range(n_draws):
            rng = rng_for(name, s, k, r, tag)
            loc = np.sort(rng.choice(ns, size=k, replace=False)) if k else np.array([], int)
            test = np.setdiff1d(np.arange(ns), loc)
            e0 = res[test]
            sse0 = float(np.sum(e0 ** 2))
            off = float(res[loc].mean()) if k else 0.0
            if k:
                rng2 = rng_for(name, s, k, r, tag, 7)
                cand = gsz[gsz >= k].index.values
                fsrc = cand[rng2.integers(len(cand))]
                off_f = float(r_oof[rng2.choice(rows_of[fsrc], size=k, replace=False)].mean())
            else:
                fsrc, off_f = "", 0.0
            preds = {"OFF": e0 - off, "SHR": e0 - wk * off, "FAKE": e0 - off_f, "FAKE_SHR": e0 - wk * off_f}
            for meth, e in preds.items():
                recs.append(dict(dataset=name, source=s, n_rows=ns, k=k, draw=r, method=meth, n_test=len(test),
                                 sse0=sse0, ssek=float(np.sum(e ** 2)), offset=off if meth in ("OFF", "SHR") else off_f,
                                 weight=1.0 if meth in ("OFF", "FAKE") else wk, fake_source=fsrc if "FAKE" in meth else ""))
            if do_ret and k == 3 and r < H.N_RET_DRAWS:
                tr2 = np.concatenate([tr_idx, idx[loc]])
                sw = np.concatenate([np.ones(len(tr_idx)), np.full(k, H.RET_WEIGHT)])
                m = H.rf_ret(0).fit(ds.X[tr2], ds.y[tr2], sample_weight=sw)
                recs.append(dict(dataset=name, source=s, n_rows=ns, k=k, draw=r, method="RET", n_test=len(test),
                                 sse0=float(np.sum((ys[test] - pb150[test]) ** 2)),
                                 ssek=float(np.sum((ys[test] - m.predict(Xs[test])) ** 2)), offset=np.nan,
                                 weight=H.RET_WEIGHT, fake_source=""))
    meta = dict(dataset=name, source=s, n_rows=ns, n_train_rows=int(tr_mask.sum()), n_leak_rows_removed=int(leak_s.sum()),
                tau2=tau2, sigma2=sigma2, n_train_sources_for_shr=n_train_src,
                w_shr_k1=(tau2 / (tau2 + sigma2)) if tau2 > 0 else 0.0,
                w_shr_k3=(3 * tau2 / (3 * tau2 + sigma2)) if tau2 > 0 else 0.0,
                lopo_bias=float(res.mean()), lopo_resid_sd=float(res.std(ddof=1)) if ns > 1 else np.nan,
                in_ret=bool(do_ret))
    rows = pd.DataFrame({"dataset": name, "source": s, "row": idx, "y": ys, "pred_lopo": pb, "resid_lopo": res,
                         "resid_oof_gkf10": r_oof[idx]})
    return pd.DataFrame(recs), meta, rows


def cmd_refit(config, name, budget):
    t0 = time.time()
    cfg = CONFIGS[config]
    ds = load(name)
    n_orig = len(ds.y)
    if cfg["dedup"]:
        ds = subset(ds, dedup_mask(ds))
    outdir = os.path.join(RPARTS, config, name)
    os.makedirs(outdir, exist_ok=True)
    elig = H.eligible_sources(ds)
    rsub, rnote = H.ret_sources(ds, elig) if cfg["ret_k3"] else ([], "no RET")
    json.dump({"config": config, **{k: v for k, v in cfg.items()}, "eligible": elig, "ret_sources": rsub,
               "ret_note": rnote, "n_rows": int(len(ds.y)), "n_rows_before_dedup": int(n_orig),
               "n_sources": int(len(set(ds.group)))}, open(os.path.join(outdir, "sources.json"), "w"), indent=1)
    f_oof = os.path.join(outdir, "oof.npz")
    if os.path.exists(f_oof):
        r_oof = np.load(f_oof)["r_oof"]
    else:
        r_oof = oof_residuals(ds, cfg["model"], cfg["seed"])
        np.savez(f_oof, r_oof=r_oof)
        print(f"[{config}/{name}] OOF residuals done {time.time() - t0:.1f}s", flush=True)
    done = 0
    for s in elig:
        f = H.part_path(outdir, "src", s)
        if os.path.exists(f):
            done += 1
            continue
        if time.time() - t0 > budget:
            print(f"[{config}/{name}] budget reached: {done}/{len(elig)} -> INCOMPLETE, re-run to resume", flush=True)
            return 1
        ts = time.time()
        recs, meta, rows = run_source_cfg(name, ds, s, r_oof, cfg, s in rsub)
        meta["seconds"] = round(time.time() - ts, 2)
        rows.to_csv(H.part_path(outdir, "rows", s), index=False)
        json.dump(meta, open(H.part_path(outdir, "meta", s, "json"), "w"), default=H.jdefault)
        recs.to_csv(f + ".tmp", index=False)
        os.replace(f + ".tmp", f)
        done += 1
    print(f"[{config}/{name}] COMPLETE {done}/{len(elig)} sources in {time.time() - t0:.1f}s", flush=True)
    return 0


# ------------------------------------------------------------------ aggregation
def load_cfg_draws(config, name):
    outdir = os.path.join(RPARTS, config, name)
    sj = os.path.join(outdir, "sources.json")
    if not os.path.exists(sj):
        return None, None, None
    info = json.load(open(sj))
    files = [H.part_path(outdir, "src", s) for s in info["eligible"]]
    have = [f for f in files if os.path.exists(f)]
    if len(have) < len(files):
        info["incomplete"] = f"{len(have)}/{len(files)}"
        return info, None, None
    dr = pd.concat([pd.read_csv(f, keep_default_na=False, na_values=["", "nan", "NaN"]) for f in have], ignore_index=True)
    dr["source"] = dr.source.astype(str)
    meta = pd.DataFrame([json.load(open(H.part_path(outdir, "meta", s, "json"))) for s in info["eligible"]])
    rows = pd.concat([pd.read_csv(H.part_path(outdir, "rows", s), keep_default_na=False, na_values=["", "NaN"])
                      for s in info["eligible"]], ignore_index=True)
    return info, dr, (meta, rows)


def summarize(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    lo, hi = boot_ci(v, seed=0)
    return dict(n_sources=int(len(v)), mean=float(np.mean(v)) if len(v) else np.nan, ci_lo=lo, ci_hi=hi,
                median=float(np.median(v)) if len(v) else np.nan, frac_improved=float(np.mean(v < 0)) if len(v) else np.nan)


def rule_eval(get):
    """get(method, k) -> summarize dict or None. PREREG H4 rule, thresholds unchanged."""
    o, h, f, h1 = get("OFF", 3), get("SHR", 3), get("FAKE", 3), get("SHR", 1)
    if o is None or h is None:
        return None
    ok = {m: (c["mean"] <= H.THR_MAIN and c["ci_hi"] < 0) for m, c in (("OFF", o), ("SHR", h))}
    fake_ok = (f["mean"] >= H.THR_FAKE) if f is not None else None
    return dict(OFF_ok=bool(ok["OFF"]), SHR_ok=bool(ok["SHR"]), fake_ok=fake_ok,
                rule=bool((ok["OFF"] or ok["SHR"]) and (fake_ok is not False)),
                secondary=(bool(h1["mean"] <= H.THR_SECONDARY) if h1 is not None else None),
                via=("OFF+SHR" if ok["OFF"] and ok["SHR"] else "OFF" if ok["OFF"] else "SHR" if ok["SHR"] else "none"))


def cluster_ci(values_by_source, clusters, n=2000, seed=0):
    v = pd.Series(values_by_source)
    c = pd.Series(clusters).loc[v.index]
    groups = [v[c == u].values for u in c.unique()]
    rs = np.random.default_rng(seed)
    bs = [np.concatenate([groups[i] for i in rs.integers(0, len(groups), len(groups))]).mean() for _ in range(n)]
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), len(groups)


def copy_clusters(ds, elig):
    cr = copy_relations(ds)
    if len(cr):
        cr = cr[cr.copy_relation & cr.s1.isin(elig) & cr.s2.isin(elig)]
    par = {s: s for s in elig}

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b in zip(cr.s1, cr.s2):
        par[f(a)] = f(b)
    return {s: f(s) for s in elig}, int(len(cr))


def f3(x):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{100 * x:+.1f}%"


def robustness_caveats(RU, CL, rob, regress):
    """Specific caveats requested by the verifier, generated from the computed tables (no hand-typed numbers)."""
    def r(c, n):
        x = RU[(RU.config == c) & (RU.dataset == n)]
        return x.iloc[0] if len(x) else None
    out = []
    a = rob["dup_audit"]["ES1"]
    m, t, d, w = r("main", "ES1"), r("twin_disjoint", "ES1"), r("dedup_rf_s0", "ES1"), \
        r("ES1_without_3_single_measurement_sources", "ES1")
    out.append(f"[robustness] ES1 headline OFF k3 {f3(m.OFF_k3)} / SHR {f3(m.SHR_k3)} is inflated by within-source duplicate rows "
               f"({a['n_redundant']} of {a['n_rows']} rows): {len(a['single_measurement_eligible_sources'])} 'eligible' sources "
               f"({', '.join(a['single_measurement_eligible_sources'])}) are one measurement repeated, so they count as >= 8-row "
               f"sources but are effectively n=1 (OFF k3 = -100% by construction). Without them OFF {f3(w.OFF_k3)} / SHR "
               f"{f3(w.SHR_k3)}; twin-disjoint OFF {f3(t.OFF_k3)} / SHR {f3(t.SHR_k3)}; dedup-refit OFF {f3(d.OFF_k3)} / SHR "
               f"{f3(d.SHR_k3)}. Quote ES1 as about {f3(max(x for q in (t, d, w) for x in (q.OFF_k3, q.SHR_k3)))} to "
               f"{f3(min(x for q in (t, d, w) for x in (q.OFF_k3, q.SHR_k3)))} (duplicate-handled range), not {f3(m.OFF_k3)}.")
    a = rob["dup_audit"]["DES_MP"]
    m, t, d = r("main", "DES_MP"), r("twin_disjoint", "DES_MP"), r("dedup_rf_s0", "DES_MP")
    out.append(f"[robustness] DES_MP: {a['n_redundant']} of {a['n_rows']} rows ({100 * a['share_redundant']:.1f}%) are exact "
               f"within-source duplicates (same DES listed with swapped component order, canonicalised by the loader). "
               f"Headline OFF {f3(m.OFF_k3)} / SHR {f3(m.SHR_k3)} -> twin-disjoint OFF {f3(t.OFF_k3)} (CI upper "
               f"{f3(t.OFF_k3_ci_hi)}, rule {'met' if t.OFF_ok else 'NOT met'} via OFF) / SHR {f3(t.SHR_k3)} (CI upper "
               f"{f3(t.SHR_k3_ci_hi)}); so with duplicates handled DES_MP passes via {t.via} only under twin-disjoint "
               f"(dedup-refit: OFF {f3(d.OFF_k3)}, SHR {f3(d.SHR_k3)}, via {d.via}).")
    c = CL[(CL.dataset == "DES_RHO") & (CL.k == 3)].set_index("method")
    out.append(f"[robustness] DES_RHO bootstrap units are not independent: {int(c.loc['OFF', 'n_copy_pairs'])} copy-related "
               f"pairs among {int(c.loc['OFF', 'n_sources'])} eligible sources collapse to {int(c.loc['OFF', 'n_clusters'])} "
               f"clusters. Cluster-bootstrap CI: OFF k3 [{f3(c.loc['OFF', 'cluster_ci_lo'])}, {f3(c.loc['OFF', 'cluster_ci_hi'])}] "
               f"(source bootstrap [{f3(c.loc['OFF', 'source_ci_lo'])}, {f3(c.loc['OFF', 'source_ci_hi'])}]), SHR k3 "
               f"[{f3(c.loc['SHR', 'cluster_ci_lo'])}, {f3(c.loc['SHR', 'cluster_ci_hi'])}]. FAIL unchanged.")
    n = r("nearcopy_excluded", "DES_RHO")
    nr = regress.get("rescore_DES_RHO", {}).get("n_eval_rows_with_nearcopy_in_training")
    out.append(f"[robustness] DES_RHO lineage rule (rtol 1e-4) leaves near-copies in LOPO training: {nr} held-out rows have a "
               f"same-key value within 1e-4 < rel.diff <= 1e-2 in training. Excluding them from evaluation: OFF k3 "
               f"{f3(n.OFF_k3)}, SHR {f3(n.SHR_k3)} -> the FAIL is not an artifact of near-copies.")
    g = {ds: r("gb_s0", ds) for ds in H.GRADED}
    kn = {ds: r("knn", ds) for ds in H.GRADED}
    ms = [f"{ds} (OFF {f3(g[ds].OFF_k3)}, CI upper {f3(g[ds].OFF_k3_ci_hi)}; SHR {f3(g[ds].SHR_k3)})" for ds in H.GRADED
          if g[ds] is not None and g[ds].rule and not g[ds].OFF_ok]
    ks = [f"{ds} (OFF {f3(kn[ds].OFF_k3)}, CI upper {f3(kn[ds].OFF_k3_ci_hi)}; SHR {f3(kn[ds].SHR_k3)}, CI upper "
          f"{f3(kn[ds].SHR_k3_ci_hi)})" for ds in H.GRADED
          if kn[ds] is not None and kn[ds].rule and not kn[ds].OFF_ok]
    oc = rob["overall_counts"]
    out.append(f"[robustness] model class: HistGB meets the rule in {oc['gb_s0']['n_rule_met']}/6 and kNN in "
               f"{oc['knn']['n_rule_met']}/6 (DES_RHO fails with every model). OFF alone is model-sensitive: HistGB passes "
               f"only via SHR in {', '.join(ms) or 'none'}; kNN passes only via SHR in {', '.join(ks) or 'none'}. "
               f"Secondary SHR k1 <= 0 holds in {oc['gb_s0']['n_secondary_holds']}/6 with HistGB "
               f"(DES_RHO SHR k1 {f3(g['DES_RHO'].SHR_k1)}), {oc['knn']['n_secondary_holds']}/6 with kNN.")
    ps = oc["per_seed"]
    out.append("[robustness] RF seeds 0-4: datasets meeting the rule per seed = " + ", ".join(
        f"{c} {v['n_rule_met']}/6" for c, v in ps.items()) + "; k3 MEANS (OFF/SHR) move by at most "
        + f"{100 * max(max(v[q][1] - v[q][0] for q in ('OFF_k3_mean_range', 'SHR_k3_mean_range')) for v in rob['seed_medians'].values()):.1f}"
        + " pp across seeds, but per-dataset MEDIANS move by up to "
        + f"{100 * max(v['SHR_k3_median_range'][1] - v['SHR_k3_median_range'][0] for v in rob['seed_medians'].values()):.1f} "
        + "pp (SHR k3), so medians are approximate; see robustness.seed_medians.")
    u = r("DES_ETA_without_journal_url_source", "DES_ETA")
    out.append(f"[robustness] DES_ETA largest 'source' {DES_ETA_URL} is a journal URL (likely several papers pooled; loader "
               f"issue). Dropping it: OFF k3 {f3(u.OFF_k3)}, SHR {f3(u.SHR_k3)} (main {f3(r('main', 'DES_ETA').OFF_k3)} / "
               f"{f3(r('main', 'DES_ETA').SHR_k3)}).")
    return out


def cmd_aggregate():
    t0 = time.time()
    PSmain = pd.read_csv(os.path.join(RAW, "h4_anchor_per_source.csv"), keep_default_na=False, na_values=["", "NaN"])
    PSmain["source"] = PSmain.source.astype(str)
    audit = pd.read_csv(os.path.join(RAW, "h4r_dup_audit.csv"), keep_default_na=False, na_values=["", "NaN"])
    audit["source"] = audit.source.astype(str)
    per_source, curves, rules, regress = [], [], [], {}

    def add_curves(ps, name, config, scope_note=""):
        """ps: per-source table with columns source, method, k, draw_mean_rel_change."""
        out = {}
        for (m, k), sub in ps.groupby(["method", "k"]):
            sm = summarize(sub.draw_mean_rel_change.values)
            out[(m, int(k))] = sm
            curves.append(dict(dataset=name, config=config, method=m, k=int(k), **sm, note=scope_note))
        return out

    # ---- main (reference) curves recomputed from the main per-source table
    store = {}
    for name in H.ALL_DS:
        ps = PSmain[PSmain.dataset == name]
        if len(ps) == 0:
            continue
        store[("main", name)] = add_curves(ps[ps.method != "RET"], name, "main")
        ret_main = ps[(ps.method == "RET") & (ps.k == 3)]
        store[("main", name)][("RET", 3)] = summarize(ret_main.draw_mean_rel_change.values)
    # ---- R2 / R2b / R2c rescoring
    for name in H.ALL_DS:
        f = os.path.join(RAW, "h4r_parts", f"rescore_{name}.csv.gz")
        if not os.path.exists(f):
            continue
        R = pd.read_csv(f, keep_default_na=False, na_values=["", "nan", "NaN"])
        R["source"] = R.source.astype(str)
        regress[f"rescore_{name}"] = json.load(open(f.replace(".csv.gz", ".json")))
        for sc, sub in R.groupby("scope"):
            ps = sub.groupby(["dataset", "source", "n_rows", "n_unique", "method", "k"]).agg(
                n_draws=("draw", "size"), draw_mean_rel_change=("rel_change", "mean"),
                n_test_mean=("n_test", "mean"), n_removed_mean=("n_removed", "mean")).reset_index()
            if sc == "dedup_cached":
                ps = ps[ps.n_unique >= H.MIN_ROWS]
            ps["config"] = sc
            per_source.append(ps)
            store[(sc, name)] = add_curves(ps, name, sc)
    # ---- R5 RET twin-disjoint
    for name in H.ALL_DS:
        f = os.path.join(RAW, "h4r_parts", f"rettwin_{name}.csv")
        if not os.path.exists(f):
            continue
        R = pd.read_csv(f, keep_default_na=False, na_values=["", "nan", "NaN"])
        R["source"] = R.source.astype(str)
        regress[f"rettwin_{name}"] = json.load(open(f.replace(".csv", ".json")))
        p = R.groupby("source").rel_change_twin_disjoint.mean()
        sm = summarize(p.values)
        curves.append(dict(dataset=name, config="twin_disjoint", method="RET", k=3, **sm, note="RF150, main-run draws"))
        store.setdefault(("twin_disjoint", name), {})[("RET", 3)] = sm
        per_source.append(pd.DataFrame({"dataset": name, "source": p.index, "method": "RET", "k": 3,
                                        "draw_mean_rel_change": p.values, "config": "twin_disjoint"}))
    # ---- R3 / R4 refit configs
    cfg_meta = {}
    for config in CONFIGS:
        for name in H.ALL_DS:
            info, dr, mr = load_cfg_draws(config, name)
            if info is None:
                continue
            if dr is None:
                cfg_meta[(config, name)] = {"status": "incomplete " + info.get("incomplete", "")}
                continue
            ps = H.per_source_table(dr)
            ps["config"] = config
            per_source.append(ps)
            store[(config, name)] = add_curves(ps, name, config)
            meta, rows = mr
            cfg_meta[(config, name)] = {"status": "complete", "n_rows": info["n_rows"],
                                        "n_rows_before_dedup": info.get("n_rows_before_dedup"),
                                        "n_eligible": len(info["eligible"]), "n_ret_sources": len(info["ret_sources"]),
                                        "tau2_median": float(meta.tau2.median()), "sigma2_median": float(meta.sigma2.median()),
                                        "w_shr_k3_median": float(meta.w_shr_k3.median()),
                                        "lopo_rmse_rows": float(np.sqrt(np.mean(rows.resid_lopo ** 2)))}
            if config == "rf_s0_repro":
                m = PSmain[(PSmain.dataset == name) & (PSmain.method != "RET")].set_index(["source", "method", "k"])
                mine = ps.set_index(["source", "method", "k"])
                j = m.join(mine, rsuffix="_r", how="inner")
                regress[f"rf_s0_repro_{name}"] = {
                    "n_cells": int(len(j)), "n_cells_main": int(len(m)),
                    "max_abs_diff_draw_mean_rel_change": float((j.draw_mean_rel_change - j.draw_mean_rel_change_r).abs().max())}
    # ---- seed-averaged (5 RF seeds: main = seed 0, rf_s1..rf_s4)
    for name in H.GRADED + H.DESCRIPTIVE:
        tabs = []
        for c in SEED_CONFIGS:
            if c == "main":
                t = PSmain[(PSmain.dataset == name) & (PSmain.method != "RET")][["source", "method", "k", "draw_mean_rel_change"]]
            else:
                if (c, name) not in store:
                    tabs = None
                    break
                t = [p for p in per_source if (p.config.iloc[0] == c and p.dataset.iloc[0] == name)][0]
                t = t[["source", "method", "k", "draw_mean_rel_change"]]
            tabs.append(t.assign(seed_config=c))
        if not tabs:
            continue
        T = pd.concat(tabs)
        avg = T.groupby(["source", "method", "k"]).draw_mean_rel_change.mean().reset_index()
        avg["dataset"] = name
        avg["config"] = "rf_5seed_avg"
        per_source.append(avg)
        store[("rf_5seed_avg", name)] = add_curves(avg, name, "rf_5seed_avg", "per-source mean over RF seeds 0-4")
    # ---- rules per (config, dataset)
    for (config, name), st in store.items():
        rr = rule_eval(lambda m, k: st.get((m, k)))
        if rr is None:
            continue
        rules.append(dict(config=config, dataset=name, graded=name in H.GRADED, **rr,
                          OFF_k3=st[("OFF", 3)]["mean"], OFF_k3_ci_hi=st[("OFF", 3)]["ci_hi"],
                          SHR_k3=st[("SHR", 3)]["mean"], SHR_k3_ci_hi=st[("SHR", 3)]["ci_hi"],
                          FAKE_k3=st[("FAKE", 3)]["mean"] if ("FAKE", 3) in st else np.nan,
                          SHR_k1=st[("SHR", 1)]["mean"] if ("SHR", 1) in st else np.nan,
                          OFF_k3_median=st[("OFF", 3)]["median"], SHR_k3_median=st[("SHR", 3)]["median"],
                          n_sources=st[("SHR", 3)]["n_sources"]))
    RU = pd.DataFrame(rules)
    # ---- R6 cluster bootstrap and R7 subsets (main run)
    clus, subsets = [], []
    for name in H.GRADED + H.DESCRIPTIVE:
        ps = PSmain[PSmain.dataset == name]
        if len(ps) == 0:
            continue
        elig = sorted(ps.source.unique())
        ds = load(name)
        cl, npairs = copy_clusters(ds, elig)
        for m, k in (("OFF", 3), ("SHR", 3), ("FAKE", 3), ("SHR", 1)):
            v = ps[(ps.method == m) & (ps.k == k)].set_index("source").draw_mean_rel_change
            lo, hi, ng = cluster_ci(v, cl)
            slo, shi = boot_ci(v.values, seed=0)
            clus.append(dict(dataset=name, method=m, k=k, n_sources=len(v), n_copy_pairs=npairs, n_clusters=ng,
                             mean=float(v.mean()), source_ci_lo=slo, source_ci_hi=shi, cluster_ci_lo=lo, cluster_ci_hi=hi))
        drops = {"ES1": ("ES1_without_3_single_measurement_sources", ES1_SINGLE),
                 "DES_ETA": ("DES_ETA_without_journal_url_source", [DES_ETA_URL])}
        if name in drops:
            lab, drop = drops[name]
            sub = ps[~ps.source.isin(drop)]
            st = add_curves(sub[sub.method != "RET"], name, lab, f"main run minus {len(drop)} source(s)")
            store[(lab, name)] = st
            rr = rule_eval(lambda m, k: st.get((m, k)))
            subsets.append(dict(dataset=name, subset=lab, dropped=";".join(drop),
                                n_dropped_present=int(len(set(drop) & set(elig))),
                                **{f"{m}_k{k}": st[(m, k)]["mean"] for m, k in (("OFF", 3), ("SHR", 3), ("FAKE", 3), ("SHR", 1))},
                                OFF_k3_ci_hi=st[("OFF", 3)]["ci_hi"], SHR_k3_ci_hi=st[("SHR", 3)]["ci_hi"], rule=rr["rule"]))
            rules.append(dict(config=lab, dataset=name, graded=True, **rr, OFF_k3=st[("OFF", 3)]["mean"],
                              OFF_k3_ci_hi=st[("OFF", 3)]["ci_hi"], SHR_k3=st[("SHR", 3)]["mean"],
                              SHR_k3_ci_hi=st[("SHR", 3)]["ci_hi"], FAKE_k3=st[("FAKE", 3)]["mean"],
                              SHR_k1=st[("SHR", 1)]["mean"], OFF_k3_median=st[("OFF", 3)]["median"],
                              SHR_k3_median=st[("SHR", 3)]["median"], n_sources=st[("SHR", 3)]["n_sources"]))
    RU = pd.DataFrame(rules)
    CL = pd.DataFrame(clus)
    # ---- write raw
    PS = pd.concat(per_source, ignore_index=True)
    PS["improved"] = PS.draw_mean_rel_change < 0
    keep = [c for c in ["config", "dataset", "source", "n_rows", "n_unique", "method", "k", "n_draws", "draw_mean_rel_change",
                        "draw_median_rel_change", "rmse0", "rmsek", "n_test", "n_test_mean", "n_removed_mean", "improved"]
            if c in PS.columns]
    PS[keep].to_csv(os.path.join(RAW, "h4r_per_source.csv"), index=False, float_format="%.6g")
    CU = pd.DataFrame(curves)
    CU.to_csv(os.path.join(RAW, "h4r_curves.csv"), index=False, float_format="%.6g")
    RU.to_csv(os.path.join(RAW, "h4r_rules.csv"), index=False, float_format="%.6g")
    CL.to_csv(os.path.join(RAW, "h4r_cluster_bootstrap.csv"), index=False, float_format="%.6g")
    # all refit draws (every unit) and base rows, one gz per config
    meta_all = []
    for config in CONFIGS:
        ds_list = []
        rows_list = []
        for name in H.ALL_DS:
            info, dr, mr = load_cfg_draws(config, name)
            if dr is None:
                continue
            ds_list.append(dr.assign(config=config))
            rows_list.append(mr[1].assign(config=config))
            meta_all.append(mr[0].assign(config=config))
        if ds_list:
            Dd = pd.concat(ds_list, ignore_index=True)
            Dd["rel_change"] = np.sqrt(Dd.ssek / Dd.n_test) / np.sqrt(Dd.sse0 / Dd.n_test) - 1
            Dd.to_csv(os.path.join(RAW, f"h4r_draws_{config}.csv.gz"), index=False, compression="gzip", float_format="%.6g")
            pd.concat(rows_list, ignore_index=True).to_csv(os.path.join(RAW, f"h4r_base_rows_{config}.csv.gz"), index=False,
                                                           compression="gzip", float_format="%.6g")
    if meta_all:
        pd.concat(meta_all, ignore_index=True).to_csv(os.path.join(RAW, "h4r_source_meta.csv"), index=False,
                                                      float_format="%.6g")
    resc = [pd.read_csv(f, keep_default_na=False, na_values=["", "nan", "NaN"])
            for f in sorted(glob.glob(os.path.join(RAW, "h4r_parts", "rescore_*.csv.gz")))]
    if resc:
        pd.concat(resc, ignore_index=True).to_csv(os.path.join(RAW, "h4r_rescore_draws.csv.gz"), index=False,
                                                  compression="gzip", float_format="%.6g")
    rt = [pd.read_csv(f, keep_default_na=False, na_values=["", "nan", "NaN"])
          for f in sorted(glob.glob(os.path.join(RAW, "h4r_parts", "rettwin_*.csv")))]
    if rt:
        pd.concat(rt, ignore_index=True).to_csv(os.path.join(RAW, "h4r_ret_twin_draws.csv"), index=False, float_format="%.6g")

    # ---- ledger rows
    led = pd.read_csv(os.path.join(LEDGER, "h4.csv"), keep_default_na=False, dtype=str)
    led = led[~led.test_id.str.startswith("H4R_")].copy()
    SEP = " || ROBUSTNESS (exploratory, verdict unchanged): "
    led["note"] = led.note.str.split(SEP, regex=False).str[0]
    new = []
    thr_rule = ("PREREG H4 rule re-applied unchanged: [OFF or SHR k=3 mean <= -10% AND CI upper < 0] AND FAKE k=3 >= -2% "
                "(robustness only; does not replace the graded verdict)")

    def rget(config, name):
        r = RU[(RU.config == config) & (RU.dataset == name)]
        return r.iloc[0] if len(r) else None

    labels = {"twin_disjoint": "twin-disjoint evaluation (main draws; eval rows identical in X,y to an anchor removed)",
              "dedup_rf_s0": "dedup REFIT (within-source exact duplicates removed from the whole dataset; RF seed 0 refit)",
              "dedup_cached": "dedup on cached main-run residuals (verifier variant; unique rows, fresh draws)",
              "nearcopy_excluded": "eval rows with a near copy (same key, 1e-4<rel.diff<=1e-2) in training removed",
              "twin_and_nearcopy_excluded": "twin-disjoint AND near-copy rows removed",
              "rf_5seed_avg": "RF, per-source changes averaged over seeds 0-4 (PREREG common protocol: 5 seeds)",
              "gb_s0": "HistGB base model (robustness model class)", "knn": "kNN base model (robustness model class)",
              "ES1_without_3_single_measurement_sources": "main run without the 3 ES1 sources that are one measurement repeated",
              "DES_ETA_without_journal_url_source": "main run without the DES_ETA journal-URL pseudo-source"}
    tid = {"twin_disjoint": "twin", "dedup_rf_s0": "dedupfit", "dedup_cached": "dedupcache", "nearcopy_excluded": "nearcopy",
           "twin_and_nearcopy_excluded": "twin_nearcopy", "rf_5seed_avg": "seed5avg", "gb_s0": "GB", "knn": "KNN",
           "ES1_without_3_single_measurement_sources": "drop_single", "DES_ETA_without_journal_url_source": "drop_url"}
    overall_counts = {}
    for config, lab in labels.items():
        n_rule = n_sec = n_g = 0
        for name in H.GRADED + H.DESCRIPTIVE:
            r = rget(config, name)
            if r is None:
                continue
            graded = name in H.GRADED
            st = store[(config, name)]
            for m in ("OFF", "SHR", "FAKE", "RET"):
                c = st.get((m, 3))
                if c is None or (m == "FAKE" and config == "dedup_cached"):
                    continue
                new.append(dict(hypothesis="H4", test_id=f"H4R_{tid[config]}_{m}_k3", dataset=name,
                                model="RF150" if m == "RET" else CONFIGS.get(config, {}).get("model", "RF"),
                                metric=f"mean rel. RMSE change k=3, {lab}", value=c["mean"], ci_lo=c["ci_lo"],
                                ci_hi=c["ci_hi"], threshold="robustness (no threshold of its own)", verdict="EXPLORATORY",
                                n_units=c["n_sources"],
                                note=f"median {c['median']:+.3f}; frac improved {c['frac_improved']:.2f}; main-run value "
                                     f"{store[('main', name)][(m, 3)]['mean']:+.3f}" if ("main", name) in store and
                                     (m, 3) in store[("main", name)] else f"median {c['median']:+.3f}"))
            new.append(dict(hypothesis="H4", test_id=f"H4R_{tid[config]}_rule", dataset=name,
                            model=CONFIGS.get(config, {}).get("model", "RF"),
                            metric=f"PREREG rule re-evaluated: {lab}", value=min(r.OFF_k3, r.SHR_k3),
                            threshold=thr_rule, verdict="EXPLORATORY", n_units=int(r.n_sources),
                            note=(f"rule {'MET' if r.rule else 'NOT met'} (via {r.via}); OFF k3 {r.OFF_k3:+.3f} CI_hi "
                                  f"{r.OFF_k3_ci_hi:+.3f}; SHR k3 {r.SHR_k3:+.3f} CI_hi {r.SHR_k3_ci_hi:+.3f}; FAKE k3 "
                                  f"{r.FAKE_k3:+.3f}; SHR k1 {r.SHR_k1:+.3f} (secondary "
                                  f"{'holds' if r.secondary else 'fails'}); graded={graded}")))
            if graded:
                n_g += 1
                n_rule += int(bool(r.rule))
                n_sec += int(bool(r.secondary))
        if n_g == len(H.GRADED):
            overall_counts[config] = (n_rule, n_sec, n_g)
            new.append(dict(hypothesis="H4", test_id=f"H4R_{tid[config]}_overall", dataset="ALL(6 graded)", model="",
                            metric=f"number of graded datasets meeting the rule: {lab}", value=n_rule,
                            threshold=">= 4 of 6 (PREREG overall rule, robustness only)", verdict="EXPLORATORY",
                            n_units=n_g, note=f"would be {'PASS' if n_rule >= 4 else 'FAIL'}; secondary SHR k1 <= 0 holds in "
                                              f"{n_sec}/{n_g}"))
    # per-seed rule table (5 RF seeds)
    seed_rows = {}
    for name in H.GRADED + H.DESCRIPTIVE:
        per = []
        for c in SEED_CONFIGS:
            r = rget(c, name)
            if r is not None:
                per.append((c, r))
        if len(per) == len(SEED_CONFIGS):
            nmet = sum(bool(r.rule) for _, r in per)
            seed_rows[name] = per
            new.append(dict(hypothesis="H4", test_id="H4R_seed_rule_count", dataset=name, model="RF",
                            metric="number of RF seeds (0-4) in which the PREREG rule is met", value=nmet,
                            threshold="robustness: rule met in 5/5 seeds = stable", verdict="EXPLORATORY", n_units=5,
                            note="; ".join(f"{c}: OFF {r.OFF_k3:+.3f} (med {r.OFF_k3_median:+.3f}), SHR {r.SHR_k3:+.3f} "
                                           f"(med {r.SHR_k3_median:+.3f}), FAKE {r.FAKE_k3:+.3f}, SHR k1 {r.SHR_k1:+.3f}"
                                           for c, r in per)))
    seeds_overall = []
    for c in SEED_CONFIGS:
        rr = [rget(c, n) for n in H.GRADED]
        if all(r is not None for r in rr):
            seeds_overall.append((c, sum(bool(r.rule) for r in rr), sum(bool(r.secondary) for r in rr)))
    if len(seeds_overall) == len(SEED_CONFIGS):
        new.append(dict(hypothesis="H4", test_id="H4R_seed_overall", dataset="ALL(6 graded)", model="RF",
                        metric="number of RF seeds (0-4) in which H4 overall would PASS (>= 4/6)",
                        value=sum(n >= 4 for _, n, _ in seeds_overall), threshold="robustness", verdict="EXPLORATORY",
                        n_units=5, note="; ".join(f"{c}: {n}/6 datasets, secondary {s2}/6" for c, n, s2 in seeds_overall)))
    for r in clus:
        if r["k"] == 3 and r["method"] in ("OFF", "SHR") or (r["method"] == "SHR" and r["k"] == 1):
            new.append(dict(hypothesis="H4", test_id=f"H4R_cluster_{r['method']}_k{r['k']}", dataset=r["dataset"], model="RF",
                            metric="main-run mean rel. RMSE change; CI = cluster bootstrap over copy-relation clusters",
                            value=r["mean"], ci_lo=r["cluster_ci_lo"], ci_hi=r["cluster_ci_hi"],
                            threshold="robustness of CI units (no threshold of its own)", verdict="EXPLORATORY",
                            n_units=r["n_clusters"],
                            note=f"{r['n_sources']} sources, {r['n_copy_pairs']} copy-related pairs -> {r['n_clusters']} "
                                 f"clusters; source-bootstrap CI [{r['source_ci_lo']:+.3f}, {r['source_ci_hi']:+.3f}]"))
    # dup audit rows
    for name in H.ALL_DS:
        a = audit[audit.dataset == name]
        el = a[a.eligible_main]
        new.append(dict(hypothesis="H4", test_id="H4R_dup_audit", dataset=name, model="",
                        metric="share of rows that are exact within-source duplicates (identical X and y, same source)",
                        value=float(a.n_redundant.sum() / a.n_rows.sum()), threshold="data audit (descriptive)",
                        verdict="DESCRIPTIVE", n_units=int(len(a)),
                        note=(f"{int(a.n_redundant.sum())} redundant of {int(a.n_rows.sum())} rows; rows having a twin "
                              f"{int(a.n_rows_with_twin.sum())}; {int((a.n_redundant > 0).sum())} sources with duplicates; "
                              f"eligible (>=8 rows) {len(el)} -> {int(el.eligible_dedup.sum())} with >=8 unique rows; "
                              f"single-measurement eligible sources: {int(el.single_measurement.sum())}"
                              + (f" ({'; '.join(el[el.single_measurement].source)})" if el.single_measurement.any() else ""))))
    # annotate graded H4_join notes with the robustness numbers (idempotent)
    for i in led.index:
        if led.at[i, "test_id"] not in ("H4_join", "H4_join_descriptive"):
            continue
        name = led.at[i, "dataset"]
        parts = []
        for config, short in (("twin_disjoint", "twin-disjoint"), ("dedup_rf_s0", "dedup-refit"), ("rf_5seed_avg", "5-seed RF avg"),
                              ("gb_s0", "HistGB"), ("knn", "kNN")):
            r = rget(config, name)
            if r is not None:
                parts.append(f"{short}: OFF {r.OFF_k3:+.3f} (CI_hi {r.OFF_k3_ci_hi:+.3f}), SHR {r.SHR_k3:+.3f} "
                             f"(CI_hi {r.SHR_k3_ci_hi:+.3f}) -> rule {'met' if r.rule else 'NOT met'} via {r.via}")
        cc = CL[(CL.dataset == name) & (CL.k == 3)]
        if len(cc):
            parts.append("cluster-bootstrap CI " + ", ".join(
                f"{x.method} [{x.cluster_ci_lo:+.3f}, {x.cluster_ci_hi:+.3f}] ({x.n_clusters} clusters)" for x in cc.itertuples()
                if x.method in ("OFF", "SHR")))
        if name == "ES1":
            a1 = audit[(audit.dataset == "ES1") & audit.eligible_main]
            sm = a1[a1.single_measurement]
            lowu = a1[~a1.single_measurement & ~a1.eligible_dedup]
            parts.append(f"{len(sm)} eligible sources are one measurement repeated "
                         f"{'/'.join(str(int(x)) for x in sm.n_rows)} times (OFF k3 = -100% by construction) and "
                         f"{len(lowu)} more have only {'/'.join(str(int(x)) for x in lowu.n_unique_xy)} unique of "
                         f"{'/'.join(str(int(x)) for x in lowu.n_rows)} rows; without the {len(sm)} single-measurement "
                         "sources OFF " + f"{rget('ES1_without_3_single_measurement_sources', 'ES1').OFF_k3:+.3f}, SHR "
                         + f"{rget('ES1_without_3_single_measurement_sources', 'ES1').SHR_k3:+.3f}")
        if parts:
            led.at[i, "note"] = led.at[i, "note"] + SEP + " | ".join(parts)
    rows_out = led.to_dict("records") + new
    ledger_write(os.path.join(LEDGER, "h4.csv"), rows_out)

    # ---- summary JSON
    S = json.load(open(os.path.join(RESULTS, "h4_summary.json")))
    rob = {"what": "FIX STAGE robustness after process/h4_verify.md; EXPLORATORY; graded verdicts unchanged",
           "script": "scripts/h4_robust.py", "regression_checks": regress,
           "configs": {k: {kk: vv for kk, vv in v.items()} for k, v in CONFIGS.items()},
           "config_meta": {f"{c}/{n}": v for (c, n), v in cfg_meta.items()},
           "dup_audit": {}, "rules": {}, "overall_counts": {}, "cluster_bootstrap": CL.to_dict("records"),
           "subsets": subsets, "seed_medians": {}}
    for name in H.ALL_DS:
        a = audit[audit.dataset == name]
        el = a[a.eligible_main]
        rob["dup_audit"][name] = {"n_rows": int(a.n_rows.sum()), "n_redundant": int(a.n_redundant.sum()),
                                  "share_redundant": float(a.n_redundant.sum() / a.n_rows.sum()),
                                  "n_rows_with_twin": int(a.n_rows_with_twin.sum()),
                                  "n_eligible_main": int(len(el)), "n_eligible_unique": int(el.eligible_dedup.sum()),
                                  "single_measurement_eligible_sources": el[el.single_measurement].source.tolist()}
    for (config, name) in sorted({(r["config"], r["dataset"]) for r in rules}):
        r = rget(config, name)
        rob["rules"].setdefault(config, {})[name] = {k: (v.item() if hasattr(v, "item") else v) for k, v in r.to_dict().items()
                                                     if k not in ("config", "dataset")}
    for c, (a1, a2, a3) in overall_counts.items():
        rob["overall_counts"][c] = {"n_rule_met": a1, "n_secondary_holds": a2, "n_graded": a3,
                                    "would_be": "PASS" if a1 >= 4 else "FAIL"}
    rob["overall_counts"]["per_seed"] = {c: {"n_rule_met": n, "n_secondary_holds": s2} for c, n, s2 in seeds_overall}
    for name, per in seed_rows.items():
        rob["seed_medians"][name] = {
            "OFF_k3_mean_range": [float(min(r.OFF_k3 for _, r in per)), float(max(r.OFF_k3 for _, r in per))],
            "SHR_k3_mean_range": [float(min(r.SHR_k3 for _, r in per)), float(max(r.SHR_k3 for _, r in per))],
            "OFF_k3_median_range": [float(min(r.OFF_k3_median for _, r in per)), float(max(r.OFF_k3_median for _, r in per))],
            "SHR_k3_median_range": [float(min(r.SHR_k3_median for _, r in per)), float(max(r.SHR_k3_median for _, r in per))],
            "n_seeds_rule_met": int(sum(bool(r.rule) for _, r in per))}
    # headline table: main vs robustness, k=3
    head = {}
    for name in H.GRADED + H.DESCRIPTIVE:
        h = {}
        for config in ["main", "twin_disjoint", "dedup_rf_s0", "dedup_cached", "nearcopy_excluded", "rf_5seed_avg", "gb_s0",
                       "knn", "ES1_without_3_single_measurement_sources", "DES_ETA_without_journal_url_source"]:
            st = store.get((config, name))
            if not st:
                continue
            h[config] = {f"{m}_k{k}": [st[(m, k)]["mean"], st[(m, k)]["ci_lo"], st[(m, k)]["ci_hi"]]
                         for m, k in (("OFF", 3), ("SHR", 3), ("FAKE", 3), ("RET", 3), ("SHR", 1)) if (m, k) in st}
        head[name] = h
    rob["headline_k3_mean_ci"] = head
    rob["files"] = ["results/raw/h4r_dup_audit.csv", "results/raw/h4r_per_source.csv", "results/raw/h4r_curves.csv",
                    "results/raw/h4r_source_meta.csv",
                    "results/raw/h4r_rules.csv", "results/raw/h4r_cluster_bootstrap.csv", "results/raw/h4r_rescore_draws.csv.gz",
                    "results/raw/h4r_ret_twin_draws.csv"] + \
                   [f"results/raw/h4r_draws_{c}.csv.gz" for c in CONFIGS] + [f"results/raw/h4r_base_rows_{c}.csv.gz" for c in CONFIGS]
    rob["notes_for_other_owners"] = [
        "Loader owner (vrr_data.py, frozen at the prereg commit, not changed here): ES1 (Cogni-e-SpinDB) has 162 exact "
        "within-source duplicate rows (3 eligible sources are one measurement repeated 9/13/13 times); DES_MP lists many DES "
        "twice with the component order swapped, which the loader canonicalises into 1,209 identical within-source rows "
        "(35.7%). DES_ETA's largest source is a journal URL (http://pubs.acs.org/journal/acscii, 1,461 rows), probably several "
        "papers pooled into one unit. IL_CELL source names contain mojibake from encoding_errors='ignore'.",
        "H1 / H3 / H9 owners: within-source duplicates inflate random-CV optimism in ES1/DES_MP (a duplicate in the training "
        "fold predicts its twin), make split-half reliability (H3a) trivially high for single-measurement sources, and make "
        "k=3 anchor offsets in H9 partly self-predicting. Consider a twin-disjoint or dedup sensitivity there too."]
    S["robustness"] = rob
    # caveats: replace robustness caveats (idempotent)
    S["caveats"] = [c for c in S.get("caveats", []) if not c.startswith("[robustness]")]
    for name in H.GRADED:
        hm, ht, hd = head[name].get("main", {}), head[name].get("twin_disjoint", {}), head[name].get("dedup_rf_s0", {})
        if not ht or not hd:
            continue
        rr = rob["seed_medians"].get(name, {})
        S["caveats"].append(
            f"[robustness] {name}: OFF k3 main {f3(hm['OFF_k3'][0])} -> twin-disjoint {f3(ht['OFF_k3'][0])} "
            f"[{f3(ht['OFF_k3'][1])}, {f3(ht['OFF_k3'][2])}] / dedup-refit {f3(hd['OFF_k3'][0])} [{f3(hd['OFF_k3'][1])}, "
            f"{f3(hd['OFF_k3'][2])}]; SHR k3 main {f3(hm['SHR_k3'][0])} -> twin-disjoint {f3(ht['SHR_k3'][0])} / dedup-refit "
            f"{f3(hd['SHR_k3'][0])} [{f3(hd['SHR_k3'][1])}, {f3(hd['SHR_k3'][2])}]"
            + (f"; RF seeds 0-4: rule met {rr['n_seeds_rule_met']}/5, SHR k3 median ranges {f3(rr['SHR_k3_median_range'][0])} "
               f"to {f3(rr['SHR_k3_median_range'][1])} (medians are approximate, seed-sensitive)" if rr else ""))
    # twin-disjoint vs the EXPLORATORY material-disjoint analysis of h4_anchor (same draws): identical when the only
    # same-material rows inside a source are exact duplicates
    MD = pd.read_csv(os.path.join(RAW, "h4_explore_matdisjoint_per_source.csv"), keep_default_na=False, na_values=["", "NaN"])
    MD["source"] = MD.source.astype(str)
    tvm = {}
    for name in H.ALL_DS:
        for m in ("OFF", "SHR"):
            a_ = PS[(PS.config == "twin_disjoint") & (PS.dataset == name) & (PS.method == m) & (PS.k == 3)].set_index(
                "source").draw_mean_rel_change
            b_ = MD[(MD.dataset == name) & (MD.method == m) & (MD.k == 3)].set_index("source").draw_mean_rel_change
            j = pd.concat([a_, b_], axis=1, join="inner")
            if len(j):
                tvm.setdefault(name, {})[m] = {"n_sources_both": int(len(j)),
                                               "n_identical_1e-5": int(((j.iloc[:, 0] - j.iloc[:, 1]).abs() < 1e-5).sum()),
                                               "twin_mean": float(j.iloc[:, 0].mean()), "matdisjoint_mean": float(j.iloc[:, 1].mean())}
    rob["twin_vs_matdisjoint_k3"] = tvm
    x = tvm.get("DES_MP", {}).get("SHR")
    if x:
        S["caveats"].append(
            f"[robustness] DES_MP: twin-disjoint and the EXPLORATORY material-disjoint analysis give identical per-source values in "
            f"{x['n_identical_1e-5']}/{x['n_sources_both']} sources (SHR k3 {f3(x['twin_mean'])} vs {f3(x['matdisjoint_mean'])}), "
            f"because inside a DES_MP source the only same-composition rows are the swapped-order duplicates. So the earlier "
            f"'material-disjoint loss' (main SHR {f3(store[('main', 'DES_MP')][('SHR', 3)]['mean'])} -> {f3(x['matdisjoint_mean'])}) "
            f"is the duplicate effect; on unique rows DES_MP anchors do transfer to the source's other compositions.")
    S["caveats"] += robustness_caveats(RU, CL, rob, regress)
    json.dump(S, open(os.path.join(RESULTS, "h4_summary.json"), "w"), indent=1, default=H.jdefault)
    print(RU[RU.graded].pivot_table(index="dataset", columns="config", values="rule", aggfunc="first").to_string())
    for c, v in rob["overall_counts"].items():
        print(c, v)
    print(f"aggregate done {time.time() - t0:.1f}s; ledger rows {len(rows_out)} ({len(new)} H4R rows)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["audit", "rescore", "rettwin", "refit", "aggregate"])
    ap.add_argument("a1", nargs="?")
    ap.add_argument("a2", nargs="?")
    ap.add_argument("--budget", type=float, default=480.0)
    a = ap.parse_args()
    if a.cmd == "audit":
        cmd_audit()
    elif a.cmd == "rescore":
        cmd_rescore(a.a1)
    elif a.cmd == "rettwin":
        cmd_rettwin(a.a1)
    elif a.cmd == "refit":
        sys.exit(cmd_refit(a.a1, a.a2, a.budget))
    else:
        cmd_aggregate()
