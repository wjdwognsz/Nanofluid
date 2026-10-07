"""PoC-5 (textile dyeing data): disperse dye exhaustion on PLA (131 records, 11 literature refs;
Sixty-four-floor/Exhaustion-PLA, GitHub). Audit + virtual round-robin (same dye in different refs)
+ random vs leave-reference-out CV + anchor calibration.
Usage: python poc_dye.py <xlsx> <outdir>
"""
import json
import sys
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator, Descriptors
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, GroupKFold

RDLogger.DisableLog("rdApp.*")
F, OUT = sys.argv[1], sys.argv[2]
d = pd.read_excel(F, sheet_name="Detail")
d.columns = ["name", "smiles", "E", "T", "pH", "owf", "ref", "type"]
rep = {}
rep["n"] = len(d); rep["n_refs"] = int(d.ref.nunique())
rep["rows_per_ref"] = d.ref.value_counts().to_dict()
# ---- audit ----
rep["E_range"] = [float(d.E.min()), float(d.E.max())]
rep["E_out_of_0_100"] = int(((d.E < 0) | (d.E > 100)).sum())
rep["conditions"] = {c: d[c].value_counts().head(8).to_dict() for c in ["T", "pH", "owf"]}
rep["dye_class_labels_language"] = d.type.value_counts().to_dict()
mols = [Chem.MolFromSmiles(s) for s in d.smiles]
rep["unparseable_smiles"] = int(sum(m is None for m in mols))
d["key"] = [Chem.MolToSmiles(m) if m is not None else None for m in mols]
# ---- virtual round-robin: same dye & same nominal conditions, different refs ----
grp = d.groupby(["key", "T", "pH", "owf"])
multi = []
for k, g in grp:
    if g.ref.nunique() > 1:
        multi.append(dict(dye=g.name.iloc[0], refs=list(g.ref), E=list(g.E), spread=float(g.E.max() - g.E.min())))
rep["same_dye_same_condition_multi_ref"] = multi
same_dye_any = d.groupby("key").ref.nunique()
rep["dyes_reported_by_multiple_refs_any_condition"] = int((same_dye_any > 1).sum())
dup_within = d.groupby(["key", "T", "pH", "owf", "ref"]).size()
rep["exact_duplicate_rows_within_ref"] = int((dup_within > 1).sum())
# ---- model ----
gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
X = np.vstack([np.concatenate([gen.GetCountFingerprintAsNumPy(m).astype(float),
                               [Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m)]]) for m in mols])
X = np.hstack([X, d[["T", "pH", "owf"]].values.astype(float)])
y = d.E.values.astype(float)
refs = d.ref.values


def rf(s=0):
    return RandomForestRegressor(n_estimators=300, max_features=0.3, min_samples_leaf=1, n_jobs=4, random_state=s)


def cv(split, groups=None, reps=5):
    out = []
    for r in range(reps):
        err = np.zeros(len(y))
        sp = split(r)
        for tr, te in sp.split(X, y, groups):
            err[te] = y[te] - rf(r).fit(X[tr], y[tr]).predict(X[te])
        out.append((np.sqrt(np.mean(err ** 2)), 1 - np.sum(err ** 2) / np.sum((y - y.mean()) ** 2)))
    return out


r_rand = cv(lambda r: KFold(10, shuffle=True, random_state=r))
r_ref = cv(lambda r: GroupKFold(n_splits=d.ref.nunique()), refs, reps=1)
rep["rmse_r2_random10fold_mean"] = [float(np.mean([a for a, b in r_rand])), float(np.mean([b for a, b in r_rand]))]
rep["rmse_r2_leave_reference_out"] = [float(r_ref[0][0]), float(r_ref[0][1])]
rep["sd_E"] = float(y.std())
# ---- anchor calibration on refs with >= 8 rows ----
res = []
for R in [r for r, n in d.ref.value_counts().items() if n >= 8]:
    te = refs == R
    base = rf(1).fit(X[~te], y[~te])
    pb = base.predict(X[te]); idx = np.where(te)[0]
    for k in [0, 1, 2, 3, 5]:
        for rr in range(20 if k else 1):
            rs = np.random.default_rng(100 * rr + k)
            loc = rs.choice(len(idx), k, replace=False) if k else np.array([], int)
            tl = np.setdiff1d(np.arange(len(idx)), loc)
            off = (y[idx[loc]] - pb[loc]).mean() if k else 0.0
            res.append(dict(ref=R, k=k, rep=rr, sse=float(np.sum((y[idx[tl]] - pb[tl] - off) ** 2)), n=len(tl),
                            bias0=float((y[te] - pb).mean())))
A = pd.DataFrame(res)
rep["anchor_refs"] = A.ref.unique().tolist()
rep["paper_bias_by_ref"] = A[A.k == 0].groupby("ref").bias0.first().round(1).to_dict()
rep["anchor_rmse_by_k"] = {int(k): float(np.sqrt(g.groupby("ref").sse.mean().sum() / g.groupby("ref").n.mean().sum()))
                           for k, g in A.groupby("k")}
json.dump(rep, open(f"{OUT}/dye_summary.json", "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps(rep, indent=1, ensure_ascii=False, default=str))
