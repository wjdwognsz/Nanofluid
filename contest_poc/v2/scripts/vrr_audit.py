"""VRR v2 audit rules R1-R4 (PREREG section 2, H5). Reusable: audit(ds) -> DataFrame of boolean flags per rule.

The rules only look at the dataset object itself (values, conditions, source ids, keys). They never see which rows were
injected in H5a. Parts that PREREG leaves open are fixed here (written before any H5 test was run; see process/h5h7_log.md):

R1  physical range
    target: density 0.5-3.0 g/cm3 (DES_RHO, y_raw), viscosity 0.2-1e7 cP (DES_ETA, y_raw),
            fiber diameter 10-50,000 nm (ES1 fiber_diameter_nm, ES2 D), temperature 150-500 K when the target is a
            temperature (DES_MP melting T). DYE exhaustion and IL_CELL solubility have no PREREG bound -> not checked.
    temperature columns: 150-500 K. DES T is K; ES1 temperature_c, DYE T, IL_CELL T are degC (+273.15 before checking).
            Missing / imputed temperatures are not checked.
R2  robust z (|z| > 5) on the modelling scale ds.y
    R2a within ds.material groups with >= 3 rows: (y - median) / (1.4826 MAD), scale floored at 0.05 x dataset robust scale
    R2b out-of-source residuals: RF (make_model "RF", seed 0), GroupKFold(10) by source (group_folds seed 0),
        z = (r - median r) / (1.4826 MAD r)
R3  copy: same key AND same value (|rel diff| <= 1e-4 on y_raw if present else y) exists in a *different* source.
    Both members of a pair are flagged.
R4  default concentration on ambient / measurement condition columns (DES_RHO, DES_ETA: T; ES1: rh, temperature_c;
    none for ES2, DYE, IL_CELL, DES_MP): mode of the reported values; a source with > 40 % of its reported rows equal
    to the mode is suspicious; its rows equal to the mode are flagged.
"""
import numpy as np
import pandas as pd

from vrr_common import make_model, group_folds

Z_THR = 5.0
R2A_MIN_GROUP = 3
R2A_SCALE_FLOOR = 0.05
R3_RTOL = 1e-4
R4_FRAC = 0.40

# dataset family -> rule configuration
CFG = {
    "DES_RHO": dict(y_range=("y_raw", 0.5, 3.0, "density g/cm3"), temp_cols=[("T", "K", None)], r4_cols=[("T", None)]),
    "DES_ETA": dict(y_range=("y_raw", 0.2, 1e7, "viscosity cP"), temp_cols=[("T", "K", None)], r4_cols=[("T", None)]),
    "DES_MP": dict(y_range=("y_raw", 150.0, 500.0, "melting temperature K"), temp_cols=[], r4_cols=[]),
    "ES1": dict(y_range=("fiber_diameter_nm", 10.0, 5e4, "fiber diameter nm"),
                temp_cols=[("temperature_c", "C", "temperature_c_missing")],
                r4_cols=[("rh", "rh_missing"), ("temperature_c", "temperature_c_missing")]),
    "ES2": dict(y_range=("D", 10.0, 5e4, "fiber diameter nm"), temp_cols=[], r4_cols=[]),
    "DYE": dict(y_range=None, temp_cols=[("T", "C", None)], r4_cols=[]),
    "IL_CELL": dict(y_range=None, temp_cols=[("T", "C", None)], r4_cols=[]),
}
T_LO, T_HI = 150.0, 500.0
RULES = ["R1", "R2", "R3", "R4"]


def family(name):
    for k in sorted(CFG, key=len, reverse=True):
        if name.startswith(k):
            return k
    raise KeyError(f"no audit configuration for dataset {name}")


def _robust_z(v, center=None, scale=None):
    v = np.asarray(v, float)
    c = np.median(v) if center is None else center
    s = 1.4826 * np.median(np.abs(v - c)) if scale is None else scale
    return (v - c) / s if s > 0 else np.zeros_like(v)


def rule_r1(ds, cfg):
    n = len(ds.y)
    r1y = np.zeros(n, bool)
    r1t = np.zeros(n, bool)
    if cfg["y_range"] is not None:
        col, lo, hi, _ = cfg["y_range"]
        v = ds.df[col].values.astype(float)
        r1y = (v < lo) | (v > hi)
    for col, unit, miss in cfg["temp_cols"]:
        v = ds.df[col].values.astype(float)
        k = v + 273.15 if unit == "C" else v
        bad = (k < T_LO) | (k > T_HI)
        if miss is not None:
            bad &= ds.df[miss].values == 0
        r1t |= bad & ~np.isnan(v)
    return r1y, r1t


