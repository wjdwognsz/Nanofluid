"""H6 -- lineage (copied values) and curation reproducibility. VRR v2.

Implements PREREG.md section 2, H6:
  H6a (graded): DES_RHO, DES_ETA -- source-level (GroupKFold 10) RMSE when copies of the test sources stay in training
       ('keep') vs when they are removed ('rm', leak_mask_for_source); change = RMSE_keep/RMSE_rm - 1;
       PASS iff >= 1 dataset has change <= -10 % and source-bootstrap CI upper < 0.
       Predictions come from h3_oof.py (same folds/seeds for both conditions; seeds 0-4).
       DES_MP, IL_CELL, DYE descriptive; ES1/ES2 have no copies (identical by construction).
  H6b (descriptive): random 5-fold RF RMSE on raw vs lineage-cleaned data (subset(ds, ~copy_mask(ds))), seeds 0-4.
  H6c (descriptive): curation round-robin ES1 (PVDF rows) vs ES2 on papers present in both (normalised DOI);
       rows matched on (concentration, voltage, distance, flow) with tolerances; identical-value rate, |dlog10 D|,
       rows present in only one database.
Interpretation choices: process/h2h3h6_log.md.

Usage (from v2/scripts):
  python h6_lineage.py h6b DATASET [DATASET ...]   # random-CV raw vs clean, parts in results/raw/h236_parts/
  python h6_lineage.py aggregate                   # H6a + H6b + H6c -> raw CSVs, summary, ledger
"""
import json
import os
import re
import sys
import time
import zlib

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from vrr_data import load, load_es1_failure, P
from vrr_common import RAW, RESULTS, LEDGER, make_model, random_folds, rmse, copy_mask, subset, ledger_write

PARTS = os.path.join(RAW, "h236_parts")
SEEDS = [0, 1, 2, 3, 4]
GRADED = ["DES_RHO", "DES_ETA"]
DESCR = ["DES_MP", "IL_CELL", "DYE", "ES1", "ES2"]
H6B_SETS = ["DES_RHO", "DES_ETA", "DES_MP", "IL_CELL", "DYE"]
THR_CHANGE = -0.10  # prereg
N_BOOT = 2000


def crc(s):
    return zlib.crc32(str(s).encode())


# ------------------------------------------------------------------ H6a
def h6a(name):
    o = pd.read_csv(os.path.join(PARTS, f"oof_{name}.csv.gz"))
    y = o.y.values
    per_seed = []
    for s in SEEDS:
        rk, rr = rmse(y, o[f"p_keep_s{s}"]), rmse(y, o[f"p_rm_s{s}"])
        per_seed.append(dict(dataset=name, seed=s, rmse_keep=rk, rmse_rm=rr, change=rk / rr - 1))
    ps = pd.DataFrame(per_seed)
    rk, rr = ps.rmse_keep.mean(), ps.rmse_rm.mean()
    change = rk / rr - 1
    se_k = np.mean([(y - o[f"p_keep_s{s}"]) ** 2 for s in SEEDS], axis=0)
    se_r = np.mean([(y - o[f"p_rm_s{s}"]) ** 2 for s in SEEDS], axis=0)
    d = pd.DataFrame({"g": o.source, "sk": se_k, "sr": se_r, "nleak": o.n_leak_rows_of_source})
    src = d.groupby("g").agg(n_rows=("sk", "size"), sse_keep=("sk", "sum"), sse_rm=("sr", "sum"),
                             n_leak_rows_of_source=("nleak", "first")).reset_index()
    src["rmse_keep"] = np.sqrt(src.sse_keep / src.n_rows)
    src["rmse_rm"] = np.sqrt(src.sse_rm / src.n_rows)
    src["change"] = src.rmse_keep / src.rmse_rm - 1
    src["affected"] = src.n_leak_rows_of_source > 0
    rs = np.random.default_rng(crc(name))
    a, b = src.sse_keep.values, src.sse_rm.values
    bs = []
    for _ in range(N_BOOT):
        ix = rs.integers(0, len(a), len(a))
        bs.append(np.sqrt(a[ix].sum() / b[ix].sum()) - 1)
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    aff = src[src.affected]
    # affected-source mean change with its own bootstrap
    if len(aff) >= 2:
        rs2 = np.random.default_rng([crc(name), 2])
        v = aff.change.values
        bs2 = [v[rs2.integers(0, len(v), len(v))].mean() for _ in range(N_BOOT)]
        aff_ci = [float(np.percentile(bs2, 2.5)), float(np.percentile(bs2, 97.5))]
    else:
        aff_ci = [np.nan, np.nan]
    # pooled over rows of affected sources only
    m = o.source.isin(aff.g)
    ch_aff_rows = float(np.sqrt(se_k[m].sum() / se_r[m].sum()) - 1) if m.any() else np.nan
    res = dict(dataset=name, rmse_keep=float(rk), rmse_rm=float(rr), change=float(change), ci=ci,
               per_seed_change=ps.change.tolist(), n_sources=int(len(src)), n_affected_sources=int(len(aff)),
               n_rows=int(len(y)), n_rows_of_affected_sources=int(m.sum()),
               n_leak_rows_total=int(src.n_leak_rows_of_source.sum()),
               affected_mean_change=float(aff.change.mean()) if len(aff) else np.nan, affected_mean_change_ci=aff_ci,
               affected_rows_pooled_change=ch_aff_rows, all_sources_mean_change=float(src.change.mean()),
               frac_affected_improved_by_copies=float((aff.change < 0).mean()) if len(aff) else np.nan)
    src.insert(0, "dataset", name)
    src = src.rename(columns={"g": "source"})
    return res, src, ps


