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

FIX ROUND (after the adversarial verification, process/h8_verify.md; PREREG thresholds unchanged):
  * issue 1 (major): the strict new-polymer setting was violated because key-based exclusion used isomeric SMILES,
    so cis/trans-annotated twins of a test polymer (e.g. PTMSP) stayed in the source training set. Now: exclusion by
    polymer identity (non-isomeric canonical SMILES) OR identical feature vector (excluded_keys), and target rows
    merged by identity after the v1 sampling (d_exp_H2 51->50, d_exp_CO2 151->150). `checkfix` proves that the 4
    twin-free targets are input-identical (v0 chunks kept); the 7 affected targets were re-run. Pre-fix outputs are
    archived in results/raw/h8_v0_keyexcl/.
  * issue 2: `runseed` adds outer repeats 3-4 (descriptive seed sensitivity; grading stays on repeats 0-2).
  * issues 3-7: failure_analysis reworded, deviations listed, post hoc EXPLORATORY Bonferroni gate, PHYS under the v1
    rule, target overlap / leave-one-target-out, s_exp_H2O bimodality caveat (fix_round_extras).

Usage (from v2/scripts):
  python h8_gate.py pool                  # pool table, sub40 keys, PHYS check
  python h8_gate.py checkfix              # fix round: key vs identity exclusion, per target x repeat x source x fold
  python h8_gate.py run <target> <repeat> [<repeat> ...]  # chunks -> results/raw/h8_parts/
  python h8_gate.py runseed <target> 3 4  # fix round: extra repeats -> results/raw/h8_parts_seedsens/
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
PARTS_SEED = os.path.join(RAW, "h8_parts_seedsens")   # FIX ROUND: extra outer repeats 3-4 (descriptive only)
V0 = os.path.join(RAW, "h8_v0_keyexcl")               # FIX ROUND: archived pre-fix (key-exclusion) outputs
os.makedirs(PARTS, exist_ok=True)
os.makedirs(PARTS_SEED, exist_ok=True)
SEED_REPEATS = [3, 4]

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


def _ident_of(key):
    """FIX ROUND: polymer identity = NON-isomeric canonical SMILES of the (isomeric) key. cis/trans-annotated
    and unannotated SMILES of the same polymer (e.g. PTMSP '*/C(C)=C(/*)[Si](C)(C)C' vs '*C(C)=C(*)[Si](C)(C)C')
    get different keys but the same identity (and identical feature vectors)."""
    return Chem.MolToSmiles(Chem.MolFromSmiles(key), isomericSmiles=False)


def _merge_identity(ser):
    """FIX ROUND: target de-duplication by polymer identity (mean of y; representative = first key in index order,
    groupby(sort=False) keeps the original order, so twin-free targets are returned unchanged)."""
    df = pd.DataFrame({"key": list(ser.index), "id": [_ident_of(k) for k in ser.index], "y": ser.values})
    g = df.groupby("id", sort=False).agg(key=("key", "first"), y=("y", "mean"), n=("y", "size"),
                                         members=("key", lambda x: list(x)), ys=("y", lambda x: list(x)))
    merged = [dict(identity=i, kept_key=r.key, merged_keys=r.members, y_values=r.ys, y_mean=r.y)
              for i, r in g[g.n > 1].iterrows()]
    return pd.Series(g.y.values, index=list(g.key.values)), merged


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
    # FIX ROUND: merge identity twins inside each target AFTER the v1 sampling (so the sub40 draws are unchanged).
    for t in list(TARGETS):
        ser, parent = TARGETS[t]
        mser, merged = _merge_identity(ser)
        TARGETS[t] = (mser, parent)
        DEDUP[t] = dict(n_before=len(ser), n_after=len(mser), merged=merged)
        fb = pd.Series([FEAT[k].tobytes() for k in mser.index])
        assert not fb.duplicated().any(), f"feature-identical rows remain inside target {t}"
    return TASKS, TARGETS, FEAT


_LOADED = None
DEDUP = {}      # FIX ROUND: per-target identity de-duplication record (filled by _build)
_IDMAPS = None  # FIX ROUND: key -> identity, key -> feature bytes


def load_all():
    """Built in memory once per process (no on-disk cache: nothing is written into the data root)."""
    global _LOADED
    if _LOADED is None:
        _LOADED = _build()
    return _LOADED


def id_maps():
    """FIX ROUND: (IDENT, FBYTES) for every featurised key."""
    global _IDMAPS
    if _IDMAPS is None:
        _, _, FEAT = load_all()
        _IDMAPS = ({k: _ident_of(k) for k in FEAT}, {k: FEAT[k].tobytes() for k in FEAT})
    return _IDMAPS


def excluded_keys(S_index, test_keys, mode="identity"):
    """Source rows removed when the polymers `test_keys` are held out.
    mode 'key' (v0, pre-fix): exact key match only.
    mode 'identity' (FIX ROUND): same non-isomeric identity OR identical feature vector (the union is conservative:
    it also removes the 1 feature-identical but structurally different polyimide isomer found in X_CED)."""
    tk = set(test_keys)
    if mode == "key":
        return frozenset(k for k in S_index if k in tk)
    IDENT, FB = id_maps()
    ti, tf = {IDENT[k] for k in tk}, {FB[k] for k in tk}
    return frozenset(k for k in S_index if k in tk or IDENT[k] in ti or FB[k] in tf)


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


