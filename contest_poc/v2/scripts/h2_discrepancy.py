"""H2 -- inter-source discrepancy for the same material under the same condition (VRR v2).

Implements PREREG.md section 2, H2 ("같은 시료·같은 조건에서 출처 간 불일치가 있고, 그 크기는 물성마다 다르다"):
  * independent source pairs only: rows flagged by vrr_common.copy_mask are dropped and source pairs flagged
    copy_relation by vrr_common.copy_relations are excluded; delta = y(source a) - y(source b) on the same exact key
    (y averaged per (key, source));
  * sigma_between = median|delta| / (0.6745*sqrt(2)); R2_ceiling = 1 - sigma_between^2 / Var(y);
  * ES1 replicates the v1 near-condition pair definition (scripts/poc_electrospin.py): same polymer, solvent and
    collector, conc +-1 wt%, voltage +-2 kV, flow +-30 %, distance +-2 cm, different paper;
  * predictions P2a (DES_RHO median|drho| <= 0.010 g/cm3), P2b (DES_ETA median fold >= 1.10),
    P2c (sigma_between/SD(y): DES_RHO < DES_ETA); H2 PASS iff >= 2 of 3;
  * R2_ceiling is compared with the RF source-CV R2 (leak-free GroupKFold(10), seeds 0-4, from h3_oof.py).
Interpretation choices are fixed in process/h2h3h6_log.md ("Interpretations fixed BEFORE running").
POST-HOC EXPLORATORY: ES1 near-condition pairs after collapsing exact within-paper duplicate rows.

Usage (from v2/scripts, after h3_oof.py has produced results/raw/h236_parts/oof_<DS>.csv.gz):
  python h2_discrepancy.py
Outputs: results/raw/h2_pairs.csv, results/raw/h2_dataset_stats.csv, results/h2_summary.json, ledger/h2.csv
"""
import json
import os
import zlib

import numpy as np
import pandas as pd

from vrr_data import load
from vrr_common import RAW, RESULTS, LEDGER, copy_relations, copy_mask, boot_ci, r2, ledger_write

DATASETS = ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]
PARTS = os.path.join(RAW, "h236_parts")
C = 0.6745 * np.sqrt(2)
N_BOOT = 2000
# prereg thresholds (do not change)
P2A_MAX_ABS_DRHO = 0.010   # g/cm3
P2B_MIN_FOLD = 1.10


# ------------------------------------------------------------------ pair builders
def exact_pairs(ds, independent=True):
    """Cross-source pairs on identical keys. independent=True: copy rows removed and copy-relation pairs dropped."""
    keep = ~copy_mask(ds) if independent else np.ones(len(ds.y), bool)
    cr = copy_relations(ds)
    cpairs = set(map(tuple, cr.loc[cr.copy_relation, ["s1", "s2"]].values)) if len(cr) else set()
    d = pd.DataFrame({"k": ds.key, "g": ds.group, "y": ds.y})[keep]
    agg = d.groupby(["k", "g"]).y.agg(["mean", "size"]).reset_index()
    multi = agg[agg.k.isin(agg.groupby("k").g.nunique().loc[lambda s: s > 1].index)]
    rows = []
    for k, sub in multi.groupby("k"):
        sub = sub.sort_values("g")
        g, y, nn = sub.g.values, sub["mean"].values, sub["size"].values
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                cp = (g[i], g[j]) in cpairs
                if independent and cp:
                    continue
                rows.append(dict(key=k, source_a=g[i], source_b=g[j], y_a=y[i], y_b=y[j], n_rows_a=int(nn[i]),
                                 n_rows_b=int(nn[j]), copy_relation_pair=bool(cp)))
    p = pd.DataFrame(rows, columns=["key", "source_a", "source_b", "y_a", "y_b", "n_rows_a", "n_rows_b",
                                    "copy_relation_pair"])
    p["delta"] = p.y_a - p.y_b
    p["abs_delta"] = p.delta.abs()
    return p


