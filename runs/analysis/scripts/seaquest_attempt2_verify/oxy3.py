# Oxygen deaths: classify up-veto steps in the FINAL contiguous S-on stretch only (rows 2..8).
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
SEEDS = [30, 31, 48, 50, 58, 68, 135, 145, 152, 163, 167, 183, 192, 197]
tot = collections.Counter()
for seed in SEEDS:
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    c = collections.Counter(); dc_last = None
    for t in range(wsp.MAX_STEPS):
        x = obs(); h1, h2, z, p = fwd(CL, x); a = int(rng.choice(6, p=p))
        g = x.reshape(10,10,6); sy, sx, sor = e.sub_y, e.sub_x, bool(e.sub_or)
        dc_last = e.diver_count
        if h1[28] <= 0: c = collections.Counter()      # reset: keep only the final S-on stretch
        elif 2 <= sy <= 8:
            cells = (sx-1, sx) if sor else (sx, sx+1)
            dang_win = g[sy-1, 2:8, 1].any()
            dang_near = any(g[sy-1, cc, 1] for cc in range(max(0, min(cells)-1), min(9, max(cells)+1)+1))
            c['S_steps'] += 1
            if h2[3] > 0:
                c['veto_reward_pull' if not dang_win else ('veto_window_far' if not dang_near else 'veto_near')] += 1
            else: c['no_veto'] += 1
        r, done = env.act(a)
        if done: break
    print(seed, "dc_at_death", dc_last, dict(c))
    tot += c
print("TOTAL final S-on stretch:", dict(tot))
