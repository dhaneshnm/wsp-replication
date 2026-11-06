"""Run my runner (sticky 0.1 and 0.0) and wsp.play_episode on seeds 0..199 for both nets; save results."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep")
import pickle, time
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import wsp, myrun

OUT = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep/"


def official(args):
    path, seeds = args
    net = wsp.load_npz(path)
    return [(s,) + tuple(wsp.play_episode(net, "seaquest", s)[:2]) for s in seeds]


if __name__ == "__main__":
    which = sys.argv[1]
    seeds = list(range(200))
    for name, path in [("claude", myrun.CLAUDE), ("astra", myrun.ASTRA)]:
        t0 = time.time()
        if which == "official":
            with ProcessPoolExecutor(4) as ex:
                res = sorted(r for part in ex.map(official, [(path, seeds[i::4]) for i in range(4)]) for r in part)
            sc = np.array([r[1] for r in res])
        else:
            sticky = float(which)
            res = myrun.run_many(path, seeds, sticky=sticky)
            sc = np.array([r["score"] for r in res])
        pickle.dump(res, open(OUT + f"{name}_{which}.pkl", "wb"))
        print(name, which, "mean", round(sc.mean(), 3), "se", round(sc.std(ddof=1) / np.sqrt(len(sc)), 3),
              "time", round(time.time() - t0))