ES1_DUP_COLS = ["source", "polymer(s)", "solvent(s)", "collector_type", "conc_wt", "voltage_kv", "flow_rate_ml/h",
                "tip_collector_distance_cm", "y"]


def near_pairs_es1(ds, dedup=False):
    """v1 near-condition pairs (row level) on ES1 regression rows.
    dedup=True (POST-HOC EXPLORATORY, added after seeing that 26 of the 51 cross-paper pairs come from one row pair
    repeated 13x): exact within-paper duplicate rows (same source, conditions and y) are collapsed first."""
    d = ds.df.reset_index(drop=True)
    yy = ds.y
    if dedup:
        keep = ~d.duplicated(subset=ES1_DUP_COLS).values
        d = d[keep].reset_index(drop=True)
        yy = ds.y[keep]
    rows = []
    q = np.log(d["flow_rate_ml/h"].values)
    for i in range(len(d)):
        a = d.iloc[i]
        j = np.arange(i + 1, len(d))
        c = d.iloc[i + 1:]
        m = ((c["polymer(s)"].values == a["polymer(s)"]) & (c["solvent(s)"].values == a["solvent(s)"]) &
             (c.collector_type.values == a.collector_type) & (np.abs(c.conc_wt.values - a.conc_wt) <= 1.0) &
             (np.abs(c.voltage_kv.values - a.voltage_kv) <= 2.0) & (np.abs(q[i + 1:] - q[i]) <= np.log(1.3)) &
             (np.abs(c.tip_collector_distance_cm.values - a.tip_collector_distance_cm) <= 2.0))
        for jj in j[m]:
            sa, sb = d.source[i], d.source[jj]
            ya, yb = yy[i], yy[jj]
            if sa > sb:
                sa, sb, ya, yb = sb, sa, yb, ya
            rows.append(dict(key=f"row{i}~row{jj}", source_a=sa, source_b=sb, y_a=ya, y_b=yb, n_rows_a=1, n_rows_b=1,
                             copy_relation_pair=False, same_source=bool(d.source[i] == d.source[jj])))
    p = pd.DataFrame(rows)
    p["delta"] = p.y_a - p.y_b
    p["abs_delta"] = p.delta.abs()
    return p


def near_pairs_es2(ds):
    """EXPLORATORY: analogous near-condition pairs for ES2 (same solvent and ratio; imputed V/L/Q may not pair)."""
    d = ds.df.reset_index(drop=True)
    ok = (d.V_missing == 0) & (d.L_missing == 0) & (d.Q_missing == 0)
    rows = []
    q = np.log(d.Q.values)
    for i in range(len(d)):
        if not ok[i]:
            continue
        for jj in range(i + 1, len(d)):
            if not ok[jj]:
                continue
            if (d.solvent[i] == d.solvent[jj] and str(d.ratio[i]).strip() == str(d.ratio[jj]).strip() and
                    abs(d.conc[i] - d.conc[jj]) <= 1.0 and abs(d.V[i] - d.V[jj]) <= 2.0 and
                    abs(q[i] - q[jj]) <= np.log(1.3) and abs(d.L[i] - d.L[jj]) <= 2.0):
                sa, sb, ya, yb = d.source[i], d.source[jj], ds.y[i], ds.y[jj]
                if sa > sb:
                    sa, sb, ya, yb = sb, sa, yb, ya
                rows.append(dict(key=f"row{i}~row{jj}", source_a=sa, source_b=sb, y_a=ya, y_b=yb, n_rows_a=1,
                                 n_rows_b=1, copy_relation_pair=False, same_source=bool(d.source[i] == d.source[jj])))
    p = pd.DataFrame(rows, columns=["key", "source_a", "source_b", "y_a", "y_b", "n_rows_a", "n_rows_b",
                                    "copy_relation_pair", "same_source"])
    p["delta"] = p.y_a - p.y_b
    p["abs_delta"] = p.delta.abs()
    return p