def crossfit_source(S, Xof, tkeys, fold_list, mode="identity"):
    """g(i) for every target polymer from a source model fitted without the polymers of i's outer fold.
    FIX ROUND: 'without the polymers' now means by polymer identity / feature identity (see excluded_keys), not by
    exact key. Models are cached by the excluded source rows. Returns (g, n_fits, n_extra) where n_extra = number of
    source rows (summed over folds) removed by the identity rule but NOT by the old key rule (= escaped twins)."""
    cache, g, nfit, n_extra = {}, np.zeros(len(tkeys)), 0, 0
    for _, te in fold_list:
        tk = [tkeys[i] for i in te]
        excl = excluded_keys(S.index, tk, mode)
        n_extra += len(excl) - len(excluded_keys(S.index, tk, "key"))
        if excl not in cache:
            sk = [k for k in S.index if k not in excl]
            cache[excl] = src_rf().fit(Xof(sk), S.loc[sk].values)
            nfit += 1
        g[te] = cache[excl].predict(Xof(tk))
    return g, nfit, n_extra


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


def run_chunk(tname, rep, parts=None):
    """parts: output directory (default PARTS = graded repeats 0-2; PARTS_SEED for the fix-round seed sensitivity)."""
    parts = parts or PARTS
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
    G, nfits, NX = {}, 0, {}
    for s, S in allsrc.items():
        G[s], nf, NX[s] = crossfit_source(S, Xof, tkeys, fl)
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
                                overlap_with_target=len(set(tkeys) & set(allsrc[s].index)),
                                n_twin_rows_excluded=NX[s]))
    pd.DataFrame(pol_rows).to_csv(f"{parts}/h8_{tname}_r{rep}_policy.csv", index=False)
    pd.DataFrame(sc_rows).to_csv(f"{parts}/h8_{tname}_r{rep}_scores.csv", index=False)
    meta = dict(target=tname, repeat=rep, n=len(y), n_real=len(reals), n_perm=len(perms), source_fits=nfits,
                twin_rows_excluded_total=int(sum(NX.values())), exclusion="identity (fix round)",
                sec_source=round(t_src, 1), sec_total=round(time.time() - t0, 1))
    json.dump(meta, open(f"{parts}/h8_{tname}_r{rep}_meta.json", "w"))
    print(json.dumps(meta), flush=True)


# ------------------------------------------------------------------ fix-round equivalence check
def check_fix():
    """FIX ROUND: for every target x graded repeat x source x outer fold, compare the source rows excluded by the
    old key rule and by the identity rule, and record target de-duplication. A target is 'unaffected' iff no row
    is merged and no exclusion set differs -> the v0 computation for it is input-identical to the fixed code."""
    TASKS, TARGETS, FEAT = load_all()
    IDENT, _ = id_maps()
    rows, twins = [], []
    for t in TARGET_NAMES:
        ser, parent = TARGETS[t]
        tkeys = list(ser.index)
        allsrc = {**{s: TASKS[s] for s in real_pool(TASKS, t, parent)}, **perm_sources(TASKS)}
        for rep in range(REPEATS):
            fl = random_folds(len(tkeys), K, seed=rep)
            ndiff, nextra, npairs = 0, 0, 0
            for s, S in allsrc.items():
                for f, (_, te) in enumerate(fl):
                    tk = [tkeys[i] for i in te]
                    a, b = excluded_keys(S.index, tk, "key"), excluded_keys(S.index, tk, "identity")
                    npairs += 1
                    if a != b:
                        ndiff += 1
                        nextra += len(b) - len(a)
                        if rep == 0:
                            for k in sorted(b - a):
                                tw = [x for x in tk if IDENT[x] == IDENT[k] or FEAT[x].tobytes() == FEAT[k].tobytes()]
                                twins.append(dict(target=t, source=s, fold_rep0=f, source_key=k, target_key="|".join(tw),
                                                  kind="stereo" if any(IDENT[x] == IDENT[k] for x in tw) else
                                                  "feature_only", y_source=float(S[k]),
                                                  y_target=float(np.mean([ser[x] for x in tw]))))
            d = DEDUP[t]
            rows.append(dict(target=t, repeat=rep, n_before=d["n_before"], n_after=d["n_after"],
                             n_merged_groups=len(d["merged"]), n_source_fold_pairs=npairs,
                             n_pairs_exclusion_differs=ndiff, n_extra_rows_excluded=nextra,
                             unaffected=(ndiff == 0 and d["n_before"] == d["n_after"])))
    E = pd.DataFrame(rows)
    E.to_csv(f"{RAW}/h8_fix_equivalence.csv", index=False)
    pd.DataFrame(twins).to_csv(f"{RAW}/h8_fix_twins_rep0.csv", index=False)
    json.dump({t: DEDUP[t] for t in TARGET_NAMES}, open(f"{RAW}/h8_fix_dedup.json", "w"), indent=1, default=str)
    print(E.to_string())
    print("affected targets:", sorted(E[~E.unaffected].target.unique()))
    return E


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


# ------------------------------------------------------------------ fix-round extras (verifier issues 1-7)
def _phys_v1_prior(src, tgt_parent):
    """v1 poc_transfer.py physics_prior, copied verbatim (X_water_* sources do not exist in this pool)."""
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