# ------------------------------------------------------------------ H6b
def h6b_run(name):
    t0 = time.time()
    ds = load(name)
    cm = copy_mask(ds)
    clean = subset(ds, ~cm)
    recs = []
    for s in SEEDS:
        p_raw = np.full(len(ds.y), np.nan)
        for tr, te in random_folds(len(ds.y), 5, seed=s):
            p_raw[te] = make_model("RF", s).fit(ds.X[tr], ds.y[tr]).predict(ds.X[te])
        p_cl = np.full(len(clean.y), np.nan)
        for tr, te in random_folds(len(clean.y), 5, seed=s):
            p_cl[te] = make_model("RF", s).fit(clean.X[tr], clean.y[tr]).predict(clean.X[te])
        recs.append(dict(dataset=name, seed=s, n_raw=len(ds.y), n_clean=len(clean.y), n_copy_rows=int(cm.sum()),
                         rmse_raw=rmse(ds.y, p_raw), rmse_clean=rmse(clean.y, p_cl),
                         rmse_raw_on_noncopy_rows=rmse(ds.y[~cm], p_raw[~cm]),
                         rmse_raw_on_copy_rows=rmse(ds.y[cm], p_raw[cm]) if cm.any() else np.nan))
        print(f"[h6b {name}] seed {s} {time.time() - t0:.1f}s", flush=True)
    pd.DataFrame(recs).to_csv(os.path.join(PARTS, f"h6b_{name}.csv"), index=False)


# ------------------------------------------------------------------ H6c
def norm_doi(s):
    s = str(s).strip().lower()
    s = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:?\s*)", "", s)
    return re.sub(r"[.,;\s]+$", "", s)


SOLV_ALIASES = {"ACETONE": "ACETONE", "DMF": "DMF", "DMAC": "DMAC", "DMSO": "DMSO", "NMP": "NMP", "THF": "THF",
                "WATER": "WATER", "ETHANOL": "ETHANOL", "AC": "ACETONE"}


def solvset_es1(s):
    return frozenset(SOLV_ALIASES.get(p, p) for p in str(s).upper().replace("-", " ").split())


def solvset_es2(s, ratio):
    parts = [p.strip().upper() for p in str(s).split(":")]
    try:
        rr = [float(x) for x in str(ratio).strip().split(":")]
    except ValueError:
        rr = [1.0] * len(parts)
    if len(rr) != len(parts):
        rr = [1.0] * len(parts)
    return frozenset(SOLV_ALIASES.get(p, p) for p, r in zip(parts, rr) if r > 0)


def num(x):
    v = pd.to_numeric(x, errors="coerce")
    return float(v) if pd.notna(v) else np.nan


TOL = dict(c=0.5, V=0.5, L=0.5, Qrel=0.10)
MANUAL = {  # sensitivity set: visibly the same paper, DOI does not match (themselves curation discrepancies)
    "10.1109/-no.2013.6720964": "10.1109/nano.2013.6720964",
}


