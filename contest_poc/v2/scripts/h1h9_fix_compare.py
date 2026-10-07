"""Fix round (H1 + H9), 2026-10-07: before/after tables for the process log and for figures.

Implements no new PREREG item. It (1) checks that every ledger row that existed before the fix round has the same
value and verdict afterwards (the primary pre-registered analyses must not move), and (2) writes per-dataset
raw-vs-dedup comparison tables:
  results/raw/h1_dedup_compare.csv   one row per dataset: RF/GB/KNN gaps, pseudo p95, random RMSE, verdict (raw | dedup)
  results/raw/h9_dedup_compare.csv   one row per dataset: naive/aware/anchor coverage, width ratio, C1-C3 (raw | dedup),
                                     plus the exploratory C3 controls (raw seed-0 re-run | dedup all seeds)
Usage (from scripts/): python h1h9_fix_compare.py
"""
import json
import os

import numpy as np
import pandas as pd

from vrr_common import RAW, RESULTS, LEDGER, V2

BEFORE = os.path.join(V2, "process", "fix_H1H9", "before")
DATASETS = ["ES1", "ES2", "DYE", "DES_RHO", "DES_ETA", "DES_MP", "IL_CELL"]


def ledger_regression(h):
    b = pd.read_csv(os.path.join(BEFORE, f"{h}.csv"), dtype=str).fillna("")
    a = pd.read_csv(os.path.join(LEDGER, f"{h}.csv"), dtype=str).fillna("")
    key = ["test_id", "dataset", "model"]
    m = b.merge(a, on=key, how="left", suffixes=("_before", "_after"), indicator=True)
    missing = m[m._merge != "both"]
    changed = m[(m._merge == "both") & ((m.value_before != m.value_after) | (m.verdict_before != m.verdict_after) |
                                        (m.ci_lo_before != m.ci_lo_after) | (m.ci_hi_before != m.ci_hi_after))]
    return {"rows_before": int(len(b)), "rows_after": int(len(a)), "missing_after": int(len(missing)),
            "changed_value_ci_or_verdict": changed[key + ["value_before", "value_after", "verdict_before",
                                                         "verdict_after"]].to_dict("records")}


def main():
    out = {"ledger_regression": {h: ledger_regression(h) for h in ("h1", "h9")}}
    s1 = json.load(open(os.path.join(RESULTS, "h1_summary.json")))
    rows = []
    for d in DATASETS:
        for v, dn in (("raw", d), ("dedup", f"{d}_dedup")):
            r = s1["datasets"].get(dn)
            if r is None:
                rows.append(dict(dataset=d, variant=v, verdict="INCONCLUSIVE (not run)"))
                continue
            rows.append(dict(dataset=d, variant=v, n_rows=r["n_rows"], n_sources=r["n_sources"],
                             rf_gap=r["models"]["RF"]["gap_group"]["value"],
                             rf_gap_ci_lo=r["models"]["RF"]["gap_group"]["ci_source_boot"][0],
                             rf_gap_ci_hi=r["models"]["RF"]["gap_group"]["ci_source_boot"][1],
                             gb_gap=r["models"]["GB"]["gap_group"]["value"], knn_gap=r["models"]["KNN"]["gap_group"]["value"],
                             pseudo_p95=r["pseudo"]["p95"], rf_rmse_random=r["models"]["RF"]["rmse_mean"]["random"],
                             rf_rmse_group=r["models"]["RF"]["rmse_mean"]["group"],
                             rf_material_gap=r["models"]["RF"]["gap_material"]["value"],
                             rf_leakfree_gap=r["models"]["RF"].get("gap_group_leakfree", {}).get("value", np.nan),
                             jackknife_min_gap=r["robustness"]["jackknife_min_gap"],
                             gap_without_top3=r["robustness"]["gap_without_top3_sources"], verdict=r["verdict"]))
    h1 = pd.DataFrame(rows)
    h1.to_csv(os.path.join(RAW, "h1_dedup_compare.csv"), index=False)

    s9 = json.load(open(os.path.join(RESULTS, "h9_summary.json")))
    rows = []
    for d in DATASETS:
        for v, blk, ctl in (("raw", s9["datasets"], s9["explore_controls"].get("raw_seed0", {})),
                            ("dedup", s9["dedup_sensitivity"]["datasets"], s9["explore_controls"].get("dedup_all_seeds", {}))):
            r = blk.get(d)
            if r is None:
                rows.append(dict(dataset=d, variant=v, note="not run"))
                continue
            m = r["methods"]
            c = ctl.get(d, {})
            rows.append(dict(dataset=d, variant=v, n_rows=r.get("n_rows"), n_sources=r["n_sources"],
                             n_sources_ge8=r["n_sources_ge8"], seeds=len(r["seeds"]),
                             cov_naive=m["naive"]["coverage"], cov_aware=m["aware"]["coverage"],
                             cov_anchor=m["anchor"]["coverage"], cov_aware_on_anchor_rows=m["aware_on_anchor_rows"]["coverage"],
                             width_ratio_anchor_vs_aware=r["anchor_width_ratio_vs_aware_same_rows"]["value"],
                             width_ratio_ci_lo=r["anchor_width_ratio_vs_aware_same_rows"]["ci_source_boot"][0],
                             width_ratio_ci_hi=r["anchor_width_ratio_vs_aware_same_rows"]["ci_source_boot"][1],
                             width_ratio_per_seed_min=min(r["anchor_width_ratio_vs_aware_same_rows"]["per_seed"]),
                             width_ratio_per_seed_max=max(r["anchor_width_ratio_vs_aware_same_rows"]["per_seed"]),
                             C1=r["conditions"]["naive_cov_lt_0.85"], C2=r["conditions"]["aware_cov_ge_0.87"],
                             C3=r["conditions"]["anchor_ratio_le_0.9_and_cov_ge_0.87"],
                             ctl_seeds=("0" if v == "raw" else "0-4") if c else "",
                             ctl_aware8_ratio=c.get("aware8_ratio_vs_aware"),
                             ctl_offset_only_ratio=c.get("offset_only_ratio_anchor_vs_aware8"),
                             ctl_material_overlap_share=c.get("share_eval_rows_sharing_anchor_material"),
                             ctl_matdisjoint_cov=c.get("matdisjoint_coverage"),
                             ctl_matdisjoint_ratio=c.get("matdisjoint_ratio_vs_aware_same_rows"),
                             ctl_matdisjoint_n_evals=c.get("matdisjoint_n_evals"),
                             ctl_matdisjoint_n_sources=c.get("matdisjoint_n_sources"),
                             ctl_matdisjoint_c3_like=c.get("matdisjoint_c3_like_holds")))
    h9 = pd.DataFrame(rows)
    h9.to_csv(os.path.join(RAW, "h9_dedup_compare.csv"), index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(h1.round(3).to_string(index=False))
    print(h9.round(3).to_string(index=False))
    print(json.dumps(out, indent=1))
    print("H1 overall", s1["overall"]["verdict"], s1["overall"]["n_pass"], "| dedup", s1["overall_dedup_sensitivity"])
    print("H9 overall", s9["overall"], "| dedup", s9["dedup_sensitivity"]["overall"])
    print(s9["robustness"])
    json.dump(out, open(os.path.join(V2, "process", "fix_H1H9", "ledger_regression.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
