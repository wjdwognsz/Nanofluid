"""PoC-3: Can a cheap a-priori 'transferability score' predict whether linking an external
dataset (source) helps or hurts a small target dataset? Does a stepping-stone chain A->B->C
beat direct transfer?

Transfer mechanism (model-agnostic, light): cross-fitted source prediction g_S(x) used as a
prior mean for the target:  y_T ≈ a + b*g_S(x) + RF_residual(x).  Baseline: RF(x).
Strict 'new polymer' setting: g_S for a target polymer is always produced by a source model
that never saw that polymer.

Usage: python poc_transfer.py <polyVERSE/Other dir> <outdir>
"""
import json
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator, Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")
OTHER, OUT = sys.argv[1], sys.argv[2]
MFP = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
LADDER = ["[d]", "[e]", "[g]", "[t]"]


def key_of(s):
    s = str(s)
    for t in LADDER:
        s = s.replace(t, "[*]")
    m = Chem.MolFromSmiles(s)
    return (Chem.MolToSmiles(m), m) if m is not None else (None, None)


FEAT, FPB = {}, {}


def add_series(raw_smiles, values):
    out = {}
    for s, v in zip(raw_smiles, values):
        if pd.isna(v):
            continue
        k, m = key_of(s)
        if k is None:
            continue
        if k not in FEAT:
            fp = MFP.GetCountFingerprintAsNumPy(m).astype(np.float32)
            desc = [Descriptors.MolWt(m), m.GetNumHeavyAtoms(), rdMolDescriptors.CalcNumAromaticRings(m),
                    rdMolDescriptors.CalcNumRotatableBonds(m), rdMolDescriptors.CalcFractionCSP3(m),
                    Descriptors.TPSA(m), sum(a.GetSymbol() == "F" for a in m.GetAtoms()) / m.GetNumHeavyAtoms(),
                    sum(a.GetSymbol() in ("N", "O") for a in m.GetAtoms()) / m.GetNumHeavyAtoms(),
                    Descriptors.MolLogP(m)]
            FEAT[k] = np.concatenate([fp, np.array(desc, np.float32)])
            FPB[k] = MFP.GetFingerprint(m)
        out.setdefault(k, []).append(float(v))
    return pd.Series({k: np.mean(v) for k, v in out.items()})


TASKS = {}
master = pd.read_csv(f"{OTHER}/Gas_permeability_solubility_diffusivity/master_transport_2025_08_13.csv", low_memory=False)
for prop, g in master.groupby("property"):
    TASKS[prop] = add_series(g.p_csmiles, g.value)
ced = pd.read_csv(f"{OTHER}/Cohesive_energy_density/Cohesive_energy_density_2025_06_23.csv")
TASKS["X_CED"] = add_series(ced.smiles1, np.log10(ced.value_COE))
for nm, f, col, sc in [("X_ionization_E", "Ionization_energy/ionization_energy_202412051526.csv", "value", "smiles"),
                       ("X_electron_aff", "Electron_Affinity/electron_affinity_202412051526.csv", "value", "smiles1"),
                       ("X_atomization_H", "Atomization_enthalpy/atomization_enthalpy_202412051524.csv", "value", "smiles1"),
                       ("X_bandgap_chain", "bandgap_chain/bandgap_chain.csv", "bandgap_chain", "smiles")]:
    t = pd.read_csv(f"{OTHER}/{f}")
    TASKS[nm] = add_series(t[sc], t[col])
up = pd.read_csv(f"{OTHER}/Solvent_Diffusivity_Sorption_MTL_NCM/master_uptake_sorption_dataset.csv")
w = up[up["Solvent Canonical SMILES"] == "O"]
if len(w) >= 20:
    TASKS["X_water_uptake"] = add_series(w["Polymer Canonical SMILES"], w["Uptake Sorption(log10)"])