def h6c():
    e1 = load_es1_failure("PVDF").df.copy()
    e1["nd"] = e1.doi.map(norm_doi)
    raw = pd.read_excel(P["ES2"])
    raw.columns = ["source_full", "solvent", "ratio", "delta", "Ra", "conc", "RED", "V", "L", "Q", "chi", "D"]
    raw["source_full"] = raw.source_full.ffill()
    doi = raw.source_full.astype(str).str.extract(r"(10\.\d{4,}/[^\s,;]+)", expand=False)
    raw["nd"] = doi.map(lambda x: norm_doi(x) if isinstance(x, str) else None)
    raw["nd"] = raw.nd.fillna(raw.source_full.astype(str).str[:60])
    raw["nd_manual"] = raw.nd.replace(MANUAL)
    pise_es1 = [d for d in e1.nd.unique() if "pise" in d]
    raw.loc[raw.source_full.astype(str).str.startswith("D.D. Pise"), "nd_manual"] = pise_es1[0] if pise_es1 else None
    shared = sorted(set(e1.nd) & set(raw.nd))
    shared_manual = sorted(set(e1.nd) & set(raw.nd_manual))
    rows, papers = [], []
    for setname, col, plist in [("doi_exact", "nd", shared), ("plus_manual", "nd_manual", shared_manual)]:
        for pap in plist:
            a = e1[e1.nd == pap].reset_index()
            b = raw[raw[col] == pap].reset_index()
            na, nb = len(a), len(b)
            cost = np.full((na, nb), 1e6)
            info = {}
            for i in range(na):
                ca = (num(a.solution_concentration[i]), num(a.voltage_kv[i]), num(a.tip_collector_distance_cm[i]),
                      num(a["flow_rate_ml/h"][i]))
                Da = num(a.fiber_diameter_nm[i])
                sa = solvset_es1(a["solvent(s)"][i])
                for j in range(nb):
                    cb = (num(b.conc[j]), num(b.V[j]), num(b.L[j]), num(b.Q[j]))
                    Db = num(b.D[j])
                    wild, dist, feas = 0, 0.0, True
                    for k, (x1, x2) in enumerate(zip(ca, cb)):
                        if np.isnan(x2) or np.isnan(x1):
                            wild += 1
                            continue
                        dd = abs(x1 / x2 - 1) / TOL["Qrel"] if k == 3 else abs(x1 - x2) / TOL[["c", "V", "L"][k]]
                        if dd > 1:
                            feas = False
                            break
                        dist += dd
                    if not feas:
                        continue
                    sm = int(sa != solvset_es2(b.solvent[j], b.ratio[j]))
                    if np.isnan(Da) and np.isnan(Db):
                        dv = 0.0
                    elif np.isnan(Da) or np.isnan(Db):
                        dv = 2.0
                    else:
                        dv = abs(np.log10(Da) - np.log10(Db))
                    cost[i, j] = 1000 * wild + 100 * dist + 10 * sm + dv
                    info[(i, j)] = (wild, dist, sm, Da, Db)
            ri, ci = linear_sum_assignment(cost) if na and nb else (np.array([], int), np.array([], int))
            matched_a, matched_b = set(), set()
            for i, j in zip(ri, ci):
                if cost[i, j] >= 1e6:
                    continue
                wild, dist, sm, Da, Db = info[(i, j)]
                # ambiguous: another feasible candidate for row i with the same (wildcards, distance, solvent) cost
                same_cond = [jj for jj in range(nb) if (i, jj) in info and jj != j and
                             info[(i, jj)][0] == wild and abs(info[(i, jj)][1] - dist) < 1e-9 and info[(i, jj)][2] == sm]
                amb = len(same_cond) > 0
                both = not (np.isnan(Da) or np.isnan(Db))
                ident = bool(both and abs(Da - Db) <= max(0.5, 1e-3 * max(Da, Db)))
                rows.append(dict(match_set=setname, paper=pap, status="matched", es1_row=int(a["index"][i]),
                                 es2_row=int(b["index"][j]), es1_solvent=a["solvent(s)"][i],
                                 es2_solvent=f"{b.solvent[j]} {b.ratio[j]}", es1_conc=num(a.solution_concentration[i]),
                                 es1_conc_unit=a.solution_concentration_unit[i], es2_conc=num(b.conc[j]),
                                 es1_V=num(a.voltage_kv[i]), es2_V=num(b.V[j]), es1_L=num(a.tip_collector_distance_cm[i]),
                                 es2_L=num(b.L[j]), es1_Q=num(a["flow_rate_ml/h"][i]), es2_Q=num(b.Q[j]),
                                 es1_stable=bool(a.was_formation_stable[i]), es1_D=Da, es2_D=Db, n_wildcards=wild,
                                 cond_dist=dist, solvent_set_mismatch=bool(sm), ambiguous_condition_tie=amb,
                                 both_have_D=both, identical_D=ident,
                                 abs_dlog10D=abs(np.log10(Da) - np.log10(Db)) if both else np.nan))
                matched_a.add(i)
                matched_b.add(j)
            for i in range(na):
                if i not in matched_a:
                    rows.append(dict(match_set=setname, paper=pap, status="ES1_only", es1_row=int(a["index"][i]),
                                     es1_solvent=a["solvent(s)"][i], es1_conc=num(a.solution_concentration[i]),
                                     es1_conc_unit=a.solution_concentration_unit[i], es1_V=num(a.voltage_kv[i]),
                                     es1_L=num(a.tip_collector_distance_cm[i]), es1_Q=num(a["flow_rate_ml/h"][i]),
                                     es1_stable=bool(a.was_formation_stable[i]), es1_D=num(a.fiber_diameter_nm[i])))
            for j in range(nb):
                if j not in matched_b:
                    rows.append(dict(match_set=setname, paper=pap, status="ES2_only", es2_row=int(b["index"][j]),
                                     es2_solvent=f"{b.solvent[j]} {b.ratio[j]}", es2_conc=num(b.conc[j]), es2_V=num(b.V[j]),
                                     es2_L=num(b.L[j]), es2_Q=num(b.Q[j]), es2_D=num(b.D[j])))
            # ES1 within-paper exact duplicates (same conditions, solvent and D)
            dupcols = ["solvent(s)", "solution_concentration", "voltage_kv", "tip_collector_distance_cm", "flow_rate_ml/h",
                       "fiber_diameter_nm", "was_formation_stable"]
            papers.append(dict(match_set=setname, paper=pap, n_es1=na, n_es2=nb,
                               n_es1_internal_duplicates=int(a.duplicated(subset=dupcols).sum())))
    R = pd.DataFrame(rows)
    PP = pd.DataFrame(papers)
    out = {}
    for setname in ["doi_exact", "plus_manual"]:
        r = R[R.match_set == setname]
        m = r[r.status == "matched"].astype({"both_have_D": bool, "ambiguous_condition_tie": bool, "identical_D": bool,
                                               "solvent_set_mismatch": bool, "es1_stable": bool})
        bd = m[m.both_have_D]
        un = bd[~bd.ambiguous_condition_tie]
        pp = PP[PP.match_set == setname]
        conc_unit_mismatch = int((m.es1_conc_unit == "w/v%").sum())
        stab = m[~m.es1_stable]
        e1o = r[r.status == "ES1_only"]
        n_es1_only_distinct = int(len(e1o.drop_duplicates(subset=["paper", "es1_solvent", "es1_conc", "es1_V", "es1_L",
                                                                   "es1_Q", "es1_D", "es1_stable"])))
        # ES1-only rows whose (conditions, D) equal an ES1 row that WAS matched (i.e. pure ES1 internal duplicates)
        mk = set(map(tuple, m[["paper", "es1_solvent", "es1_conc", "es1_V", "es1_L", "es1_Q"]].astype(str).values))
        n_es1_only_dup_of_matched = int(sum(tuple(x) in mk for x in
                                            e1o[["paper", "es1_solvent", "es1_conc", "es1_V", "es1_L", "es1_Q"]].astype(str).values))
        out[setname] = dict(
            n_es1_only_distinct_conditions=n_es1_only_distinct, n_es1_only_duplicating_a_matched_row=n_es1_only_dup_of_matched,
            n_papers=int(len(pp)), n_es1_rows=int(pp.n_es1.sum()), n_es2_rows=int(pp.n_es2.sum()),
            n_matched=int(len(m)), n_es1_only=int((r.status == "ES1_only").sum()), n_es2_only=int((r.status == "ES2_only").sum()),
            n_matched_with_wildcard=int((m.n_wildcards > 0).sum()), n_matched_both_D=int(len(bd)),
            identical_rate=float(bd.identical_D.mean()) if len(bd) else np.nan,
            n_identical=int(bd.identical_D.sum()),
            identical_rate_unambiguous=float(un.identical_D.mean()) if len(un) else np.nan,
            n_unambiguous_both_D=int(len(un)), n_ambiguous_ties=int(m.ambiguous_condition_tie.sum()),
            median_abs_dlog10D=float(bd.abs_dlog10D.median()) if len(bd) else np.nan,
            mean_abs_dlog10D=float(bd.abs_dlog10D.mean()) if len(bd) else np.nan,
            max_abs_dlog10D=float(bd.abs_dlog10D.max()) if len(bd) else np.nan,
            n_nonidentical=int((~bd.identical_D).sum()),
            median_abs_dlog10D_nonidentical=float(bd[~bd.identical_D].abs_dlog10D.median()) if (~bd.identical_D).any() else np.nan,
            n_value_in_one_db_only=int((m.es1_D.isna() ^ m.es2_D.isna()).sum()),
            n_es1_unstable_matched=int(len(stab)), n_es1_unstable_matched_es2_D_missing=int(stab.es2_D.isna().sum()),
            n_matched_es1_conc_wv_vs_es2_wt_label=conc_unit_mismatch,
            n_matched_solvent_set_mismatch=int(m.solvent_set_mismatch.sum()),
            n_es1_internal_duplicate_rows=int(pp.n_es1_internal_duplicates.sum()),
            per_paper=r.groupby("paper").status.value_counts().unstack(fill_value=0).to_dict(orient="index"))
    return R, PP, out


