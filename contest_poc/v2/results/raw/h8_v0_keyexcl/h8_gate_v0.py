"""H8 -- link gate with a permutation threshold, nested evaluation (PREREG section 2, H8).

Implements PREREG H8 exactly:
  * data: polyVERSE small targets (11, as v1): p_exp_H2O, s_exp_H2O, d_exp_H2O, s_exp_He, s_exp_H2, d_exp_He,
    d_exp_H2, s_exp_CO2, d_exp_CO2, p_exp_CO2_sub40, p_exp_N2_sub40 (sub40 = v1 code path, default_rng(0)).
  * source pool: 37 real sources (every polyVERSE task with >=30 polymers, as v1: 19 experimental transport,
    13 simulated transport, 4 unrelated DFT, 1 other property) minus the target itself and its parent,
    + 10 label-permuted sources (bases p_exp_O2, s_exp_CH4, d_sim_CO2, X_CED, X_ionization_E; seeds 500..509).
  * strict new-polymer setting: g_s(i) for target polymer i in outer fold Fk comes from a source RF fitted on
    source s with every Fk polymer removed.
  * nested: outer 5-fold x 3 repeats; in each outer fold the score of every real and permuted source is
    |Pearson r(g_s[Tr], y[Tr])| using target labels of the outer-training part only; GATE threshold = 95th
    percentile of the 10 permuted-source scores on the same Tr.
  * policies: NONE (RF on X), PHYS (pre-specified, below), TOP (best-scored real source, no gate),
    GATE (TOP if score > threshold else NONE), ALL3 (top-3 real sources jointly).
    Transfer model: y ~ LinearRegression(g) + RF residual on X (as v1).
  * metric: per outer fold RMSE gain vs NONE; per-target gain = mean over 15 folds; negative transfer = gain < -1%.
  * pass (all three): GATE negative-transfer targets <= 1/11; mean GATE gain > 0;
    GATE negative-transfer rate < TOP's or PHYS's rate.

PHYS mapping (pre-specified before any H8 model was run; rule in process/h8_log.md):
  p_exp_H2O -> s_sim_H2O      s_exp_H2O -> s_sim_H2O      d_exp_H2O -> d_exp_He
  s_exp_He  -> s_exp_H2       s_exp_H2  -> s_exp_He       d_exp_He  -> d_exp_H2      d_exp_H2 -> d_exp_He
  s_exp_CO2 -> s_sim_CO2      d_exp_CO2 -> d_sim_CO2      p_exp_CO2_sub40 -> p_sim_CO2  p_exp_N2_sub40 -> p_sim_N2

Exploratory / descriptive (declared before running, never graded): GATE_MAX (threshold = max permuted score),
per-source realized gain in every fold (ORACLE / RANDOM / score-vs-gain), pooled-RMSE gain.
POST HOC (added to aggregate() after the graded result was seen; EXPLORATORY only): v1-style score validity on
(target, source) pairs averaged over folds (h8_source_target.csv), pooled-metric negative-transfer counts,
gain by source class, and the reproducibility note (results/raw/h8_repro/).

Usage (from v2/scripts):
  python h8_gate.py pool                  # pool table, sub40 keys, PHYS check
  python h8_gate.py run <target> <repeat> [<repeat> ...]  # chunks -> results/raw/h8_parts/
  python h8_gate.py aggregate             # raw csv, summary json, ledger
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdFingerprintGenerator, rdMolDescriptors
from scipy.stats import pearsonr, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

from vrr_common import LEDGER, N_JOBS, RAW, RESULTS, V2, boot_ci, ledger_write, make_model, random_folds

RDLogger.DisableLog("rdApp.*")
ROOT = os.environ.get("VRR_DATA", "/tmp/claude-0/-home-user-Nanofluid/18167133-ff89-5f87-bba0-dd738bb11169/scratchpad")
OTHER = f"{ROOT}/data/polyVERSE/Other"
PARTS = os.path.join(RAW, "h8_parts")
os.makedirs(PARTS, exist_ok=True)

TARGET_NAMES = ["p_exp_H2O", "s_exp_H2O", "d_exp_H2O", "s_exp_He", "s_exp_H2", "d_exp_He", "d_exp_H2",
                "s_exp_CO2", "d_exp_CO2", "p_exp_CO2_sub40", "p_exp_N2_sub40"]
PHYS = {"p_exp_H2O": "s_sim_H2O", "s_exp_H2O": "s_sim_H2O", "d_exp_H2O": "d_exp_He",
        "s_exp_He": "s_exp_H2", "s_exp_H2": "s_exp_He", "d_exp_He": "d_exp_H2", "d_exp_H2": "d_exp_He",
        "s_exp_CO2": "s_sim_CO2", "d_exp_CO2": "d_sim_CO2", "p_exp_CO2_sub40": "p_sim_CO2",
        "p_exp_N2_sub40": "p_sim_N2"}
PERM_BASES = ["p_exp_O2", "s_exp_CH4", "d_sim_CO2", "X_CED", "X_ionization_E"]
N_PERM, PERM_SEED0 = 10, 500
REPEATS, K = 3, 5
NEG = -0.01
POLICIES = ["NONE", "PHYS", "TOP", "GATE", "ALL3"]
EXPL_POLICIES = ["GATE_MAX"]
MFP = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
LADDER = ["[d]", "[e]", "[g]", "[t]"]


# ------------------------------------------------------------------ data (v1 poc_transfer.py featurisation)
def _key_of(s):
    s = str(s)
    for t in LADDER:
        s = s.replace(t, "[*]")
    m = Chem.MolFromSmiles(s)
    return (Chem.MolToSmiles(m), m) if m is not None else (None, None)


def _build():
    FEAT = {}

    def add_series(raw_smiles, values):
        out = {}
        for s, v in zip(raw_smiles, values):
            if pd.isna(v):
                continue
            k, m = _key_of(s)
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
            out.setdefault(k, []).append(float(v))
        return pd.Series({k: np.mean(v) for k, v in out.items()})

    TASKS = {}
    master = pd.read_csv(f"{OTHER}/Gas_permeability_solubility_diffusivity/master_transport_2025_08_13.csv",
                         low_memory=False)
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
    # targets, exactly the v1 code path (incl. the rng call order for the _sub40 subsamples)
    rng = np.random.default_rng(0)
    TARGETS = {}
    for t in ["p_exp_H2O", "s_exp_H2O", "d_exp_H2O", "s_exp_He", "s_exp_H2", "d_exp_He", "d_exp_H2", "s_exp_CO2",
              "d_exp_CO2"]:
        TARGETS[t] = (TASKS[t], t)
    for t in ["p_exp_CO2", "p_exp_N2"]:
        s = TASKS[t]
        TARGETS[f"{t}_sub40"] = (s.loc[rng.choice(s.index, 40, replace=False)], t)
    return TASKS, TARGETS, FEAT


_LOADED = None


def load_all():
    """Built in memory once per process (no on-disk cache: nothing is written into the data root)."""
    global _LOADED
    if _LOADED is None:
        _LOADED = _build()
    return _LOADED


def source_class(name):
    if name.startswith("X_"):
        return "other_property" if name == "X_CED" else "unrelated_DFT"
    return "sim_transport" if "_sim_" in name else "exp_transport"


def real_pool(TASKS, tname, parent):
    return [k for k, v in TASKS.items() if len(v) >= 30 and k not in (tname, parent)]


def perm_sources(TASKS):
    out = {}
    for i in range(N_PERM):
        base = PERM_BASES[i % len(PERM_BASES)]
        b = TASKS[base]
        out[f"PERM{i:02d}_{base}"] = pd.Series(np.random.default_rng(PERM_SEED0 + i).permutation(b.values), index=b.index)
    return out


# ------------------------------------------------------------------ modelling
def src_rf():
    return RandomForestRegressor(n_estimators=100, max_features=0.2, n_jobs=N_JOBS, random_state=11)


def tgt_rf(seed):
    return make_model("RF", seed).set_params(n_jobs=1)


def crossfit_source(S, Xof, tkeys, fold_list):
    """g(i) for every target polymer from a source model fitted without the polymers of i's outer fold.
    Models are cached by the excluded polymers that actually occur in the source."""
    cache, g, nfit = {}, np.zeros(len(tkeys)), 0
    sidx = set(S.index)
    for _, te in fold_list:
        excl = frozenset(tkeys[i] for i in te) & sidx
        if excl not in cache:
            sk = [k for k in S.index if k not in excl]
            cache[excl] = src_rf().fit(Xof(sk), S.loc[sk].values)
            nfit += 1
        g[te] = cache[excl].predict(Xof([tkeys[i] for i in te]))
    return g, nfit


def fit_predict(X, y, tr, te, G, seed):
    """NONE if G is None, else LinearRegression(G) + RF residual."""
    if G is None:
        return tgt_rf(seed).fit(X[tr], y[tr]).predict(X[te])
    lin = LinearRegression().fit(G[tr], y[tr])
    res = y[tr] - lin.predict(G[tr])
    return lin.predict(G[te]) + tgt_rf(seed).fit(X[tr], res).predict(X[te])


def score(g, y):
    if np.std(g) == 0 or np.std(y) == 0:
        return 0.0
    return float(abs(pearsonr(g, y)[0]))


def run_chunk(tname, rep):
    t0 = time.time()
    TASKS, TARGETS, FEAT = load_all()

    def Xof(keys):
        return np.vstack([FEAT[k] for k in keys])

    ser, parent = TARGETS[tname]
    tkeys = list(ser.index)
    y = ser.values.astype(float)
    X = Xof(tkeys)
    reals = real_pool(TASKS, tname, parent)
    assert PHYS[tname] in reals, (tname, PHYS[tname])
    perms = perm_sources(TASKS)
    allsrc = {**{s: TASKS[s] for s in reals}, **perms}
    fl = random_folds(len(y), K, seed=rep)
    G, nfits = {}, 0
    for s, S in allsrc.items():
        G[s], nf = crossfit_source(S, Xof, tkeys, fl)
        nfits += nf
    t_src = time.time() - t0
    seed = rep
    pol_rows, sc_rows = [], []
    for f, (tr, te) in enumerate(fl):
        sc = {s: score(G[s][tr], y[tr]) for s in allsrc}
        psc = np.array([sc[s] for s in perms])
        thr = float(np.percentile(psc, 95))
        thr_max = float(psc.max())
        ranked = sorted(reals, key=lambda s: -sc[s])
        top, top3 = ranked[0], ranked[:3]
        jobs = [("NONE", None)] + [(s, G[s][:, None]) for s in allsrc] + \
               [("ALL3", np.column_stack([G[s] for s in top3]))]
        preds = Parallel(n_jobs=N_JOBS, prefer="threads")(
            delayed(fit_predict)(X, y, tr, te, Gm, seed) for _, Gm in jobs)
        P = {name: p for (name, _), p in zip(jobs, preds)}
        r_none = float(np.sqrt(np.mean((y[te] - P["NONE"]) ** 2)))

        def rec(policy, chosen, p, **extra):
            r = float(np.sqrt(np.mean((y[te] - p) ** 2)))
            pol_rows.append(dict(target=tname, repeat=rep, fold=f, policy=policy, chosen_source=chosen, rmse=r,
                                 gain=(r_none - r) / r_none, rmse_none=r_none, n_test=len(te), n_train=len(tr),
                                 threshold95=thr, threshold_max=thr_max, top_source=top, top_score=sc[top],
                                 **extra))
            return r

        rec("NONE", "", P["NONE"])
        rec("PHYS", PHYS[tname], P[PHYS[tname]], chosen_score=sc[PHYS[tname]])
        rec("TOP", top, P[top], chosen_score=sc[top])
        gate_open = sc[top] > thr
        rec("GATE", top if gate_open else "", P[top] if gate_open else P["NONE"], gate_open=gate_open,
            chosen_score=sc[top])
        rec("ALL3", "|".join(top3), P["ALL3"], chosen_score=float(np.mean([sc[s] for s in top3])))
        gm_open = sc[top] > thr_max
        rec("GATE_MAX", top if gm_open else "", P[top] if gm_open else P["NONE"], gate_open=gm_open,
            chosen_score=sc[top])
        rank = {s: i + 1 for i, s in enumerate(ranked)}
        for s in allsrc:
            r = float(np.sqrt(np.mean((y[te] - P[s]) ** 2)))
            sc_rows.append(dict(target=tname, repeat=rep, fold=f, source=s, is_permuted=s in perms,
                                source_class="permuted" if s in perms else source_class(s), score=sc[s],
                                rank_among_real=rank.get(s, np.nan), threshold95=thr, above_threshold=sc[s] > thr,
                                rmse_if_used=r, gain_if_used=(r_none - r) / r_none, rmse_none=r_none,
                                n_source=len(allsrc[s]),
                                overlap_with_target=len(set(tkeys) & set(allsrc[s].index))))
    pd.DataFrame(pol_rows).to_csv(f"{PARTS}/h8_{tname}_r{rep}_policy.csv", index=False)
    pd.DataFrame(sc_rows).to_csv(f"{PARTS}/h8_{tname}_r{rep}_scores.csv", index=False)
    meta = dict(target=tname, repeat=rep, n=len(y), n_real=len(reals), n_perm=len(perms), source_fits=nfits,
                sec_source=round(t_src, 1), sec_total=round(time.time() - t0, 1))
    json.dump(meta, open(f"{PARTS}/h8_{tname}_r{rep}_meta.json", "w"))
    print(json.dumps(meta), flush=True)


# ------------------------------------------------------------------ pool description
def write_pool():
    TASKS, TARGETS, FEAT = load_all()
    rows = []
    for s, v in TASKS.items():
        r = dict(source=s, n_polymers=len(v), source_class=source_class(s), in_pool=len(v) >= 30)
        for t, (ser, parent) in TARGETS.items():
            r[f"overlap_{t}"] = len(set(ser.index) & set(v.index)) if len(v) >= 30 and s not in (t, parent) else np.nan
        rows.append(r)
    pd.DataFrame(rows).to_csv(f"{RAW}/h8_pool.csv", index=False)
    sk = []
    for t in ["p_exp_CO2_sub40", "p_exp_N2_sub40"]:
        ser, parent = TARGETS[t]
        sk += [dict(target=t, parent=parent, polymer_key=k, y=float(v)) for k, v in ser.items()]
    pd.DataFrame(sk).to_csv(f"{RAW}/h8_sub40_keys.csv", index=False)
    for t, (ser, parent) in TARGETS.items():
        reals = real_pool(TASKS, t, parent)
        print(t, "n", len(ser), "sd", round(float(ser.std()), 3), "real sources", len(reals),
              "PHYS", PHYS[t], "in pool", PHYS[t] in reals)
    print("pool size (>=30):", sum(len(v) >= 30 for v in TASKS.values()))


# ------------------------------------------------------------------ aggregation
def aggregate():
    pol = pd.concat([pd.read_csv(f"{PARTS}/h8_{t}_r{r}_policy.csv") for t in TARGET_NAMES for r in range(REPEATS)
                     if os.path.exists(f"{PARTS}/h8_{t}_r{r}_policy.csv")], ignore_index=True)
    scs = pd.concat([pd.read_csv(f"{PARTS}/h8_{t}_r{r}_scores.csv") for t in TARGET_NAMES for r in range(REPEATS)
                     if os.path.exists(f"{PARTS}/h8_{t}_r{r}_scores.csv")], ignore_index=True)
    metas = [json.load(open(f"{PARTS}/h8_{t}_r{r}_meta.json")) for t in TARGET_NAMES for r in range(REPEATS)
             if os.path.exists(f"{PARTS}/h8_{t}_r{r}_meta.json")]
    done = pol.groupby("target").repeat.nunique()
    missing = [t for t in TARGET_NAMES if done.get(t, 0) < REPEATS]
    pol.to_csv(f"{RAW}/h8_policy.csv", index=False)
    scs.to_csv(f"{RAW}/h8_scores.csv", index=False)
    TASKS, TARGETS, _ = load_all()

    # per-target table
    trows = []
    for t in TARGET_NAMES:
        p = pol[pol.target == t]
        if p.empty:
            continue
        ser, parent = TARGETS[t]
        r = dict(target=t, n=len(ser), sd_y=float(ser.std()), n_folds=int(len(p[p.policy == "NONE"])),
                 rmse_none_mean=float(p[p.policy == "NONE"].rmse.mean()), phys_source=PHYS[t])
        for pl in POLICIES[1:] + EXPL_POLICIES:
            q = p[p.policy == pl]
            r[f"gain_{pl}"] = float(q.gain.mean())
            r[f"neg_{pl}"] = bool(q.gain.mean() < NEG)
            lo, hi = boot_ci(q.gain.values)
            r[f"gain_{pl}_ci_lo"], r[f"gain_{pl}_ci_hi"] = lo, hi
            # pooled-RMSE sensitivity: per repeat, RMSE over all predictions = sqrt(sum n*rmse^2 / sum n)
            pooled = []
            for rep, qq in q.groupby("repeat"):
                nn = p[(p.policy == "NONE") & (p.repeat == rep)]
                rp = np.sqrt(np.sum(qq.n_test * qq.rmse ** 2) / qq.n_test.sum())
                rn = np.sqrt(np.sum(nn.n_test * nn.rmse ** 2) / nn.n_test.sum())
                pooled.append((rn - rp) / rn)
            r[f"pooled_gain_{pl}"] = float(np.mean(pooled))
        g = p[p.policy == "GATE"]
        r["gate_open_rate"] = float(g.gate_open.astype(bool).mean())
        r["gate_max_open_rate"] = float(p[p.policy == "GATE_MAX"].gate_open.astype(bool).mean())
        tops = p[p.policy == "TOP"].chosen_source.value_counts()
        r["top_modal_source"] = tops.index[0]
        r["top_modal_frac"] = float(tops.iloc[0] / tops.sum())
        r["top_distinct_sources"] = int(len(tops))
        s = scs[scs.target == t]
        real = s[~s.is_permuted]
        fold_best = real.groupby(["repeat", "fold"]).gain_if_used.max()
        r["gain_ORACLE_per_fold"] = float(fold_best.mean())
        per_src = real.groupby("source").gain_if_used.mean()
        r["gain_ORACLE_fixed_source"] = float(per_src.max())
        r["oracle_fixed_source"] = per_src.idxmax()
        r["gain_RANDOM_real"] = float(per_src.mean())
        r["frac_real_sources_negative"] = float((per_src < NEG).mean())
        perm = s[s.is_permuted].groupby("source").gain_if_used.mean()
        r["gain_PERM_mean"] = float(perm.mean())
        r["gain_PERM_max"] = float(perm.max())
        # score-vs-realized-gain across real sources (per fold Spearman, averaged)
        rho = [spearmanr(q.score, q.gain_if_used).correlation for _, q in real.groupby(["repeat", "fold"])]
        r["score_gain_spearman_mean"] = float(np.nanmean(rho))
        r["mean_n_real_sources"] = float(real.groupby(["repeat", "fold"]).size().mean())
        r["top_real_score_mean"] = float(p[p.policy == "TOP"].top_score.mean())
        r["threshold95_mean"] = float(g.threshold95.mean())
        trows.append(r)
    T = pd.DataFrame(trows)
    T.to_csv(f"{RAW}/h8_targets.csv", index=False)
    nT = len(T)

    # graded criteria
    neg = {pl: int(T[f"neg_{pl}"].sum()) for pl in POLICIES[1:] + EXPL_POLICIES}
    mean_gain = {pl: float(T[f"gain_{pl}"].mean()) for pl in POLICIES[1:] + EXPL_POLICIES}
    ci = {pl: boot_ci(T[f"gain_{pl}"].values) for pl in POLICIES[1:] + EXPL_POLICIES}
    c1 = neg["GATE"] <= 1
    c2 = mean_gain["GATE"] > 0
    c3 = (neg["GATE"] / nT < neg["TOP"] / nT) or (neg["GATE"] / nT < neg["PHYS"] / nT)
    met = int(c1) + int(c2) + int(c3)
    complete = (nT == len(TARGET_NAMES)) and not missing
    overall = ("PASS" if met == 3 else "FAIL") if complete else "INCONCLUSIVE"

    # descriptive diagnostics
    real = scs[~scs.is_permuted]
    permd = scs[scs.is_permuted]
    fold_open = pol[pol.policy == "GATE"]
    diag = dict(
        frac_folds_gate_open=float(fold_open.gate_open.astype(bool).mean()),
        frac_real_source_fold_pairs_above_thr=float(real.above_threshold.mean()),
        frac_perm_source_fold_pairs_above_thr=float(permd.above_threshold.mean()),
        mean_gain_real_source_fold_pairs=float(real.gain_if_used.mean()),
        mean_gain_perm_source_fold_pairs=float(permd.gain_if_used.mean()),
        frac_perm_source_fold_pairs_gain_pos=float((permd.gain_if_used > 0).mean()),
        frac_real_source_fold_pairs_negative=float((real.gain_if_used < NEG).mean()),
        top_choice_negative_in_fold=float((pol[pol.policy == "TOP"].gain < NEG).mean()),
        gate_open_choice_negative_in_fold=float((fold_open[fold_open.gate_open.astype(bool)].gain < NEG).mean())
        if fold_open.gate_open.astype(bool).any() else None,
        mean_score_gain_spearman_over_targets=float(T.score_gain_spearman_mean.mean()),
    )
    try:
        diag["auroc_score_detects_negative_fold_pairs_real"] = float(
            roc_auc_score((real.gain_if_used < NEG).astype(int), -real.score))
    except ValueError:
        diag["auroc_score_detects_negative_fold_pairs_real"] = None

    # POST HOC (added after the graded result was seen; EXPLORATORY): v1-style validity of the score, i.e.
    # (target, source) pairs with score and realized gain each averaged over the 15 outer folds.
    st = scs.groupby(["target", "source", "is_permuted", "source_class"]).agg(
        mean_score=("score", "mean"), mean_gain=("gain_if_used", "mean"), sd_gain=("gain_if_used", "std"),
        frac_above_thr=("above_threshold", "mean"), n_folds=("score", "size"),
        n_source=("n_source", "first"), overlap_with_target=("overlap_with_target", "first")).reset_index()
    topc = pol[pol.policy == "TOP"].groupby(["target", "chosen_source"]).size()
    st["n_chosen_as_TOP"] = [int(topc.get((t, s), 0)) for t, s in zip(st.target, st.source)]
    st["is_phys"] = [PHYS.get(t) == s for t, s in zip(st.target, st.source)]
    st.to_csv(f"{RAW}/h8_source_target.csv", index=False)
    # pooled-RMSE gain per (target, source): per repeat sqrt(sum n*rmse^2/sum n) vs NONE, mean over repeats
    nt = pol[pol.policy == "NONE"][["target", "repeat", "fold", "n_test"]]
    sm = scs.merge(nt, on=["target", "repeat", "fold"])
    sm["se_s"], sm["se_n"] = sm.n_test * sm.rmse_if_used ** 2, sm.n_test * sm.rmse_none ** 2
    pr = sm.groupby(["target", "source", "repeat"])[["se_s", "se_n", "n_test"]].sum().reset_index()
    pr["pg"] = 1 - np.sqrt(pr.se_s / pr.n_test) / np.sqrt(pr.se_n / pr.n_test)
    pooled_pair = pr.groupby(["target", "source"]).pg.mean()
    st["pooled_gain"] = [float(pooled_pair.get((t, s_), np.nan)) for t, s_ in zip(st.target, st.source)]
    st.to_csv(f"{RAW}/h8_source_target.csv", index=False)
    stR = st[~st.is_permuted]
    rho_t = [spearmanr(q.mean_score, q.mean_gain).correlation for _, q in stR.groupby("target")]
    try:
        auc_agg = float(roc_auc_score((stR.mean_gain < NEG).astype(int), -stR.mean_score))
    except ValueError:
        auc_agg = None
    posthoc = dict(note="post hoc, added after seeing the graded result; EXPLORATORY",
                   v1style_mean_per_target_spearman=float(np.nanmean(rho_t)),
                   v1style_per_target_spearman=dict(zip(sorted(stR.target.unique()), [float(x) for x in rho_t])),
                   v1style_auroc_negative=auc_agg, v1style_frac_pairs_negative=float((stR.mean_gain < NEG).mean()),
                   v1style_pooled_mean_per_target_spearman=float(np.nanmean(
                       [spearmanr(q.mean_score, q.pooled_gain).correlation for _, q in stR.groupby("target")])),
                   v1style_pooled_auroc_negative=float(roc_auc_score((stR.pooled_gain < NEG).astype(int),
                                                                     -stR.mean_score)),
                   v1style_pooled_frac_pairs_negative=float((stR.pooled_gain < NEG).mean()),
                   v1_reference=dict(mean_per_target_spearman=0.558, auroc_detect_negative=0.820,
                                     frac_negative=0.608))
    diag["posthoc_v1style"] = posthoc

    summary = dict(
        hypothesis="H8", complete=complete, missing_targets=missing, n_targets=nT,
        prereg_criteria=dict(
            c1=dict(text="GATE negative-transfer targets <= 1/11", value=neg["GATE"], passed=bool(c1)),
            c2=dict(text="mean GATE gain over targets > 0", value=mean_gain["GATE"], ci=ci["GATE"], passed=bool(c2)),
            c3=dict(text="GATE neg-transfer rate < TOP or PHYS rate", gate=neg["GATE"], top=neg["TOP"],
                    phys=neg["PHYS"], passed=bool(c3))),
        criteria_met=met, verdict=overall,
        negative_transfer_targets={pl: neg[pl] for pl in neg},
        mean_gain={pl: mean_gain[pl] for pl in mean_gain},
        mean_gain_ci_over_targets={pl: ci[pl] for pl in ci},
        mean_pooled_gain={pl: float(T[f"pooled_gain_{pl}"].mean()) for pl in POLICIES[1:] + EXPL_POLICIES},
        negative_transfer_targets_pooled={pl: int((T[f"pooled_gain_{pl}"] < NEG).sum())
                                          for pl in POLICIES[1:] + EXPL_POLICIES},
        gate_closed_folds=pol[(pol.policy == "GATE") & (~pol.gate_open.astype(bool))][
            ["target", "repeat", "fold", "top_source", "top_score", "threshold95"]].to_dict(orient="records"),
        gate_closed_folds_TOP_gain=pol[(pol.policy == "TOP")].merge(
            pol[(pol.policy == "GATE") & (~pol.gate_open.astype(bool))][["target", "repeat", "fold"]],
            on=["target", "repeat", "fold"]).gain.tolist(),
        oracle_per_fold_mean_gain=float(T.gain_ORACLE_per_fold.mean()),
        oracle_fixed_source_mean_gain=float(T.gain_ORACLE_fixed_source.mean()),
        random_real_source_mean_gain=float(T.gain_RANDOM_real.mean()),
        perm_source_mean_gain=float(T.gain_PERM_mean.mean()),
        diagnostics=diag,
        gain_by_source_class=scs.groupby("source_class").gain_if_used.agg(["mean", "median", "size"]).to_dict(orient="index"),
        frac_fold_pairs_above_thr_by_class=scs.groupby("source_class").above_threshold.mean().to_dict(),
        top_choice_class_counts=pol[pol.policy == "TOP"].chosen_source.map(source_class).value_counts().to_dict(),
        reproducibility_check="results/raw/h8_repro/: s_exp_H2O repeat 0 re-run; scores/thresholds/choices equal to 1e-15, "
                              "realized RMSE jitter (RF tie-breaking after 1e-15 differences from multi-threaded source RF): "
                              "policy 5-fold mean gain |diff| <= 0.0005, single source-fold gain |diff| <= 0.062",
        per_target=T.to_dict(orient="records"),
        phys_mapping=PHYS, perm_bases=PERM_BASES, n_perm=N_PERM,
        runtime_chunks=metas,
        settings=dict(outer="5-fold x 3 repeats (vrr_common.random_folds seed=repeat)",
                      score="|Pearson r(g_s[Tr], y[Tr])|", threshold="95th percentile of 10 permuted-source scores",
                      source_model="RF(100 trees, max_features=0.2, seed 11) as v1",
                      target_model="vrr_common.make_model('RF', seed=repeat), n_jobs=1 in 2-thread pool",
                      negative_transfer="per-target mean outer-fold gain < -1%"),
    )
    json.dump(summary, open(f"{RESULTS}/h8_summary.json", "w"), indent=1, default=str)

    # ledger
    L = []
    for _, r in T.iterrows():
        L.append(dict(hypothesis="H8", test_id="H8_c1_GATE_no_negative_transfer", dataset=r.target, model="RF",
                      metric="mean outer-fold RMSE gain GATE vs NONE (15 folds)", value=round(r.gain_GATE, 4),
                      ci_lo=round(r.gain_GATE_ci_lo, 4), ci_hi=round(r.gain_GATE_ci_hi, 4),
                      threshold="gain >= -1% (no negative transfer); unit of criterion c1",
                      verdict="FAIL" if r.neg_GATE else "PASS", n_units=int(r.n_folds),
                      note=f"n={int(r.n)}; gate open in {r.gate_open_rate:.0%} of folds; TOP modal source "
                           f"{r.top_modal_source} ({r.top_modal_frac:.0%}); CI = bootstrap over folds (not independent)"))
        for pl in ["TOP", "PHYS", "ALL3"]:
            L.append(dict(hypothesis="H8", test_id=f"H8_{pl}_gain", dataset=r.target, model="RF",
                          metric=f"mean outer-fold RMSE gain {pl} vs NONE (15 folds)", value=round(r[f"gain_{pl}"], 4),
                          ci_lo=round(r[f"gain_{pl}_ci_lo"], 4), ci_hi=round(r[f"gain_{pl}_ci_hi"], 4),
                          threshold="descriptive; negative transfer = gain < -1%" +
                                    ("; input to c3" if pl in ("TOP", "PHYS") else ""),
                          verdict="DESCRIPTIVE", n_units=int(r.n_folds),
                          note=("negative transfer" if r[f"neg_{pl}"] else "no negative transfer") +
                               (f"; PHYS source {r.phys_source}" if pl == "PHYS" else "")))
    L.append(dict(hypothesis="H8", test_id="H8_c1", dataset="ALL(11 targets)", model="RF",
                  metric="# targets with GATE negative transfer", value=neg["GATE"], threshold="<= 1 of 11",
                  verdict="PASS" if c1 else "FAIL", n_units=nT,
                  note="; ".join(T[T.neg_GATE].target) or "none"))
    L.append(dict(hypothesis="H8", test_id="H8_c2", dataset="ALL(11 targets)", model="RF",
                  metric="mean over targets of GATE gain", value=round(mean_gain["GATE"], 4),
                  ci_lo=round(ci["GATE"][0], 4), ci_hi=round(ci["GATE"][1], 4), threshold="> 0",
                  verdict="PASS" if c2 else "FAIL", n_units=nT, note="CI = bootstrap over targets"))
    L.append(dict(hypothesis="H8", test_id="H8_c3", dataset="ALL(11 targets)", model="RF",
                  metric="neg-transfer rate GATE vs TOP / PHYS", value=f"{neg['GATE']}/{nT}",
                  threshold="GATE rate < TOP rate OR < PHYS rate", verdict="PASS" if c3 else "FAIL", n_units=nT,
                  note=f"TOP {neg['TOP']}/{nT}, PHYS {neg['PHYS']}/{nT}, ALL3 {neg['ALL3']}/{nT}"))
    L.append(dict(hypothesis="H8", test_id="H8_overall", dataset="ALL(11 targets)", model="RF",
                  metric="all of c1,c2,c3", value=f"{met}/3", threshold="PASS iff c1 and c2 and c3 (PREREG)",
                  verdict=overall, n_units=nT,
                  note=f"mean gain: GATE {mean_gain['GATE']:+.3f}, TOP {mean_gain['TOP']:+.3f}, "
                       f"PHYS {mean_gain['PHYS']:+.3f}, ALL3 {mean_gain['ALL3']:+.3f}"
                       + ("" if complete else f"; missing targets {missing}")))
    L.append(dict(hypothesis="H8", test_id="H8_x_GATE_MAX", dataset="ALL(11 targets)", model="RF",
                  metric="mean GATE_MAX gain; # neg-transfer targets", value=round(mean_gain["GATE_MAX"], 4),
                  ci_lo=round(ci["GATE_MAX"][0], 4), ci_hi=round(ci["GATE_MAX"][1], 4),
                  threshold="exploratory (threshold = max of permuted scores)", verdict="EXPLORATORY", n_units=nT,
                  note=f"neg-transfer targets {neg['GATE_MAX']}/{nT}"))
    L.append(dict(hypothesis="H8", test_id="H8_x_oracle_random_perm", dataset="ALL(11 targets)", model="RF",
                  metric="mean gain: ORACLE per fold / ORACLE fixed source / RANDOM real / PERM mean",
                  value=f"{summary['oracle_per_fold_mean_gain']:.3f}/{summary['oracle_fixed_source_mean_gain']:.3f}/"
                        f"{summary['random_real_source_mean_gain']:.3f}/{summary['perm_source_mean_gain']:.3f}",
                  threshold="descriptive (hindsight bounds; not policies)", verdict="DESCRIPTIVE", n_units=nT,
                  note="ORACLE uses test-fold labels -> upper bound only"))
    L.append(dict(hypothesis="H8", test_id="H8_x_score_vs_gain", dataset="ALL(11 targets)", model="RF",
                  metric="mean per-fold Spearman(score, realized gain) over real sources; AUROC score->negative",
                  value=round(diag["mean_score_gain_spearman_over_targets"], 4),
                  threshold="exploratory", verdict="EXPLORATORY", n_units=nT,
                  note=f"AUROC (fold-source pairs, real) = {diag['auroc_score_detects_negative_fold_pairs_real']:.3f}; "
                       f"declared before running"))
    L.append(dict(hypothesis="H8", test_id="H8_x_posthoc_v1style_score_validity", dataset="ALL(11 targets)",
                  model="RF", metric="(target,source) pairs, 15-fold means: mean per-target Spearman(score, gain)",
                  value=round(posthoc["v1style_mean_per_target_spearman"], 4),
                  threshold="POST HOC exploratory (added after seeing the graded result); v1 reported 0.56 / AUROC 0.82",
                  verdict="EXPLORATORY", n_units=int(len(stR)),
                  note=f"AUROC(mean score -> mean gain < -1%) = {auc_agg:.3f}; frac pairs negative = "
                       f"{posthoc['v1style_frac_pairs_negative']:.3f}; pooled-gain version: Spearman "
                       f"{posthoc['v1style_pooled_mean_per_target_spearman']:.3f}, AUROC "
                       f"{posthoc['v1style_pooled_auroc_negative']:.3f}, frac negative "
                       f"{posthoc['v1style_pooled_frac_pairs_negative']:.3f}; score averaged over folds uses all "
                       f"target labels across folds -> not a nested quantity"))
    L.append(dict(hypothesis="H8", test_id="H8_x_pooled_gain", dataset="ALL(11 targets)", model="RF",
                  metric="mean pooled-RMSE gain GATE / TOP / PHYS / ALL3",
                  value="/".join(f"{summary['mean_pooled_gain'][pl]:.3f}" for pl in ["GATE", "TOP", "PHYS", "ALL3"]),
                  threshold="sensitivity metric (not graded)", verdict="DESCRIPTIVE", n_units=nT,
                  note="neg-transfer targets under pooled metric: " + ", ".join(
                      f"{pl} {summary['negative_transfer_targets_pooled'][pl]}/{nT}" for pl in
                      ["GATE", "TOP", "PHYS", "ALL3"])))
    ledger_write(os.path.join(LEDGER, "h8.csv"), L)
    print(json.dumps({k: summary[k] for k in ["verdict", "criteria_met", "negative_transfer_targets", "mean_gain",
                                              "oracle_per_fold_mean_gain", "random_real_source_mean_gain",
                                              "perm_source_mean_gain", "diagnostics"]}, indent=1, default=str))
    print(T[["target", "n", "gain_NONE" if "gain_NONE" in T else "rmse_none_mean", "gain_PHYS", "gain_TOP",
             "gain_GATE", "gain_ALL3", "gain_GATE_MAX", "gate_open_rate", "top_modal_source",
             "gain_ORACLE_per_fold", "gain_RANDOM_real", "gain_PERM_max"]].round(3).to_string())


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "pool":
        write_pool()
    elif cmd == "run":
        for rep in sys.argv[3:]:
            run_chunk(sys.argv[2], int(rep))
    elif cmd == "pending":
        # run unfinished (target, repeat) chunks in order; start a new chunk only while elapsed < budget seconds
        budget, t_start = float(sys.argv[2]), time.time()
        todo = [(t, r) for t in TARGET_NAMES for r in range(REPEATS)
                if not os.path.exists(f"{PARTS}/h8_{t}_r{r}_meta.json")]
        print("pending chunks:", len(todo), flush=True)
        for t, r in todo:
            if time.time() - t_start > budget:
                break
            run_chunk(t, r)
    elif cmd == "aggregate":
        aggregate()
    else:
        raise SystemExit(__doc__)
