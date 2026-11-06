import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/refute")
import wsp, rf_runner as R, pickle, numpy as np
from concurrent.futures import ProcessPoolExecutor
def getnet(cfg):
    if cfg.startswith("claude"): n = wsp.load_npz(R.CLAUDE)
    else: n = wsp.load_npz(R.ASTRA)
    if "guard2" in cfg: n = R.guard2(n)
    return n
def work(args):
    cfg, seeds = args
    net = getnet(cfg)
    if cfg.endswith("_pe"):
        return [dict(seed=s, pe=wsp.play_episode(net, "seaquest", s)[:2]) for s in seeds]
    st = 0.0 if "sticky0" in cfg else None
    return [R.run(net, s, sticky=st) for s in seeds]
if __name__ == "__main__":
    cfg = sys.argv[1]; N = 200
    seeds = list(range(N))
    with ProcessPoolExecutor(4) as ex:
        res = [r for part in ex.map(work, [(cfg, seeds[i::4]) for i in range(4)]) for r in part]
    res.sort(key=lambda r: r["seed"])
    pickle.dump(res, open(f"rf_{cfg}.pkl", "wb"))
    if cfg.endswith("_pe"):
        sc = np.array([r["pe"][0] for r in res])
    else:
        sc = np.array([r["score"] for r in res])
    print(cfg, "N", len(sc), "mean", round(sc.mean(), 2), "se", round(sc.std(ddof=1) / np.sqrt(len(sc)), 2), flush=True)