sd = pd.read_csv(f"{OTHER}/Solvent_Diffusivity_Sorption_MTL_NCM/master_solvent_diffusivity_dataset.csv")
w2 = sd[sd["Solvent Canonical SMILES"] == "O"]
if len(w2) >= 20:
    TASKS["X_water_diffusivity"] = add_series(w2["Polymer Canonical SMILES"], w2["Target Diffusivity Value(log10)"])
chi = pd.read_csv(f"{OTHER}/chi_parameter/chi_parameter.csv")
w3 = chi[chi.Solvent_SMILES == "O"]
if len(w3) >= 20:
    TASKS["X_chi_water"] = add_series(w3.Polymer_SMILES, w3.chi)

sizes = {k: len(v) for k, v in TASKS.items()}
print(json.dumps(sizes, indent=0), flush=True)

rng = np.random.default_rng(0)
TARGETS = {}
for t in ["p_exp_H2O", "s_exp_H2O", "d_exp_H2O", "s_exp_He", "s_exp_H2", "d_exp_He", "d_exp_H2", "s_exp_CO2", "d_exp_CO2"]:
    TARGETS[t] = (TASKS[t], t)
for t in ["p_exp_CO2", "p_exp_N2"]:
    s = TASKS[t]
    TARGETS[f"{t}_sub40"] = (s.loc[rng.choice(s.index, 40, replace=False)], t)

SOURCES = [k for k, v in TASKS.items() if len(v) >= 30]


def Xof(keys):
    return np.vstack([FEAT[k] for k in keys])


def rf(n=100, mf=0.2, seed=0):
    return RandomForestRegressor(n_estimators=n, max_features=mf, n_jobs=4, random_state=seed)


def physics_prior(src, tgt_parent):
    """expert relatedness: same mechanism/gas -> higher."""
    if src.startswith("X_"):
        rel = {"X_water_uptake": 1.5, "X_water_diffusivity": 1.5, "X_chi_water": 1.0, "X_CED": 0.5}
        base = rel.get(src, 0.0)
        return base if "H2O" in tgt_parent else (0.5 if src == "X_CED" else 0.0)
    ts, _, tg = tgt_parent.split("_")
    ss, sf, sg = src.split("_")
    if ss == ts and sg == tg:
        return 2.0
    if ss == ts:
        return 1.5
    if sg == tg:
        return 1.0
    return 0.5


def tax_cov(src_keys, tgt_keys):
    sfp = [FPB[k] for k in src_keys]
    return float(np.mean([max(DataStructs.BulkTanimotoSimilarity(FPB[k], sfp)) for k in tgt_keys]))


REPEATS, K = 2, 5


def folds(n, rep):
    r = np.random.default_rng(rep)
    perm = r.permutation(n)
    return [perm[i::K] for i in range(K)]


def crossfit_source(src, tkeys, fold_list):
    """g_S(x) for every target polymer, from a source model that excluded that polymer's fold."""
    S = TASKS[src]
    g = np.zeros(len(tkeys))
    for te in fold_list:
        excl = set(tkeys[i] for i in te)
        sk = [k for k in S.index if k not in excl]
        m = rf(seed=11).fit(Xof(sk), S.loc[sk].values)
        g[te] = m.predict(Xof([tkeys[i] for i in te]))
    return g


def eval_target(y, X, fold_list, G=None):
    """returns per-sample squared errors (baseline if G is None else transfer with prior(s) G (n x m))."""
    se = np.zeros(len(y))
    for te in fold_list:
        tr = np.setdiff1d(np.arange(len(y)), te)
        if G is None:
            p = rf(200, 0.3, 5).fit(X[tr], y[tr]).predict(X[te])
        else:
            lin = LinearRegression().fit(G[tr], y[tr])
            res = y[tr] - lin.predict(G[tr])
            p = lin.predict(G[te]) + rf(200, 0.3, 5).fit(X[tr], res).predict(X[te])
        se[te] = (y[te] - p) ** 2
    return se


