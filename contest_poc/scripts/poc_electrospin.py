"""PoC-2: Electrospinning (Cogni-e-SpinDB 1.0, 809 records, 57 papers, 12 polymers).
 (a) harmonization steps actually needed (units, ranges, missing values)
 (b) reproducibility floor: |Δlog10 D| between records with near-identical conditions
     reported by different papers vs within the same paper
 (c) leave-one-polymer-out k-shot: does a materials taxonomy prior help? Two different
     plausible trees are compared (tree non-uniqueness test) plus a random-tree control.
Usage: python poc_electrospin.py <cogni.csv> <outdir>
"""
import json
import sys
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors, rdFingerprintGenerator
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold

RDLogger.DisableLog("rdApp.*")
SRC, OUT = sys.argv[1], sys.argv[2]
d = pd.read_csv(SRC)
log = {}

# ---------------- (a) harmonization ----------------
SOLV = {  # density g/mL, dielectric constant, boiling point C (handbook values, approximate)
    "DMF": (0.944, 36.7, 153), "WATER": (1.0, 80.1, 100), "ETHANOL": (0.789, 24.5, 78),
    "ACETONE": (0.784, 20.7, 56), "DMAC": (0.937, 37.8, 165), "DMSO": (1.10, 46.7, 189),
    "CHLOROFORM": (1.49, 4.8, 61), "TFA": (1.49, 8.4, 72), "ACETIC_ACID": (1.05, 6.2, 118),
    "NMP": (1.03, 32.2, 202), "AC": (1.05, 6.2, 118), "DSM": (1.33, 9.1, 40),
}
POLY = {  # repeat-unit SMILES, bulk density g/cm3 (approx.)
    "PVDF": ("[*]CC([*])(F)F", 1.78), "PVA": ("[*]CC([*])O", 1.19), "PVP": ("[*]CC([*])N1CCCC1=O", 1.2),
    "PAN": ("[*]CC([*])C#N", 1.18), "PS": ("[*]CC([*])c1ccccc1", 1.05), "PCL": ("[*]CCCCCC(=O)O[*]", 1.145),
    "PMMA": ("[*]CC([*])(C)C(=O)OC", 1.18), "Y_PGA": ("[*]NC(CCC(=O)[*])C(=O)O", 1.4),
    "PDLLA": ("[*]OC(C)C([*])=O", 1.25), "PLA": ("[*]OC(C)C([*])=O", 1.25),
    "CA": ("[*]OC1C(COC(C)=O)OC([*])C(OC(C)=O)C1O", 1.3), "PET": ("[*]OCCOC(=O)c1ccc(C([*])=O)cc1", 1.38),
}


def solvent_props(s):
    parts = s.replace("-", " ").split()
    vals = np.array([SOLV.get(p, (np.nan, np.nan, np.nan)) for p in parts], dtype=float)
    return np.nanmean(vals, axis=0)


sp = np.vstack([solvent_props(s) for s in d["solvent(s)"]])
d["solv_density"], d["solv_eps"], d["solv_bp"] = sp[:, 0], sp[:, 1], sp[:, 2]
rho_p = d["polymer(s)"].map(lambda p: POLY[p][1])
c = d.solution_concentration.astype(float)
wv = d.solution_concentration_unit == "w/v%"
# w/v% (g per 100 mL solution) -> wt%: wt% = c / (100*rho_solution) *100, rho_solution ≈ rho_s + c/100*(1 - rho_s/rho_p)
rho_sol = d.solv_density + c / 100 * (1 - d.solv_density / rho_p)
d["conc_wt"] = np.where(wv, c / rho_sol, c)
log["n_wv_converted"] = int(wv.sum())
log["wv_conversion_median_rel_change"] = float(np.median((c[wv] / rho_sol[wv] - c[wv]) / c[wv]))


