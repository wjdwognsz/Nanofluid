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
SRC = sys.argv[1]
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

