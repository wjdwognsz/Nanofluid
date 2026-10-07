"""Null control for PoC-3: how large are 'transfer gains' from sources whose labels were randomly
permuted (chemically meaningless)? If permuted sources often produce gains comparable to real ones,
picking the best-looking source on a small target is unreliable (winner's curse).
Usage: python poc_transfer_null.py <polyVERSE/Other dir> <outdir>
"""
import json
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator, Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")
OTHER, OUT = sys.argv[1], sys.argv[2]
MFP = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
FEAT = {}


def key_of(s):
    for t in ["[d]", "[e]", "[g]", "[t]"]:
        s = str(s).replace(t, "[*]")
    m = Chem.MolFromSmiles(s)
    return (Chem.MolToSmiles(m), m) if m is not None else (None, None)


def add_series(smiles, vals):
    out = {}
    for s, v in zip(smiles, vals):
        if pd.isna(v):
            continue
        k, m = key_of(s)
        if k is None:
            continue
        if k not in FEAT:
            FEAT[k] = np.concatenate([MFP.GetCountFingerprintAsNumPy(m).astype(np.float32),
                                      [Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m),
                                       rdMolDescriptors.CalcNumAromaticRings(m)]])
        out.setdefault(k, []).append(float(v))
    return pd.Series({k: np.mean(v) for k, v in out.items()})


master = pd.read_csv(f"{OTHER}/Gas_permeability_solubility_diffusivity/master_transport_2025_08_13.csv", low_memory=False)
T = {p: add_series(g.p_csmiles, g.value) for p, g in master.groupby("property")}
bg = pd.read_csv(f"{OTHER}/bandgap_chain/bandgap_chain.csv")
T["X_bandgap_chain"] = add_series(bg.smiles, bg.bandgap_chain)


def Xof(keys):
    return np.vstack([FEAT[k] for k in keys])


def rf(n=100, mf=0.2, seed=0):
    return RandomForestRegressor(n_estimators=n, max_features=mf, n_jobs=4, random_state=seed)


def folds(n, rep, K=5):
    p = np.random.default_rng(rep).permutation(n)
    return [p[i::K] for i in range(K)]


def gain(src_series, tser, reps=2):
    tk = list(tser.index); y = tser.values; X = Xof(tk)
    se_b, se_t = [], []
    for r in range(reps):
        fl = folds(len(y), r)
        g = np.zeros(len(y))
        for te in fl:
            ex = set(tk[i] for i in te)
            sk = [k for k in src_series.index if k not in ex]
            g[te] = rf(seed=11).fit(Xof(sk), src_series.loc[sk].values).predict(Xof([tk[i] for i in te]))
        eb = np.zeros(len(y)); et = np.zeros(len(y))
        for te in fl:
            tr = np.setdiff1d(np.arange(len(y)), te)
            eb[te] = y[te] - rf(200, 0.3, 5).fit(X[tr], y[tr]).predict(X[te])
            lin = LinearRegression().fit(g[tr, None], y[tr])
            et[te] = y[te] - (lin.predict(g[te, None]) + rf(200, 0.3, 5).fit(X[tr], y[tr] - lin.predict(g[tr, None])).predict(X[te]))
        se_b.append(eb ** 2); se_t.append(et ** 2)
    b = np.sqrt(np.mean(se_b)); t = np.sqrt(np.mean(se_t))
    return float((b - t) / b)


out = {}
for tgt in ["p_exp_H2O", "s_exp_H2O", "d_exp_H2O"]:
    tser = T[tgt]
    res = {"real": {}, "null": []}
    for src in ["X_bandgap_chain", "p_exp_O2", "s_exp_CH4", "d_exp_H2", "s_sim_N2"]:
        res["real"][src] = gain(T[src], tser)
    for i in range(12):
        base = T["X_bandgap_chain"] if i % 2 == 0 else T["p_exp_O2"]
        perm = pd.Series(np.random.default_rng(500 + i).permutation(base.values), index=base.index)
        res["null"].append(gain(perm, tser))
    res["null_max"] = float(np.max(res["null"])); res["null_mean"] = float(np.mean(res["null"]))
    res["null_95pct"] = float(np.percentile(res["null"], 95))
    out[tgt] = res
    print(tgt, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items() if k != "null"}),
          "null:", np.round(res["null"], 3).tolist(), flush=True)
json.dump(out, open(f"{OUT}/transfer_null.json", "w"), indent=1)
