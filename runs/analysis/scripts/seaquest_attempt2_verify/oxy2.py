# For the oxygen-death episodes: while S is on, why is 'up' blocked?  Classify each S-on step in rows 2..8.
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
SEEDS = [30, 31, 48, 50, 58, 68, 135, 145, 152, 163, 167, 183, 192, 197]
W1 = CL['W1']; b1 = CL['b1']
for seed in SEEDS:
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    c = collections.Counter(); last = None
    for t in range(wsp.MAX_STEPS):
        x = obs(); h1, h2, z, p = fwd(CL, x); a = int(rng.choice(6, p=p))
        g = x.reshape(10,10,6); sy, sx, sor = e.sub_y, e.sub_x, bool(e.sub_or)
        if h1[28] > 0 and 2 <= sy <= 8:
            k = sy - 2
            cells = (sx-1, sx) if sor else (sx, sx+1)
            dang_win = g[sy-1, 2:8, 1].any()
            dang_near = any(g[sy-1, cc, 1] for cc in range(max(0, min(cells)-1), min(9, max(cells)+1)+1))
            # contribution of reward (ch2) inputs to V_k pre-activation
            rew = sum(W1[(r*10+cc)*6+2, k] * g[r, cc, 2] for r in range(10) for cc in range(10))
            uv = h2[3] > 0
            c['S_steps'] += 1
            if uv:
                if not dang_win: c['veto_no_danger(reward pull)'] += 1
                elif not dang_near: c['veto_danger_in_window_not_near'] += 1
                else: c['veto_danger_near'] += 1
            else:
                c['no_veto'] += 1
            c['p_up_sum'] += p[2]
            last = (t, sy, sx, round(float(h1[k]),2), round(float(rew),2), dang_win, dang_near, uv, round(float(p[2]),2))
        r, done = env.act(a)
        if done: break
    print(seed, "dc", e.diver_count, dict(c), "mean p(up) while S on: %.2f" % (c['p_up_sum']/max(1,c['S_steps'])))
    print("    last S-on row2-8 step (t,row,col,V,reward-contrib,dangerCols2-7above,dangerNearAbove,upVeto,p_up):", last)
