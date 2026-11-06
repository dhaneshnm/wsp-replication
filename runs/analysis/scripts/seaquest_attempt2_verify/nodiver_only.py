# Isolate "remove diver steering" from the bullet-weight change in experiments.py's nodiverD:
# D_k computed from an observation with diver-only cells (reward ch2 without danger ch1) removed; everything else unchanged.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from experiments import variant
def run(args):
    mode, seed = args
    NET = CL if mode == 'divOnly' else variant('nodiverD')
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    sc = 0
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1 = np.tanh(x @ NET["W1"] + NET["b1"])
        if mode == 'divOnly':
            g = x.reshape(10,10,6).copy()
            diver_only = (g[..., 2] > 0) & (g[..., 1] == 0)
            g[..., 2][diver_only] = 0
            x2 = g.reshape(600)
            h1[14:21] = np.tanh(x2 @ NET["W1"][:, 14:21] + NET["b1"][14:21])
        h2 = np.tanh(h1 @ NET["W2"] + NET["b2"]); z = h2 @ NET["W3"] + NET["b3"]
        p = np.exp(z - z.max()); p /= p.sum(); a = int(rng.choice(6, p=p))
        r, done = env.act(a); sc += r
        if done: return sc, t+1
    return sc, wsp.MAX_STEPS
if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    for mode in sys.argv[1:]:
        with ProcessPoolExecutor(4) as ex: res = list(ex.map(run, [(mode, s) for s in range(200)], chunksize=10))
        sc = np.array([r[0] for r in res]); L = np.array([r[1] for r in res])
        print(f"{mode:10s} mean {sc.mean():6.2f} (se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f}) len {L.mean():7.1f}", flush=True)
