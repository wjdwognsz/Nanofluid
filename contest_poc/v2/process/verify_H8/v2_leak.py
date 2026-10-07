"""Verifier: (a) target sizes; (b) feature-identical twins that escape key-based source exclusion;
(c) duplicate feature vectors inside a target (train/test twins)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h8_gate as H
TASKS, TARGETS, FEAT = H.load_all()
def fkey(k):
    return FEAT[k].tobytes()
rows = []
for t, (ser, parent) in TARGETS.items():
    tk = list(ser.index)
    tf = {k: fkey(k) for k in tk}
    # within-target feature duplicates
    vc = pd.Series(list(tf.values())).value_counts()
    within = int((vc > 1).sum())
    reals = H.real_pool(TASKS, t, parent)
    twin_src = {}
    for s in reals:
        S = TASKS[s]
        sf = {}
        for k in S.index:
            sf.setdefault(fkey(k), []).append(k)
        n = 0
        for k in tk:
            others = [j for j in sf.get(tf[k], []) if j != k]
            if others:
                n += 1
        if n:
            twin_src[s] = n
    rows.append(dict(target=t, n=len(tk), within_target_feature_dup_groups=within,
                     n_sources_with_twins=len(twin_src), max_twins=max(twin_src.values()) if twin_src else 0,
                     twins=twin_src))
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200)
print(pd.DataFrame(rows).to_string())
