import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3")
import wsp, trace as T, numpy as np
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
NETS = {"claude": "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz",
        "astra": "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz"}
def work(args):
    name, seeds, sticky = args
    net = wsp.load_npz(NETS[name])
    return [(r["score"], r["steps"], r["cause"], r["kills"]) for r in (T.run(net, s, sticky=sticky) for s in seeds)]
if __name__ == "__main__":
    name, N, sticky = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    seeds = list(range(N))
    with ProcessPoolExecutor(4) as ex:
        res = [r for part in ex.map(work, [(name, seeds[i::4], sticky) for i in range(4)]) for r in part]
    sc = np.array([r[0] for r in res]); st = np.array([r[1] for r in res])
    print(name, "sticky", sticky, "mean", round(sc.mean(), 2), "se", round(sc.std(ddof=1)/np.sqrt(N), 2), "steps", round(st.mean()), "causes", dict(Counter(r[2] for r in res)))
