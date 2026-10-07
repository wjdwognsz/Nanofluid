"""Common loaders for the Virtual Round-Robin (VRR) v2 validation.

Every loader returns a `DS` object with the same fields so that every hypothesis test runs
identically on every dataset:

    name, y_name, y_unit, df (harmonised rows), X (float array), feats (names),
    y (float array), group (source id: paper/reference), key (exact replicate key:
    same material + same nominal condition), material (material id, condition-free),
    audit (loader-level findings: dropped rows, unit fixes, malformed fields ...)

Data root: env VRR_DATA (directory that contains poc_scout/ and data/ clones; see README).
Nothing here looks at y when building X, group or key.
"""
import os
import re
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")
ROOT = os.environ.get("VRR_DATA", "/tmp/claude-0/-home-user-Nanofluid/18167133-ff89-5f87-bba0-dd738bb11169/scratchpad")
P = {
    "ES1": f"{ROOT}/data/Cogni-E-Spin-FIRE/Cogni-e-SpinDB 1.0.csv",
    "ES2": f"{ROOT}/poc_scout/Electrospinning-fiber-diameter-prediction/fiber_data.xlsx",
    "DYE": f"{ROOT}/poc_scout/Exhaustion-PLA/Data_131 Exhaustion to PLA.xlsx",
    "DES_RHO": f"{ROOT}/poc_scout/DES-MP-Density_tingtingwuwu/data_DESs_density_data.csv",
    "DES_MP": f"{ROOT}/poc_scout/DES-MP-Density_tingtingwuwu/data_DESs_melting_point_data.csv",
    "DES_ETA": f"{ROOT}/poc_scout/DES-Viscosity_tingtingwuwu/src_data_processing_DES_Viscosity.csv",
    "IL_CELL": f"{ROOT}/poc_scout/ML4IL/ML_for_cellulose_solubility_prediction_dataset_for_cellulose_solubility_ML_model.csv",
}


class DS:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return (f"DS({self.name}: n={len(self.y)}, sources={len(set(self.group))}, "
                f"materials={len(set(self.material))}, feats={len(self.feats)}, y={self.y_name} [{self.y_unit}])")


# ---------------------------------------------------------------- molecular descriptors
DESC_NAMES = ["mw", "logp", "tpsa", "hbd", "hba", "rotb", "rings", "arom", "fsp3", "heavy",
              "nfrag", "abs_charge", "n_hal", "n_N", "n_O"]
_cache = {}


def canon(smi):
    if not isinstance(smi, str):
        return None
    m = Chem.MolFromSmiles(smi)
    return Chem.MolToSmiles(m) if m is not None else None


def mdesc(smi):
    if smi in _cache:
        return _cache[smi]
    m = Chem.MolFromSmiles(smi)
    if m is None:
        v = [np.nan] * len(DESC_NAMES)
    else:
        sym = [a.GetSymbol() for a in m.GetAtoms()]
        v = [Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m),
             rdMolDescriptors.CalcNumHBD(m), rdMolDescriptors.CalcNumHBA(m),
             rdMolDescriptors.CalcNumRotatableBonds(m), rdMolDescriptors.CalcNumRings(m),
             rdMolDescriptors.CalcNumAromaticRings(m), rdMolDescriptors.CalcFractionCSP3(m),
             m.GetNumHeavyAtoms(), len(Chem.GetMolFrags(m)),
             sum(abs(a.GetFormalCharge()) for a in m.GetAtoms()),
             sum(s in ("F", "Cl", "Br", "I") for s in sym), sym.count("N"), sym.count("O")]
    _cache[smi] = v
    return v


# ---------------------------------------------------------------- DES family
def _des_name_map():
    """name(lower) -> canonical SMILES, learned from rows whose SMILES parse (all 3 DES files)."""
    mp = {}
    for k, cols in [("DES_RHO", [("Component#1", "SMILES1"), ("Component#2", "SMILES2")]),
                    ("DES_ETA", [("Component#1", "Component#1_SMILES"), ("Component#2", "Component#2_SMILES")]),
                    ("DES_MP", [("Component#1", "SMILES1"), ("Component#2", "SMILES2")])]:
        d = pd.read_csv(P[k], encoding_errors="ignore")
        for n, s in cols:
            for name, smi in d[[n, s]].drop_duplicates().itertuples(index=False):
                c = canon(smi)
                if c is not None and isinstance(name, str):
                    mp.setdefault(name.strip().lower(), c)
    return mp


