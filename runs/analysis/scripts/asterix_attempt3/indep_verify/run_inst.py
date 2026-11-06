# Instrumented 200-episode runs (seeds 0..199, sticky 0.1) for both nets; stores per-step logs.
import sys, os, pickle, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from concurrent.futures import ProcessPoolExecutor
NETS = nets()
def job(args):
    name, seed = args
    out = episode(NETS[name], seed, sticky=0.1, instrument=True)
    # compute counterfactual outcomes at the death step here (snapshot is pre-act, post sticky draw)
    if out["done"]:
        out["cf"] = {k: counterfactual_dies(out["death_snap"], k) for k in range(6)}
    out["death_snap"] = None
    return out
if __name__ == "__main__":
    for name in ("claude", "astra"):
        t0 = time.time()
        with ProcessPoolExecutor(4) as ex:
            res = list(ex.map(job, [(name, s) for s in range(200)], chunksize=5))
        pickle.dump(res, open(f"my_inst_{name}.pkl", "wb"))
        sc = np.array([r["score"] for r in res]); L = np.array([r["steps"] for r in res])
        print(name, "n", len(res), "mean %.2f se %.3f" % (sc.mean(), sc.std(ddof=1)/np.sqrt(len(sc))),
              "mean_len %.2f median_len %.1f" % (L.mean(), np.median(L)), "capped", int((~np.array([r['done'] for r in res])).sum()),
              "secs %.0f" % (time.time()-t0), flush=True)
