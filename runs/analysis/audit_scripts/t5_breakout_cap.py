import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import os, numpy as np, wsp
from concurrent.futures import ProcessPoolExecutor

def main():
    net = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
    N, W = 200, max(1, (os.cpu_count() or 2) - 1)
    seeds = list(range(N)); chunks = [seeds[i::W] for i in range(W)]
    with ProcessPoolExecutor(W) as ex:
        res = [r for part in ex.map(wsp._worker, [(net, "breakout", c) for c in chunks]) for r in part]
    sc = np.array([r[0] for r in res]); ln = np.array([r[1] for r in res])
    capped = ln == 10_000
    print(f"N={N} mean={sc.mean():.1f} se={sc.std(ddof=1)/np.sqrt(N):.1f} max={sc.max()} mean_len={ln.mean():.1f} "
          f"capped={capped.mean():.3f} score|capped: min={sc[capped].min() if capped.any() else None} max={sc[capped].max() if capped.any() else None} mean={sc[capped].mean() if capped.any() else None}")
    print("published: mean 517.411 max 800.0 mean_length 7417.202")

if __name__ == "__main__":
    main()