def score_in_fold(src, g, y, tkeys, fold_list):
    """a-priori scores computed on TRAINING part of each fold only; averaged."""
    out = {"S_proxy_corr": [], "S_label_overlap_corr": []}
    S = TASKS[src]
    for te in fold_list:
        tr = np.setdiff1d(np.arange(len(y)), te)
        out["S_proxy_corr"].append(abs(pearsonr(g[tr], y[tr])[0]) if np.std(g[tr]) > 0 else 0.0)
        ov = [i for i in tr if tkeys[i] in S.index]
        out["S_label_overlap_corr"].append(
            abs(spearmanr(S.loc[[tkeys[i] for i in ov]].values, y[ov]).correlation) if len(ov) >= 6 else np.nan)
    return {k: float(np.nanmean(v)) if not np.all(np.isnan(v)) else np.nan for k, v in out.items()}


rows, chains = [], []
for tname, (ser, parent) in TARGETS.items():
    tkeys = list(ser.index)
    y = ser.values
    X = Xof(tkeys)
    base_se = np.mean([eval_target(y, X, folds(len(y), r)) for r in range(REPEATS)], axis=0)
    base_rmse = float(np.sqrt(base_se.mean()))
    print(f"== {tname} n={len(y)} base RMSE={base_rmse:.3f} sd(y)={y.std():.3f}", flush=True)
    G_cache = {}
    for src in SOURCES:
        if src == parent or src == tname:
            continue
        gains, scs = [], []
        for r in range(REPEATS):
            fl = folds(len(y), r)
            g = crossfit_source(src, tkeys, fl)
            G_cache[(src, r)] = g
            se = eval_target(y, X, fl, g[:, None])
            gains.append(se)
            scs.append(score_in_fold(src, g, y, tkeys, fl))
        rmse = float(np.sqrt(np.mean(np.mean(gains, axis=0))))
        sc = {k: float(np.nanmean([s[k] for s in scs])) for k in scs[0]}
        overlap = len(set(tkeys) & set(TASKS[src].index)) / len(tkeys)
        rows.append(dict(target=tname, source=src, n_target=len(y), n_source=len(TASKS[src]), base_rmse=base_rmse,
                         rmse=rmse, rel_gain=(base_rmse - rmse) / base_rmse,
                         S_size=np.log10(len(TASKS[src])), S_coverage=tax_cov(list(TASKS[src].index)[:1500], tkeys),
                         S_physics=physics_prior(src, parent), S_overlap_frac=overlap, **sc))
    df_t = pd.DataFrame([r for r in rows if r["target"] == tname])
    print(df_t.sort_values("rel_gain", ascending=False)[["source", "rel_gain", "S_proxy_corr", "S_physics", "S_size"]]
          .head(6).round(3).to_string(), flush=True)

    # ---- pre-registered stepping-stone test, selection by score only ----
    # B = best-scored source among small/medium experimental tasks (n<=200), A = best-scored source for B
    cand_B = df_t[(df_t.n_source <= 200) & (~df_t.source.str.startswith("X_"))]
    if len(cand_B) == 0:
        continue
    B = cand_B.sort_values("S_proxy_corr", ascending=False).source.iloc[0]
    A_direct = df_t.sort_values("S_proxy_corr", ascending=False).source.iloc[0]
    # choose A for B using B's own data (proxy corr of large sources on B), excluding target task
    serB = TASKS[B]
    bkeys = list(serB.index)
    yB = serB.values
    bestA, bestc = None, -1
    for src in SOURCES:
        if src in (B, parent, tname) or len(TASKS[src]) < 200:
            continue
        common = [k for k in bkeys if k in TASKS[src].index]
        gA = crossfit_source(src, bkeys, folds(len(bkeys), 99))
        c_ = abs(pearsonr(gA, yB)[0])
        if c_ > bestc:
            bestA, bestc = src, c_
    res_chain = {"target": tname, "B": B, "A_for_B": bestA, "A_direct": A_direct}
    for r in range(REPEATS):
        fl = folds(len(y), r)
        tkeys_set = tkeys
        # chain: model B|A built on B data, cross-fitted to target folds (excludes target test-fold polymers)
        gBA = np.zeros(len(y))
        for te in fl:
            excl = set(tkeys[i] for i in te)
            bk = [k for k in bkeys if k not in excl]
            # prior from A for B polymers, cross-fitted within B
            gA_B = np.zeros(len(bk))
            bfl = folds(len(bk), 7)
            for bte in bfl:
                ex2 = excl | set(bk[i] for i in bte)
                ak = [k for k in TASKS[bestA].index if k not in ex2]
                gA_B[bte] = rf(seed=13).fit(Xof(ak), TASKS[bestA].loc[ak].values).predict(Xof([bk[i] for i in bte]))
            ak = [k for k in TASKS[bestA].index if k not in excl]
            mA = rf(seed=13).fit(Xof(ak), TASKS[bestA].loc[ak].values)
            yb = serB.loc[bk].values
            lin = LinearRegression().fit(gA_B[:, None], yb)
            mres = rf(200, 0.3, 5).fit(Xof(bk), yb - lin.predict(gA_B[:, None]))
            xt = Xof([tkeys[i] for i in te])
            gBA[te] = lin.predict(mA.predict(xt)[:, None]) + mres.predict(xt)
        variants = {
            "direct_A_best_scored": G_cache[(A_direct, r)][:, None],
            "direct_B": G_cache[(B, r)][:, None],
            "direct_A_for_B": G_cache.get((bestA, r), crossfit_source(bestA, tkeys, fl))[:, None],
            "chain_A_to_B_to_C": gBA[:, None],
            "multi_A_and_B": np.column_stack([G_cache.get((bestA, r), crossfit_source(bestA, tkeys, fl)), G_cache[(B, r)]]),
        }
        for nm, G in variants.items():
            res_chain.setdefault(nm, []).append(eval_target(y, X, fl, G))
    for nm in list(res_chain):
        if isinstance(res_chain[nm], list):
            res_chain[nm] = float(np.sqrt(np.mean(np.mean(res_chain[nm], axis=0))))
    res_chain["baseline"] = base_rmse
    chains.append(res_chain)
    print("chain:", json.dumps(res_chain), flush=True)