def fix_round_extras(pol, scs, T, st, TARGETS):
    """Returns (extras dict for the summary, per-target note fragments, extra ledger rows).
    Rules for the seed-sensitivity flags were written down in process/h8_log.md (Fix round) BEFORE repeats 3-4 ran."""
    from scipy.stats import norm
    out, notes, L = {}, {t: [] for t in T.target}, []
    nT = len(T)
    Ti = T.set_index("target")

    # ---- (issue 1) before / after the identity-exclusion fix
    eq = pd.read_csv(f"{RAW}/h8_fix_equivalence.csv") if os.path.exists(f"{RAW}/h8_fix_equivalence.csv") else None
    if os.path.exists(f"{V0}/h8_targets.csv"):
        T0 = pd.read_csv(f"{V0}/h8_targets.csv").set_index("target")
        pol0 = pd.read_csv(f"{V0}/h8_policy.csv")
        S0 = json.load(open(f"{V0}/h8_summary_v0.json"))
        # n_twin_rows_excluded is a per-(chunk, source) total repeated on each of the 5 fold rows -> take it once
        twin_rows = scs.groupby(["target", "repeat", "source"]).n_twin_rows_excluded.first() \
            .groupby(["target", "repeat"]).sum().groupby("target").mean()
        rows = []
        for t in T.target:
            r, r0 = Ti.loc[t], T0.loc[t]
            d = dict(target=t, affected=bool(eq is not None and not eq[eq.target == t].unaffected.all()),
                     rerun=bool(eq is not None and not eq[eq.target == t].unaffected.all()),
                     n_v0=int(r0.n), n_fixed=int(r.n), twin_rows_excluded_per_repeat=float(twin_rows.get(t, 0.0)))
            for pl in ["GATE", "TOP", "PHYS", "ALL3", "GATE_MAX"]:
                d[f"gain_{pl}_v0"], d[f"gain_{pl}_fixed"] = float(r0[f"gain_{pl}"]), float(r[f"gain_{pl}"])
                d[f"delta_{pl}"] = float(r[f"gain_{pl}"] - r0[f"gain_{pl}"])
            d["neg_GATE_v0"], d["neg_GATE_fixed"] = bool(r0.neg_GATE), bool(r.neg_GATE)
            d["rmse_none_v0"], d["rmse_none_fixed"] = float(r0.rmse_none_mean), float(r.rmse_none_mean)
            if int(r0.n) == int(r.n):
                a = pol0[(pol0.target == t) & (pol0.policy == "TOP")].set_index(["repeat", "fold"]).chosen_source
                b = pol[(pol.target == t) & (pol.policy == "TOP")].set_index(["repeat", "fold"]).chosen_source
                d["top_same_choice_frac"] = float((a.reindex(b.index) == b).mean())
            else:
                d["top_same_choice_frac"] = np.nan   # n changed -> different outer partition, not fold-aligned
            rows.append(d)
        BA = pd.DataFrame(rows)
        BA.to_csv(f"{RAW}/h8_fix_before_after.csv", index=False)
        out["fix_before_after"] = dict(
            per_target_csv="results/raw/h8_fix_before_after.csv",
            c1_v0=S0["prereg_criteria"]["c1"]["value"], c2_v0=S0["prereg_criteria"]["c2"]["value"],
            c3_v0=dict(gate=S0["prereg_criteria"]["c3"]["gate"], top=S0["prereg_criteria"]["c3"]["top"],
                       phys=S0["prereg_criteria"]["c3"]["phys"]),
            verdict_v0=S0["verdict"], criteria_met_v0=S0["criteria_met"],
            neg_targets_v0=sorted(BA[BA.neg_GATE_v0].target), neg_targets_fixed=sorted(BA[BA.neg_GATE_fixed].target),
            targets_rerun=sorted(BA[BA.rerun].target), targets_kept_v0_input_identical=sorted(BA[~BA.rerun].target))
        for _, d in BA.iterrows():
            if d.rerun:
                notes[d.target].append(
                    f"FIX ROUND: re-run with identity exclusion ({d.twin_rows_excluded_per_repeat:.0f} escaped twin "
                    f"source rows/repeat now excluded); v0 GATE {d.gain_GATE_v0:+.4f} -> {d.gain_GATE_fixed:+.4f}"
                    + (f"; n {d.n_v0}->{d.n_fixed} (PTMSP stereo twin rows merged, new partition)"
                       if d.n_v0 != d.n_fixed else "")
                    + ("; c1 verdict changed" if d.neg_GATE_v0 != d.neg_GATE_fixed else ""))
            else:
                notes[d.target].append("FIX ROUND: no twins -> v0 chunks kept (input-identical, h8_fix_equivalence.csv)")

    # ---- (issue 2) seed sensitivity: extra outer repeats 3-4 (descriptive; grading stays on repeats 0-2)
    sp = [f"{PARTS_SEED}/h8_{t}_r{r}_policy.csv" for t in TARGET_NAMES for r in SEED_REPEATS]
    sp = [p for p in sp if os.path.exists(p)]
    if sp:
        ps = pd.concat([pd.read_csv(p) for p in sp], ignore_index=True)
        allp = pd.concat([pol.assign(repeat_set="graded_r0-2"), ps.assign(repeat_set="seedsens_r3-4")],
                         ignore_index=True)
        pls = POLICIES[1:] + EXPL_POLICIES
        PR = allp[allp.policy.isin(pls)].groupby(["target", "repeat", "repeat_set", "policy"]).agg(
            gain=("gain", "mean"), n_folds=("gain", "size"),
            gate_open_rate=("gate_open", lambda x: float(pd.Series(x).fillna(True).astype(bool).mean())),
            top_modal_source=("chosen_source", lambda x: pd.Series(x).fillna("").value_counts().index[0])).reset_index()
        PR.to_csv(f"{RAW}/h8_seed_sensitivity.csv", index=False)
        done_t = ps.groupby("target").repeat.nunique()
        seed_complete = all(done_t.get(t, 0) == len(SEED_REPEATS) for t in TARGET_NAMES)
        rows = []
        for t in TARGET_NAMES:
            q = allp[allp.target == t]
            d = dict(target=t)
            for pl in pls:
                qq = q[q.policy == pl]
                d[f"{pl}_r0-2"] = float(qq[qq.repeat_set == "graded_r0-2"].gain.mean())
                d[f"{pl}_r3-4"] = float(qq[qq.repeat_set == "seedsens_r3-4"].gain.mean()) \
                    if (qq.repeat_set == "seedsens_r3-4").any() else np.nan
                d[f"{pl}_r0-4"] = float(qq.gain.mean())
            per = PR[(PR.target == t) & (PR.policy == "GATE")].sort_values("repeat")
            d["GATE_per_repeat"] = "/".join(f"{g:+.3f}" for g in per.gain)
            d["n_repeats"] = int(len(per))
            d["n_repeats_below_bar"] = int((per.gain < NEG).sum())
            g02, g34, g04 = d["GATE_r0-2"], d["GATE_r3-4"], d["GATE_r0-4"]
            # rule fixed before repeats 3-4 ran (log, Fix round): seed-sensitive iff the c1 status of the graded
            # mean differs from that of the r3-4 mean OR of the r0-4 mean; robust negative iff all three < -1%.
            d["seed_sensitive"] = bool(np.isfinite(g34) and (((g02 < NEG) != (g34 < NEG)) or ((g02 < NEG) != (g04 < NEG))))
            d["robust_negative"] = bool(np.isfinite(g34) and g02 < NEG and g34 < NEG and g04 < NEG)
            rows.append(d)
        SS = pd.DataFrame(rows)
        SS.to_csv(f"{RAW}/h8_seed_sensitivity_targets.csv", index=False)
        cnt = {}
        for rs in ["r0-2", "r3-4", "r0-4"]:
            negs = {pl: int((SS[f"{pl}_{rs}"] < NEG).sum()) for pl in ["GATE", "TOP", "PHYS", "ALL3", "GATE_MAX"]}
            cnt[rs] = dict(neg=negs, mean_GATE=float(SS[f"GATE_{rs}"].mean()),
                           neg_targets_GATE=sorted(SS[SS[f"GATE_{rs}"] < NEG].target),
                           c1=negs["GATE"] <= 1, c2=float(SS[f"GATE_{rs}"].mean()) > 0,
                           c3=(negs["GATE"] < negs["TOP"]) or (negs["GATE"] < negs["PHYS"]))
        out["seed_sensitivity"] = dict(
            status="DESCRIPTIVE (fix round; PREREG grading stays on repeats 0-2)", complete=seed_complete,
            extra_repeats=SEED_REPEATS, per_repeat_csv="results/raw/h8_seed_sensitivity.csv",
            per_target_csv="results/raw/h8_seed_sensitivity_targets.csv", by_repeat_set=cnt,
            seed_sensitive_targets=sorted(SS[SS.seed_sensitive].target),
            robust_negative_targets=sorted(SS[SS.robust_negative].target),
            rule="seed-sensitive iff c1 status (gain < -1%) of the graded r0-2 mean differs from the r3-4 or r0-4 "
                 "mean; robust negative iff r0-2, r3-4 and r0-4 means are all < -1% (rule fixed before running)")
        for _, d in SS.iterrows():
            notes[d.target].append(
                f"seed sensitivity (descriptive): GATE per repeat r0..r{d.n_repeats - 1} = {d.GATE_per_repeat}; "
                f"r3-4 mean {d['GATE_r3-4']:+.4f}, r0-4 mean {d['GATE_r0-4']:+.4f}; "
                + ("SEED-SENSITIVE verdict" if d.seed_sensitive else
                   ("robust negative transfer" if d.robust_negative else "verdict stable across repeat sets")))
        L.append(dict(hypothesis="H8", test_id="H8_x_seed_sensitivity", dataset="ALL(11 targets)", model="RF",
                      metric="# GATE neg-transfer targets: graded r0-2 / extra r3-4 / all r0-4",
                      value=f"{cnt['r0-2']['neg']['GATE']}/{cnt['r3-4']['neg']['GATE']}/{cnt['r0-4']['neg']['GATE']}",
                      threshold="descriptive (not graded; PREREG = 3 repeats)", verdict="DESCRIPTIVE", n_units=nT,
                      note=f"seed-sensitive: {', '.join(out['seed_sensitivity']['seed_sensitive_targets']) or 'none'}; "
                           f"robust negative: {', '.join(out['seed_sensitivity']['robust_negative_targets']) or 'none'}; "
                           f"mean GATE gain r0-2/r3-4/r0-4 = {cnt['r0-2']['mean_GATE']:+.4f}/"
                           f"{cnt['r3-4']['mean_GATE']:+.4f}/{cnt['r0-4']['mean_GATE']:+.4f}; c1 under r0-4: "
                           f"{'PASS' if cnt['r0-4']['c1'] else 'FAIL'}" + ("" if seed_complete else "; INCOMPLETE")))

    # ---- (issue 3) POST HOC: family-wise (Bonferroni Fisher-z) gate, verifier-suggested; EXPLORATORY
    O = []
    nt = pol[pol.policy == "NONE"].set_index(["target", "repeat", "fold"]).n_train
    for (t, r, f), q in scs.groupby(["target", "repeat", "fold"]):
        rq = q[~q.is_permuted]
        m, ntr = len(rq), int(nt.loc[(t, r, f)])
        top = rq.loc[rq.score.idxmax()]
        thr_b = float(np.tanh(norm.ppf(1 - 0.05 / (2 * m)) / np.sqrt(ntr - 3)))
        O.append(dict(target=t, repeat=r, fold=f, m=m, n_train=ntr, top_source=top.source, top_score=top.score,
                      thr_bonf=thr_b, open=bool(top.score > thr_b), top_gain=top.gain_if_used,
                      gain_BONF=top.gain_if_used if top.score > thr_b else 0.0))
    O = pd.DataFrame(O)
    O.to_csv(f"{RAW}/h8_posthoc_bonferroni_gate.csv", index=False)
    gb = O.groupby("target").agg(gain=("gain_BONF", "mean"), open_rate=("open", "mean"),
                                 thr_mean=("thr_bonf", "mean"), top_mean=("top_score", "mean"))
    real = scs[~scs.is_permuted]
    try:
        auc_fold = float(roc_auc_score((real.gain_if_used < NEG).astype(int), -real.score))
    except ValueError:
        auc_fold = None
    out["posthoc_bonferroni_gate"] = dict(
        status="POST HOC (fix round, verifier-suggested); EXPLORATORY",
        rule="open iff top real |r| > tanh(z_{1-0.05/(2m)}/sqrt(n_train-3)), m = # real sources in the fold",
        open_rate=float(O.open.mean()), neg_targets=int((gb.gain < NEG).sum()),
        neg_target_names=sorted(gb[gb.gain < NEG].index), mean_gain=float(gb.gain.mean()),
        per_target={t: dict(gain=float(v.gain), open_rate=float(v.open_rate), thr_mean=float(v.thr_mean),
                            top_score_mean=float(v.top_mean)) for t, v in gb.iterrows()},
        thr_range=[float(gb.thr_mean.min()), float(gb.thr_mean.max())],
        top_score_range=[float(gb.top_mean.min()), float(gb.top_mean.max())],
        auroc_score_detects_negative_fold_pairs=auc_fold)
    L.append(dict(hypothesis="H8", test_id="H8_x_posthoc_bonferroni_gate", dataset="ALL(11 targets)", model="RF",
                  metric="family-wise Bonferroni Fisher-z gate: mean gain; # neg-transfer targets",
                  value=round(out["posthoc_bonferroni_gate"]["mean_gain"], 4),
                  threshold="POST HOC exploratory (fix round, verifier-suggested; not graded)", verdict="EXPLORATORY",
                  n_units=nT, note=f"gate open in {O.open.mean():.1%} of folds; neg-transfer targets "
                                   f"{int((gb.gain < NEG).sum())}/{nT} ({', '.join(sorted(gb[gb.gain < NEG].index))}); "
                                   + ("a family-wise threshold does not stop negative transfer -> multiplicity is not "
                                      "the binding problem" if int((gb.gain < NEG).sum()) > 1 else
                                      "a family-wise threshold would meet the c1 bar post hoc")))

    # ---- (issue 4) POST HOC: PHYS comparator under v1's mechanical physics_prior rule (tie-break bounds)
    stR = st[~st.is_permuted]
    pr_rows = []
    for t, q in stR.groupby("target"):
        par = t.replace("_sub40", "")
        pr = q.source.map(lambda s: _phys_v1_prior(s, par))
        best = q[pr == pr.max()]
        pr_rows.append(dict(target=t, v1_prior_max=float(pr.max()), tie_set="|".join(best.source),
                            n_tie=int(len(best)), best_case_gain=float(best.mean_gain.max()),
                            worst_case_gain=float(best.mean_gain.min()),
                            neg_best_case=bool(best.mean_gain.max() < NEG), neg_worst_case=bool(best.mean_gain.min() < NEG),
                            v2_phys=PHYS[t], v2_phys_gain=float(Ti.loc[t, "gain_PHYS"])))
    PV = pd.DataFrame(pr_rows)
    PV.to_csv(f"{RAW}/h8_posthoc_phys_v1rule.csv", index=False)
    negG, negTOP, negPHYS = int(T.neg_GATE.sum()), int(T.neg_TOP.sum()), int(T.neg_PHYS.sum())
    nb, nw = int(PV.neg_best_case.sum()), int(PV.neg_worst_case.sum())
    out["posthoc_phys_v1rule"] = dict(
        status="POST HOC (fix round, verifier-suggested); EXPLORATORY", csv="results/raw/h8_posthoc_phys_v1rule.csv",
        neg_targets_best_case_tiebreak=nb, neg_targets_worst_case_tiebreak=nw,
        c3_with_v1rule_best_case=bool(negG < negTOP or negG < nb),
        c3_with_v1rule_worst_case=bool(negG < negTOP or negG < nw),
        note="gain per (target, source) = 15-fold mean of the realized gain of that source (h8_source_target.csv)")

    # ---- (issue 5) target overlap and leave-one-target-out for c2
    _, TG, _ = load_all()
    ks = {t: set(TG[t][0].index) for t in TARGET_NAMES}
    IDENT, _ = id_maps()
    ki = {t: {IDENT[k] for k in ks[t]} for t in TARGET_NAMES}
    ov = []
    for i, a in enumerate(TARGET_NAMES):
        for b in TARGET_NAMES[i + 1:]:
            o = len(ki[a] & ki[b])
            ov.append(dict(target_a=a, target_b=b, n_a=len(ki[a]), n_b=len(ki[b]), overlap=o,
                           frac_of_smaller=o / min(len(ki[a]), len(ki[b]))))
    OV = pd.DataFrame(ov)
    OV.to_csv(f"{RAW}/h8_target_overlap.csv", index=False)
    gG = Ti.gain_GATE
    loto = {t: float(gG.drop(t).mean()) for t in gG.index}
    out["c2_dependence"] = dict(
        overlap_csv="results/raw/h8_target_overlap.csv",
        pairs_overlap_ge_80pct_of_smaller=[f"{r.target_a}~{r.target_b} ({r.overlap}/{min(r.n_a, r.n_b)})"
                                           for _, r in OV[OV.frac_of_smaller >= 0.8].iterrows()],
        leave_one_target_out_mean_GATE=loto, loto_min=min(loto.values()), loto_max=max(loto.values()),
        ci_bootstrap_seeds={s: boot_ci(gG.values, seed=s) for s in [0, 1, 7, 123]},
        note="targets share polymers (and P = S*D), so the bootstrap over 11 targets treats dependent units as "
             "independent -> the CI is optimistic (too narrow)")

    # ---- (issue 7) s_exp_H2O bimodality caveat (descriptive)
    y = TG["s_exp_H2O"][0].values.astype(float)
    med, mad = np.median(y), np.median(np.abs(y - np.median(y)))
    rz = 0.6745 * (y - med) / mad
    ys = np.sort(y)
    gi = int(np.argmax(np.diff(ys)))
    out["caveat_s_exp_H2O"] = dict(
        n=int(len(y)), sorted_y=[round(float(v), 3) for v in ys], largest_gap_between=[float(ys[gi]), float(ys[gi + 1])],
        n_low_cluster=int(gi + 1), max_abs_robust_z=float(np.abs(rz).max()),
        note="bimodal target: a small low cluster far below the rest (possible unit/curation artifact); many sources "
             "reach |r| > 0.9 by separating it, and the large s_exp_H2O gain rests on that separation")
    notes["s_exp_H2O"].append(
        f"CAVEAT: bimodal y ({gi + 1} polymers at {ys[0]:.2f}..{ys[gi]:.2f} vs {len(y) - gi - 1} at "
        f"{ys[gi + 1]:.2f}..{ys[-1]:.2f}; max robust |z| {np.abs(rz).max():.1f}); the gain rests on separating that cluster")
    return out, notes, L


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
    # FIX ROUND: kept v0 chunks (twin-free targets) have no twin column; checkfix proved 0 extra rows for them
    if "n_twin_rows_excluded" not in scs:
        scs["n_twin_rows_excluded"] = np.nan
    scs["n_twin_rows_excluded"] = scs["n_twin_rows_excluded"].fillna(0).astype(int)
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

    # FIX ROUND extras (before/after, seed sensitivity, post hoc family-wise gate, PHYS v1 rule, overlap, caveat)
    fx, fnotes, L_fix = fix_round_extras(pol, scs, T, st, TARGETS)
    bonf = fx["posthoc_bonferroni_gate"]
    mult_binding = bonf["neg_targets"] <= 1 or neg["GATE_MAX"] <= 1
    failure_analysis = (
        f"The pre-registered gate is open in {diag['frac_folds_gate_open']:.1%} of outer folds, so GATE ~= TOP. "
        + (f"Multiplicity is NOT the binding problem: a post hoc family-wise Bonferroni Fisher-z gate is still open in "
           if not mult_binding else
           f"CAUTION: a stricter (family-wise) gate would have met c1 post hoc, so multiplicity may matter: the "
           f"Bonferroni Fisher-z gate is open in ")
        + f"{bonf['open_rate']:.1%} of folds and leaves {bonf['neg_targets']}/{nT} targets with negative transfer "
        f"(mean gain {bonf['mean_gain']:+.3f}); GATE_MAX (max of permuted scores) leaves {neg['GATE_MAX']}/{nT}. Real "
        f"sources genuinely exceed any null (mean top |r| per target {bonf['top_score_range'][0]:.2f}-"
        f"{bonf['top_score_range'][1]:.2f} vs Bonferroni threshold {bonf['thr_range'][0]:.2f}-"
        f"{bonf['thr_range'][1]:.2f}). The binding problem is that the in-fold correlation |r(g_s, y)| at n = 25-150 "
        f"does not predict the out-of-fold gain over the RF baseline (fold-level AUROC of the score for negative "
        f"transfer = {diag['auroc_score_detects_negative_fold_pairs_real']:.2f}; mean per-fold Spearman(score, gain) "
        f"= {diag['mean_score_gain_spearman_over_targets']:.2f}). Correlation with the target is not the same as "
        f"usefulness on top of a model that already sees the structure.")
    deviations = [
        "Outer partition reused for inner cross-fitting (v1 scheme): g_s for an outer-training polymer of fold k comes "
        "from a source model that excluded fold k only, so it may have seen the outer-TEST polymers' SOURCE labels "
        "(never target labels). Selection uses y[Tr] only.",
        "Permutation bases: X_bandgap_chain (v1 null) replaced by X_ionization_E for runtime (decided before any "
        "result); bases p_exp_O2, s_exp_CH4, d_sim_CO2, X_CED, X_ionization_E x 2 seeds = 10 permuted sources.",
        "PHYS mapping was fixed in process/h8_log.md and this docstring before any H8 model ran, but it was not "
        "committed to git with PREREG; c3 depends on it (see posthoc_phys_v1rule).",
        "FIX ROUND: source exclusion changed from exact isomeric-SMILES key to polymer identity (non-isomeric SMILES) "
        "OR identical feature vector; target rows merged by identity (d_exp_H2 51->50, d_exp_CO2 151->150, PTMSP). "
        "7 targets re-run; 4 twin-free targets keep their v0 chunks (input-identical, results/raw/h8_fix_equivalence.csv).",
        "FIX ROUND: d_exp_H2 and d_exp_CO2 have a new outer partition (random_folds depends on n), so their before/"
        "after difference mixes the leak fix with a partition change.",
        "FIX ROUND: extra outer repeats 3-4 for all 11 targets as DESCRIPTIVE seed sensitivity (grading stays on the "
        "pre-registered 3 repeats).",
        "FIX ROUND: post hoc EXPLORATORY analyses added after verification (Bonferroni gate, PHYS under v1 rule, "
        "target overlap / leave-one-target-out, s_exp_H2O bimodality); none is graded.",
    ]

    summary = dict(
        hypothesis="H8", complete=complete, missing_targets=missing, n_targets=nT,
        prereg_criteria=dict(
            c1=dict(text="GATE negative-transfer targets <= 1/11", value=neg["GATE"], passed=bool(c1)),
            c2=dict(text="mean GATE gain over targets > 0", value=mean_gain["GATE"], ci=ci["GATE"], passed=bool(c2)),
            c3=dict(text="GATE neg-transfer rate < TOP or PHYS rate", gate=neg["GATE"], top=neg["TOP"],
                    phys=neg["PHYS"], passed=bool(c3))),
        criteria_met=met, verdict=overall,
        failure_analysis=failure_analysis,
        deviations=deviations,
        fix_round=dict(
            exclusion_rule="identity: source rows with the same non-isomeric canonical SMILES OR identical feature "
                           "vector as any test-fold polymer are removed; target rows merged by identity (mean y)",
            issue_responses={
                "1_stereo_twin_leak (major)": "fixed in code; 7 affected targets re-run (21 chunks); see fix_before_after",
                "2_seed_sensitivity (minor)": "extra repeats 3-4 for all targets (descriptive) + ledger notes",
                "3_cause_wording (minor)": "reworded (failure_analysis), backed by posthoc_bonferroni_gate",
                "4_c3_PHYS_fragility (minor)": "ledger c3 note + posthoc_phys_v1rule",
                "5_c2_CI_dependence (minor)": "ledger c2 note + c2_dependence (overlap, leave-one-target-out)",
                "6_deviations_undocumented (minor)": "deviations list here + H8_overall ledger note",
                "7_s_exp_H2O_bimodal (minor)": "caveat_s_exp_H2O + ledger note"},
            v1_implication="v1 poc_transfer.py used the same key-based exclusion, so v1's transfer gains on the "
                           "diffusivity / solubility targets with stereo twins (d_exp_*, s_exp_He/H2/CO2) carry the "
                           "same optimistic inflation; v1 was not re-run here.",
            **fx),
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
                      negative_transfer="per-target mean outer-fold gain < -1%",
                      source_exclusion="FIX ROUND: polymer identity (non-isomeric SMILES) or identical features "
                                       "(v0: exact isomeric key)"),
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
                           f"{r.top_modal_source} ({r.top_modal_frac:.0%}); CI = bootstrap over folds (not independent)"
                           + "".join(f"; {x}" for x in fnotes.get(r.target, []))))
        for pl in ["TOP", "PHYS", "ALL3"]:
            L.append(dict(hypothesis="H8", test_id=f"H8_{pl}_gain", dataset=r.target, model="RF",
                          metric=f"mean outer-fold RMSE gain {pl} vs NONE (15 folds)", value=round(r[f"gain_{pl}"], 4),
                          ci_lo=round(r[f"gain_{pl}_ci_lo"], 4), ci_hi=round(r[f"gain_{pl}_ci_hi"], 4),
                          threshold="descriptive; negative transfer = gain < -1%" +
                                    ("; input to c3" if pl in ("TOP", "PHYS") else ""),
                          verdict="DESCRIPTIVE", n_units=int(r.n_folds),
                          note=("negative transfer" if r[f"neg_{pl}"] else "no negative transfer") +
                               (f"; PHYS source {r.phys_source}" if pl == "PHYS" else "")))
    ba = fx.get("fix_before_after", {})
    ss = fx.get("seed_sensitivity", {})
    c2d, pv = fx["c2_dependence"], fx["posthoc_phys_v1rule"]
    L.append(dict(hypothesis="H8", test_id="H8_c1", dataset="ALL(11 targets)", model="RF",
                  metric="# targets with GATE negative transfer", value=neg["GATE"], threshold="<= 1 of 11",
                  verdict="PASS" if c1 else "FAIL", n_units=nT,
                  note=("; ".join(T[T.neg_GATE].target) or "none")
                       + (f"; FIX ROUND: v0 (key exclusion) {ba['c1_v0']}/11 ({', '.join(ba['neg_targets_v0'])})"
                          if ba else "")
                       + (f"; seed sensitivity (descriptive): count r0-2/r3-4/r0-4 = "
                          f"{ss['by_repeat_set']['r0-2']['neg']['GATE']}/{ss['by_repeat_set']['r3-4']['neg']['GATE']}/"
                          f"{ss['by_repeat_set']['r0-4']['neg']['GATE']}; seed-sensitive targets: "
                          f"{', '.join(ss['seed_sensitive_targets']) or 'none'}; robust negative core: "
                          f"{', '.join(ss['robust_negative_targets']) or 'none'}" if ss else "")))
    L.append(dict(hypothesis="H8", test_id="H8_c2", dataset="ALL(11 targets)", model="RF",
                  metric="mean over targets of GATE gain", value=round(mean_gain["GATE"], 4),
                  ci_lo=round(ci["GATE"][0], 4), ci_hi=round(ci["GATE"][1], 4), threshold="> 0",
                  verdict="PASS" if c2 else "FAIL", n_units=nT,
                  note="CI = bootstrap over targets; targets OVERLAP (e.g. "
                       + ", ".join(c2d["pairs_overlap_ge_80pct_of_smaller"][:4])
                       + ") so the units are not independent and the CI is optimistic; leave-one-target-out mean "
                       f"{c2d['loto_min']:+.4f}..{c2d['loto_max']:+.4f}"
                       + (f"; FIX ROUND: v0 {ba['c2_v0']:+.4f}" if ba else "")))
    L.append(dict(hypothesis="H8", test_id="H8_c3", dataset="ALL(11 targets)", model="RF",
                  metric="neg-transfer rate GATE vs TOP / PHYS", value=f"{neg['GATE']}/{nT}",
                  threshold="GATE rate < TOP rate OR < PHYS rate", verdict="PASS" if c3 else "FAIL", n_units=nT,
                  note=f"TOP {neg['TOP']}/{nT}, PHYS {neg['PHYS']}/{nT}, ALL3 {neg['ALL3']}/{nT}; WEAK evidence: "
                       f"GATE == TOP in negative-transfer count (gate adds nothing), so the PASS rests only on the "
                       f"pre-specified PHYS rule (fixed in the log, not committed to git before the runs); under v1's "
                       f"mechanical physics_prior rule PHYS has {pv['neg_targets_best_case_tiebreak']}/{nT} (best-case "
                       f"tie-break) .. {pv['neg_targets_worst_case_tiebreak']}/{nT} (worst-case) negative targets -> "
                       f"c3 would be {'PASS' if pv['c3_with_v1rule_best_case'] else 'FAIL'} / "
                       f"{'PASS' if pv['c3_with_v1rule_worst_case'] else 'FAIL'} (post hoc)"
                       + (f"; FIX ROUND: v0 GATE {ba['c3_v0']['gate']} / TOP {ba['c3_v0']['top']} / PHYS "
                          f"{ba['c3_v0']['phys']}" if ba else "")))
    L.append(dict(hypothesis="H8", test_id="H8_overall", dataset="ALL(11 targets)", model="RF",
                  metric="all of c1,c2,c3", value=f"{met}/3", threshold="PASS iff c1 and c2 and c3 (PREREG)",
                  verdict=overall, n_units=nT,
                  note=f"mean gain: GATE {mean_gain['GATE']:+.3f}, TOP {mean_gain['TOP']:+.3f}, "
                       f"PHYS {mean_gain['PHYS']:+.3f}, ALL3 {mean_gain['ALL3']:+.3f}"
                       + ("" if complete else f"; missing targets {missing}")
                       + f"; cause: gate open in {diag['frac_folds_gate_open']:.0%} of folds and in-fold |r| does not "
                         f"predict out-of-fold gain (AUROC {diag['auroc_score_detects_negative_fold_pairs_real']:.2f}); "
                         + (f"multiplicity is not the binding issue (post hoc Bonferroni gate still "
                            f"{bonf['neg_targets']}/{nT} negative, GATE_MAX {neg['GATE_MAX']}/{nT})" if not mult_binding
                            else f"post hoc family-wise gates: Bonferroni {bonf['neg_targets']}/{nT}, GATE_MAX "
                                 f"{neg['GATE_MAX']}/{nT} negative (multiplicity may matter)")
                       + (f"; FIX ROUND: v0 verdict {ba['verdict_v0']} ({ba['criteria_met_v0']}/3), stereo-twin leak "
                          f"closed, 7 targets re-run" if ba else "")
                       + "; DEVIATIONS: (a) outer partition reused for inner cross-fitting (source models for "
                         "training-part polymers may include test-fold polymers' SOURCE labels, never target labels); "
                         "(b) permutation base X_bandgap_chain replaced by X_ionization_E; (c) PHYS mapping not "
                         "git-committed before runs; (d) fix-round exclusion by polymer/feature identity, d_exp_H2 and "
                         "d_exp_CO2 re-partitioned (n-1); (e) seed sensitivity repeats 3-4 descriptive only"))
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
    L.append(dict(hypothesis="H8", test_id="H8_x_posthoc_phys_v1rule", dataset="ALL(11 targets)", model="RF",
                  metric="# PHYS neg-transfer targets under v1 physics_prior rule (best / worst tie-break)",
                  value=f"{pv['neg_targets_best_case_tiebreak']}/{pv['neg_targets_worst_case_tiebreak']}",
                  threshold="POST HOC exploratory (fix round, verifier-suggested; c3 sensitivity)",
                  verdict="EXPLORATORY", n_units=nT,
                  note=f"v2 pre-specified PHYS: {neg['PHYS']}/{nT}; c3 under v1 rule: best-case "
                       f"{'PASS' if pv['c3_with_v1rule_best_case'] else 'FAIL'}, worst-case "
                       f"{'PASS' if pv['c3_with_v1rule_worst_case'] else 'FAIL'}"))
    if ba:
        L.append(dict(hypothesis="H8", test_id="H8_x_fix_before_after", dataset="ALL(11 targets)", model="RF",
                      metric="c1 count / mean GATE gain: v0 key exclusion -> identity exclusion",
                      value=f"{ba['c1_v0']}->{neg['GATE']} / {ba['c2_v0']:+.4f}->{mean_gain['GATE']:+.4f}",
                      threshold="descriptive (process data: effect of closing the stereo-twin leak)",
                      verdict="DESCRIPTIVE", n_units=nT,
                      note=f"re-run: {', '.join(ba['targets_rerun'])}; kept (input-identical): "
                           f"{', '.join(ba['targets_kept_v0_input_identical'])}; per target in "
                           f"results/raw/h8_fix_before_after.csv"))
    L.extend(L_fix)
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
    elif cmd == "runseed":
        # FIX ROUND: extra outer repeats (default 3 4) -> h8_parts_seedsens/ (descriptive seed sensitivity only)
        for rep in sys.argv[3:]:
            run_chunk(sys.argv[2], int(rep), parts=PARTS_SEED)
    elif cmd == "checkfix":
        check_fix()
    elif cmd == "aggregate":
        aggregate()
    else:
        raise SystemExit(__doc__)
