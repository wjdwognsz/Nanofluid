import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h8_gate as H
TASKS, TARGETS, FEAT = H.load_all()
for t in ["d_exp_He", "d_exp_CO2", "s_exp_He"]:
    ser, parent = TARGETS[t]
    src = TASKS["p_exp_CO2"] if t != "d_exp_CO2" else TASKS["p_exp_CO2"]
    sf = {}
    for k in src.index: sf.setdefault(FEAT[k].tobytes(), []).append(k)
    for k in ser.index:
        o = [j for j in sf.get(FEAT[k].tobytes(), []) if j != k]
        if o:
            print(t, "| target key:", k, "y=%.3f" % ser[k], "| twin in p_exp_CO2:", o, [round(src[j], 3) for j in o],
                  "| target key itself in source:", k in src.index)
    # within-target dup
    vc = {}
    for k in ser.index: vc.setdefault(FEAT[k].tobytes(), []).append(k)
    for v in vc.values():
        if len(v) > 1: print(t, "within-target twins:", v, [round(ser[j], 3) for j in v])
