import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3")
import wsp, trace as T, pickle, numpy as np
from concurrent.futures import ProcessPoolExecutor
NETS = {"claude": "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz",
        "astra": "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz"}
def work(args):
    name, seeds = args
    net = wsp.load_npz(NETS[name])
    out = []
    for s in seeds:
        r = T.run(net, s)
        r.pop("last_x", None)
        out.append(r)
    return out
if __name__ == "__main__":
    name = sys.argv[1]; N = int(sys.argv[2])
    seeds = list(range(N))
    chunks = [(name, seeds[i::4]) for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        res = [r for part in ex.map(work, chunks) for r in part]
    res.sort(key=lambda r: r["seed"])
    pickle.dump(res, open(f"{sys.argv[3]}/{name}_{N}.pkl", "wb"))
    sc = np.array([r["score"] for r in res]); print(name, "mean", sc.mean(), "se", sc.std(ddof=1)/np.sqrt(len(sc)))
