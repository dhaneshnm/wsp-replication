import sys, os, json, copy, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

def variant(name):
    if name == 'astra': return {k: v.copy() for k, v in AS.items()}
    n = {k: v.copy() for k, v in CL.items()}
    parts = name.split('+')
    for v in parts:
        if v == 'base': pass
        elif v == 'Ofix':      # O_k read linearly over all 10 columns instead of the 3..6 window
            for k in range(7):
                r = 2 + k
                for c in range(10):
                    n['W1'][(r*10+c)*6+0, 7+k] = 2*c + 1
                    n['W1'][(r*10+c)*6+4, 7+k] = 18 - 4*c
        elif v == 'vetofix':   # shrink reward-pull weights in V units so they cannot reach the |V|>0.9 veto band
            for k in range(7):
                for r in range(10):
                    for c in range(10):
                        i = (r*10+c)*6+2
                        n['W1'][i, k] *= 0.4
        elif v == 'nohoriz':   # never move left/right (Astra-like): kill left/right logits
            n['b3'][1] = -100; n['b3'][3] = -100
        elif v == 'nodiverD':  # D_k ignores divers: danger weight 1.2, reward weight 0 (enemy still 1.2)
            for k in range(7):
                r = 2 + k
                for c in range(10):
                    w = n['W1'][(r*10+c)*6+1, 14+k] + n['W1'][(r*10+c)*6+2, 14+k]
                    n['W1'][(r*10+c)*6+1, 14+k] = w; n['W1'][(r*10+c)*6+2, 14+k] = 0
        else: raise ValueError(v)
    return n

def run(args):
    vname, seed = args
    net = variant(vname)
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    s = dict(score=0, kill=0, bonus=0, pick=0, surf=0, surf6=0, steps=0, cause='cap', edge=0)
    for t in range(wsp.MAX_STEPS):
        z = fwd(net, obs())[3]; a = int(rng.choice(6, p=z))
        pre_dc, pre_oxy, pre_sy = e.diver_count, e.oxygen, e.sub_y
        if e.sub_x in (0,1,8,9): s['edge'] += 1
        r, done = env.act(a)
        s['score'] += r; s['steps'] = t+1
        b = 0
        if e.sub_y == 0 and pre_sy > 0 and pre_dc > 0:
            s['surf'] += 1
            if pre_dc == 6: s['surf6'] += 1; b = pre_oxy*10//200
        s['bonus'] += b; s['kill'] += r - b
        if e.diver_count > pre_dc: s['pick'] += e.diver_count - pre_dc
        if done:
            if e.sub_y == 0 and pre_sy > 0 and pre_dc == 0: s['cause'] = 'surface_no_diver'
            elif pre_oxy <= 0: s['cause'] = 'oxygen'
            else: s['cause'] = 'collision'
            break
    return s

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    for vname in sys.argv[1:]:
        with ProcessPoolExecutor(4) as ex: res = list(ex.map(run, [(vname, sd) for sd in range(200)], chunksize=10))
        sc = np.array([r['score'] for r in res]); L = np.array([r['steps'] for r in res])
        c = collections.Counter(r['cause'] for r in res)
        print(f"{vname:22s} mean {sc.mean():6.2f} (se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f})  len {L.mean():7.1f}  kills/ep {np.mean([r['kill'] for r in res]):.2f}  bonus/ep {np.mean([r['bonus'] for r in res]):.2f}  pickups/ep {np.mean([r['pick'] for r in res]):.2f}  surf/ep {np.mean([r['surf'] for r in res]):.2f} surf6/ep {np.mean([r['surf6'] for r in res]):.2f}  edge-col steps {100*sum(r['edge'] for r in res)/L.sum():.1f}%  deaths {dict(c)}", flush=True)
