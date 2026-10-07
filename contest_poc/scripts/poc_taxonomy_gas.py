"""PoC-1: Does a chemistry-informed materials taxonomy ("계통수") add information
beyond molecular-fingerprint similarity, and does hierarchical partial pooling help
predict a held-out polymer class (few-shot)?

Data: polyVERSE gas transport (experimental log10 permeability, 6 gases).
Usage: python poc_taxonomy_gas.py <master_transport.csv> <taxonomy.csv> <outdir>
"""
import json
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from rdkit import DataStructs

sys.path.insert(0, ".")
from featurize import featurize  # noqa: E402

SRC, TAX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
GASES = ["O2", "N2", "CO2", "CH4", "H2", "He"]
KS = [0, 3, 5, 10]
REPEATS = 5
MIN_CLASS = 15
rng_master = np.random.default_rng(0)

raw = pd.read_csv(SRC, low_memory=False)
tax = pd.read_csv(TAX).set_index("psmiles")
uniq = raw.p_csmiles.drop_duplicates().tolist()
rows, fps, _ = featurize(uniq)
X_all = {s: r for s, r in zip(uniq, rows) if r is not None}
FP_all = {s: f for s, f in zip(uniq, fps) if f is not None}


def rf(seed=0):
    return RandomForestRegressor(n_estimators=150, max_features=0.3, n_jobs=4, random_state=seed)


def load_gas(g):
    d = raw[raw.property == f"p_exp_{g}"]
    d = d[d.p_csmiles.isin(X_all)]
    y = d.groupby("p_csmiles").value.mean()
    t = tax.loc[y.index]
    return pd.DataFrame({"y": y.values, "L1": t.L1.values, "L2": t.L2.values, "L3": t.L3.values}, index=y.index)


def tree_dist(a, b):
    if a.L3 == b.L3:
        return 0
    if a.L2 == b.L2:
        return 1
    if a.L1 == b.L1:
        return 2
    return 3


def pair_analysis(df, n_perm=200):
    idx = df.index.tolist()
    fpl = [FP_all[s] for s in idx]
    sim = np.array([DataStructs.BulkTanimotoSimilarity(f, fpl) for f in fpl])
    iu = np.triu_indices(len(idx), 1)
    dy = np.abs(df.y.values[:, None] - df.y.values[None, :])[iu]
    dfp = 1 - sim[iu]

    def tdist(L1, L2, L3):
        L1, L2, L3 = np.asarray(L1), np.asarray(L2), np.asarray(L3)
        td = np.full((len(L1), len(L1)), 3)
        td[L1[:, None] == L1[None, :]] = 2
        td[L2[:, None] == L2[None, :]] = 1
        td[L3[:, None] == L3[None, :]] = 0
        return td[iu]

    td = tdist(df.L1, df.L2, df.L3)
    # residualize |dy| on FP distance with 20-quantile bin means
    bins = np.quantile(dfp, np.linspace(0, 1, 21))
    b = np.clip(np.digitize(dfp, bins[1:-1]), 0, 19)
    bin_mean = np.array([dy[b == k].mean() for k in range(20)])
    resid = dy - bin_mean[b]
    rho_tree = spearmanr(td, dy).correlation
    rho_fp = spearmanr(dfp, dy).correlation
    rho_partial = spearmanr(td, resid).correlation
    # null: shuffle whole taxonomy tuples across polymers (random tree, same class sizes)
    null = []
    tup = df[["L1", "L2", "L3"]].values
    for p in range(n_perm):
        perm = rng_master.permutation(len(tup))
        tp = tup[perm]
        null.append(spearmanr(tdist(tp[:, 0], tp[:, 1], tp[:, 2]), resid).correlation)
    null = np.array(null)
    p_val = (np.sum(null >= rho_partial) + 1) / (n_perm + 1)
    by_td = {int(k): float(dy[td == k].mean()) for k in range(4)}
    # FP-similarity matched comparison: among pairs with Tanimoto>=0.5, is tree still informative?
    hi = dfp <= 0.5
    rho_hi = spearmanr(td[hi], dy[hi]).correlation if hi.sum() > 50 else None
    return dict(n=len(idx), n_pairs=int(len(dy)), mean_absdy_by_treedist=by_td,
                spearman_tree=rho_tree, spearman_fp=rho_fp, partial_tree_given_fp=rho_partial,
                null_mean=float(null.mean()), null_sd=float(null.std()), p_perm=float(p_val),
                spearman_tree_within_similar_pairs=rho_hi)


