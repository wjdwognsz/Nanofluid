"""H3 -- source offsets are a stable property of a source (premise of the anchor protocol). VRR v2.

Implements PREREG.md section 2, H3:
  H3a split-half reliability
    * eligible datasets: >= 8 sources with >= 10 rows; units = sources with >= 10 rows
    * out-of-source residuals: GroupKFold(10) RF with leak copies removed (seed 0, from h3_oof.py: y - p_rm_s0)
    * per source, rows split in two halves; Pearson r across sources of the half-mean residuals; Spearman-Brown
      R = 2 r/(1+r) with r = mean over 50 random splits
    * two split modes: (1) row-random, (2) material-disjoint (graded; sources with < 2 materials fall back to (1))
    * null: 200 permutations of residuals across rows (ignoring source); CI: source bootstrap
    * dataset PASS iff R >= 0.5, CI_lo > 0, R > null p95; overall PASS iff >= 4 eligible datasets pass
  H3b physical reference transfer (DES_RHO, DES_ETA)
    * reference = ChCl:urea, ChCl:EG, ChCl:glycerol with |x_ChCl - 1/3| <= 0.01
    * sources that measured a reference and other materials: Spearman rho(offset_ref, offset_other),
      5000-permutation p (two-sided primary); PASS iff rho >= 0.3 and p < 0.05 in >= 1 of 2 datasets
Interpretation choices: process/h2h3h6_log.md ("Interpretations fixed BEFORE running" + addendum).
EXPLORATORY (not graded): strict multi-material sources, lineage-cleaned DES, seeds 1-4; POST-HOC (added after seeing
results): system-disjoint split and SD(source offset)/sigma_between(H2) ratio.

Usage (from v2/scripts, after h3_oof.py):  python h3_offset.py
Outputs: results/raw/h3_splithalf.csv (per split), results/raw/h3_splithalf_null.csv (per permutation),
         results/raw/h3_source_offsets.csv (per source), results/raw/h3b_reference.csv (per source),
         results/raw/h3b_null.csv, results/h3_summary.json, ledger/h3.csv
"""
import json
import os
import zlib

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from vrr_data import load, canon
from vrr_common import RAW, RESULTS, LEDGER, copy_mask, ledger_write

DATASETS = ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]
PARTS = os.path.join(RAW, "h236_parts")
MIN_ROWS, MIN_SOURCES = 10, 8
N_SPLITS, N_NULL, N_BOOT = 50, 200, 2000
N_PERM_B = 5000
# prereg thresholds (do not change)
THR_R, THR_RHO, THR_P = 0.5, 0.3, 0.05
N_PASS_H3A = 4

CHCL = canon("C[N+](C)(C)CCO.[Cl-]")
REFS = {"ChCl:urea": canon("NC(N)=O"), "ChCl:EG": canon("OCCO"), "ChCl:glycerol": canon("OCC(O)CO")}
X_TOL = 0.01


def system_label(ds):
    """POST-HOC EXPLORATORY: coarser 'chemical system' label (added after seeing H3a/H3b results):
    DES_* -> component pair A|B (composition ignored); IL_CELL -> ionic liquid (cation.anion, crystal form ignored);
    ES1/ES2 -> polymer (ES1) / solvent system (ES2); DYE -> dye."""
    n = ds.name
    if n.startswith("DES"):
        return (ds.df.A + " | " + ds.df.B).values
    if n == "IL_CELL":
        return (ds.df.cat + "." + ds.df.an).values
    if n == "ES1":
        return ds.df["polymer(s)"].values
    return np.asarray(ds.material)


def crc(s):
    return zlib.crc32(str(s).encode())


def sb(r):
    return 2 * r / (1 + r)