# ------------------------------------------------------------------ aggregate
def aggregate():
    L, summ = [], {"H6a": {}, "H6b": {}, "H6c": {}}
    src_all, seed_all = [], []
    for name in GRADED + DESCR:
        f = os.path.join(PARTS, f"oof_{name}.csv.gz")
        res, src, ps = h6a(name)
        summ["H6a"][name] = res
        src_all.append(src)
        seed_all.append(ps)
        meets = res["change"] <= THR_CHANGE and res["ci"][1] < 0
        res["meets_rule"] = bool(meets)
        print(f"H6a {name:8s} keep {res['rmse_keep']:.5f} rm {res['rmse_rm']:.5f} change {res['change']:+.4f} "
              f"CI {res['ci']} affected {res['n_affected_sources']}/{res['n_sources']} aff-mean {res['affected_mean_change']:+.4f}")
        note = (f"RMSE keep={res['rmse_keep']:.5g}, rm={res['rmse_rm']:.5g} (mean of 5 seeds; per-seed change "
                f"{min(res['per_seed_change']):+.4f}..{max(res['per_seed_change']):+.4f}); affected sources "
                f"{res['n_affected_sources']}/{res['n_sources']} ({res['n_rows_of_affected_sources']} rows), their mean change "
                f"{res['affected_mean_change']:+.4f} CI [{res['affected_mean_change_ci'][0]:+.4f}, {res['affected_mean_change_ci'][1]:+.4f}], "
                f"pooled over their rows {res['affected_rows_pooled_change']:+.4f}; leak rows total {res['n_leak_rows_total']}")
        if name in GRADED:
            L.append(dict(hypothesis="H6", test_id="H6a_copy_leak", dataset=name, model="RF",
                          metric="RMSE_keep/RMSE_removed - 1 (source GroupKFold 10, all rows)", value=f"{res['change']:.4f}",
                          ci_lo=f"{res['ci'][0]:.4f}", ci_hi=f"{res['ci'][1]:.4f}",
                          threshold="change <= -0.10 AND CI upper < 0 (>= 1 of 2 datasets)",
                          verdict="PASS" if meets else "FAIL", n_units=res["n_sources"], note=note))
        elif res["n_leak_rows_total"] == 0:
            L.append(dict(hypothesis="H6", test_id="H6a_copy_leak", dataset=name, model="RF",
                          metric="RMSE_keep/RMSE_removed - 1", value="0.0000", threshold="descriptive (not graded)",
                          verdict="DESCRIPTIVE", n_units=res["n_sources"], note="no copy rows in this dataset: identical by construction"))
        else:
            L.append(dict(hypothesis="H6", test_id="H6a_copy_leak", dataset=name, model="RF",
                          metric="RMSE_keep/RMSE_removed - 1 (source GroupKFold 10, all rows)", value=f"{res['change']:.4f}",
                          ci_lo=f"{res['ci'][0]:.4f}", ci_hi=f"{res['ci'][1]:.4f}", threshold="descriptive (not graded)",
                          verdict="DESCRIPTIVE", n_units=res["n_sources"], note=note))
    n_meet = sum(summ["H6a"][n]["meets_rule"] for n in GRADED)
    h6a_verdict = "PASS" if n_meet >= 1 else "FAIL"
    L.append(dict(hypothesis="H6", test_id="H6a_overall", dataset="DES_RHO+DES_ETA", model="RF", metric="datasets meeting rule",
                  value=n_meet, threshold=">= 1 of 2 datasets with change <= -10% and CI upper < 0", verdict=h6a_verdict,
                  n_units=2, note="; ".join(f"{n}: {summ['H6a'][n]['change']:+.4f} CI [{summ['H6a'][n]['ci'][0]:+.4f}, "
                                            f"{summ['H6a'][n]['ci'][1]:+.4f}]" for n in GRADED)))
    pd.concat(src_all, ignore_index=True).to_csv(os.path.join(RAW, "h6_leak.csv"), index=False)
    pd.concat(seed_all, ignore_index=True).to_csv(os.path.join(RAW, "h6_leak_seeds.csv"), index=False)

    # H6b
    b_all = []
    for name in H6B_SETS:
        f = os.path.join(PARTS, f"h6b_{name}.csv")
        if not os.path.exists(f):
            L.append(dict(hypothesis="H6", test_id="H6b_randomcv_raw_vs_clean", dataset=name, model="RF",
                          threshold="descriptive", verdict="INCONCLUSIVE", note="not run"))
            continue
        b = pd.read_csv(f)
        b_all.append(b)
        r = dict(rmse_raw=b.rmse_raw.mean(), rmse_clean=b.rmse_clean.mean(), rmse_raw_noncopy=b.rmse_raw_on_noncopy_rows.mean(),
                 rmse_raw_copy=b.rmse_raw_on_copy_rows.mean(), n_raw=int(b.n_raw[0]), n_clean=int(b.n_clean[0]),
                 n_copy_rows=int(b.n_copy_rows[0]))
        r["change_raw_vs_clean"] = r["rmse_raw"] / r["rmse_clean"] - 1
        r["change_raw_noncopy_vs_clean"] = r["rmse_raw_noncopy"] / r["rmse_clean"] - 1
        r["per_seed_change"] = (b.rmse_raw / b.rmse_clean - 1).tolist()
        summ["H6b"][name] = r
        print(f"H6b {name:8s} raw {r['rmse_raw']:.5f} clean {r['rmse_clean']:.5f} change {r['change_raw_vs_clean']:+.4f} "
              f"raw-on-noncopy {r['rmse_raw_noncopy']:.5f} copy-rows {r['rmse_raw_copy']:.5f}")
        L.append(dict(hypothesis="H6", test_id="H6b_randomcv_raw_vs_clean", dataset=name, model="RF",
                      metric="random 5-fold RMSE raw / lineage-cleaned - 1", value=f"{r['change_raw_vs_clean']:.4f}",
                      ci_lo=f"{min(r['per_seed_change']):.4f}", ci_hi=f"{max(r['per_seed_change']):.4f}",
                      threshold="descriptive (PREREG H6b); ci = min..max over 5 seeds", verdict="DESCRIPTIVE", n_units=5,
                      note=f"RMSE raw={r['rmse_raw']:.5g} (n={r['n_raw']}), clean={r['rmse_clean']:.5g} (n={r['n_clean']}); "
                           f"raw model on non-copy rows={r['rmse_raw_noncopy']:.5g}, on the {r['n_copy_rows']} copy rows={r['rmse_raw_copy']:.5g}"))
    if b_all:
        pd.concat(b_all, ignore_index=True).to_csv(os.path.join(RAW, "h6b_randomcv.csv"), index=False)

    # H6c
    R, PP, out = h6c()
    R.to_csv(os.path.join(RAW, "h6c_curation.csv"), index=False)
    PP.to_csv(os.path.join(RAW, "h6c_papers.csv"), index=False)
    summ["H6c"] = out
    for setname, o in out.items():
        print(f"H6c {setname}: " + json.dumps({k: v for k, v in o.items() if k != "per_paper"}, default=float))
        tag = "" if setname == "doi_exact" else "_sens_plus_manual"
        L.append(dict(hypothesis="H6", test_id=f"H6c_identical_rate{tag}", dataset="ES1(PVDF) vs ES2", model="",
                      metric="share of matched rows (D in both) with identical diameter", value=f"{o['identical_rate']:.4f}",
                      threshold="descriptive (PREREG H6c)", verdict="DESCRIPTIVE", n_units=o["n_papers"],
                      note=f"{o['n_identical']}/{o['n_matched_both_D']} identical; on unambiguous matches "
                           f"{o['identical_rate_unambiguous']:.4f} (n={o['n_unambiguous_both_D']}); {o['n_ambiguous_ties']} matches resolved "
                           f"by value tie-break; papers={o['n_papers']} ({'normalised DOI' if setname == 'doi_exact' else 'DOI + 2 manual identity matches'})"))
        L.append(dict(hypothesis="H6", test_id=f"H6c_abs_dlog10D{tag}", dataset="ES1(PVDF) vs ES2", model="",
                      metric="|dlog10 D| on matched rows: median (ci_lo=mean, ci_hi=max)", value=f"{o['median_abs_dlog10D']:.4f}",
                      ci_lo=f"{o['mean_abs_dlog10D']:.4f}", ci_hi=f"{o['max_abs_dlog10D']:.4f}",
                      threshold="descriptive (PREREG H6c); ci columns hold mean and max, not a CI", verdict="DESCRIPTIVE",
                      n_units=o["n_matched_both_D"],
                      note=f"non-identical matches: {o['n_nonidentical']}, their median |dlog10 D|={o['median_abs_dlog10D_nonidentical']:.4f}"))
        L.append(dict(hypothesis="H6", test_id=f"H6c_rows_one_db_only{tag}", dataset="ES1(PVDF) vs ES2", model="",
                      metric="rows present in only one database (ES1-only + ES2-only)", value=o["n_es1_only"] + o["n_es2_only"],
                      threshold="descriptive (PREREG H6c)", verdict="DESCRIPTIVE", n_units=o["n_papers"],
                      note=f"ES1 rows {o['n_es1_rows']}, ES2 rows {o['n_es2_rows']}, matched {o['n_matched']} "
                           f"({o['n_matched_with_wildcard']} via ES2 missing-field wildcard); ES1-only {o['n_es1_only']} "
                           f"({o['n_es1_only_distinct_conditions']} distinct after collapsing ES1 internal repeats; "
                           f"{o['n_es1_only_duplicating_a_matched_row']} merely repeat a matched row), ES2-only {o['n_es2_only']}; "
                           f"value in one DB only {o['n_value_in_one_db_only']}; ES1 unstable matched {o['n_es1_unstable_matched']} "
                           f"(ES2 D missing for {o['n_es1_unstable_matched_es2_D_missing']}); ES1 w/v% vs ES2 'wt%' label {o['n_matched_es1_conc_wv_vs_es2_wt_label']}; "
                           f"solvent-set mismatch {o['n_matched_solvent_set_mismatch']}; ES1 internal duplicate rows {o['n_es1_internal_duplicate_rows']}"))
    L.append(dict(hypothesis="H6", test_id="H6_overall", dataset="all", model="RF", metric="H6a verdict (H6b, H6c descriptive)",
                  value=n_meet, threshold="= H6a verdict", verdict=h6a_verdict, n_units=2,
                  note="H6b and H6c are descriptive by PREREG; see their rows"))
    ledger_write(os.path.join(LEDGER, "h6.csv"), L)
    summ.update(hypothesis="H6", prereg="PREREG.md section 2 H6", H6a_verdict=h6a_verdict, H6a_n_meeting=int(n_meet),
                H6_overall=h6a_verdict, tolerances_H6c=TOL)
    json.dump(summ, open(os.path.join(RESULTS, "h6_summary.json"), "w"), indent=1,
              default=lambda o: o.tolist() if hasattr(o, "tolist") else (bool(o) if isinstance(o, np.bool_) else float(o)))
    print("H6a:", h6a_verdict)


if __name__ == "__main__":
    if sys.argv[1] == "h6b":
        for nm in sys.argv[2:]:
            h6b_run(nm)
    elif sys.argv[1] == "aggregate":
        aggregate()
