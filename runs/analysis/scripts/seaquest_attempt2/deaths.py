import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

def ent_list(e):
    L = []
    for f in e.e_fish: L.append(('fish', f[0], f[1], f[2]))
    for s in e.e_subs: L.append(('esub', s[0], s[1], s[2]))
    for b in e.e_bullets: L.append(('ebul', b[0], b[1], b[2]))
    return L

def run(seed):
    net = CL
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    hist = []
    for t in range(wsp.MAX_STEPS):
        x = obs(); h1, h2, z, p = fwd(net, x)
        a = int(rng.choice(6, p=p))
        sy, sx, sor = e.sub_y, e.sub_x, e.sub_or
        pre_ents = ent_list(e)
        rec = dict(t=t, sub=(sx, sy, bool(sor)), oxy=e.oxygen, dc=e.diver_count, shot_timer=e.shot_timer,
                   h2on=[H2N[j] for j in range(16) if h2[j] > 0], a=ACT[a],
                   p={ACT[i]: round(float(p[i]), 3) for i in range(6)},
                   ents_near=[en for en in pre_ents if abs(en[2]-sy) <= 1])
        if 2 <= sy <= 8:
            k = sy-2; rec.update(V=round(float(h1[k]),3), O=round(float(h1[7+k]),3), D=round(float(h1[14+k]),3), Y=round(float(h1[21+k]),3))
        r, done = env.act(a)
        rec['a_exec'] = ACT[env.last_action]; rec['post_sub'] = (e.sub_x, e.sub_y)
        hist.append(rec); hist = hist[-6:]
        if done:
            if e.oxygen < 0 or (e.sub_y == 0 and rec['dc'] == 0) or rec['oxy'] <= 0:
                return None
            return dict(seed=seed, hist=hist, post_ents=ent_list(e))
    return None

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    seeds = list(range(200)); W = 4
    with ProcessPoolExecutor(W) as ex:
        res = list(ex.map(run, seeds, chunksize=10))
    res = [r for r in res if r]
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "deaths_claude.json"), "w"))
    print(len(res), "collision deaths recorded")