def rh(x):
    x = str(x)
    if "-" in x:
        a, b = x.split("-")
        return (float(a) + float(b)) / 2
    try:
        return float(x)
    except ValueError:
        return np.nan


d["rh"] = d["humidity_%"].map(rh)
log["rh_ranges_converted"] = int(d["humidity_%"].astype(str).str.contains("-").sum())
d["rpm"] = d.rotation_speed_rpm.fillna(0.0)
for col in ["needle_diameter_g", "temperature_c", "rh"]:
    d[col + "_missing"] = d[col].isna().astype(float)
    d[col] = d[col].fillna(d[col].median())
d["collector_drum"] = (d.collector_type == "Rolling Drum").astype(float)
d["collector_bath"] = (d.collector_type == "Flat With Ethanol Bath").astype(float)
mfp = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
pdesc, pfp = {}, {}
for p, (smi, rho) in POLY.items():
    m = Chem.MolFromSmiles(smi)
    pdesc[p] = [Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m),
                rdMolDescriptors.CalcNumAromaticRings(m), rho]
    pfp[p] = mfp.GetFingerprint(m)
P = np.vstack([pdesc[p] for p in d["polymer(s)"]])
for i, n in enumerate(["p_mw_ru", "p_logp", "p_tpsa", "p_arom", "p_density"]):
    d[n] = P[:, i]

d = d[d.was_formation_stable & d.fiber_diameter_nm.notna() & (d.fiber_diameter_nm > 0)].copy()
d["logD"] = np.log10(d.fiber_diameter_nm)
log["n_used"] = int(len(d))
FEATS = ["conc_wt", "voltage_kv", "flow_rate_ml/h", "tip_collector_distance_cm", "needle_diameter_g",
         "rpm", "temperature_c", "rh", "needle_diameter_g_missing", "temperature_c_missing", "rh_missing",
         "collector_drum", "collector_bath", "solv_density", "solv_eps", "solv_bp", "is_solvent_blend",
         "p_mw_ru", "p_logp", "p_tpsa", "p_arom", "p_density"]
d["is_solvent_blend"] = d.is_solvent_blend.astype(float)
X = d[FEATS].values.astype(float)
y = d.logD.values
poly = d["polymer(s)"].values
doi = d.doi.values

# ---------------- (b) reproducibility floor ----------------
rows = d[["polymer(s)", "solvent(s)", "conc_wt", "voltage_kv", "flow_rate_ml/h", "tip_collector_distance_cm",
          "collector_type", "doi", "logD"]].reset_index(drop=True)
same_paper, diff_paper = [], []
for i in range(len(rows)):
    a = rows.iloc[i]
    cand = rows.iloc[i + 1:]
    m = ((cand["polymer(s)"] == a["polymer(s)"]) & (cand["solvent(s)"] == a["solvent(s)"]) &
         (cand.collector_type == a.collector_type) & ((cand.conc_wt - a.conc_wt).abs() <= 1.0) &
         ((cand.voltage_kv - a.voltage_kv).abs() <= 2.0) &
         ((np.log(cand["flow_rate_ml/h"]) - np.log(a["flow_rate_ml/h"])).abs() <= np.log(1.3)) &
         ((cand.tip_collector_distance_cm - a.tip_collector_distance_cm).abs() <= 2.0))
    for _, b in cand[m].iterrows():
        (same_paper if b.doi == a.doi else diff_paper).append(abs(b.logD - a.logD))
log["matched_pairs_same_paper"] = len(same_paper)
log["matched_pairs_diff_paper"] = len(diff_paper)
for nm, arr in [("same_paper", same_paper), ("diff_paper", diff_paper)]:
    if arr:
        arr = np.array(arr)
        log[f"{nm}_median_abs_dlog10D"] = float(np.median(arr))
        log[f"{nm}_median_fold"] = float(10 ** np.median(arr))
        log[f"{nm}_rms_dlog10D_over_sqrt2"] = float(np.sqrt(np.mean(arr ** 2) / 2))


