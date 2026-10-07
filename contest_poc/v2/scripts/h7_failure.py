"""H7 failure-data value: success-only (one-class) vs failure-inclusive (supervised) detection of failures
(PREREG section 2, H7: H7a ES1 PVDF unstable electrospinning, H7b DES melting point > 298.15 K).

Implements
  * H7a: v1 survivor.py logic on the shared loader (load_es1_failure("PVDF"), ES1_FEATS): leave-one-failure-paper-out over
    the 10 failure papers; one-class IsolationForest / OneClassSVM (scaled, nu=0.1) / kNN distance (k=5, scaled) trained on
    stable rows of the other papers; supervised RF / HistGB classifiers on all rows of the other papers; 5 seeds;
    pooled AUC; paper-bootstrap CI of (best supervised - best one-class) and of every pairing.
  * H7b: failure = DES_MP melting T > 298.15 K; one-class trained on the success-only reference set = unique (A, B, xA)
    materials of DES_RHO and DES_ETA (descriptor features without T); supervised on DES_MP labels with source
    GroupKFold(10); AUC on held-out DES_MP sources; source-bootstrap CI; learning curve over the number of failure labels
    kept in training (5, 10, 20, 50, 100, all; 10 draws).
  * Exploratory (not graded, fixed before running): reference restricted to materials measured at T <= 298.15 K;
    reference without materials that also occur in DES_MP; one-class trained on DES_MP's own successes (same folds).

Usage (from scripts/):  python h7_failure.py a | b | lc N | summarize      (N in 5,10,20,50,100,all)
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.ensemble import IsolationForest, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from vrr_data import load, load_es1_failure
from vrr_common import group_folds, ledger_write, RAW, RESULTS, LEDGER, N_JOBS

PARTS = os.path.join(RAW, "h7_parts")
os.makedirs(PARTS, exist_ok=True)
SEEDS = range(5)
OC = ["IF", "OCSVM", "KNN5"]
SUP = ["RF", "HGB"]
LC_NS = ["5", "10", "20", "50", "100", "all"]
B = 2000


# ------------------------------------------------------------------ models
def oc_scores(name, Xtr, Xte, seed):
    """Higher score = more anomalous = predicted failure."""
    if name == "IF":
        m = IsolationForest(n_estimators=300, random_state=seed, n_jobs=N_JOBS).fit(Xtr)
        return -m.score_samples(Xte)
    if name == "OCSVM":
        m = make_pipeline(StandardScaler(), OneClassSVM(kernel="rbf", nu=0.1, gamma="scale")).fit(Xtr)
        return -m.decision_function(Xte)
    if name == "KNN5":
        sc = StandardScaler().fit(Xtr)
        nn = NearestNeighbors(n_neighbors=5).fit(sc.transform(Xtr))
        d, _ = nn.kneighbors(sc.transform(Xte))
        return d.mean(1)
    raise ValueError(name)


def sup_scores(name, Xtr, ytr, Xte, seed):
    if name == "RF":
        m = RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=seed, n_jobs=N_JOBS)
    elif name == "HGB":
        m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, min_samples_leaf=10,
                                           class_weight="balanced", random_state=seed)
    else:
        raise ValueError(name)
    return m.fit(Xtr, ytr).predict_proba(Xte)[:, 1]


def fast_auc(y, s):
    y = np.asarray(y)
    npos, nneg = int(y.sum()), int(len(y) - y.sum())
    if npos == 0 or nneg == 0:
        return np.nan
    r = rankdata(s)
    return float((r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))


# ------------------------------------------------------------------ H7a
def run_a():
    t0 = time.time()
    ds = load_es1_failure("PVDF")
    X, y, paper = ds.X, ds.y.astype(int), ds.group
    fps = sorted(set(paper[y == 1]))
    rows = []
    for seed in SEEDS:
        for p in fps:
            te = paper == p
            tr = ~te
            Xs = X[tr & (y == 0)]
            sc = {m: oc_scores(m, Xs, X[te], seed) for m in OC}
            sc.update({m: sup_scores(m, X[tr], y[tr], X[te], seed) for m in SUP})
            idx = np.where(te)[0]
            for m, s in sc.items():
                rows += [("H7a_PVDF", m, seed, int(i), p, int(y[i]), float(v)) for i, v in zip(idx, s)]
        print("H7a seed", seed, f"{time.time() - t0:.0f}s", flush=True)
    df = pd.DataFrame(rows, columns=["case", "model", "seed", "row", "group", "y", "score"])
    df.to_csv(os.path.join(PARTS, "scores_a.csv.gz"), index=False)
    meta = {"n_rows": int(len(y)), "n_fail": int(y.sum()), "n_fail_papers": len(fps), "fail_papers": fps,
            "test_rows": int(df[(df.model == "RF") & (df.seed == 0)].shape[0]),
            "test_fail": int(df[(df.model == "RF") & (df.seed == 0)].y.sum()),
            "rows_per_fail_paper": {p: int((paper == p).sum()) for p in fps},
            "fails_per_fail_paper": {p: int(((paper == p) & (y == 1)).sum()) for p in fps}}
    json.dump(meta, open(os.path.join(PARTS, "meta_a.json"), "w"), indent=1)
    print(json.dumps(meta)[:800])


# ------------------------------------------------------------------ H7b
def des_reference(mp_feats):
    parts = []
    for nm in ["DES_RHO", "DES_ETA"]:
        d = load(nm)
        assert d.feats[:-1] == mp_feats and d.feats[-1] == "T", (d.feats, mp_feats)
        f = pd.DataFrame(d.X[:, :-1], columns=mp_feats)
        f["material"] = d.material
        f["T"] = d.df["T"].values
        f["db"] = nm
        parts.append(f)
    r = pd.concat(parts, ignore_index=True)
    g = r.groupby("material")
    ref = g[mp_feats].first()
    ref["minT"] = g["T"].min()
    ref["dbs"] = g["db"].agg(lambda s: "+".join(sorted(set(s))))
    return ref


def run_b():
    t0 = time.time()
    mp = load("DES_MP")
    X, y, src = mp.X, (mp.y > 298.15).astype(int), mp.group
    ref = des_reference(mp.feats)
    mats_mp = set(mp.material)
    refsets = {"H7b_DES": ref,
               "H7b_DES_refRT": ref[ref.minT <= 298.15],
               "H7b_DES_refNoOverlap": ref[~ref.index.isin(mats_mp)]}
    meta = {"n_rows": int(len(y)), "n_fail": int(y.sum()), "n_sources": int(len(set(src))),
            "ref_sizes": {k: int(len(v)) for k, v in refsets.items()},
            "ref_materials_also_in_DES_MP": int(ref.index.isin(mats_mp).sum()),
            "DES_MP_rows_whose_material_is_in_ref": int(pd.Series(mp.material).isin(ref.index).sum()),
            "DES_MP_fail_rows_whose_material_is_in_ref": int(pd.Series(mp.material[y == 1]).isin(ref.index).sum())}
    rows = []
    idx = np.arange(len(y))
    for case, R in refsets.items():
        Xr = R[mp.feats].values.astype(float)
        for seed in SEEDS:
            for m in OC:
                s = oc_scores(m, Xr, X, seed)
                rows += [(case, m, seed, int(i), src[i], int(y[i]), float(v)) for i, v in zip(idx, s)]
        print(case, "one-class done", f"{time.time() - t0:.0f}s", flush=True)
    for seed in SEEDS:
        folds = group_folds(src, 10, seed)
        sc = {m: np.full(len(y), np.nan) for m in SUP + OC}
        for tr, te in folds:
            for m in SUP:
                sc[m][te] = sup_scores(m, X[tr], y[tr], X[te], seed)
            Xs = X[tr[y[tr] == 0]]
            for m in OC:
                sc[m][te] = oc_scores(m, Xs, X[te], seed)
        for m in SUP:
            rows += [("H7b_DES", m, seed, int(i), src[i], int(y[i]), float(v)) for i, v in zip(idx, sc[m])]
        for m in OC:
            rows += [("H7b_DES_ocInDS", m, seed, int(i), src[i], int(y[i]), float(v)) for i, v in zip(idx, sc[m])]
        print("H7b supervised + in-dataset one-class seed", seed, f"{time.time() - t0:.0f}s", flush=True)
    pd.DataFrame(rows, columns=["case", "model", "seed", "row", "group", "y", "score"]).to_csv(
        os.path.join(PARTS, "scores_b.csv.gz"), index=False)
    json.dump(meta, open(os.path.join(PARTS, "meta_b.json"), "w"), indent=1)
    print(json.dumps(meta))


def run_lc(nspec):
    t0 = time.time()
    mp = load("DES_MP")
    X, y, src = mp.X, (mp.y > 298.15).astype(int), mp.group
    folds = group_folds(src, 10, 0)
    out = []
    for draw in range(10):
        pred = np.full(len(y), np.nan)
        used = []
        for fi, (tr, te) in enumerate(folds):
            pos = tr[y[tr] == 1]
            neg = tr[y[tr] == 0]
            if nspec != "all":
                k = min(int(nspec), len(pos))
                pos = np.random.default_rng(100_000 * draw + fi).choice(pos, k, replace=False)
            used.append(len(pos))
            trn = np.r_[neg, pos]
            pred[te] = sup_scores("RF", X[trn], y[trn], X[te], draw)
        out.append(dict(case="H7b_DES", model="RF", n_fail_requested=nspec, draw=draw,
                        n_fail_used_mean=float(np.mean(used)), n_success_train_mean=float(np.mean([np.sum(y[tr] == 0) for tr, _ in folds])),
                        auc=fast_auc(y, pred)))
        print("lc", nspec, draw, round(out[-1]["auc"], 4), f"{time.time() - t0:.0f}s", flush=True)
    pd.DataFrame(out).to_csv(os.path.join(PARTS, f"lc_{nspec}.csv"), index=False)


# ------------------------------------------------------------------ summarize
def auc_table(sc):
    rows = []
    for (case, m, seed), g in sc.groupby(["case", "model", "seed"]):
        rows.append(dict(case=case, model=m, kind="supervised" if m in SUP else "one-class", seed=seed,
                         auc=fast_auc(g.y.values, g.score.values), n_pos=int(g.y.sum()), n_neg=int((1 - g.y).sum())))
    return pd.DataFrame(rows)


def unit_boot(sc_case, models, n=B, seed=0):
    """Bootstrap over units (column 'group'); returns dict model -> array of seed-mean AUCs (length n)."""
    groups = np.array(sorted(sc_case.group.unique()))
    data = {}
    for m in models:
        g = sc_case[sc_case.model == m]
        piv = {sd: gg.sort_values("row") for sd, gg in g.groupby("seed")}
        data[m] = piv
    ref = next(iter(data[models[0]].values()))
    rowgroup = ref.group.values
    yv = ref.y.values
    gidx = {gname: np.where(rowgroup == gname)[0] for gname in groups}
    rs = np.random.default_rng(seed)
    out = {m: np.full(n, np.nan) for m in models}
    for b in range(n):
        pick = rs.choice(groups, len(groups), replace=True)
        ii = np.concatenate([gidx[p] for p in pick])
        yy = yv[ii]
        if yy.sum() == 0 or yy.sum() == len(yy):
            continue
        for m in models:
            out[m][b] = np.mean([fast_auc(yy, d.score.values[ii]) for d in data[m].values()])
    return out


def summarize():
    S, L = {}, []
    sa = pd.read_csv(os.path.join(PARTS, "scores_a.csv.gz"))
    sb = pd.read_csv(os.path.join(PARTS, "scores_b.csv.gz"))
    sc = pd.concat([sa, sb], ignore_index=True)
    sc.to_csv(os.path.join(RAW, "h7_scores.csv"), index=False)
    at = auc_table(sc)
    at.to_csv(os.path.join(RAW, "h7_auc.csv"), index=False)
    meta_a = json.load(open(os.path.join(PARTS, "meta_a.json")))
    meta_b = json.load(open(os.path.join(PARTS, "meta_b.json")))
    # per-paper within AUC (H7a)
    pp = []
    for (m, seed, p), g in sa.groupby(["model", "seed", "group"]):
        pp.append(dict(model=m, seed=seed, paper=p, n=len(g), n_fail=int(g.y.sum()), auc_within=fast_auc(g.y.values, g.score.values)))
    pp = pd.DataFrame(pp)
    pp.to_csv(os.path.join(RAW, "h7a_per_paper.csv"), index=False)
    wp = pp.dropna(subset=["auc_within"]).groupby(["model", "paper"]).auc_within.mean().groupby("model").agg(["mean", "count"])
    S["H7a_within_paper"] = {m: dict(mean_auc=float(r["mean"]), n_papers_with_both_classes=int(r["count"])) for m, r in wp.iterrows()}
    for m, r in wp.iterrows():
        L.append(dict(hypothesis="H7", test_id="H7a_within_paper_auc", dataset="H7a_PVDF", model=m,
                      metric="mean within-paper AUC over failure papers that also report stable rows",
                      value=round(float(r["mean"]), 4), threshold="descriptive (diagnostic: pooled AUC also compares across papers)",
                      verdict="DESCRIPTIVE", n_units=int(r["count"]), note="seed-mean per paper, then mean over papers"))
    # learning curve
    lcs = [pd.read_csv(os.path.join(PARTS, f"lc_{n}.csv")) for n in LC_NS if os.path.exists(os.path.join(PARTS, f"lc_{n}.csv"))]
    lc = pd.concat(lcs, ignore_index=True) if lcs else pd.DataFrame()
    if len(lc):
        lc.to_csv(os.path.join(RAW, "h7_learning_curve.csv"), index=False)
    case_units = {"H7a_PVDF": ("failure papers", meta_a["n_fail_papers"]), "H7b_DES": ("DES_MP sources", meta_b["n_sources"])}
    verdicts = {}
    for case in ["H7a_PVDF", "H7b_DES"]:
        hyp_id = "H7a" if case.startswith("H7a") else "H7b"
        cs = sc[sc.case == case]
        mean_auc = at[at.case == case].groupby("model").auc.mean()
        best_sup = mean_auc[SUP].idxmax()
        best_oc = mean_auc[OC].idxmax()
        boots = unit_boot(cs, SUP + OC, seed=0)
        diff = boots[best_sup] - boots[best_oc]
        diff = diff[~np.isnan(diff)]
        ci = (float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5)))
        d0 = float(mean_auc[best_sup] - mean_auc[best_oc])
        v = "PASS" if (d0 >= 0.10 and ci[0] > 0) else "FAIL"
        verdicts[hyp_id] = v
        S[case] = {"auc_seed_mean": mean_auc.to_dict(),
                   "auc_seed_range": at[at.case == case].groupby("model").auc.agg(["min", "max"]).to_dict("index"),
                   "best_supervised": best_sup, "best_one_class": best_oc, "diff": d0, "diff_ci": ci,
                   "n_boot_valid": int(len(diff)), "verdict": v, "pairs": {}}
        unit_name, n_units = case_units[case]
        for m in SUP + OC:
            bb = boots[m][~np.isnan(boots[m])]
            mci = (float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5)))
            S[case].setdefault("auc_ci", {})[m] = mci
            rng_ = S[case]["auc_seed_range"][m]
            L.append(dict(hypothesis="H7", test_id=f"{hyp_id}_auc", dataset=case, model=m,
                          metric="pooled AUC (seed mean, 5 seeds)", value=round(mean_auc[m], 4), ci_lo=round(mci[0], 4),
                          ci_hi=round(mci[1], 4), threshold="descriptive (component of the graded difference)",
                          verdict="DESCRIPTIVE", n_units=n_units,
                          note=f"{'supervised' if m in SUP else 'one-class'}; seed range {rng_['min']:.4f}..{rng_['max']:.4f}; CI = {unit_name} bootstrap"))
        for ms in SUP:
            for mo in OC:
                dd = boots[ms] - boots[mo]
                dd = dd[~np.isnan(dd)]
                pci = (float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5)))
                pv = float(mean_auc[ms] - mean_auc[mo])
                S[case]["pairs"][f"{ms}-{mo}"] = dict(diff=pv, ci=pci, meets_rule=bool(pv >= 0.10 and pci[0] > 0))
                L.append(dict(hypothesis="H7", test_id=f"{hyp_id}_pair", dataset=case, model=f"{ms} - {mo}",
                              metric="AUC difference supervised - one-class", value=round(pv, 4), ci_lo=round(pci[0], 4),
                              ci_hi=round(pci[1], 4), threshold="reported for every pairing; graded only for best-vs-best",
                              verdict="DESCRIPTIVE", n_units=n_units,
                              note=f"would {'meet' if (pv >= 0.10 and pci[0] > 0) else 'NOT meet'} the >=0.10 & CI>0 rule"))
        extra = ""
        if case == "H7a_PVDF":
            extra = (f"; test rows {meta_a['test_rows']} ({meta_a['test_fail']} failures) from the 10 failure papers; "
                     f"{meta_a['n_rows']} PVDF rows total")
        else:
            extra = (f"; {meta_b['n_rows']} DES_MP rows, {meta_b['n_fail']} failures (mp>298.15 K, the MAJORITY class); "
                     f"reference = {meta_b['ref_sizes']['H7b_DES']} unique RHO/ETA materials; "
                     f"{meta_b['DES_MP_rows_whose_material_is_in_ref']} DES_MP rows have their material in the reference")
        L.append(dict(hypothesis="H7", test_id=f"{hyp_id}_best_diff", dataset=case, model=f"{best_sup} - {best_oc}",
                      metric="AUC(best supervised) - AUC(best one-class), best by seed-mean AUC", value=round(d0, 4),
                      ci_lo=round(ci[0], 4), ci_hi=round(ci[1], 4), threshold="diff >= 0.10 AND CI lower > 0 (in both H7a and H7b)",
                      verdict=v, n_units=n_units, note=f"CI = {B} {unit_name} bootstrap resamples ({len(diff)} valid)" + extra))
    # exploratory sensitivities (one-class variants vs the same best supervised model)
    best_sup_b = S["H7b_DES"]["best_supervised"]
    cs_sup = sc[(sc.case == "H7b_DES") & (sc.model == best_sup_b)]
    for case in ["H7b_DES_refRT", "H7b_DES_refNoOverlap", "H7b_DES_ocInDS"]:
        mean_auc = at[at.case == case].groupby("model").auc.mean()
        bo = mean_auc.idxmax()
        comb = pd.concat([cs_sup, sc[(sc.case == case) & (sc.model == bo)]])
        boots = unit_boot(comb, [best_sup_b, bo], seed=0)
        dd = boots[best_sup_b] - boots[bo]
        dd = dd[~np.isnan(dd)]
        ci = (float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5)))
        d0 = float(S["H7b_DES"]["auc_seed_mean"][best_sup_b] - mean_auc[bo])
        S[case] = dict(auc_seed_mean=mean_auc.to_dict(), best_one_class=bo, diff_vs_best_supervised=d0, ci=ci)
        desc = {"H7b_DES_refRT": f"reference restricted to materials measured at T <= 298.15 K (n={meta_b['ref_sizes']['H7b_DES_refRT']})",
                "H7b_DES_refNoOverlap": f"reference without materials that occur in DES_MP (n={meta_b['ref_sizes']['H7b_DES_refNoOverlap']})",
                "H7b_DES_ocInDS": "one-class trained on DES_MP's own successes of the training folds (same source GroupKFold)"}[case]
        L.append(dict(hypothesis="H7", test_id="H7b_sensitivity", dataset=case, model=f"{best_sup_b} - {bo}",
                      metric="AUC(best supervised) - AUC(best one-class of this variant)", value=round(d0, 4),
                      ci_lo=round(ci[0], 4), ci_hi=round(ci[1], 4), threshold="exploratory (not graded)", verdict="EXPLORATORY",
                      n_units=meta_b["n_sources"],
                      note=desc + "; one-class AUCs: " + ", ".join(f"{k}={v:.4f}" for k, v in mean_auc.items())))
    # learning curve rows
    if len(lc):
        best_oc_auc = S["H7b_DES"]["auc_seed_mean"][S["H7b_DES"]["best_one_class"]]
        S["H7b_learning_curve"] = {}
        for nspec in LC_NS:
            g = lc[lc.n_fail_requested.astype(str) == nspec]
            if len(g) == 0:
                L.append(dict(hypothesis="H7", test_id="H7b_learning_curve", dataset="H7b_DES", model="RF",
                              metric=f"AUC with n={nspec} failure labels", verdict="INCONCLUSIVE", note="not run"))
                continue
            m, lo, hi = float(g.auc.mean()), float(g.auc.min()), float(g.auc.max())
            S["H7b_learning_curve"][nspec] = dict(auc_mean=m, auc_min=lo, auc_max=hi, n_draws=int(len(g)),
                                                  n_fail_used_mean=float(g.n_fail_used_mean.mean()),
                                                  beats_best_one_class_share=float(np.mean(g.auc > best_oc_auc)))
            L.append(dict(hypothesis="H7", test_id="H7b_learning_curve", dataset="H7b_DES", model="RF",
                          metric=f"pooled AUC with n={nspec} failure labels per training fold (mean of draws)",
                          value=round(m, 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                          threshold="descriptive (ci columns = min..max over draws)", verdict="DESCRIPTIVE", n_units=int(len(g)),
                          note=f"failures used per fold {g.n_fail_used_mean.mean():.1f}, successes per fold {g.n_success_train_mean.mean():.0f}; "
                               f"draws beating best one-class AUC ({best_oc_auc:.4f}): {int((g.auc > best_oc_auc).sum())}/{len(g)}"))
    ov = "PASS" if all(v == "PASS" for v in verdicts.values()) else ("FAIL" if all(v == "FAIL" for v in verdicts.values()) else "PARTIAL")
    S["overall"] = dict(verdict=ov, **verdicts)
    S["meta_a"], S["meta_b"] = meta_a, meta_b
    L.append(dict(hypothesis="H7", test_id="H7_overall", dataset="H7a_PVDF+H7b_DES", metric="cases meeting the rule",
                  value=sum(v == "PASS" for v in verdicts.values()), threshold="both H7a and H7b: diff >= 0.10 and CI lower > 0",
                  verdict=ov, n_units=2, note=f"H7a={verdicts['H7a']}, H7b={verdicts['H7b']}; PARTIAL = exactly one case passes (rule fixed before running)"))
    for r in L:   # NaN -> empty cell in the ledger
        for k, v in list(r.items()):
            if isinstance(v, float) and np.isnan(v):
                r[k] = ""
    ledger_write(os.path.join(LEDGER, "h7.csv"), L)
    with open(os.path.join(RESULTS, "h7_summary.json"), "w") as f:
        json.dump(S, f, indent=1, default=float)
    print(json.dumps({k: (v if k in ("overall",) else {kk: v[kk] for kk in ("best_supervised", "best_one_class", "diff", "diff_ci", "verdict")})
                      for k, v in S.items() if k in ("overall", "H7a_PVDF", "H7b_DES")}, default=float, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "a":
        run_a()
    elif mode == "b":
        run_b()
    elif mode == "lc":
        run_lc(sys.argv[2])
    else:
        summarize()