_NAME_MAP = None


def _des_common(d, n1, s1, n2, s2, x1, x2, ycol, tcol, name, y_name, y_unit, ylog=False):
    global _NAME_MAP
    audit = {"n_raw": int(len(d))}
    if _NAME_MAP is None:
        _NAME_MAP = _des_name_map()
    ca, cb, fixed, bad = [], [], 0, 0
    for a_n, a_s, b_n, b_s in d[[n1, s1, n2, s2]].itertuples(index=False):
        out = []
        for nm, sm in ((a_n, a_s), (b_n, b_s)):
            c = canon(sm)
            if c is None and isinstance(nm, str) and nm.strip().lower() in _NAME_MAP:
                c = _NAME_MAP[nm.strip().lower()]
                fixed += 1
            out.append(c)
        bad += any(o is None for o in out)
        ca.append(out[0]); cb.append(out[1])
    audit["smiles_unparseable_repaired_by_name"] = int(fixed)
    audit["rows_dropped_unparseable_smiles"] = int(bad)
    d = d.assign(_a=ca, _b=cb, _x1=d[x1].astype(float), _x2=d[x2].astype(float))
    d = d[d._a.notna() & d._b.notna()].copy()
    # order-invariant component order: sort by canonical SMILES (component order differs between papers)
    swap = d._a > d._b
    audit["rows_with_swapped_component_order"] = int(swap.sum())
    d["A"] = np.where(swap, d._b, d._a)
    d["B"] = np.where(swap, d._a, d._b)
    d["xA"] = np.where(swap, d._x2, d._x1)
    d["xB"] = np.where(swap, d._x1, d._x2)
    d["x_sum"] = d.xA + d.xB
    audit["rows_molar_fraction_sum_not_1(|1-sum|>0.01)"] = int((np.abs(d.x_sum - 1) > 0.01).sum())
    d["T"] = d[tcol].astype(float) if tcol else np.nan
    d["y_raw"] = d[ycol].astype(float)
    d["source"] = d["Reference (DOI)"].astype(str).str.strip().str.lower() \
        .str.replace(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", regex=True)
    audit["reference_field_not_a_doi"] = int((~d.source.str.contains(r"^10\.\d{4,}/")).sum())
    audit["reference_field_not_a_doi_examples"] = d.source[~d.source.str.contains(r"^10\.\d{4,}/")].value_counts().head(5).to_dict()
    if ylog:
        audit["rows_dropped_nonpositive_y"] = int((d.y_raw <= 0).sum())
        d = d[d.y_raw > 0].copy()
        d["y"] = np.log10(d.y_raw)
    else:
        d["y"] = d.y_raw
    DA = np.vstack([mdesc(s) for s in d.A])
    DB = np.vstack([mdesc(s) for s in d.B])
    feats = [f"A_{n}" for n in DESC_NAMES] + [f"B_{n}" for n in DESC_NAMES] + ["xA", "xB"]
    X = np.hstack([DA, DB, d[["xA", "xB"]].values])
    if tcol:
        X = np.hstack([X, d[["T"]].values]); feats.append("T")
    d["material"] = d.A + " | " + d.B + " | " + d.xA.round(3).astype(str)
    d["key"] = d.material + (" | T=" + d["T"].round(1).astype(str) if tcol else "")
    audit["n_used"] = int(len(d))
    return DS(name=name, y_name=y_name, y_unit=y_unit, df=d.reset_index(drop=True), X=X.astype(float), feats=feats,
              y=d.y.values.astype(float), group=d.source.values, key=d.key.values, material=d.material.values,
              audit=audit)


def load_des_density():
    d = pd.read_csv(P["DES_RHO"], encoding_errors="ignore")
    return _des_common(d, "Component#1", "SMILES1", "Component#2", "SMILES2", "X#1 (molar fraction).1",
                       "X#2 (molar fraction).1", "Density, g/cm^3", "Temperature, K",
                       "DES_RHO", "density", "g/cm3")


def load_des_viscosity():
    d = pd.read_csv(P["DES_ETA"], encoding_errors="ignore")
    return _des_common(d, "Component#1", "Component#1_SMILES", "Component#2", "Component#2_SMILES",
                       "X#1 (molar fraction)", "X#2 (molar fraction)", "Viscosity, cP", "Temperature, K",
                       "DES_ETA", "log10 viscosity", "log10 cP", ylog=True)


def load_des_mp():
    d = pd.read_csv(P["DES_MP"], encoding_errors="ignore")
    ds = _des_common(d, "Component#1", "SMILES1", "Component#2", "SMILES2", "X#1 (molar fraction)",
                     "X#2 (molar fraction)", "DES melting temperature, K", None,
                     "DES_MP", "melting temperature", "K")
    # pure-component melting points are reported in the file (T#1/T#2); keep them in df only
    return ds


# ---------------------------------------------------------------- IL / cellulose
def load_il_cellulose():
    d = pd.read_csv(P["IL_CELL"], encoding_errors="ignore")
    audit = {"n_raw": int(len(d))}
    d["source"] = d["Ref."].astype(str).str.strip()
    d["cat"] = d.cation.map(canon)
    d["an"] = d.anion.map(canon)
    audit["rows_dropped_unparseable_smiles"] = int((d.cat.isna() | d.an.isna()).sum())
    d = d[d.cat.notna() & d.an.notna()].copy()
    d["y"] = d.solv.astype(float)
    audit["solubility_out_of_0_100"] = int(((d.y < 0) | (d.y > 100)).sum())
    C = np.vstack([mdesc(s) for s in d.cat]); A = np.vstack([mdesc(s) for s in d.an])
    cr = pd.get_dummies(d.cellulose_crystal.astype(str), prefix="cell").astype(float)
    X = np.hstack([C, A, cr.values, d[["T", "heating_time"]].astype(float).values])
    feats = [f"cat_{n}" for n in DESC_NAMES] + [f"an_{n}" for n in DESC_NAMES] + list(cr.columns) + ["T", "heating_time"]
    d["material"] = d.cat + "." + d.an + " | " + d.cellulose_crystal.astype(str)
    d["key"] = d.material + " | T=" + d["T"].astype(str) + " | t=" + d.heating_time.astype(str)
    audit["n_used"] = int(len(d))
    return DS(name="IL_CELL", y_name="cellulose solubility", y_unit="wt%", df=d.reset_index(drop=True),
              X=X.astype(float), feats=feats, y=d.y.values, group=d.source.values, key=d.key.values,
              material=d.material.values, audit=audit)


# ---------------------------------------------------------------- PLA disperse dye exhaustion
def load_dye():
    d = pd.read_excel(P["DYE"], sheet_name="Detail")
    d.columns = ["name", "smiles", "E", "T", "pH", "owf", "ref", "type"]
    audit = {"n_raw": int(len(d)), "dye_class_labels": d.type.value_counts().to_dict()}
    d["dye"] = d.smiles.map(canon)
    audit["rows_dropped_unparseable_smiles"] = int(d.dye.isna().sum())
    d = d[d.dye.notna()].copy()
    d["y"] = d.E.astype(float)
    audit["exhaustion_out_of_0_100"] = int(((d.y < 0) | (d.y > 100)).sum())
    from rdkit.Chem import rdFingerprintGenerator
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=256)
    FP = np.vstack([gen.GetCountFingerprintAsNumPy(Chem.MolFromSmiles(s)).astype(float) for s in d.dye])
    D = np.vstack([mdesc(s) for s in d.dye])
    cond = d[["T", "pH", "owf"]].astype(float)
    audit["condition_missing"] = cond.isna().sum().to_dict()
    miss = cond.isna().astype(float).add_suffix("_missing")
    cond = cond.fillna(cond.median())
    d[["T", "pH", "owf"]] = cond
    X = np.hstack([D, FP, cond.values, miss.values])
    feats = [f"dye_{n}" for n in DESC_NAMES] + [f"fp{i}" for i in range(FP.shape[1])] + ["T", "pH", "owf"] + list(miss.columns)
    d["source"] = d.ref.astype(str)
    d["material"] = d.dye
    d["key"] = d.dye + " | T=" + d["T"].astype(str) + " | pH=" + d.pH.astype(str) + " | owf=" + d.owf.astype(str)
    audit["n_used"] = int(len(d))
    return DS(name="DYE", y_name="exhaustion", y_unit="%", df=d.reset_index(drop=True), X=X, feats=feats,
              y=d.y.values, group=d.source.values, key=d.key.values, material=d.material.values, audit=audit)


