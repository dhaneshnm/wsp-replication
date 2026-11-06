import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
net = nets()["claude"]
for seed in range(6):
    env = wsp._make_env("breakout", seed); env.sticky_action_prob = 0.0
    obs = wsp.make_obs_fn(env, "breakout"); e = env.env
    start = (e.ball_y, e.ball_x)
    seen = {}; score = 0; rt = []
    for t in range(2000):
        key = (e.ball_x, e.ball_y, e.ball_dir, e.pos, e.last_x, e.last_y, e.strike, e.brick_map.tobytes())
        if key in seen: break
        seen[key] = t
        h1, h2, z, p = forward(net, obs())
        r, done = env.act(int(np.argmax(p))); score += r
        if r: rt.append(t)
    print(f"seed {seed}: start ball {start}; argmax, no sticky: state at t={t} repeats t={seen[key]} (period {t-seen[key]}), score {score}, last reward t={rt[-1]}, bricks left {int(e.brick_map.sum())}")
    print("   bricks left (rows 1-3):\n", e.brick_map[1:4].astype(int))
