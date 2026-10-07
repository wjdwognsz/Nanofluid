import sys, pandas as pd, itertools
sys.path.insert(0, "/home/user/Nanofluid/contest_poc/v2/scripts")
import h8_gate as H
TASKS, TARGETS, FEAT = H.load_all()
ks = {t: set(s.index) for t, (s, p) in TARGETS.items()}
for a, b in itertools.combinations(ks, 2):
    o = len(ks[a] & ks[b])
    if o >= 10: print(f"{a:16s} {b:16s} overlap {o:3d}  ({o/min(len(ks[a]),len(ks[b])):.0%} of smaller)")