# ---------------------------------------------------------------- Electrospinning (Cogni-e-SpinDB)
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
ES1_FEATS = ["conc_wt", "voltage_kv", "flow_rate_ml/h", "tip_collector_distance_cm", "needle_diameter_g",
             "rpm", "temperature_c", "rh", "needle_diameter_g_missing", "temperature_c_missing", "rh_missing",
             "collector_drum", "collector_bath", "solv_density", "solv_eps", "solv_bp", "is_solvent_blend",
             "p_mw_ru", "p_logp", "p_tpsa", "p_arom", "p_density"]


def _es1_frame():
    d = pd.read_csv(P["ES1"])
    audit = {"n_raw": int(len(d))}
    sp = []
    for s in d["solvent(s)"]:
        parts = s.replace("-", " ").split()
        sp.append(np.nanmean(np.array([SOLV.get(p, (np.nan,) * 3) for p in parts], dtype=float), axis=0))
    sp = np.vstack(sp)
    d["solv_density"], d["solv_eps"], d["solv_bp"] = sp[:, 0], sp[:, 1], sp[:, 2]
    rho_p = d["polymer(s)"].map(lambda p: POLY[p][1])
    c = d.solution_concentration.astype(float)
    wv = d.solution_concentration_unit == "w/v%"
    rho_sol = d.solv_density + c / 100 * (1 - d.solv_density / rho_p)
    d["conc_wt"] = np.where(wv, c / rho_sol, c)
    audit["w/v%_converted_to_wt%"] = int(wv.sum())

    def rh(x):
        x = str(x)
        if "-" in x:
            a, b = x.split("-")
            return (float(a) + float(b)) / 2
        try:
            return float(x)
        except ValueError:
            return np.nan

    audit["humidity_range_strings"] = int(d["humidity_%"].astype(str).str.contains("-").sum())
    d["rh"] = d["humidity_%"].map(rh)
    audit["humidity_eq_45_rows"] = int((d.rh == 45).sum())
    audit["humidity_eq_45_papers"] = int(d[d.rh == 45].doi.nunique())
    audit["temperature_missing_rows"] = int(d.temperature_c.isna().sum())
    d["rpm"] = d.rotation_speed_rpm.fillna(0.0)
    for col in ["needle_diameter_g", "temperature_c", "rh"]:
        d[col + "_missing"] = d[col].isna().astype(float)
        d[col] = d[col].fillna(d[col].median())
    d["collector_drum"] = (d.collector_type == "Rolling Drum").astype(float)
    d["collector_bath"] = (d.collector_type == "Flat With Ethanol Bath").astype(float)
    d["is_solvent_blend"] = d.is_solvent_blend.astype(float)
    pdesc = {}
    for p, (smi, rho) in POLY.items():
        m = Chem.MolFromSmiles(smi)
        pdesc[p] = [Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m),
                    rdMolDescriptors.CalcNumAromaticRings(m), rho]
    Pm = np.vstack([pdesc[p] for p in d["polymer(s)"]])
    for i, n in enumerate(["p_mw_ru", "p_logp", "p_tpsa", "p_arom", "p_density"]):
        d[n] = Pm[:, i]
    d["source"] = d.doi.astype(str).str.strip().str.lower().str.replace(r"^(https?://(dx\.)?doi\.org/|doi:?\s*)", "", regex=True)
    d["material"] = d["polymer(s)"] + " | " + d["solvent(s)"]
    d["key"] = (d.material + " | c=" + d.conc_wt.round(1).astype(str) + " | V=" + d.voltage_kv.astype(str) +
                " | Q=" + d["flow_rate_ml/h"].astype(str) + " | L=" + d.tip_collector_distance_cm.astype(str))
    return d, audit


