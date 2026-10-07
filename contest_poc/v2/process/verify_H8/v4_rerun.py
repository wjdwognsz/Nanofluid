"""Verifier re-runs of h8_gate.run_chunk, outputs only under process/verify_H8/.
mode 'seed'  : unmodified code, new outer repeats (fold seed + target-RF seed) -> seed_parts/
mode 'featex': source exclusion by FEATURE identity (catches cis/trans-annotated duplicates of a
               test polymer that escape key-based exclusion), same repeats as original -> featex_parts/
usage: python v4_rerun.py mode:target:rep [mode:target:rep ...]"""
import os, sys, time
import numpy as np
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h8_gate as H
VD = "/home/user/Nanofluid/contest_poc/v2/process/verify_H8"
_orig = H.crossfit_source

def crossfit_featex(S, Xof, tkeys, fold_list):
    TASKS, TARGETS, FEAT = H.load_all()
    cache, g, nfit = {}, np.zeros(len(tkeys)), 0
    sfb = {k: FEAT[k].tobytes() for k in S.index}
    for _, te in fold_list:
        tb = {FEAT[tkeys[i]].tobytes() for i in te}
        excl = frozenset(k for k in S.index if sfb[k] in tb) | (frozenset(tkeys[i] for i in te) & set(S.index))
        if excl not in cache:
            sk = [k for k in S.index if k not in excl]
            cache[excl] = H.src_rf().fit(Xof(sk), S.loc[sk].values)
            nfit += 1
        g[te] = cache[excl].predict(Xof([tkeys[i] for i in te]))
    return g, nfit

for job in sys.argv[1:]:
    mode, t, rep = job.split(":")
    out = f"{VD}/{mode}_parts"
    os.makedirs(out, exist_ok=True)
    if os.path.exists(f"{out}/h8_{t}_r{rep}_meta.json"):
        print("skip", job, flush=True); continue
    H.PARTS = out
    H.crossfit_source = crossfit_featex if mode == "featex" else _orig
    t0 = time.time()
    H.run_chunk(t, int(rep))
    print("done", job, round(time.time() - t0), "s", flush=True)