# ------------------------------------------------------------------ H3a machinery
def make_splits(name, src_idx, mat, n_src, mode):
    """labels (N_SPLITS x n_rows) in {0,1}; src_idx: source index per row (rows ordered arbitrarily)."""
    n = len(src_idx)
    rows_of = [np.where(src_idx == s)[0] for s in range(n_src)]
    L = np.zeros((N_SPLITS, n), np.int8)
    fallback = np.zeros(n_src, bool)
    for b in range(N_SPLITS):
        rng = np.random.default_rng([crc(name), b])
        for s in range(n_src):
            rr = rows_of[s]
            mats = np.unique(mat[rr])
            if mode == "material" and len(mats) >= 2:
                order = rng.permutation(mats)
                cnt = [0, 0]
                for m in order:
                    h = 0 if cnt[0] <= cnt[1] else 1
                    sel = rr[mat[rr] == m]
                    L[b, sel] = h
                    cnt[h] += len(sel)
            else:
                if mode == "material":
                    fallback[s] = True
                perm = rng.permutation(rr)
                L[b, perm[len(rr) // 2:]] = 1
    return L, fallback


def half_means(r, src_idx, L, n_src):
    """(N_SPLITS, n_src, 2) mean residual of each half."""
    nb = L.shape[0]
    idx = (np.arange(nb)[:, None] * (2 * n_src) + src_idx[None, :] * 2 + L).ravel()
    w = np.tile(r, nb)
    s = np.bincount(idx, weights=w, minlength=nb * 2 * n_src).reshape(nb, n_src, 2)
    c = np.bincount(idx, minlength=nb * 2 * n_src).reshape(nb, n_src, 2)
    return s / c


def split_r(M):
    """Pearson r across sources for each split; M (nb, S, 2)."""
    a, b = M[:, :, 0], M[:, :, 1]
    a = a - a.mean(1, keepdims=True)
    b = b - b.mean(1, keepdims=True)
    return (a * b).sum(1) / np.sqrt((a ** 2).sum(1) * (b ** 2).sum(1))


def reliability(name, r, src, mat, mode, do_null=True, do_boot=True):
    us = np.array(sorted(pd.unique(src)))
    si = pd.Series(src).map({s: i for i, s in enumerate(us)}).values
    S = len(us)
    L, fb = make_splits(name, si, np.asarray(mat), S, mode)
    M = half_means(r, si, L, S)
    rb = split_r(M)
    rbar = float(np.mean(rb))
    out = dict(R=float(sb(rbar)), r_mean=rbar, r_splits=rb, n_sources=S, n_rows=int(len(r)),
               n_fallback_row_random=int(fb.sum()) if mode == "material" else S, sources=us,
               halfA_split0=M[0, :, 0], halfB_split0=M[0, :, 1])
    if do_boot:
        rs = np.random.default_rng([crc(name), 7, 1 if mode == "material" else 0])
        bs = np.empty(N_BOOT)
        for k in range(N_BOOT):
            ix = rs.integers(0, S, S)
            with np.errstate(invalid="ignore", divide="ignore"):
                rr_ = split_r(M[:, ix, :])
            bs[k] = sb(np.nanmean(rr_)) if np.isfinite(rr_).any() else np.nan
        out["ci"] = [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]
        out["n_boot_undefined"] = int(np.isnan(bs).sum())
    if do_null:
        nul = np.empty(N_NULL)
        for j in range(N_NULL):
            rp = np.random.default_rng([crc(name), 999, j]).permutation(r)
            nul[j] = sb(np.mean(split_r(half_means(rp, si, L, S))))
        out["null"] = nul
        out["null_p95"] = float(np.percentile(nul, 95))
        out["p_perm"] = float((1 + np.sum(nul >= out["R"])) / (N_NULL + 1))
    return out


# ------------------------------------------------------------------ H3b machinery
def ref_label(ds):
    d = ds.df
    isA, isB = (d.A == CHCL).values, (d.B == CHCL).values
    x = np.where(isA, d.xA, np.where(isB, d.xB, np.nan))
    other = np.where(isA, d.B, np.where(isB, d.A, None))
    lab = np.array([""] * len(d), dtype=object)
    for nm, smi in REFS.items():
        m = (other == smi) & (np.abs(x - 1 / 3) <= X_TOL)
        lab[m] = nm
    return lab


def spearman_perm(a, b, name, n=N_PERM_B):
    ra, rb_ = rankdata(a), rankdata(b)
    ra = (ra - ra.mean()) / ra.std()
    rb_ = (rb_ - rb_.mean()) / rb_.std()
    rho = float(np.mean(ra * rb_))
    rs = np.random.default_rng([crc(name), 5000])
    perm = np.array([np.mean(ra * rs.permutation(rb_)) for _ in range(n)])
    return rho, float((1 + np.sum(np.abs(perm) >= abs(rho) - 1e-12)) / (n + 1)), \
        float((1 + np.sum(perm >= rho - 1e-12)) / (n + 1)), perm


def ref_offsets(ds, r, lab, keep, min_each=1, only_ref=None):
    d = pd.DataFrame({"g": ds.group, "r": r, "lab": lab})[keep]
    isref = (d.lab != "") if only_ref is None else (d.lab == only_ref)
    isother = d.lab == ""
    rows = []
    for g, sub in d.groupby("g"):
        rf, ot = sub[isref.loc[sub.index]], sub[isother.loc[sub.index]]
        if len(rf) >= min_each and len(ot) >= min_each:
            rows.append(dict(source=g, offset_ref=float(rf.r.mean()), offset_other=float(ot.r.mean()),
                             n_ref=int(len(rf)), n_other=int(len(ot)),
                             reference_material=";".join(sorted(rf.lab.unique()))))
    return pd.DataFrame(rows, columns=["source", "offset_ref", "offset_other", "n_ref", "n_other", "reference_material"])


def boot_rho(t, name):
    rs = np.random.default_rng([crc(name), 77])
    a, b = t.offset_ref.values, t.offset_other.values
    out = []
    for _ in range(N_BOOT):
        ix = rs.integers(0, len(a), len(a))
        if np.unique(a[ix]).size < 2 or np.unique(b[ix]).size < 2:
            continue
        ra, rb_ = rankdata(a[ix]), rankdata(b[ix])
        out.append(np.corrcoef(ra, rb_)[0, 1])
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


# ------------------------------------------------------------------ main
def main():
    split_rows, null_rows, src_rows, L, summ = [], [], [], [], {"H3a": {}, "H3b": {}}
    h3a_pass = {}
    for name in DATASETS:
        ds = load(name)
        oof = pd.read_csv(os.path.join(PARTS, f"oof_{name}.csv.gz"))
        assert np.allclose(oof.y.values, ds.y)
        g = pd.Series(ds.group).value_counts()
        el_src = g[g >= MIN_ROWS].index
        n_el = len(el_src)
        if n_el < MIN_SOURCES:
            L.append(dict(hypothesis="H3", test_id="H3a_matdisjoint", dataset=name, model="RF",
                          metric="Spearman-Brown split-half R of source mean residuals",
                          threshold=">= 8 sources with >= 10 rows required", verdict="INCONCLUSIVE", n_units=n_el,
                          note=f"ineligible: only {n_el} sources with >= 10 rows"))
            summ["H3a"][name] = dict(eligible=False, n_sources_ge10=int(n_el))
            continue
        variants = [("primary", 0, np.ones(len(ds.y), bool), None)]
        variants += [(f"seed{s}", s, np.ones(len(ds.y), bool), None) for s in range(1, 5)]
        if name in ("DES_RHO", "DES_ETA"):
            variants.append(("lineage_clean", 0, ~copy_mask(ds), None))
        variants.append(("strict_multi_material", 0, np.ones(len(ds.y), bool), "multi"))
        variants.append(("system_disjoint", 0, np.ones(len(ds.y), bool), "system"))
        variants.append(("system_disjoint_strict", 0, np.ones(len(ds.y), bool), "system_multi"))
        sysl = system_label(ds)
        summ["H3a"][name] = dict(eligible=True, n_sources_ge10=int(n_el))
        for vname, seed, keep, restrict in variants:
            r_all = ds.y - oof[f"p_rm_s{seed}"].values
            gk = pd.Series(ds.group[keep]).value_counts()
            el = set(gk[gk >= MIN_ROWS].index)
            m = keep & np.isin(ds.group, list(el))
            if restrict == "multi":
                nm = pd.DataFrame({"g": ds.group[m], "m": ds.material[m]}).groupby("g").m.nunique()
                multi = set(nm[nm >= 2].index)
                m &= np.isin(ds.group, list(multi))
            if restrict == "system_multi":
                ns_ = pd.DataFrame({"g": ds.group[m], "m": sysl[m]}).groupby("g").m.nunique()
                m &= np.isin(ds.group, list(set(ns_[ns_ >= 2].index)))
            if m.sum() == 0 or len(pd.unique(ds.group[m])) < 3:
                summ["H3a"][name][f"{vname}|material"] = dict(n_sources=int(len(pd.unique(ds.group[m]))), R=None)
                print(f"H3a {name} {vname}: too few sources", flush=True)
                continue
            r, src = r_all[m], ds.group[m]
            mat = sysl[m] if restrict in ("system", "system_multi") else ds.material[m]
            modes = ["material", "row"] if vname == "primary" else ["material"]
            for mode in modes:
                full = vname in ("primary", "lineage_clean", "strict_multi_material", "system_disjoint",
                                 "system_disjoint_strict")
                res = reliability(name, r, src, mat, mode, do_null=full, do_boot=full)
                key = f"{vname}|{mode}"
                for b, rv in enumerate(res["r_splits"]):
                    split_rows.append(dict(dataset=name, variant=vname, split_mode=mode, split=b, pearson_r=rv,
                                           sb_R_this_split=sb(rv), n_sources=res["n_sources"], n_rows=res["n_rows"]))
                if "null" in res:
                    for j, nv in enumerate(res["null"]):
                        null_rows.append(dict(dataset=name, variant=vname, split_mode=mode, perm=j, null_R=nv))
                if vname == "primary":
                    off = pd.DataFrame({"g": src, "r": r, "mat": mat}).groupby("g").agg(
                        n_rows=("r", "size"), n_materials=("mat", "nunique"), mean_resid=("r", "mean"), sd_resid=("r", "std"))
                    for i, s in enumerate(res["sources"]):
                        src_rows.append(dict(dataset=name, split_mode=mode, source=s, n_rows=int(off.loc[s, "n_rows"]),
                                             n_materials=int(off.loc[s, "n_materials"]), mean_resid=off.loc[s, "mean_resid"],
                                             sd_resid=off.loc[s, "sd_resid"], halfA_mean_split0=res["halfA_split0"][i],
                                             halfB_mean_split0=res["halfB_split0"][i]))
                d = {k: v for k, v in res.items() if k not in ("r_splits", "null", "sources", "halfA_split0", "halfB_split0")}
                if full:
                    d["pass_R"] = bool(res["R"] >= THR_R)
                    d["pass_ci"] = bool(res["ci"][0] > 0)
                    d["pass_null"] = bool(res["R"] > res["null_p95"])
                    d["pass_all"] = d["pass_R"] and d["pass_ci"] and d["pass_null"]
                summ["H3a"][name][key] = d
                print(f"H3a {name:8s} {vname:22s} {mode:8s} S={res['n_sources']:3d} R={res['R']:.3f} "
                      f"CI={d.get('ci')} null95={d.get('null_p95')} pass={d.get('pass_all')}", flush=True)
        # ledger rows for H3a
        P = summ["H3a"][name]["primary|material"]
        h3a_pass[name] = P["pass_all"]
        L.append(dict(hypothesis="H3", test_id="H3a_matdisjoint", dataset=name, model="RF",
                      metric="Spearman-Brown split-half R of source mean residuals (material-disjoint split)",
                      value=f"{P['R']:.4f}", ci_lo=f"{P['ci'][0]:.4f}", ci_hi=f"{P['ci'][1]:.4f}",
                      threshold="R >= 0.5 AND CI_lo > 0 AND R > null p95 (200 permutations)",
                      verdict="PASS" if P["pass_all"] else "FAIL", n_units=P["n_sources"],
                      note=f"null p95={P['null_p95']:.4f} (perm p={P['p_perm']:.4f}); mean split r={P['r_mean']:.4f}; "
                           f"{P['n_fallback_row_random']}/{P['n_sources']} sources had <2 materials -> row-random fallback; "
                           f"conditions R>=0.5:{P['pass_R']}, CI_lo>0:{P['pass_ci']}, >null95:{P['pass_null']}; rows={P['n_rows']}"))
        Rr = summ["H3a"][name]["primary|row"]
        L.append(dict(hypothesis="H3", test_id="H3a_rowrandom", dataset=name, model="RF",
                      metric="Spearman-Brown split-half R (row-random split)", value=f"{Rr['R']:.4f}",
                      ci_lo=f"{Rr['ci'][0]:.4f}", ci_hi=f"{Rr['ci'][1]:.4f}",
                      threshold="same rule, reported only (graded split is material-disjoint)", verdict="DESCRIPTIVE",
                      n_units=Rr["n_sources"], note=f"null p95={Rr['null_p95']:.4f}; would pass rule: {Rr['pass_all']}"))
        for vname in ["strict_multi_material", "lineage_clean", "system_disjoint", "system_disjoint_strict"]:
            k = f"{vname}|material"
            if k not in summ["H3a"][name]:
                continue
            E = summ["H3a"][name][k]
            if E.get("R") is None:
                L.append(dict(hypothesis="H3", test_id=f"H3a_explore_{vname}", dataset=name, model="RF",
                              metric="Spearman-Brown split-half R", threshold="exploratory", verdict="EXPLORATORY",
                              n_units=E["n_sources"], note="fewer than 3 sources qualify; not computed"))
                continue
            what = {"strict_multi_material": "only sources with >= 2 materials",
                    "lineage_clean": "copy_mask rows dropped",
                    "system_disjoint": "POST-HOC: halves disjoint in chemical system (DES: A|B pair; IL: ionic liquid; ES1: polymer); "
                                       f"{E['n_fallback_row_random']} sources with 1 system fall back to row-random",
                    "system_disjoint_strict": "POST-HOC: only sources with >= 2 chemical systems, halves system-disjoint"}[vname]
            L.append(dict(hypothesis="H3", test_id=f"H3a_explore_{vname}", dataset=name, model="RF",
                          metric="Spearman-Brown split-half R (material-disjoint)", value=f"{E['R']:.4f}",
                          ci_lo=f"{E['ci'][0]:.4f}", ci_hi=f"{E['ci'][1]:.4f}", threshold="exploratory",
                          verdict="EXPLORATORY", n_units=E["n_sources"],
                          note=f"null p95={E['null_p95']:.4f}; would pass rule: {E['pass_all']}; " + what))
        seedR = [summ["H3a"][name][f"seed{s}|material"]["R"] for s in range(1, 5)]
        L.append(dict(hypothesis="H3", test_id="H3a_seed_robustness", dataset=name, model="RF",
                      metric="R (material-disjoint) with residuals from fold/model seeds 1-4", value=f"{np.mean(seedR):.4f}",
                      ci_lo=f"{min(seedR):.4f}", ci_hi=f"{max(seedR):.4f}", threshold="descriptive (min-max over seeds)",
                      verdict="DESCRIPTIVE", n_units=4, note="seed 1..4 R = " + ", ".join(f"{x:.3f}" for x in seedR)))

    el = [n for n in DATASETS if summ["H3a"][n].get("eligible")]
    npass = sum(h3a_pass[n] for n in el)
    # POST-HOC EXPLORATORY diagnostic (added after seeing H3a PASS + H3b FAIL): is the stable 'offset' a lab measurement
    # bias (should be of the size of sigma_between from H2) or model error specific to the chemistry a source studies?
    h2f = os.path.join(RESULTS, "h2_summary.json")
    if os.path.exists(h2f):
        h2 = json.load(open(h2f))["per_dataset"]
        so = pd.DataFrame([r for r in src_rows if r["split_mode"] == "material"])
        summ["offset_vs_sigma_between"] = {}
        for n in el:
            lab = "near_condition_cross_paper" if n == "ES1" else "exact_independent"
            sig = h2[n][lab].get("sigma_between")
            g = so[so.dataset == n]
            sd_off = float(g.mean_resid.std(ddof=1))
            med_within = float(g.sd_resid.median())
            ratio = sd_off / sig if sig else np.nan
            summ["offset_vs_sigma_between"][n] = dict(sd_source_offset=sd_off, median_within_source_resid_sd=med_within,
                                                     sigma_between_H2=sig, ratio=ratio, h2_pair_set=lab,
                                                     n_h2_source_pairs=h2[n][lab].get("n_source_pairs"))
            L.append(dict(hypothesis="H3", test_id="H3_explore_offset_vs_sigma_between", dataset=n, model="RF",
                          metric="SD(source mean out-of-source residual) / sigma_between(H2)", value=f"{ratio:.3f}",
                          threshold="exploratory (post-hoc)", verdict="EXPLORATORY", n_units=len(g),
                          note=f"SD of source offsets={sd_off:.4g}, sigma_between={sig:.4g} ({lab}, "
                               f"{h2[n][lab].get('n_source_pairs')} source pairs), median within-source residual SD={med_within:.4g}; "
                               "ratio >> 1 means the stable offset is mostly model error for the source's chemistry, not lab bias"))
    h3a_verdict = "PASS" if npass >= N_PASS_H3A else "FAIL"
    L.append(dict(hypothesis="H3", test_id="H3a_overall", dataset="+".join(el), model="RF", metric="eligible datasets passing",
                  value=npass, threshold=">= 4 eligible datasets PASS", verdict=h3a_verdict, n_units=len(el),
                  note="; ".join(f"{n}={'PASS' if h3a_pass[n] else 'FAIL'}" for n in el) + "; ES2, DYE ineligible (INCONCLUSIVE)"))

    # ------------------------------------------------ H3b
    b_rows, bnull_rows, h3b_pass = [], [], {}
    for name in ["DES_RHO", "DES_ETA"]:
        ds = load(name)
        oof = pd.read_csv(os.path.join(PARTS, f"oof_{name}.csv.gz"))
        r = ds.y - oof["p_rm_s0"].values
        lab = ref_label(ds)
        cm = copy_mask(ds)
        variants = [("primary", np.ones(len(r), bool), 1, None), ("no_copy_rows", ~cm, 1, None),
                    ("min3_each", np.ones(len(r), bool), 3, None)]
        variants += [(f"only_{k}", np.ones(len(r), bool), 1, k) for k in REFS]
        summ["H3b"][name] = dict(n_reference_rows=int((lab != "").sum()),
                                 n_reference_rows_by_material={k: int((lab == k).sum()) for k in REFS},
                                 n_sources_with_reference=int(pd.Series(ds.group[lab != ""]).nunique()))
        for vname, keep, mn, only in variants:
            t = ref_offsets(ds, r, lab, keep, mn, only)
            t.insert(0, "variant", vname)
            t.insert(0, "dataset", name)
            b_rows.append(t)
            if len(t) < 4:
                summ["H3b"][name][vname] = dict(n_sources=int(len(t)), rho=None)
                print(f"H3b {name} {vname}: only {len(t)} sources", flush=True)
                continue
            rho, p2, p1, perm = spearman_perm(t.offset_ref.values, t.offset_other.values, name + vname)
            ci = boot_rho(t, name + vname)
            if vname == "primary":
                bnull_rows.append(pd.DataFrame({"dataset": name, "variant": vname, "perm": np.arange(len(perm)), "null_rho": perm}))
            summ["H3b"][name][vname] = dict(n_sources=int(len(t)), rho=rho, p_two_sided=p2, p_one_sided=p1, ci=ci,
                                            pass_rule=bool(rho >= THR_RHO and p2 < THR_P))
            print(f"H3b {name:8s} {vname:20s} S={len(t):3d} rho={rho:.3f} p2={p2:.4f} p1={p1:.4f} CI={ci}", flush=True)
        P = summ["H3b"][name]["primary"]
        h3b_pass[name] = P["pass_rule"]
        L.append(dict(hypothesis="H3", test_id="H3b_reference", dataset=name, model="RF",
                      metric="Spearman rho(source offset on reference DES, source offset on other materials)",
                      value=f"{P['rho']:.4f}", ci_lo=f"{P['ci'][0]:.4f}", ci_hi=f"{P['ci'][1]:.4f}",
                      threshold="rho >= 0.3 AND permutation p < 0.05 (two-sided, 5000 perms)",
                      verdict="PASS" if P["pass_rule"] else "FAIL", n_units=P["n_sources"],
                      note=f"p two-sided={P['p_two_sided']:.4f}, one-sided={P['p_one_sided']:.4f}; reference rows="
                           f"{summ['H3b'][name]['n_reference_rows']} {summ['H3b'][name]['n_reference_rows_by_material']}; "
                           f"CI = source bootstrap"))
        for vname, _, _, _ in variants[1:]:
            E = summ["H3b"][name][vname]
            if E.get("rho") is None:
                L.append(dict(hypothesis="H3", test_id=f"H3b_sens_{vname}", dataset=name, model="RF", metric="Spearman rho",
                              threshold="sensitivity (descriptive)", verdict="DESCRIPTIVE", n_units=E["n_sources"],
                              note="fewer than 4 eligible sources; not computed"))
                continue
            L.append(dict(hypothesis="H3", test_id=f"H3b_sens_{vname}", dataset=name, model="RF", metric="Spearman rho",
                          value=f"{E['rho']:.4f}", ci_lo=f"{E['ci'][0]:.4f}", ci_hi=f"{E['ci'][1]:.4f}",
                          threshold="sensitivity (descriptive)", verdict="DESCRIPTIVE", n_units=E["n_sources"],
                          note=f"p two-sided={E['p_two_sided']:.4f}; would pass rule: {E['pass_rule']}"))
    nb = sum(h3b_pass.values())
    h3b_verdict = "PASS" if nb >= 1 else "FAIL"
    L.append(dict(hypothesis="H3", test_id="H3b_overall", dataset="DES_RHO+DES_ETA", model="RF", metric="datasets passing",
                  value=nb, threshold=">= 1 of 2 datasets with rho >= 0.3 and p < 0.05", verdict=h3b_verdict, n_units=2,
                  note="; ".join(f"{n}={'PASS' if v else 'FAIL'}" for n, v in h3b_pass.items())))
    both = (h3a_verdict == "PASS") + (h3b_verdict == "PASS")
    h3_verdict = {2: "PASS", 1: "PARTIAL", 0: "FAIL"}[both]
    L.append(dict(hypothesis="H3", test_id="H3_overall", dataset="all", model="RF", metric="sub-tests passing (H3a, H3b)",
                  value=both, threshold="both PASS -> PASS; one -> PARTIAL; none -> FAIL (combination rule fixed by agent "
                                        "before running; PREREG gives none)", verdict=h3_verdict, n_units=2,
                  note=f"H3a={h3a_verdict}, H3b={h3b_verdict}"))

    pd.DataFrame(split_rows).to_csv(os.path.join(RAW, "h3_splithalf.csv"), index=False)
    pd.DataFrame(null_rows).to_csv(os.path.join(RAW, "h3_splithalf_null.csv"), index=False)
    pd.DataFrame(src_rows).to_csv(os.path.join(RAW, "h3_source_offsets.csv"), index=False)
    pd.concat(b_rows, ignore_index=True).to_csv(os.path.join(RAW, "h3b_reference.csv"), index=False)
    pd.concat(bnull_rows, ignore_index=True).to_csv(os.path.join(RAW, "h3b_null.csv"), index=False)
    ledger_write(os.path.join(LEDGER, "h3.csv"), L)
    summ.update(hypothesis="H3", prereg="PREREG.md section 2 H3", H3a_verdict=h3a_verdict, H3a_n_pass=int(npass),
                H3a_eligible=el, H3b_verdict=h3b_verdict, H3_overall=h3_verdict,
                reference_definition=dict(ChCl=CHCL, refs=REFS, x_tol=X_TOL))
    json.dump(summ, open(os.path.join(RESULTS, "h3_summary.json"), "w"), indent=1,
              default=lambda o: o.tolist() if hasattr(o, "tolist") else (bool(o) if isinstance(o, np.bool_) else float(o)))
    print("H3a:", h3a_verdict, npass, "/", len(el), "| H3b:", h3b_verdict, "| H3:", h3_verdict)


if __name__ == "__main__":
    main()
