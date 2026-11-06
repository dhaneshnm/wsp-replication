import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import pickle
for which in ["claude", "astra"]:
    res = pickle.load(open(f"episodes_{which}_200.pkl", "rb"))
    sc = np.array([r["score"] for r in res]); ln = np.array([r["steps"] for r in res]); done = np.array([r["done"] for r in res])
    print(f"===== {which}: mean {sc.mean():.2f}, median {np.median(sc)}, misses {done.sum()}, cap {(~done).sum()}")
    print("  score percentiles 10/25/50/75/90:", np.percentile(sc, [10, 25, 50, 75, 90]))
    print("  score among miss-ended:", f"mean {sc[done].mean():.2f}", "among cap-ended:", f"mean {sc[~done].mean():.2f}" if (~done).any() else "-")
    print("  length among miss-ended: mean", ln[done].mean(), "median", np.median(ln[done]))
    print("  score histogram bins:", np.histogram(sc, bins=[0,1,5,10,20,29,30,31,60,90,120,300,1000])[0].tolist(), "edges [0,1,5,10,20,29,30,31,60,90,120,300,1000]")
    # last reward time and loops for cap-ended
    cap = [r for r in res if not r["done"]]
    lastr = np.array([r["rewards_t"][-1] if r["rewards_t"] else -1 for r in cap])
    loops = [r["loop"] for r in cap]
    print("  cap-ended: last reward step median", np.median(lastr) if len(lastr) else None, "max", lastr.max() if len(lastr) else None)
    print("  cap-ended: exact-state loop detected in", sum(l is not None for l in loops), "/", len(cap))
    per = [l[1]-l[0] for l in loops if l is not None]
    if per: print("  loop periods (steps) histogram:", np.unique(per, return_counts=True))
    be = np.array([r["bricks_end"] for r in cap])
    if len(be): print("  cap-ended bricks remaining: ", np.unique(be, return_counts=True))
    # steps after last reward for all episodes
    gap = np.array([r["steps"] - 1 - (r["rewards_t"][-1] if r["rewards_t"] else 0) for r in res])
    print("  steps between last reward and episode end: median", np.median(gap), "share >2000:", (gap > 2000).mean())
    refills = np.array([r["refills"] for r in res])
    print("  walls refilled per episode: ", np.unique(refills, return_counts=True))
    # points per 1000 steps among capped
    if len(cap): print("  capped episodes: mean score", np.mean([r['score'] for r in cap]))
