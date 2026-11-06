import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
def make(variant):
    net = {k: v.copy() for k, v in CL.items()}
    if "nohoriz" in variant:
        net["b3"][1] = -100; net["b3"][3] = -100   # weight edit: left/right never chosen
    if "nodiverT" in variant:
        # weight edit: T units (9..15, rows 2..8) stop reading ch2 (so divers no longer count); ch1 weight doubled so an enemy still counts 0.8
        for k in range(2, 9):
            u = 9 + k - 2
            for c in range(10):
                net["W1"][(k * 10 + c) * 6 + 1, u] *= 2
                net["W1"][(k * 10 + c) * 6 + 2, u] = 0
    return net
def run(args):
    variant, seed = args
    net = make(variant)
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    score = 0
    for t in range(wsp.MAX_STEPS):
        x = ob(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        if "safesurf" in variant and a == 2 and g.oxygen < 60 and g.diver_count >= 1 and g.sub_y >= 1:
            # ORACLE wrapper (not a weight edit): do not climb into a row with an enemy/bullet within 2 cols of the sub
            ty = g.sub_y - 1
            if any(e[1] == ty and abs(e[0] - g.sub_x) <= 2 for e in g.e_fish + g.e_subs + g.e_bullets):
                a = 5
        r, done = env.act(a); score += r
        if done: break
    return score, t + 1
if __name__ == "__main__":
    variant, n = sys.argv[1], int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(variant, s) for s in range(n)], chunksize=10))
    s = np.array([r[0] for r in res]); L = np.array([r[1] for r in res])
    print(f"{variant:20s} mean {s.mean():.2f} se {s.std(ddof=1)/np.sqrt(n):.2f} mean_len {L.mean():.0f}")
