# Full-width linear O_k: weights w0(c) = a + 2c on the player channel and w4(c) = g - 4c on the trail channel,
# with 2a + g = 20, which gives exactly +2 (facing R) / -2 (facing L) at every column in an otherwise empty row.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlib import *
from probe_lib import obs_of
from concurrent.futures import ProcessPoolExecutor

def build(a):
    g = 20 - 2*a
    net = {k: v.copy() for k, v in CL.items()}
    for k in range(7):
        row = k + 2
        for c in range(10):
            net['W1'][(row*10 + c)*6 + 0, 7 + k] = a + 2*c
            net['W1'][(row*10 + c)*6 + 4, 7 + k] = g - 4*c
    return net

def run(args):
    a, seed = args
    return episode(build(a), seed)

if __name__ == "__main__":
    for a in (1, 10):
        net = build(a)
        bad = [(f, r) for r in (True, False) for f in range(10) if not ((r and f == 0) or ((not r) and f == 9))
               if abs(layers(net, obs_of(5, f, r))['h1'][7+3] - (0.964 if r else -0.964)) > 1e-3]
        with ProcessPoolExecutor(4) as ex:
            res = list(ex.map(run, [(a, s) for s in range(200)], chunksize=5))
        sc = np.array([r[0] for r in res]); L = np.array([r[1] for r in res])
        print(f"full-width O (w0=a+2c, w4={20-2*a}-4c, a={a}): empty-row placements with wrong O: {bad}; "
              f"seeds0-199 mean {sc.mean():.2f} (se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f}) len {L.mean():.1f}", flush=True)
