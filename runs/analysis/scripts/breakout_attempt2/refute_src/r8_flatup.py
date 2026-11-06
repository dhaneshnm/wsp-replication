import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
from collections import Counter
from minatar import Environment
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz")
DY = {0: -1, 1: -1, 2: 1, 3: 1}
ctx = Counter()
for s in range(1000, 1040):
    env = Environment("breakout", sticky_action_prob=0.1); env.seed(s); env.reset(); e = env.env
    obs = wsp.make_obs_fn(env, "breakout"); rng = np.random.default_rng(s)
    hist = []
    for t in range(10000):
        cur = (e.ball_y, e.ball_x, e.last_y, e.last_x, e.ball_dir)
        z = wsp.logits(net, obs()); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p)); r, done = env.act(a)
        hist.append((cur, r, (e.ball_y, e.ball_x, e.ball_dir)))
        if done: break
    for i, (cur, r, nxt) in enumerate(hist):
        by, bx, ly, lx, d = cur
        if by == ly and by != 8 and DY[d] < 0:
            prev_cur, prev_r, _ = hist[i - 1]
            ctx[(f"row{by}", f"prev ball row {prev_cur[0]} dirDY {DY[prev_cur[4]]:+d} reward_into_this {prev_r}", f"next ball row {nxt[0]} next dirDY {DY[nxt[2]]:+d}")] += 1
for k, v in ctx.items(): print(k, v)