# ------------------------------------------------------------------ statistics
def cluster_boot_median(p, n=N_BOOT, seed=0):
    """Bootstrap over source pairs: resample source pairs, pool their |delta|, median.
    seed: callers pass crc32(dataset) so that the bootstraps of different datasets are independent streams."""
    if len(p) == 0:
        return np.full(n, np.nan)
    cl = (p.source_a + "||" + p.source_b).values
    arrs = [g.values for _, g in p.abs_delta.groupby(cl)]
    rs = np.random.default_rng(seed)
    out = np.empty(n)
    for b in range(n):
        idx = rs.integers(0, len(arrs), len(arrs))
        out[b] = np.median(np.concatenate([arrs[i] for i in idx]))
    return out


def stats(p, ds, oof, label):
    sd = float(np.std(ds.y, ddof=1))
    seed = zlib.crc32(ds.name.encode())
    var = sd ** 2
    out = dict(pair_set=label, n_pairs=int(len(p)))
    if len(p) == 0:
        out.update(dict(n_keys=0, n_source_pairs=0, n_sources=0, median_abs_delta=np.nan, sigma_between=np.nan))
    else:
        bm = cluster_boot_median(p, seed=seed)
        med = float(np.median(p.abs_delta))
        cl = p.source_a + "||" + p.source_b
        bal = float(p.groupby(cl).abs_delta.median().median())
        sig = med / C
        out.update(dict(n_keys=int(p.key.nunique()), n_source_pairs=int(cl.nunique()),
                        n_sources=int(len(set(p.source_a) | set(p.source_b))),
                        median_abs_delta=med, median_abs_delta_ci=[float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
                        median_abs_delta_source_pair_balanced=bal,
                        mean_abs_delta=float(p.abs_delta.mean()), p90_abs_delta=float(np.percentile(p.abs_delta, 90)),
                        sigma_between=sig, sigma_between_ci=[float(np.percentile(bm, 2.5) / C), float(np.percentile(bm, 97.5) / C)],
                        sigma_over_sd=sig / sd,
                        sigma_over_sd_ci=[float(np.percentile(bm, 2.5) / C / sd), float(np.percentile(bm, 97.5) / C / sd)],
                        R2_ceiling=1 - sig ** 2 / var,
                        R2_ceiling_ci=[float(1 - (np.percentile(bm, 97.5) / C) ** 2 / var),
                                       float(1 - (np.percentile(bm, 2.5) / C) ** 2 / var)],
                        frac_identical=float((p.abs_delta <= 1e-9).mean()),
                        _boot=bm))
    out["sd_y"] = sd
    out["var_y"] = var
    if oof is not None:
        r_rm = [r2(oof.y, oof[f"p_rm_s{s}"]) for s in range(5)]
        r_kp = [r2(oof.y, oof[f"p_keep_s{s}"]) for s in range(5)]
        out.update(dict(R2_RF_sourceCV_leakfree=float(np.mean(r_rm)), R2_RF_sourceCV_leakfree_per_seed=r_rm,
                        R2_RF_sourceCV_plain=float(np.mean(r_kp))))
        if "R2_ceiling" in out:
            out["headroom_R2_ceiling_minus_RF"] = out["R2_ceiling"] - out["R2_RF_sourceCV_leakfree"]
    return out


def main():
    allp, st = [], {}
    for name in DATASETS:
        ds = load(name)
        f = os.path.join(PARTS, f"oof_{name}.csv.gz")
        oof = pd.read_csv(f) if os.path.exists(f) else None
        if oof is not None:
            assert np.allclose(oof.y.values, ds.y), name
        sets = {}
        p_ind = exact_pairs(ds, independent=True)
        p_all = exact_pairs(ds, independent=False)
        sets["exact_independent"] = p_ind
        sets["exact_with_copies"] = p_all
        if name == "ES1":
            pn = near_pairs_es1(ds)
            sets["near_condition_cross_paper"] = pn[~pn.same_source].drop(columns="same_source")
            sets["near_condition_same_paper"] = pn[pn.same_source].drop(columns="same_source")
            pd_ = near_pairs_es1(ds, dedup=True)
            sets["near_condition_cross_paper_dedup"] = pd_[~pd_.same_source].drop(columns="same_source")
            sets["near_condition_same_paper_dedup"] = pd_[pd_.same_source].drop(columns="same_source")
        if name == "ES2":
            pn = near_pairs_es2(ds)
            sets["near_condition_cross_paper"] = pn[~pn.same_source].drop(columns="same_source")
            sets["near_condition_same_paper"] = pn[pn.same_source].drop(columns="same_source")
        st[name] = {}
        for lab, p in sets.items():
            s = stats(p, ds, oof, lab)
            st[name][lab] = s
            q = p.copy()
            q.insert(0, "pair_set", lab)
            q.insert(0, "dataset", name)
            allp.append(q)
            print(f"{name:8s} {lab:28s} pairs={s['n_pairs']:5d} med|d|={s.get('median_abs_delta', np.nan):.4g} "
                  f"sig/sd={s.get('sigma_over_sd', np.nan):.3f} R2ceil={s.get('R2_ceiling', np.nan):.3f} "
                  f"R2rf={s.get('R2_RF_sourceCV_leakfree', np.nan):.3f}", flush=True)
    pairs = pd.concat(allp, ignore_index=True)
    pairs.to_csv(os.path.join(RAW, "h2_pairs.csv"), index=False)

    primary = {n: ("near_condition_cross_paper" if n == "ES1" else "exact_independent") for n in DATASETS}
    rows_stats = []
    for n in DATASETS:
        for lab, s in st[n].items():
            r = {k: v for k, v in s.items() if not k.startswith("_") and not isinstance(v, list)}
            for k, v in s.items():
                if isinstance(v, list) and len(v) == 2:
                    r[k + "_lo"], r[k + "_hi"] = v
            r.update(dataset=n, is_primary=(lab == primary[n]))
            rows_stats.append(r)
    pd.DataFrame(rows_stats).to_csv(os.path.join(RAW, "h2_dataset_stats.csv"), index=False)

    # ------------------------------------------------ graded predictions
    rho, eta = st["DES_RHO"]["exact_independent"], st["DES_ETA"]["exact_independent"]
    p2a_v = rho["median_abs_delta"]
    p2a = p2a_v <= P2A_MAX_ABS_DRHO
    p2b_v = 10 ** eta["median_abs_delta"]
    p2b_ci = [10 ** x for x in eta["median_abs_delta_ci"]]
    p2b = p2b_v >= P2B_MIN_FOLD
    diff = rho["sigma_over_sd"] - eta["sigma_over_sd"]
    bdiff = rho["_boot"] / C / rho["sd_y"] - eta["_boot"] / C / eta["sd_y"]  # independent bootstraps, paired by index
    p2c_ci = [float(np.percentile(bdiff, 2.5)), float(np.percentile(bdiff, 97.5))]
    p2c = diff < 0
    n_hold = int(p2a) + int(p2b) + int(p2c)
    overall = "PASS" if n_hold >= 2 else "FAIL"

    def fmt_set(s):
        return (f"pairs={s['n_pairs']}, keys={s['n_keys']}, source pairs={s['n_source_pairs']}, sources={s['n_sources']}; "
                f"source-pair-balanced median={s['median_abs_delta_source_pair_balanced']:.4g}")

    L = []
    L.append(dict(hypothesis="H2", test_id="H2_P2a", dataset="DES_RHO", model="", metric="median |delta rho| (g/cm3), independent exact-key pairs",
                  value=f"{p2a_v:.5f}", ci_lo=f"{rho['median_abs_delta_ci'][0]:.5f}", ci_hi=f"{rho['median_abs_delta_ci'][1]:.5f}",
                  threshold="median |delta rho| <= 0.010 g/cm3 (point estimate)", verdict="PASS" if p2a else "FAIL",
                  n_units=rho["n_source_pairs"], note=fmt_set(rho) + "; CI = cluster bootstrap over source pairs"))
    L.append(dict(hypothesis="H2", test_id="H2_P2b", dataset="DES_ETA", model="", metric="median fold difference 10^median|dlog10 eta|",
                  value=f"{p2b_v:.4f}", ci_lo=f"{p2b_ci[0]:.4f}", ci_hi=f"{p2b_ci[1]:.4f}",
                  threshold="median fold >= 1.10 (point estimate)", verdict="PASS" if p2b else "FAIL",
                  n_units=eta["n_source_pairs"], note=fmt_set(eta) + f"; median|dlog10|={eta['median_abs_delta']:.4f}"))
    L.append(dict(hypothesis="H2", test_id="H2_P2c", dataset="DES_RHO vs DES_ETA", model="",
                  metric="sigma_between/SD(y): DES_RHO minus DES_ETA",
                  value=f"{diff:.4f}", ci_lo=f"{p2c_ci[0]:.4f}", ci_hi=f"{p2c_ci[1]:.4f}",
                  threshold="sigma_between/SD(y) of DES_RHO < that of DES_ETA (difference < 0)",
                  verdict="PASS" if p2c else "FAIL", n_units=rho["n_source_pairs"] + eta["n_source_pairs"],
                  note=f"DES_RHO {rho['sigma_over_sd']:.4f} (sigma {rho['sigma_between']:.5f} g/cm3, SD {rho['sd_y']:.4f}); "
                       f"DES_ETA {eta['sigma_over_sd']:.4f} (sigma {eta['sigma_between']:.4f} log10 cP, SD {eta['sd_y']:.4f})"))
    L.append(dict(hypothesis="H2", test_id="H2_overall", dataset="DES_RHO+DES_ETA", model="", metric="predictions holding",
                  value=n_hold, threshold=">= 2 of 3 predictions (P2a, P2b, P2c)", verdict=overall, n_units=3,
                  note=f"P2a={'PASS' if p2a else 'FAIL'}, P2b={'PASS' if p2b else 'FAIL'}, P2c={'PASS' if p2c else 'FAIL'}"))
    # descriptive per dataset
    for n in DATASETS:
        s = st[n][primary[n]]
        lab = primary[n]
        if s["n_pairs"] == 0:
            L.append(dict(hypothesis="H2", test_id="H2_sigma_between", dataset=n, model="", metric="sigma_between",
                          threshold="descriptive (no threshold)", verdict="INCONCLUSIVE", n_units=0,
                          note=f"no cross-source pairs on identical keys ({lab}); R2_RF_sourceCV_leakfree={s.get('R2_RF_sourceCV_leakfree', np.nan):.4f}"))
            continue
        L.append(dict(hypothesis="H2", test_id="H2_sigma_between", dataset=n, model="",
                      metric=f"sigma_between ({lab}) in {load_unit(n)}", value=f"{s['sigma_between']:.5g}",
                      ci_lo=f"{s['sigma_between_ci'][0]:.5g}", ci_hi=f"{s['sigma_between_ci'][1]:.5g}",
                      threshold="descriptive (no threshold)", verdict="DESCRIPTIVE", n_units=s["n_source_pairs"],
                      note=f"sigma/SD(y)={s['sigma_over_sd']:.4f}; median|d|={s['median_abs_delta']:.5g}; " + fmt_set(s)
                           + ("; small number of source pairs -> fragile" if s["n_source_pairs"] < 5 else "")))
        L.append(dict(hypothesis="H2", test_id="H2_R2_ceiling_vs_RF", dataset=n, model="RF",
                      metric="R2_ceiling (1 - sigma_between^2/Var y) vs RF source-CV R2", value=f"{s['R2_ceiling']:.4f}",
                      ci_lo=f"{s['R2_ceiling_ci'][0]:.4f}", ci_hi=f"{s['R2_ceiling_ci'][1]:.4f}",
                      threshold="descriptive (no threshold)", verdict="DESCRIPTIVE", n_units=s["n_source_pairs"],
                      note=f"RF leak-free source GroupKFold(10) R2 = {s['R2_RF_sourceCV_leakfree']:.4f} (mean of 5 seeds; plain {s['R2_RF_sourceCV_plain']:.4f}); "
                           f"headroom = {s['headroom_R2_ceiling_minus_RF']:.4f}"
                           + ("; ES1 sigma comes from NEAR-condition pairs (tolerances add condition differences) -> ceiling is a lower bound"
                              if n == "ES1" else "")
                           + ("; only 2 independent pairs -> ceiling is fragile" if s["n_source_pairs"] < 5 and n != "ES1" else "")))
    # exploratory / sensitivity rows
    for n in ["ES1", "ES2"]:
        extra = (["near_condition_cross_paper"] if n == "ES2" else
                 ["exact_independent", "near_condition_cross_paper_dedup", "near_condition_same_paper_dedup"])
        for lab in ["near_condition_same_paper"] + extra:
            s = st[n][lab]
            if s["n_pairs"] == 0:
                L.append(dict(hypothesis="H2", test_id=f"H2_explore_{lab}", dataset=n, metric="median |dlog10 D|",
                              threshold="exploratory", verdict="EXPLORATORY", n_units=0, note="no pairs"))
                continue
            L.append(dict(hypothesis="H2", test_id=f"H2_explore_{lab}", dataset=n, model="",
                          metric="median |dlog10 D| between paired rows", value=f"{s['median_abs_delta']:.4f}",
                          ci_lo=f"{s['median_abs_delta_ci'][0]:.4f}", ci_hi=f"{s['median_abs_delta_ci'][1]:.4f}",
                          threshold="exploratory", verdict="EXPLORATORY", n_units=s["n_source_pairs"],
                          note=f"sigma={s['sigma_between']:.4f}, fold={10 ** s['median_abs_delta']:.3f}, " + fmt_set(s)))
    for n in ["DES_RHO", "DES_ETA", "DES_MP", "IL_CELL", "DYE"]:
        s = st[n]["exact_with_copies"]
        si = st[n]["exact_independent"]
        if s["n_pairs"] == 0:
            continue
        L.append(dict(hypothesis="H2", test_id="H2_sens_with_copies", dataset=n, model="",
                      metric="median |delta| if copies are NOT removed", value=f"{s['median_abs_delta']:.5g}",
                      ci_lo=f"{s['median_abs_delta_ci'][0]:.5g}", ci_hi=f"{s['median_abs_delta_ci'][1]:.5g}",
                      threshold="sensitivity (descriptive)", verdict="DESCRIPTIVE", n_units=s["n_source_pairs"],
                      note=f"pairs={s['n_pairs']} (independent set: {si['n_pairs']}); share of exactly identical pairs "
                           f"{s['frac_identical']:.3f} vs {si.get('frac_identical', np.nan):.3f} independent"))
    ledger_write(os.path.join(LEDGER, "h2.csv"), L)

    summ = dict(hypothesis="H2", prereg="PREREG.md section 2 H2", primary_pair_set=primary,
                predictions=dict(P2a=dict(value=p2a_v, ci=rho["median_abs_delta_ci"], threshold="<= 0.010", holds=bool(p2a)),
                                 P2b=dict(value=p2b_v, ci=p2b_ci, threshold=">= 1.10", holds=bool(p2b)),
                                 P2c=dict(value=diff, ci=p2c_ci, rho_ratio=rho["sigma_over_sd"], eta_ratio=eta["sigma_over_sd"],
                                          threshold="< 0", holds=bool(p2c))),
                n_predictions_holding=n_hold, verdict=overall,
                per_dataset={n: {lab: {k: v for k, v in s.items() if not k.startswith("_")} for lab, s in st[n].items()}
                             for n in DATASETS})
    json.dump(summ, open(os.path.join(RESULTS, "h2_summary.json"), "w"), indent=1, default=float)
    print(json.dumps(summ["predictions"], indent=1, default=float), "\nH2 overall:", overall)


def load_unit(n):
    return {"ES1": "log10 nm", "ES2": "log10 nm", "DYE": "%", "DES_RHO": "g/cm3", "DES_ETA": "log10 cP",
            "DES_MP": "K", "IL_CELL": "wt%"}[n]


if __name__ == "__main__":
    main()
