import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
env = wsp._make_env("asterix", 119); obs = wsp.make_obs_fn(env, "asterix")
rng = np.random.default_rng(119 + 1_000_003)
for t in range(94):
    x = obs(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
    a = int(rng.choice(6, p=p))
    if t >= 90:
        g = x.reshape(10, 10, 6)
        print(f"t={t} player={(env.env.player_y, env.env.player_x)} move_timer={env.env.move_timer} a={a} p(n,u,d)={p[[0,2,4]].round(3)}")
        for r in range(5, 10):
            print("   row", r, "".join("P" if g[r,c,0] else "E" if g[r,c,1] else "G" if g[r,c,2] else "t" if g[r,c,4] else "." for c in range(10)))
        h1 = np.tanh(x @ net["W1"] + net["b1"]); print("   D rows1-8:", h1[0:8].round(2))
    r, done = env.act(a)
    if done: print("died at t", t); break
