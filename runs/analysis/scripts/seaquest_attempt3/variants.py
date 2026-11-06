"""Diagnostic variants of Claude's net (in-memory copies only) to test the two failure hypotheses."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3")
import numpy as np, wsp, copy, trace as T
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
BASE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz"
def variant(name):
    n = wsp.load_npz(BASE)
    if name in ("surf60", "both"):   # SURF reads gauge cols 2,3,4 instead of 1,2,3 -> fires ~20 oxygen earlier
        n["W1"][551, 26] = 0; n["W1"][557, 26] = -12; n["W1"][563, 26] = -24; n["W1"][569, 26] = 24
    if name in ("guard2", "both"):   # also veto a vertical move when the row two away is unsafe (sticky double move)
        for r in range(3, 9):        # Up_r = unit r-1, row r-2 danger = unit 17 + (r-2) - 1
            n["W2"][17 + r - 3, r - 1] = -75; n["b2"][r - 1] -= 75
        n["W2"][18, 8] = -75; n["b2"][8] -= 75          # Down_0 also checks row 2
        for r in range(1, 7):        # Down_r = unit 8 + r, row r+2 danger = unit 17 + r + 1
            n["W2"][17 + r + 1, 8 + r] = -75; n["b2"][8 + r] -= 75
    return n
def work(args):
    name, seeds = args; net = variant(name)
    return [(r["score"], r["steps"], r["cause"]) for r in (T.run(net, s) for s in seeds)]
if __name__ == "__main__":
    name = sys.argv[1]
    if name == "table":
        n = variant("surf60"); env = wsp._make_env("seaquest", 0); obsf = wsp.make_obs_fn(env, "seaquest"); E = env.env
        for oxy in [100, 80, 79, 60, 59, 40, 39]:
            row = []
            for d in range(7):
                E.reset(); E.sub_x, E.sub_y, E.oxygen, E.diver_count = 8, 4, oxy, d
                h = np.tanh(obsf() @ n["W1"] + n["b1"]); row.append(("H" if h[25] > 0 else "-") + ("S" if h[26] > 0 else "-"))
            print(oxy, row)
        sys.exit()
    seeds = list(range(200))
    with ProcessPoolExecutor(4) as ex:
        res = [r for part in ex.map(work, [(name, seeds[i::4]) for i in range(4)]) for r in part]
    sc = np.array([r[0] for r in res])
    print(name, "mean", round(sc.mean(), 2), "se", round(sc.std(ddof=1) / np.sqrt(len(sc)), 2), "steps", round(np.mean([r[1] for r in res])), dict(Counter(r[2] for r in res)))