def rule_r2(ds, seed=0, model="RF", n_folds=10):
    y = np.asarray(ds.y, float)
    gscale = 1.4826 * np.median(np.abs(y - np.median(y)))
    floor = R2A_SCALE_FLOOR * gscale
    za = np.zeros(len(y))
    mat = pd.Series(ds.material)
    for _, idx in mat.groupby(mat).indices.items():
        if len(idx) < R2A_MIN_GROUP:
            continue
        v = y[idx]
        med = np.median(v)
        sc = max(1.4826 * np.median(np.abs(v - med)), floor)
        if sc > 0:
            za[idx] = (v - med) / sc
    pred = np.full(len(y), np.nan)
    for tr, te in group_folds(ds.group, n_folds, seed):
        pred[te] = make_model(model, seed).fit(ds.X[tr], y[tr]).predict(ds.X[te])
    res = y - pred
    zb = _robust_z(res)
    return np.abs(za) > Z_THR, np.abs(zb) > Z_THR, za, zb, pred


def rule_r3(ds):
    vals = ds.df["y_raw"].values.astype(float) if "y_raw" in ds.df else np.asarray(ds.y, float)
    d = pd.DataFrame({"k": ds.key, "g": ds.group, "v": vals})
    flag = np.zeros(len(d), bool)
    ng = d.groupby("k").g.nunique()
    multi = d[d.k.isin(ng[ng > 1].index)]
    for _, sub in multi.groupby("k"):
        idx, gs, vs = sub.index.values, sub.g.values, sub.v.values
        for a in range(len(idx)):
            for b in range(len(idx)):
                if gs[a] == gs[b]:
                    continue
                if abs(vs[a] - vs[b]) <= R3_RTOL * max(abs(vs[a]), abs(vs[b]), 1e-12):
                    flag[idx[a]] = True
                    break
    return flag


def rule_r4(ds, cfg):
    n = len(ds.y)
    flag = np.zeros(n, bool)
    detail = {}
    for col, miss in cfg["r4_cols"]:
        v = ds.df[col].values.astype(float)
        rep = ~np.isnan(v)
        if miss is not None:
            rep &= ds.df[miss].values == 0
        if rep.sum() == 0:
            continue
        mode = pd.Series(v[rep]).round(6).mode().values[0]
        eq = rep & np.isclose(v, mode, rtol=1e-6, atol=1e-9)
        g = pd.Series(ds.group)
        frac = pd.Series(eq).groupby(g).sum() / pd.Series(rep).groupby(g).sum().replace(0, np.nan)
        sus = set(frac[frac > R4_FRAC].index)
        f = eq & g.isin(sus).values
        flag |= f
        detail[col] = dict(mode=float(mode), n_sources_flagged=len(sus), n_rows_flagged=int(f.sum()))
    return flag, detail


def audit(ds, seed=0, model="RF", return_detail=False):
    """Apply R1-R4 to a DS. Returns a DataFrame (one row per ds row) with boolean columns
    R1, R1_y, R1_T, R2, R2a, R2b, R3, R4, any, R12 (= R1 | R2), the z-scores and a 'reasons' string."""
    cfg = CFG[family(ds.name)]
    r1y, r1t = rule_r1(ds, cfg)
    r2a, r2b, za, zb, pred = rule_r2(ds, seed=seed, model=model)
    r3 = rule_r3(ds)
    r4, r4d = rule_r4(ds, cfg)
    out = pd.DataFrame({"R1_y": r1y, "R1_T": r1t, "R2a": r2a, "R2b": r2b, "R3": r3, "R4": r4,
                        "z_material": za, "z_residual": zb, "oof_pred": pred})
    out["R1"] = out.R1_y | out.R1_T
    out["R2"] = out.R2a | out.R2b
    out["R12"] = out.R1 | out.R2
    out["any"] = out.R1 | out.R2 | out.R3 | out.R4
    sub = ["R1_y", "R1_T", "R2a", "R2b", "R3", "R4"]
    M = out[sub].values
    out["reasons"] = ["+".join(s for s, f in zip(sub, row) if f) for row in M]
    if return_detail:
        return out, {"family": family(ds.name), "r4": r4d,
                     "r1_y_range": cfg["y_range"], "r1_temp_cols": cfg["temp_cols"]}
    return out
