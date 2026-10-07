"""Featurization + rule-based polymer taxonomy for polyVERSE transport data.

Taxonomy levels (hand-made, chemistry-informed):
  L1 backbone type : ladder | inorganic | hetero (condensation) | carbon (chain-growth)
  L2 class         : polyimide, polysulfone, polyamide, ... (priority rules on backbone)
  L3 leaf          : L2 + fluorinated / non-fluorinated
"""
import re
import sys
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator, Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

LADDER_TOKENS = ["[d]", "[e]", "[g]", "[t]"]
MFP = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

PAT = {
    "imide": Chem.MolFromSmarts("[#6](=O)[#7]([#6]=O)"),
    "sulfone": Chem.MolFromSmarts("[#16](=O)(=O)"),
    "amide": Chem.MolFromSmarts("[#6](=O)[#7]"),
    "urethane": Chem.MolFromSmarts("[#7][#6](=O)[#8]"),
    "carbonate": Chem.MolFromSmarts("[#8][#6](=O)[#8]"),
    "ester": Chem.MolFromSmarts("[#6](=O)[#8]"),
    "azole": Chem.MolFromSmarts("[#6]1:[#7]:[#6]2:[#6]:[#6]:[#6]:[#6]:[#6]:2:[#7,#8,#16]:1"),
    "azole2": Chem.MolFromSmarts("c1nc2ccccc2[n,o,s]1"),
}


def to_mol(psmiles):
    s = psmiles
    n_ladder = sum(s.count(t) for t in LADDER_TOKENS)
    for t in LADDER_TOKENS:
        s = s.replace(t, "[*]")
    m = Chem.MolFromSmiles(s)
    return m, n_ladder


def backbone_atoms(m):
    dummies = [a.GetIdx() for a in m.GetAtoms() if a.GetAtomicNum() == 0]
    if len(dummies) < 2:
        return set()
    path = Chem.GetShortestPath(m, dummies[0], dummies[1])
    return set(path) - set(dummies)


def _match_on_backbone(m, patt, bb):
    for match in m.GetSubstructMatches(patt):
        if bb & set(match):
            return True
    return False


def classify(m, n_ladder):
    if n_ladder >= 2 or sum(a.GetAtomicNum() == 0 for a in m.GetAtoms()) > 2:
        return "ladder", "PIM/ladder"
    bb = backbone_atoms(m)
    if not bb:
        return "other", "other"
    syms = {m.GetAtomWithIdx(i).GetSymbol() for i in bb}
    if syms & {"Si", "Ge", "Sn"}:
        return "inorganic", ("polysiloxane" if "O" in syms else "Si/Ge-backbone")
    ri = m.GetRingInfo()
    bb_ring_atoms = set()
    for ring in ri.AtomRings():
        if bb & set(ring):
            bb_ring_atoms |= set(ring)
    ext = bb | bb_ring_atoms  # backbone incl. rings it passes through
    if _match_on_backbone(m, PAT["imide"], ext):
        return "hetero", "polyimide"
    if _match_on_backbone(m, PAT["azole2"], ext) or _match_on_backbone(m, PAT["azole"], ext):
        return "hetero", "polybenzazole"
    if _match_on_backbone(m, PAT["sulfone"], bb):
        return "hetero", "polysulfone"
    if _match_on_backbone(m, PAT["urethane"], bb):
        return "hetero", "polyurethane"
    if _match_on_backbone(m, PAT["amide"], bb):
        return "hetero", "polyamide"
    if _match_on_backbone(m, PAT["carbonate"], bb):
        return "hetero", "polycarbonate"
    if _match_on_backbone(m, PAT["ester"], bb):
        return "hetero", "polyester"
    if "O" in syms:
        return "hetero", "polyether"
    if syms - {"C"}:
        return "hetero", "other-hetero"
    # all-carbon backbone
    bb_bonds = [m.GetBondBetweenAtoms(i, j) for i in bb for j in bb if i < j and m.GetBondBetweenAtoms(i, j)]
    has_db = any(b.GetBondType() == Chem.BondType.DOUBLE for b in bb_bonds)
    bb_in_aliph_ring = any(
        (bb & set(r)) and not all(m.GetAtomWithIdx(k).GetIsAromatic() for k in r) for r in ri.AtomRings()
    )
    bb_in_arom_ring = any(m.GetAtomWithIdx(i).GetIsAromatic() for i in bb)
    if has_db and bb_in_aliph_ring:
        return "carbon", "ROMP-polynorbornene"
    if has_db:
        return "carbon", "polyacetylene"
    if bb_in_aliph_ring:
        return "carbon", "addition-cycloolefin"
    if bb_in_arom_ring:
        return "carbon", "poly(arylene)"
    # vinyl family: look at side groups
    if any(a.GetSymbol() == "F" for a in m.GetAtoms()):
        return "carbon", "fluorovinyl"
    if m.HasSubstructMatch(PAT["ester"]):
        return "carbon", "acrylic/vinyl-ester"
    if any(a.GetIsAromatic() for a in m.GetAtoms()):
        return "carbon", "styrenic"
    return "carbon", "polyolefin"


def featurize(psmiles_list):
    rows, fps, tax = [], [], []
    for s in psmiles_list:
        m, nl = to_mol(s)
        if m is None:
            rows.append(None); fps.append(None); tax.append((None, None, None)); continue
        fp = MFP.GetCountFingerprintAsNumPy(m).astype(np.float32)
        bv = MFP.GetFingerprint(m)
        l1, l2 = classify(m, nl)
        fl = "F" if any(a.GetSymbol() == "F" for a in m.GetAtoms()) else "noF"
        desc = [
            Descriptors.MolWt(m), m.GetNumHeavyAtoms(),
            rdMolDescriptors.CalcNumAromaticRings(m), rdMolDescriptors.CalcNumRotatableBonds(m),
            rdMolDescriptors.CalcFractionCSP3(m), Descriptors.TPSA(m),
            sum(a.GetSymbol() == "F" for a in m.GetAtoms()) / m.GetNumHeavyAtoms(),
            sum(a.GetSymbol() in ("N", "O") for a in m.GetAtoms()) / m.GetNumHeavyAtoms(),
            Descriptors.MolLogP(m),
        ]
        rows.append(np.concatenate([fp, np.array(desc, dtype=np.float32)]))
        fps.append(bv)
        tax.append((l1, l2, f"{l2}|{fl}"))
    return rows, fps, tax


def tanimoto_matrix(fps_a, fps_b):
    return np.array([DataStructs.BulkTanimotoSimilarity(f, fps_b) for f in fps_a])


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2]
    d = pd.read_csv(src, low_memory=False)
    uniq = d.p_csmiles.drop_duplicates().tolist()
    rows, fps, tax = featurize(uniq)
    t = pd.DataFrame(tax, columns=["L1", "L2", "L3"])
    t["psmiles"] = uniq
    t.to_csv(out, index=False)
    print(t.L1.value_counts(dropna=False).to_string())
    print(t.L2.value_counts(dropna=False).to_string())
