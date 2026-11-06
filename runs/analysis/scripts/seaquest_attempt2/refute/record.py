# Record every step of seeds 0..199 for one net (my own recorder). Output: rec_<net>.pkl
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlib import *
import pickle
from concurrent.futures import ProcessPoolExecutor

def one(args):
    nm, seed = args
    net = CL if nm == 'claude' else AS
    steps = []
    end = {}
    def cb(t, pre, out, a, ae, r, done, g):
        h1, h2 = out['h1'], out['h2']
        rec = dict(t=t, pre=pre, a=a, ae=ae, r=r, p=out['p'].astype(np.float32))
        if nm == 'claude':
            k = pre['sy'] - 2
            if 0 <= k <= 6:
                rec.update(V=float(h1[k]), O=float(h1[7+k]), D=float(h1[14+k]), Y=float(h1[21+k]))
            rec.update(S=float(h1[28]), R01=float(h1[29]), h2=(h2[:16] > 0))
            rec['ch1_rowabove_2to7'] = bool(out['x'].reshape(10,10,6)[pre['sy']-1, 2:8, 1].any()) if pre['sy'] >= 1 else False
        else:
            # keep Astra records light
            rec = dict(t=t, pre=dict(sx=pre['sx'], sy=pre['sy'], sor=pre['sor'], dc=pre['dc'], oxy=pre['oxy']), a=a, ae=ae, r=r)
        steps.append(rec)
        if done:
            end['cause'] = end_cause(pre, g)
            end['post'] = snapshot(g)
    score, n = episode(net, seed, step_cb=cb)
    return dict(seed=seed, score=score, n=n, steps=steps, **end)

if __name__ == "__main__":
    nm = sys.argv[1]
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(one, [(nm, s) for s in range(200)], chunksize=5))
    pickle.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"rec_{nm}.pkl"), "wb"))
    sc = np.array([r['score'] for r in res]); L = np.array([r['n'] for r in res])
    print(nm, "mean score", sc.mean(), "mean len", L.mean(), "total steps", L.sum())
