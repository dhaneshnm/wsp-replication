# For steps where S (surface) is on and player in rows 2..8: is up vetoed, and is the veto caused by real danger
# (danger cells in cols 2..7 of the row above) or by accumulated downward reward pull?
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
def run(seed):
    env = wsp._make_env("seaquest", seed); e = env.env
    obs = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    c = collections.Counter()
    for t in range(wsp.MAX_STEPS):
        x = obs(); h1, h2, z, p = fwd(CL, x); a = int(rng.choice(6, p=p))
        g = x.reshape(10,10,6); sy = e.sub_y
        if 2 <= sy <= 8:
            k = sy - 2
            pre = x @ CL['W1'][:, k] + CL['b1'][k]
            real_up_danger = g[sy-1, 2:8, 1].any()
            real_dn_danger = sy < 8 and g[sy+1, 2:8, 1].any()
            upveto = h2[3] > 0; dnveto = h2[1] > 0
            c['steps'] += 1
            if upveto:
                c['upveto'] += 1
                if not real_up_danger: c['upveto_false'] += 1
            if dnveto:
                c['dnveto'] += 1
                if not real_dn_danger: c['dnveto_false'] += 1
            if h1[28] > 0:
                c['S_steps'] += 1
                if upveto: c['S_upveto'] += 1
                if upveto and not real_up_danger: c['S_upveto_false'] += 1
        r, done = env.act(a)
        if done: break
    return c
if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(4) as ex: cs = list(ex.map(run, range(200), chunksize=10))
    tot = sum(cs, collections.Counter()); print(dict(tot))
    print("up-veto active in %.1f%% of rows2-8 steps; %.1f%% of those have no danger in cols2-7 of the row above" % (100*tot['upveto']/tot['steps'], 100*tot['upveto_false']/max(1,tot['upveto'])))
    print("down-veto active in %.1f%% of steps; %.1f%% false" % (100*tot['dnveto']/tot['steps'], 100*tot['dnveto_false']/max(1,tot['dnveto'])))
    print("while S (surface) on: %d steps, up vetoed %d (%.1f%%), falsely %d" % (tot['S_steps'], tot['S_upveto'], 100*tot['S_upveto']/max(1,tot['S_steps']), tot['S_upveto_false']))
