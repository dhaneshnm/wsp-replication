import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
def run(args):
    which, seed = args
    net = CL if which == "claude" else AS
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    c = Counter(); open_req = False
    for t in range(wsp.MAX_STEPS):
        x = ob(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        req = g.oxygen < 60 and g.diver_count >= 1 and g.sub_y > 0
        if req and not open_req: open_req = True; c["req"] += 1
        py, pox = g.sub_y, g.oxygen
        r, done = env.act(a)
        if g.sub_y == 0 and py > 0 and not done:
            if open_req: c["success"] += 1; open_req = False
            else: c["surf_without_req"] += 1
        if done:
            if open_req: c["fail_died"] += 1
            c["oxy_death"] += int(pox <= 0)
            break
    return c
if __name__ == "__main__":
    which = sys.argv[1]; n = int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(which, s) for s in range(n)], chunksize=10))
    tot = Counter(); [tot.update(r) for r in res]
    print(which, dict(tot), "success/req", tot["success"] / tot["req"])