def lofo(df, g):
    X = np.vstack([X_all[s] for s in df.index])
    y = df.y.values
    L1 = df.L1.values
    L2 = df.L2.values
    fpl = [FP_all[s] for s in df.index]
    sim = np.array([DataStructs.BulkTanimotoSimilarity(f, fpl) for f in fpl])
    counts = pd.Series(L2).value_counts()
    targets = counts[counts >= MIN_CLASS].index.tolist()
    bias_classes = counts[counts >= 5].index.tolist()
    onehot = pd.get_dummies(pd.DataFrame({"L1": L1, "L2": L2})).values.astype(float)
    Xtax = np.hstack([X, onehot])
    records = []
    for C in targets:
        inC = L2 == C
        # --- honest biases of other classes, computed without C ---
        biases, wvars, ns, sib_l1 = {}, [], {}, {}
        for Cp in bias_classes:
            if Cp == C:
                continue
            tr = ~inC & (L2 != Cp)
            te = L2 == Cp
            m = rf(1).fit(X[tr], y[tr])
            r = y[te] - m.predict(X[te])
            biases[Cp] = r.mean(); ns[Cp] = te.sum(); wvars.append(r.var(ddof=1))
            sib_l1[Cp] = L1[te][0]
        sw2 = float(np.mean(wvars))
        bvals = np.array(list(biases.values()))
        tau2 = max(np.var(bvals, ddof=1) - np.mean([sw2 / ns[c] for c in biases]), 1e-3)
        myL1 = L1[inC][0]
        sibs = [c for c in biases if sib_l1[c] == myL1]
        if len(sibs) >= 2:
            mu_p = float(np.mean([biases[c] for c in sibs]))
            tau2_p = max(np.var([biases[c] for c in sibs], ddof=1), 1e-3)
        else:
            mu_p, tau2_p = 0.0, tau2
        # random-tree control: assign C a random pseudo-parent group of same size
        others = list(biases.keys())
        rnd_sibs = list(rng_master.choice(others, size=max(len(sibs), 2), replace=False))
        mu_r = float(np.mean([biases[c] for c in rnd_sibs]))
        tau2_r = max(np.var([biases[c] for c in rnd_sibs], ddof=1), 1e-3)
        # structure-similarity prior: weight other classes by mean Tanimoto to C
        w = np.array([sim[np.ix_(inC, L2 == c)].mean() for c in others])
        w = w ** 4 / (w ** 4).sum()
        mu_s = float(np.dot(w, [biases[c] for c in others]))
        # base model without any C data
        base = rf(2).fit(X[~inC], y[~inC])
        idxC = np.where(inC)[0]
        for k in KS:
            for rep in range(REPEATS if k > 0 else 1):
                rs = np.random.default_rng(1000 * rep + k)
                shots = rs.choice(idxC, size=k, replace=False) if k > 0 else np.array([], int)
                test = np.setdiff1d(idxC, shots)
                p_base = base.predict(X[test])
                rshot = (y[shots] - base.predict(X[shots])) if k > 0 else np.array([])
                # M1: pool shots into training
                if k > 0:
                    tr = np.concatenate([np.where(~inC)[0], shots])
                    m1 = rf(3).fit(X[tr], y[tr]).predict(X[test])
                    m5 = rf(3).fit(Xtax[tr], y[tr]).predict(Xtax[test])
                    m0 = np.full(len(test), y[shots].mean())
                else:
                    m1 = p_base
                    m5 = rf(3).fit(Xtax[~inC], y[~inC]).predict(Xtax[test])
                    m0 = np.full(len(test), y[~inC].mean())

                def shrink(mu, t2):
                    lam = sw2 / t2
                    return (rshot.sum() + lam * mu) / (len(rshot) + lam)

                preds = {
                    "M0_local_mean": m0,
                    "M1_global_pooled": m1,
                    "M2_flat_shrink": p_base + shrink(0.0, tau2),
                    "M3_tree_hier_shrink": p_base + shrink(mu_p, tau2_p),
                    "M3r_random_tree": p_base + shrink(mu_r, tau2_r),
                    "M4_fpsim_prior": p_base + shrink(mu_s, tau2),
                    "M5_tax_onehot_feature": m5,
                }
                for name, p in preds.items():
                    records.append(dict(gas=g, cls=C, L1=myL1, n_cls=int(inC.sum()), k=k, rep=rep, model=name,
                                        rmse=float(np.sqrt(np.mean((y[test] - p) ** 2))),
                                        bias=float(np.mean(y[test] - p))))
        print(f"  {g} {C} n={inC.sum()} sibs={len(sibs)} mu_p={mu_p:.3f} tau2={tau2:.3f} tau2_p={tau2_p:.3f}", flush=True)
    return records


summary = {}
allrec = []
for g in GASES:
    df = load_gas(g)
    print(f"== {g}: n={len(df)}", flush=True)
    summary[g] = pair_analysis(df)
    print(json.dumps(summary[g], indent=1), flush=True)
    allrec += lofo(df, g)

res = pd.DataFrame(allrec)
res.to_csv(f"{OUT}/taxonomy_lofo_records.csv", index=False)
json.dump(summary, open(f"{OUT}/taxonomy_pair_summary.json", "w"), indent=1)
agg = res.groupby(["k", "model"]).rmse.mean().unstack()
print(agg.round(3).to_string())
