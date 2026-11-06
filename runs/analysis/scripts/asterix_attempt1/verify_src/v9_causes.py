"""Independent replay of Claude's 200 episodes (seeds 0..199, sticky 0.1, same RNG as wsp.play_episode); classify each death:
trapped = noop/up/down all fatal; sticky = a sticky repeat happened, executed action fatal, sampled action would have survived."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy, collections
from multiprocessing import Pool
import numpy as np, wsp
NET = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
def fatal(inner, a):
    e = copy.deepcopy(inner); e.random.rand(); e.act(a); return e.terminal
def run(seed):
    env = wsp._make_env("asterix", seed); obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003); inner = env.env; score = 0
    for t in range(wsp.MAX_STEPS):
        z = wsp.logits(NET, obs()); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        snap = copy.deepcopy(inner); prev = env.last_action
        sticky = copy.deepcopy(env.random).rand() < 0.1
        r, done = env.act(a); score += r
        if done:
            ex = prev if sticky else a
            if all(fatal(snap, b) for b in (0, 2, 4)): c = "trapped"
            elif sticky and fatal(snap, ex) and not fatal(snap, a): c = "sticky"
            else: c = "other"
            return score, c, snap.player_y
    return score, None, None
if __name__ == "__main__":
    with Pool(4) as pool: res = pool.map(run, range(200), chunksize=5)
    print("mean", np.mean([r[0] for r in res]))
    print("causes", collections.Counter(r[1] for r in res))
    print("trapped rows", dict(sorted(collections.Counter(r[2] for r in res if r[1] == "trapped").items())))
