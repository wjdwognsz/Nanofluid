"""Verifier: H6c matching-free identity check. For each shared PVDF paper, is each ES1 diameter value present among
ES2's diameter values for that paper (within 0.5 nm), and vice versa? Plus DOI overlap count and ES2 sources overlap."""
import sys, re, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
from vrr_data import load_es1_failure, P
def nd(s):
    s = str(s).strip().lower(); s = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:?\s*)", "", s); return re.sub(r"[.,;\s]+$", "", s)
e1 = load_es1_failure("PVDF").df; e1["nd"] = e1.doi.map(nd)
raw = pd.read_excel(P["ES2"]); raw.columns = ["source_full","solvent","ratio","delta","Ra","conc","RED","V","L","Q","chi","D"]
raw["source_full"] = raw.source_full.ffill()
raw["nd"] = raw.source_full.astype(str).str.extract(r"(10\.\d{4,}/[^\s,;]+)", expand=False).map(lambda x: nd(x) if isinstance(x,str) else None)
raw["nd"] = raw.nd.fillna(raw.source_full.astype(str).str[:60])
shared = sorted(set(e1.nd) & set(raw.nd))
print("shared DOIs:", len(shared), "| ES2 distinct sources:", raw.nd.nunique(), "| ES1-PVDF distinct DOIs:", e1.nd.nunique())
tot1 = hit1 = tot2 = hit2 = 0
for pap in shared:
    a = pd.to_numeric(e1[e1.nd == pap].fiber_diameter_nm, errors="coerce").dropna().values
    b = pd.to_numeric(raw[raw.nd == pap].D, errors="coerce").dropna().values
    h1 = sum(np.any(np.abs(b - x) <= 0.5) for x in a); h2 = sum(np.any(np.abs(a - x) <= 0.5) for x in b)
    tot1 += len(a); hit1 += h1; tot2 += len(b); hit2 += h2
    if h1 < len(a) or h2 < len(b): print("  ", pap, f"ES1 vals in ES2 {h1}/{len(a)}, ES2 vals in ES1 {h2}/{len(b)}")
print(f"ES1 D values found in ES2 (same paper): {hit1}/{tot1}; ES2 D values found in ES1: {hit2}/{tot2}")
# null: chance that a random ES1 value from a *different* shared paper hits the paper's ES2 set
rs = np.random.default_rng(0); allv = pd.to_numeric(e1[e1.nd.isin(shared)].fiber_diameter_nm, errors="coerce").dropna().values
ch = []
for pap in shared:
    b = pd.to_numeric(raw[raw.nd == pap].D, errors="coerce").dropna().values
    if len(b): ch += [np.any(np.abs(b - x) <= 0.5) for x in rs.choice(allv, 50)]
print("chance hit rate with values from other papers:", round(np.mean(ch), 3))
