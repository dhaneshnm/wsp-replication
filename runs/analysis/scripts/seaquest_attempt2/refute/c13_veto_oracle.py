# h2-level oracle: when the sub is in rows 2..8 and there is no fish/sub/bullet in cols 2..7 of the row above,
# force the up-veto unit (h2[3]) off. Counts end causes on seeds 0..199 vs the unmodified net.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlib import *
import collections
from concurrent.futures import ProcessPoolExecutor

def run(args):
    mode, seed = args
    env = wsp._make_env("seaquest", seed); g = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    sc = 0.0
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1 = np.tanh(x @ CL['W1'] + CL['b1'])
        h2 = np.tanh(h1 @ CL['W2'] + CL['b2'])
        if mode == 'oracle' and 2 <= g.sub_y <= 8:
            row = g.sub_y - 1
            if not any(e[1] == row and 2 <= e[0] <= 7 for e in g.e_fish + g.e_subs + g.e_bullets):
                h2[3] = -1.0
        z = h2 @ CL['W3'] + CL['b3']; p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        pre = dict(sy=g.sub_y, dc=g.diver_count, oxy=g.oxygen)
        r, done = env.act(a); sc += r
        if done:
            return sc, t + 1, end_cause(pre, g), pre['dc']
    return sc, wsp.MAX_STEPS, 'cap', None

if __name__ == "__main__":
    for mode in ('base', 'oracle'):
        with ProcessPoolExecutor(4) as ex:
            res = list(ex.map(run, [(mode, s) for s in range(200)], chunksize=5))
        sc = np.array([r[0] for r in res])
        cz = collections.Counter(r[2] for r in res)
        oxd = sum(1 for r in res if r[2] == 'oxygen' and r[3] and r[3] > 0)
        print(f"{mode:7s} mean {sc.mean():.2f} len {np.mean([r[1] for r in res]):.1f} causes {dict(cz)} oxygen deaths with divers aboard {oxd}")
