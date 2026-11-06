import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from concurrent.futures import ProcessPoolExecutor
def run(args):
    which, seed = args
    net = CL if which == "claude" else AS
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    k300 = s300 = 0
    for t in range(wsp.MAX_STEPS):
        x = ob(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p)); py, pdc = g.sub_y, g.diver_count
        r, done = env.act(a)
        bonus = (g.sub_y == 0 and py > 0 and pdc == 6)
        if t < 300:
            s300 += 1; k300 += 0 if bonus else r
        if done or t >= 300: break
    return k300, s300
if __name__ == "__main__":
    for w in ["claude", "astra"]:
        with ProcessPoolExecutor(4) as ex:
            res = list(ex.map(run, [(w, s) for s in range(200)], chunksize=10))
        k = sum(r[0] for r in res); s = sum(r[1] for r in res)
        print(w, "kills per 100 steps within first 300 steps:", round(100 * k / s, 3), "steps", s)
