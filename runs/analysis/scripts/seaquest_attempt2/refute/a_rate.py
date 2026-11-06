import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pickle, numpy as np
D = os.path.dirname(os.path.abspath(__file__))
for nm in ('claude', 'astra'):
    R = pickle.load(open(os.path.join(D, f"rec_{nm}.pkl"), "rb"))
    for lo, hi in ((0, 100), (0, 300), (300, 1000), (1000, 10000)):
        pts = sum(s['r'] for r in R for s in r['steps'] if lo <= s['t'] < hi)
        n = sum(1 for r in R for s in r['steps'] if lo <= s['t'] < hi)
        print(f"{nm:6s} steps t in [{lo},{hi}): {n:7d} steps, points/step {pts/max(n,1):.4f}")