def rf(seed=0):
    return RandomForestRegressor(n_estimators=300, max_features=0.5, min_samples_leaf=2, n_jobs=4, random_state=seed)


# random-split CV (optimistic) vs leave-one-paper-out (realistic) vs leave-one-polymer-out
from sklearn.model_selection import KFold
def cv_rmse(splitter, groups=None):
    err = []
    for tr, te in splitter.split(X, y, groups):
        p = rf().fit(X[tr], y[tr]).predict(X[te])
        err.append((y[te] - p) ** 2)
    return float(np.sqrt(np.mean(np.concatenate(err))))


log["rmse_random5fold"] = cv_rmse(KFold(5, shuffle=True, random_state=0))
log["rmse_leave_paper_out_5group"] = cv_rmse(GroupKFold(5), doi)
log["rmse_leave_polymer_out"] = cv_rmse(GroupKFold(len(set(poly))), poly)
log["rmse_predict_mean"] = float(np.std(y))

# ---------------- (c) leave-one-polymer-out k-shot with taxonomy priors ----------------
TREE_A = {  # origin -> backbone chemistry (user's proposed order)
    "PVDF": ("synthetic", "vinyl"), "PVA": ("synthetic", "vinyl"), "PVP": ("synthetic", "vinyl"),
    "PAN": ("synthetic", "vinyl"), "PS": ("synthetic", "vinyl"), "PMMA": ("synthetic", "vinyl"),
    "PET": ("synthetic", "polyester"), "PCL": ("synthetic", "polyester"),
    "PLA": ("bio", "polyester"), "PDLLA": ("bio", "polyester"), "CA": ("bio", "polysaccharide"),
    "Y_PGA": ("bio", "polypeptide"),
}
TREE_B = {  # solvent system / hydrophilicity first
    "PVA": ("aqueous", "vinyl"), "PVP": ("aqueous", "vinyl"), "Y_PGA": ("aqueous", "polypeptide"),
    "PVDF": ("organic", "vinyl"), "PAN": ("organic", "vinyl"), "PS": ("organic", "vinyl"),
    "PMMA": ("organic", "vinyl"), "PET": ("organic", "polyester"), "PCL": ("organic", "polyester"),
    "PLA": ("organic", "polyester"), "PDLLA": ("organic", "polyester"), "CA": ("organic", "polysaccharide"),
}
polys = sorted(set(poly))
# honest LOPO biases of every polymer when it is held out (excluding target too, computed per target)
recs = []
rng = np.random.default_rng(0)
targets = [p for p in polys if (poly == p).sum() >= 15]
for T in targets:
    inT = poly == T
    biases, wv_, ns = {}, [], {}
    for Q in polys:
        if Q == T:
            continue
        tr = ~inT & (poly != Q)
        te = poly == Q
        r = y[te] - rf(1).fit(X[tr], y[tr]).predict(X[te])
        biases[Q] = r.mean(); wv_.append(r.var(ddof=1) if te.sum() > 1 else np.nan); ns[Q] = te.sum()
    sw2 = float(np.nanmean(wv_))
    bv = np.array(list(biases.values()))
    tau2 = max(np.var(bv, ddof=1) - np.mean([sw2 / ns[q] for q in biases]), 1e-3)

    def prior_from(group):
        if len(group) >= 2:
            return float(np.mean([biases[q] for q in group])), max(np.var([biases[q] for q in group], ddof=1), 1e-3)
        if len(group) == 1:
            return float(biases[group[0]]), tau2
        return 0.0, tau2

    def tree_prior(tree):
        # nearest ancestors first: same (L1,L2) siblings, else same L1
        sib = [q for q in biases if tree[q] == tree[T]]
        if not sib:
            sib = [q for q in biases if tree[q][0] == tree[T][0]]
        return prior_from(sib)

    muA, tA = tree_prior(TREE_A)
    muB, tB = tree_prior(TREE_B)
    rnd = list(rng.choice(list(biases), size=3, replace=False))
    muR, tR = prior_from(rnd)
    w = np.array([DataStructs.TanimotoSimilarity(pfp[T], pfp[q]) for q in biases]) ** 4
    w = w / w.sum() if w.sum() > 0 else np.ones_like(w) / len(w)
    muS = float(np.dot(w, list(biases.values())))
    base = rf(2).fit(X[~inT], y[~inT])
    idxT = np.where(inT)[0]
    for k in [0, 3, 5, 10]:
        for rep in range(10 if k > 0 else 1):
            rs = np.random.default_rng(100 * rep + k)
            shots = rs.choice(idxT, size=k, replace=False) if k else np.array([], int)
            test = np.setdiff1d(idxT, shots)
            pb = base.predict(X[test])
            rsh = y[shots] - base.predict(X[shots]) if k else np.array([])

            def shrink(mu, t2):
                lam = sw2 / t2
                return (rsh.sum() + lam * mu) / (len(rsh) + lam)

            if k:
                tr = np.concatenate([np.where(~inT)[0], shots])
                m1 = rf(3).fit(X[tr], y[tr]).predict(X[test])
                m0 = np.full(len(test), y[shots].mean())
            else:
                m1 = pb
                m0 = np.full(len(test), y[~inT].mean())
            def sel_train(group):
                idx = np.concatenate([np.where(np.isin(poly, group))[0], shots])
                if len(idx) < 5:
                    return np.full(len(test), np.nan)
                return rf(4).fit(X[idx], y[idx]).predict(X[test])
            sibA = [q for q in biases if TREE_A[q] == TREE_A[T]] or [q for q in biases if TREE_A[q][0] == TREE_A[T][0]]
            sibB = [q for q in biases if TREE_B[q] == TREE_B[T]] or [q for q in biases if TREE_B[q][0] == TREE_B[T][0]]
            nsel = max(len(sibA), 2)
            simq = sorted(biases, key=lambda q: -DataStructs.TanimotoSimilarity(pfp[T], pfp[q]))[:nsel]
            rndq = list(np.random.default_rng(7 + rep).choice(list(biases), size=nsel, replace=False))
            extra = {"M6A_train_on_treeA_relatives": sel_train(sibA), "M6B_train_on_treeB_relatives": sel_train(sibB),
                     "M7_train_on_fp_nearest": sel_train(simq), "M8_train_on_random_subset": sel_train(rndq)}
            preds = {"M0_local_mean": m0, "M1_global_pooled": m1, "M2_flat_shrink": pb + shrink(0.0, tau2),
                     "M3A_tree_origin_first": pb + shrink(muA, tA), "M3B_tree_solvent_first": pb + shrink(muB, tB),
                     "M3r_random_tree": pb + shrink(muR, tR), "M4_fpsim_prior": pb + shrink(muS, tau2), **extra}
            for nm, p in preds.items():
                if np.isnan(p).any():
                    continue
                recs.append(dict(polymer=T, n=int(inT.sum()), n_papers=int(len(set(doi[inT]))), k=k, rep=rep,
                                 model=nm, rmse=float(np.sqrt(np.mean((y[test] - p) ** 2)))))
    print(T, int(inT.sum()), "tau2", round(tau2, 4), "muA", round(muA, 3), "muB", round(muB, 3), flush=True)

res = pd.DataFrame(recs)
res.to_csv(f"{OUT}/electrospin_lopo_records.csv", index=False)
json.dump(log, open(f"{OUT}/electrospin_summary.json", "w"), indent=1)
print(json.dumps(log, indent=1))
print(res.groupby(["k", "model"]).rmse.mean().unstack().round(4).T.to_string())
print(res[res.k == 10].groupby(["polymer", "model"]).rmse.mean().unstack().round(3).to_string())
