import sys, os, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

def pos_set(lst): return {(e[0], e[1]) for e in lst}

def run(net_name, seed):
    net = CL if net_name == "claude" else AS
    env = wsp._make_env("seaquest", seed)
    e = env.env
    obs = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    st = dict(seed=seed, score=0.0, kills=0, surf_reward=0, pickups=0, surfacings=0, surf6=0,
              rows=[0]*10, cols=[0]*10, acts=[0]*6, exec_acts=[0]*6, steps=0,
              O_eval=0, O_wrong=0, O_zero=0, in_window=0,
              row_steps_with_enemy=0, max_dc=0, ramp=0, death=None, death_info=None,
              first_pickup_step=None, oxy_at_death=None, dc_at_death=None)
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1, h2, z, p = fwd(net, x)
        a = int(rng.choice(6, p=p))
        st['acts'][a] += 1
        sy, sx, sor = e.sub_y, e.sub_x, e.sub_or
        st['rows'][sy] += 1; st['cols'][sx] += 1
        if net_name == "claude" and 2 <= sy <= 8:
            k = sy - 2
            O = h1[7 + k]
            st['O_eval'] += 1
            if abs(O) < 0.5: st['O_zero'] += 1
            elif (O > 0) != bool(sor): st['O_wrong'] += 1
        if any(f[1] == sy for f in e.e_fish + e.e_subs): st['row_steps_with_enemy'] += 1
        pre = dict(fish=pos_set(e.e_fish), subs=pos_set(e.e_subs), eb=pos_set(e.e_bullets),
                   dc=e.diver_count, oxy=e.oxygen, sy=sy, sx=sx)
        r, done = env.act(a)
        ea = env.last_action
        st['exec_acts'][ea] += 1
        st['score'] += r
        if e.diver_count > pre['dc']: st['pickups'] += e.diver_count - pre['dc']
        if st['first_pickup_step'] is None and e.diver_count > pre['dc']: st['first_pickup_step'] = t
        st['max_dc'] = max(st['max_dc'], e.diver_count)
        surfaced = (e.sub_y == 0 and pre['sy'] > 0 and not done) or (e.sub_y == 0 and pre['sy'] > 0 and pre['dc'] > 0)
        if e.sub_y == 0 and pre['sy'] > 0 and pre['dc'] > 0:
            st['surfacings'] += 1
            if pre['dc'] == 6: st['surf6'] += 1
            # surfacing reward (only with 6)
        st['steps'] = t + 1
        if done:
            p_ = (e.sub_x, e.sub_y)
            info = dict(t=t, a_sampled=ACT[a], a_exec=ACT[ea], sticky=(ea != a), pre_pos=(pre['sx'], pre['sy']),
                        post_pos=p_, oxy=pre['oxy'], dc=pre['dc'])
            if e.sub_y == 0 and pre['sy'] > 0 and pre['dc'] == 0:
                cause = "surface_no_diver"
            elif pre['oxy'] <= 0:
                cause = "oxygen"
            else:
                hits = []
                for nm, pre_s, post_l in (("fish", pre['fish'], e.e_fish), ("esub", pre['subs'], e.e_subs), ("ebullet", pre['eb'], e.e_bullets)):
                    post_s = pos_set(post_l)
                    if p_ in pre_s: hits.append(nm + ":pre")
                    if p_ in post_s: hits.append(nm + ":post")
                cause = "collision"
                info['hits'] = hits
                moved = p_ != (pre['sx'], pre['sy'])
                info['moved'] = ("vert" if p_[1] != pre['sy'] else "horiz") if moved else "stay"
                # threat type
                kinds = sorted({h.split(':')[0] for h in hits})
                info['kind'] = "+".join(kinds) if kinds else "unknown"
                # did the player move into an entity that was already there?
                info['moved_into'] = moved and any(h.endswith(':pre') for h in hits)
                # policy context at the final observation
                if net_name == "claude" and 2 <= pre['sy'] <= 8:
                    k = pre['sy'] - 2
                    info['V'] = float(h1[k]); info['Y'] = float(h1[21 + k]); info['D'] = float(h1[14 + k]); info['O'] = float(h1[7+k])
                info['probs'] = {ACT[i]: round(float(p[i]), 3) for i in range(6)}
            st['death'] = cause; st['death_info'] = info
            st['oxy_at_death'] = pre['oxy']; st['dc_at_death'] = pre['dc']
            break
    else:
        st['death'] = 'cap'
    st['ramp'] = e.ramp_index
    return st

def work(args):
    net_name, seeds = args
    return [run(net_name, s) for s in seeds]

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    net_name = sys.argv[1]; n = int(sys.argv[2]); base = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    seeds = list(range(base, base + n)); W = 4
    with ProcessPoolExecutor(W) as ex:
        res = [r for part in ex.map(work, [(net_name, seeds[i::W]) for i in range(W)]) for r in part]
    res.sort(key=lambda s: s['seed'])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"instr_{net_name}_{base}_{n}.json")
    json.dump(res, open(out, "w"))
    print("wrote", out)
