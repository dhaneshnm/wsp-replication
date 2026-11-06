# Score both nets with sticky 0.0 (seeds 0..199, same softmax sampling), using my own loop.
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from concurrent.futures import ProcessPoolExecutor
NETS = nets()
def job(args):
    name, seed, st = args
    o = episode(NETS[name], seed, sticky=st)
    return o["score"], o["steps"], o["done"]
if __name__ == "__main__":
    for st in (0.0,):
        for name in ("claude", "astra"):
            t0 = time.time()
            with ProcessPoolExecutor(4) as ex:
                r = list(ex.map(job, [(name, s, st) for s in range(200)], chunksize=5))
            sc = np.array([x[0] for x in r]); L = np.array([x[1] for x in r])
            print(f"{name} sticky={st}: n={len(sc)} mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f} mean_len {L.mean():.0f} capped {sum(not x[2] for x in r)} ({time.time()-t0:.0f}s)", flush=True)
