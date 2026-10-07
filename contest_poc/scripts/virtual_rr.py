"""Virtual round-robin across public polymer databases: how much do values for the SAME polymer
(same canonical repeat-unit SMILES) disagree between independently curated datasets?
Usage: python virtual_rr.py <scratchpad dir> <outdir>
"""
import itertools
import json
import re
import sys
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
S, OUT = sys.argv[1], sys.argv[2]
P = S + "/poc_scout/"


def canon(s):
    s = str(s)
    s = s.replace("<polymer_spg>", "")
    s = re.sub(r";\d+->\d+$", "", s)
    s = re.sub(r"\[\*:\d+\]", "[*]", s)
    for t in ["[d]", "[e]", "[g]", "[t]"]:
        s = s.replace(t, "[*]")
    s = re.sub(r"(?<!\[)\*(?!\])", "[*]", s)
    m = Chem.MolFromSmiles(s)
    if m is None:
        return None
    m = Chem.RemoveHs(m)
    return Chem.MolToSmiles(m)


def series(smiles, vals):
    d = pd.DataFrame({"k": [canon(x) for x in smiles], "v": vals}).dropna()
    return d.groupby("k").v.median()


report = {}

# ---------------- gas permeability (log10 Barrer) ----------------
pv = pd.read_csv(S + "/data/polyVERSE/Other/Gas_permeability_solubility_diffusivity/master_transport_2025_08_13.csv", low_memory=False)
ya = pd.read_csv(P + "PolymerGasMembraneML/datasets_datasetA_imputed_all.csv")
netl = pd.read_csv(P + "IBM_materials/models_str_bamba_data_polymer_NETL_polymer_perm_jcim_24.csv")
for gas in ["O2", "CO2", "N2", "CH4"]:
    src = {}
    g = pv[pv.property == f"p_exp_{gas}"]
    src["polyVERSE"] = series(g.p_csmiles, g.value + 10)
    v = ya[gas]
    src["Yang2022_SciAdv"] = series(ya.Smiles[v > 0], np.log10(v[v > 0]))
    try:
        k = pd.read_csv(P + f"KaggleNotebooks_OfficialBhattacharya/NeurIPS_OpenPolymerPrediction_RawData_{gas}_raw.csv")
        k = k[k[gas] > 0]
        src["PoLyInfo_Kaggle"] = series(k.SMILES, np.log10(k[gas]))
    except FileNotFoundError:
        pass
    if gas == "O2":
        gr = pd.read_csv(P + "GREA/data_o2_prop_raw_o2_raw.csv")
        gr = gr[gr.o2 > 0]
        src["GREA"] = series(gr.SMILES, np.log10(gr.o2))
    col = {"CO2": "log CO2 (barrer)", "CH4": "log CH4 (barrer)", "N2": "log N2 (barrer)"}.get(gas)
    if col:
        src["NETL_JCIM24"] = series(netl["POLYMER SMILES"], netl[col])
    rows = []
    for a, b in itertools.combinations(src, 2):
        common = src[a].index.intersection(src[b].index)
        if len(common) < 10:
            rows.append(dict(a=a, b=b, n=len(common)))
            continue
        d = (src[a].loc[common] - src[b].loc[common]).values
        rows.append(dict(a=a, b=b, n=len(common), median_abs=float(np.median(np.abs(d))),
                         frac_exact=float(np.mean(np.abs(d) < 0.005)), frac_gt_2x=float(np.mean(np.abs(d) > np.log10(2))),
                         frac_gt_10x=float(np.mean(np.abs(d) > 1)), sigmaR_est=float(np.sqrt(np.mean(d ** 2) / 2)),
                         sigmaR_robust=float(1.4826 * np.median(np.abs(d - np.median(d))) / np.sqrt(2)),
                         mean_bias=float(d.mean()), r=float(np.corrcoef(src[a].loc[common], src[b].loc[common])[0, 1])))
    report[f"P_{gas}"] = dict(sizes={k: int(len(v)) for k, v in src.items()}, pairs=rows,
                              between_polymer_sd=float(src["polyVERSE"].std()))

# ---------------- Tg (K) ----------------
tg = {}
lam = pd.read_csv(P + "NeurIPS-polymer-prediction/data_preprocessing_results_Tg_LAMALAB.csv")
kag = pd.read_csv(P + "KaggleNotebooks_OfficialBhattacharya/NeurIPS_OpenPolymerPrediction_RawData_Tg_SMILES_class_pid_polyinfo_median.csv")
neu = pd.read_csv(P + "NeurIPS-Open-Polymer-Prediction_kevzhu14/data_raw data_train.csv")
pid = pd.read_csv(P + "polyID/data_stereopolymer_input_nopush.csv")
acs = pd.read_csv(P + "IBM_materials/models_str_bamba_data_polymer_ACS-AMI-Homopolymer-Tg_polymer_tg_gcn.csv")
units = {}
for nm, df, sc, vc in [("LAMALAB", lam, "SMILES", "Tg_label"), ("PoLyInfo_Kaggle", kag, "SMILES", "Tg"),
                       ("NeurIPS2025_train", neu, "SMILES", "Tg"), ("NREL_polyID", pid, "smiles_polymer", "Tg"),
                       ("ACS-AMI_gcn", acs, acs.columns[1], acs.columns[2])]:
    x = df[[sc, vc]].dropna()
    med = float(x[vc].median())
    units[nm] = {"column": vc, "median": med}
    vals = x[vc].astype(float).values
    if med < 200:  # looks like Celsius
        vals = vals + 273.15
        units[nm]["converted_C_to_K"] = True
    tg[nm] = series(x[sc], vals)
rows = []
for a, b in itertools.combinations(tg, 2):
    common = tg[a].index.intersection(tg[b].index)
    if len(common) < 10:
        rows.append(dict(a=a, b=b, n=len(common)))
        continue
    d = (tg[a].loc[common] - tg[b].loc[common]).values
    rows.append(dict(a=a, b=b, n=len(common), median_abs_K=float(np.median(np.abs(d))),
                     frac_exact=float(np.mean(np.abs(d) < 0.5)), frac_gt_10K=float(np.mean(np.abs(d) > 10)),
                     frac_gt_30K=float(np.mean(np.abs(d) > 30)), sigmaR_est_K=float(np.sqrt(np.mean(d ** 2) / 2)),
                     sigmaR_robust_K=float(1.4826 * np.median(np.abs(d - np.median(d))) / np.sqrt(2)),
                     mean_bias_K=float(d.mean())))
report["Tg"] = dict(units=units, sizes={k: int(len(v)) for k, v in tg.items()}, pairs=rows,
                    between_polymer_sd_K=float(tg["PoLyInfo_Kaggle"].std()))
json.dump(report, open(f"{OUT}/virtual_rr.json", "w"), indent=1)
for k, v in report.items():
    print("==", k, v.get("sizes"), v.get("units", ""))
    for r in v["pairs"]:
        print("   ", {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in r.items()})
    print("   between-polymer SD:", v.get("between_polymer_sd", v.get("between_polymer_sd_K")))