def load_es1():
    """Regression set: stable formations only, y = log10 fiber diameter (nm)."""
    d, audit = _es1_frame()
    audit["unstable_rows_excluded"] = int((~d.was_formation_stable).sum())
    d = d[d.was_formation_stable & d.fiber_diameter_nm.notna() & (d.fiber_diameter_nm > 0)].copy()
    d["y"] = np.log10(d.fiber_diameter_nm)
    audit["n_used"] = int(len(d))
    return DS(name="ES1", y_name="log10 fiber diameter", y_unit="log10 nm", df=d.reset_index(drop=True),
              X=d[ES1_FEATS].values.astype(float), feats=ES1_FEATS, y=d.y.values, group=d.source.values,
              key=d.key.values, material=d.material.values, audit=audit)


def load_es1_failure(polymer="PVDF"):
    """Classification set for H7: label 1 = unstable formation (reported failure)."""
    d, audit = _es1_frame()
    if polymer:
        d = d[d["polymer(s)"] == polymer].copy()
    d["y"] = (~d.was_formation_stable).astype(int)
    return DS(name=f"ES1_FAIL_{polymer}", y_name="unstable formation", y_unit="0/1", df=d.reset_index(drop=True),
              X=d[ES1_FEATS].values.astype(float), feats=ES1_FEATS, y=d.y.values, group=d.source.values,
              key=d.key.values, material=d.material.values, audit=audit)


