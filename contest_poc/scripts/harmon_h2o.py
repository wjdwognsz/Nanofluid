"""Harmonization demo: how much do test conditions (temperature, water activity) move
reported H2O transport values for the SAME polymer? (analogue of textile WVTR method/condition mismatch)"""
import sys, numpy as np, pandas as pd
d = pd.read_csv(sys.argv[1], low_memory=False)
for prop in ["p_exp_H2O", "d_exp_H2O", "s_exp_H2O"]:
    g = d[d.property == prop]
    multi = g.groupby("p_csmiles").filter(lambda x: len(x) > 1)
    spread = multi.groupby("p_csmiles").value.agg(lambda v: v.max() - v.min())
    nconds = multi.groupby("p_csmiles").apply(lambda x: x[["Temp", "Activity"]].drop_duplicates().shape[0])
    print(f"{prop}: rows={len(g)} polymers={g.p_csmiles.nunique()} polymers_with_multiple_conditions={multi.p_csmiles.nunique()}")
    if len(spread):
        print(f"   within-polymer max-min of log10 value across conditions: median={spread.median():.2f} "
              f"(={10**spread.median():.1f}x) max={spread.max():.2f} (={10**spread.max():.0f}x); conditions per polymer median={nconds.median()}")
    between = g.groupby("p_csmiles").value.mean()
    print(f"   between-polymer SD of log10 value = {between.std():.2f}")
    # activity effect within polymer: slope of log value vs activity
    sl = []
    for s, x in multi.groupby("p_csmiles"):
        if x.Activity.nunique() > 1 and x.Temp.nunique() == 1:
            sl.append(np.polyfit(x.Activity, x.value, 1)[0])
    if sl:
        print(f"   within-polymer slope dlog10/dActivity (isothermal): median={np.median(sl):.2f}, n={len(sl)}")
