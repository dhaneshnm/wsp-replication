"""Run 200 episodes (seeds 0-199) with my runner for: Claude sticky 0.1, Claude sticky 0.0, Astra sticky 0.1.
Saves per-episode results (death step details, aggregates) to pickles."""
import sys
HERE = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1/indep_verify"
sys.path.insert(0, HERE)
import pickle
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import common, wsp


def job(args):
    path, seeds, sticky = args
    net = wsp.load_npz(path)
    return [common.run(net, s, sticky=sticky) for s in seeds]


def run_many(path, sticky, n=200):
    seeds = list(range(n))
    chunks = [(path, seeds[i::4], sticky) for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        out = [r for part in ex.map(job, chunks) for r in part]
    return sorted(out, key=lambda r: r["seed"])


if __name__ == "__main__":
    which = sys.argv[1]
    cfg = {"claude01": (common.CLAUDE, 0.1), "claude00": (common.CLAUDE, 0.0), "astra01": (common.ASTRA, 0.1)}[which]
    res = run_many(*cfg)
    sc = np.array([r["score"] for r in res]); ln = np.array([r["length"] for r in res])
    print(which, "episodes", len(res), "mean score", sc.mean(), "se", sc.std(ddof=1) / np.sqrt(len(sc)),
          "mean length", ln.mean(), "all ended by death:", all(r["done"] for r in res),
          "collision-model mismatches:", sum(r["mismatch"] for r in res))
    pickle.dump(res, open(f"{HERE}/main_{which}.pkl", "wb"))
