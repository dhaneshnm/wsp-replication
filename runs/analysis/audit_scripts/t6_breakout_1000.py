import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import os, json, numpy as np, wsp
from concurrent.futures import ProcessPoolExecutor

def main():
    game = sys.argv[1]; N = int(sys.argv[2])
    net = wsp.load_npz(f"/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/{game}/hand.npz")
    W = max(1, (os.cpu_count() or 2) - 1)
    seeds = list(range(N)); chunks = [seeds[i::W] for i in range(W)]
    with ProcessPoolExecutor(W) as ex:
        res = [r for part in ex.map(wsp._worker, [(net, game, c) for c in chunks]) for r in part]
    sc = np.array([r[0] for r in res]); ln = np.array([r[1] for r in res])
    np.save(f"{game}_{N}_scores.npy", np.stack([sc, ln]))
    capped = ln == 10_000
    print(f"{game} N={N} mean={sc.mean():.2f} se={sc.std(ddof=1)/np.sqrt(N):.2f} max={sc.max()} mean_len={ln.mean():.1f} capped_frac={capped.mean():.3f}")
    print("  episodes with score > 800:", int((sc > 800).sum()), " >= 800:", int((sc >= 800).sum()))
    if capped.any():
        print("  capped-episode score percentiles 1/10/50/90/99:", np.percentile(sc[capped], [1, 10, 50, 90, 99]))
    pub = json.load(open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/eval/minatar_eval.json"))[game]["hand"]
    print("  published:", pub)

if __name__ == "__main__":
    main()