R = pd.DataFrame(rows)
R.to_csv(f"{OUT}/transfer_pairs.csv", index=False)
pd.DataFrame(chains).to_csv(f"{OUT}/transfer_chains.csv", index=False)

# ---- evaluation of scores ----
summ = {}
R["neg"] = (R.rel_gain < 0).astype(int)
summ["frac_negative_transfer"] = float(R.neg.mean())
for s in ["S_proxy_corr", "S_physics", "S_size", "S_coverage", "S_label_overlap_corr", "S_overlap_frac"]:
    v = R[[s, "rel_gain", "neg", "target"]].dropna()
    per_t = [spearmanr(g[s], g.rel_gain).correlation for _, g in v.groupby("target") if g[s].nunique() > 1]
    try:
        auc = roc_auc_score(v.neg, -v[s])
    except ValueError:
        auc = np.nan
    # top-1 selection regret: gain of top-scored source / gain of best source
    top1, rand = [], []
    for _, g in v.groupby("target"):
        best = g.rel_gain.max()
        top1.append(g.sort_values(s, ascending=False).rel_gain.iloc[0])
        rand.append(g.rel_gain.mean())
    summ[s] = dict(n_pairs=int(len(v)), mean_per_target_spearman=float(np.nanmean(per_t)),
                   auroc_detect_negative=float(auc), mean_gain_of_top1_selected=float(np.mean(top1)),
                   mean_gain_random_source=float(np.mean(rand)))
summ["mean_gain_oracle_best"] = float(R.groupby("target").rel_gain.max().mean())
json.dump(summ, open(f"{OUT}/transfer_summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
print(pd.DataFrame(chains).round(3).to_string())