# ---------------------------------------------------------------- Electrospinning (PVDF compilation, independent)
def load_es2():
    d = pd.read_excel(P["ES2"])
    d.columns = ["source_full", "solvent", "ratio", "delta", "Ra", "conc", "RED", "V", "L", "Q", "chi", "D"]
    audit = {"n_raw": int(len(d))}
    audit["source_cells_blank_forward_filled"] = int(d.source_full.isna().sum())
    d["source_full"] = d.source_full.ffill()
    doi = d.source_full.astype(str).str.extract(r"(10\.\d{4,}/[^\s,;]+)", expand=False)
    d["source"] = doi.str.rstrip(".").str.lower().fillna(d.source_full.astype(str).str[:60])
    for c in ["delta", "Ra", "conc", "RED", "V", "L", "Q", "chi", "D"]:
        bad = pd.to_numeric(d[c], errors="coerce").isna() & d[c].notna()
        if bad.any():
            audit[f"non_numeric_{c}"] = d.loc[bad, c].astype(str).value_counts().head(5).to_dict()
        d[c] = pd.to_numeric(d[c], errors="coerce")
    audit["rows_dropped_missing_core(delta,Ra,conc,D)"] = int(d[["delta", "Ra", "conc", "D"]].isna().any(axis=1).sum())
    d = d.dropna(subset=["delta", "Ra", "conc", "D"]).copy()
    for c in ["V", "L", "Q", "RED", "chi"]:
        d[c + "_missing"] = d[c].isna().astype(float)
        audit[f"imputed_median_{c}"] = int(d[c].isna().sum())
        d[c] = d[c].fillna(d[c].median())
    d = d[d.D > 0].copy()
    d["y"] = np.log10(d.D)
    sv = d.solvent.astype(str).str.upper()
    for s in ["DMF", "DMAC", "ACETONE", "DMSO", "NMP", "THF"]:
        d["s_" + s] = sv.str.contains(s).astype(float)
    feats = ["delta", "Ra", "conc", "RED", "V", "L", "Q", "chi", "V_missing", "L_missing", "Q_missing"] + \
        [c for c in d if c.startswith("s_")]
    d["material"] = "PVDF | " + d.solvent.astype(str) + " | " + d.ratio.astype(str)
    d["key"] = d.material + " | c=" + d.conc.astype(str) + " | V=" + d.V.astype(str) + " | L=" + d.L.astype(str) + " | Q=" + d.Q.astype(str)
    audit["n_used"] = int(len(d))
    return DS(name="ES2", y_name="log10 fiber diameter", y_unit="log10 nm", df=d.reset_index(drop=True),
              X=d[feats].values.astype(float), feats=feats, y=d.y.values, group=d.source.values,
              key=d.key.values, material=d.material.values, audit=audit)


LOADERS = {"ES1": load_es1, "ES2": load_es2, "DYE": load_dye, "DES_RHO": load_des_density,
           "DES_ETA": load_des_viscosity, "DES_MP": load_des_mp, "IL_CELL": load_il_cellulose}
REGRESSION_SETS = list(LOADERS)


def load(name):
    return LOADERS[name]()


if __name__ == "__main__":
    import json
    for k in LOADERS:
        ds = load(k)
        g = pd.Series(ds.group).value_counts()
        kk = pd.DataFrame({"k": ds.key, "g": ds.group}).groupby("k").g.nunique()
        print(ds, "| sources>=8 rows:", int((g >= 8).sum()), "| keys in >=2 sources:", int((kk >= 2).sum()),
              "| nan in X:", int(np.isnan(ds.X).sum()))
        print("   audit:", json.dumps(ds.audit, ensure_ascii=False, default=str)[:600])
