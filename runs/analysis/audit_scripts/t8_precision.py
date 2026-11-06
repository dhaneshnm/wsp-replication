import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
from concurrent.futures import ProcessPoolExecutor

def run(args):
    mode, seeds = args
    import wsp as w
    net = w.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
    if mode == "f64":
        net = {k: v.astype(np.float64) for k, v in net.items()}
        f = w.logits
        w.logits = lambda n, x: f(n, x.astype(np.float64))
    return [w.play_episode(net, "breakout", s)[:2] for s in seeds]

def main():
    seeds = list(range(120)); W = 7
    chunks = [seeds[i::W] for i in range(W)]
    out = {}
    with ProcessPoolExecutor(W) as ex:
        for mode in ("f32", "f64"):
            out[mode] = [r for part in ex.map(run, [(mode, c) for c in chunks]) for r in part]
    a = np.array(out["f32"]); b = np.array(out["f64"])
    print("episodes:", len(a), " identical (score, steps):", int(np.all(a == b, axis=1).sum()),
          " mean f32:", a[:, 0].mean(), " mean f64:", b[:, 0].mean())

if __name__ == "__main__":
    main()
