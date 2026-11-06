import sys, os, copy; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
for seed in [39, 76, 78, 102, 118, 143, 149]:
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    hist = []
    for t in range(wsp.MAX_STEPS):
        x = ob(); z = wsp.logits(CL, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        pre_ids = {id(e) for e in g.e_fish + g.e_subs}
        pre = (t, g.sub_x, g.sub_y, 'R' if g.sub_or else 'L', [tuple(e[:3]) for e in g.e_fish if e[1]==g.sub_y], [tuple(e[:3]) for e in g.e_subs if e[1]==g.sub_y], [tuple(b) for b in g.e_bullets if b[1]==g.sub_y])
        r, done = env.act(a)
        new = [tuple(e[:3]) for e in g.e_fish + g.e_subs if id(e) not in pre_ids]
        hist.append(pre + (ACT[a], ACT[env.last_action], new))
        if done:
            print(f"seed {seed} died t={t} sub front=({g.sub_x},{g.sub_y}) face={'R' if g.sub_or else 'L'} oxy={g.oxygen}")
            for h in hist[-4:]: print("   t=%d front_x=%d row=%d face=%s fish_in_row=%s esub_in_row=%s bul_in_row=%s sampled=%s exec=%s newly_spawned=%s" % h)
            break
