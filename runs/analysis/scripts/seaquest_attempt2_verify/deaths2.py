import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

def ents(e, divers=True):
    L = [('fish', f[0], f[1], f[2]) for f in e.e_fish] + [('esub', s[0], s[1], s[2]) for s in e.e_subs] + [('ebul', b[0], b[1], b[2]) for b in e.e_bullets]
    if divers: L += [('diver', d[0], d[1], d[2]) for d in e.divers]
    return L

def run(args):
    net_name, seed = args
    net = CL if net_name == "claude" else AS
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    hist = []
    for t in range(wsp.MAX_STEPS):
        x = obs(); h1, h2, z, p = fwd(net, x)
        a = int(rng.choice(6, p=p))
        sy, sx, sor = e.sub_y, e.sub_x, bool(e.sub_or)
        rec = dict(t=t, sx=sx, sy=sy, sor=sor, oxy=e.oxygen, dc=e.diver_count, st=e.shot_timer, a=ACT[a],
                   p=[round(float(q), 3) for q in p], ents=[en for en in ents(e) if abs(en[2]-sy) <= 1])
        if net_name == "claude":
            rec['on'] = [H2N[j] for j in range(16) if h2[j] > 0]
            if 2 <= sy <= 8:
                k = sy-2; rec.update(V=float(h1[k]), O=float(h1[7+k]), D=float(h1[14+k]), Y=float(h1[21+k]))
        r, done = env.act(a)
        rec['ax'] = ACT[env.last_action]; rec['nx'] = e.sub_x; rec['ny'] = e.sub_y
        hist.append(rec); hist = hist[-8:]
        if done:
            dead_by = None
            if e.sub_y == 0 and rec['dc'] == 0 and sy > 0: dead_by = 'surface_no_diver'
            elif rec['oxy'] <= 0: dead_by = 'oxygen'
            else: dead_by = 'collision'
            return dict(seed=seed, t=t, cause=dead_by, hist=hist, post=ents(e, False))
    return dict(seed=seed, t=wsp.MAX_STEPS, cause='cap', hist=hist, post=[])

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    nm = sys.argv[1]
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(nm, s) for s in range(200)], chunksize=10))
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"deaths2_{nm}.json"), "w"))
    print(nm, collections.Counter(r['cause'] for r in res))
