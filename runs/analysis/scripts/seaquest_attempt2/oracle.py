# Diagnostic: override individual first-layer units with ground truth from the game state, to measure what each
# misreading costs. Not a network the reply could have written; used only to attribute the score.
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

from experiments import variant
_NETS = {}
def forward_override(x, e, mode):
    key = 'nodiverD' if 'ndD' in mode else 'base'
    if key not in _NETS: _NETS[key] = variant(key)
    NET = _NETS[key]
    h1 = np.tanh(x @ NET["W1"] + NET["b1"])
    sy, sx = e.sub_y, e.sub_x
    if 2 <= sy <= 8:
        k = sy - 2
        if 'Oor' in mode:
            h1[7+k] = 0.964 if e.sub_or else -0.964
        if 'Yor' in mode:
            h1[21+k] = 0.905 if any(b[1] == sy for b in e.e_bullets) else -0.905
        if 'Drel' in mode:   # side-of-target measured relative to the sub's front cell instead of absolute columns
            g = x.reshape(10,10,6)
            pre = 0.0
            for c in range(10):
                if c == sx: continue
                sgn = 1 if c > sx else -1
                pre += sgn * 0.6 * (g[sy, c, 1] + g[sy, c, 2])
            pre += 0.06 * (9 - (sx + (sx-1 if e.sub_or else sx+1)))  # same re-centre term as the reply
            h1[14+k] = np.tanh(pre)
    h2 = np.tanh(h1 @ NET["W2"] + NET["b2"])
    z = h2 @ NET["W3"] + NET["b3"]
    p = np.exp(z - z.max()); return p / p.sum()

def run(args):
    mode, seed = args
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    sc = 0
    for t in range(wsp.MAX_STEPS):
        p = forward_override(obs(), e, mode); a = int(rng.choice(6, p=p))
        pre_dc, pre_oxy, pre_sy = e.diver_count, e.oxygen, e.sub_y
        r, done = env.act(a); sc += r
        if done:
            cause = 'surface_no_diver' if (e.sub_y == 0 and pre_sy > 0 and pre_dc == 0) else ('oxygen' if pre_oxy <= 0 else 'collision')
            return sc, t+1, cause
    return sc, wsp.MAX_STEPS, 'cap'

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    for mode in sys.argv[1:]:
        with ProcessPoolExecutor(4) as ex: res = list(ex.map(run, [(mode, s) for s in range(200)], chunksize=10))
        sc = np.array([r[0] for r in res]); L = np.array([r[1] for r in res])
        print(f"{mode:16s} mean {sc.mean():6.2f} (se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f}) len {L.mean():7.1f} deaths {dict(collections.Counter(r[2] for r in res))}", flush=True)
