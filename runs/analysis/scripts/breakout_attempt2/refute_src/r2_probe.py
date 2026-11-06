import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
from collections import Counter
from minatar import Environment
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz"
net = wsp.load_npz(A)
DX = {0: -1, 1: 1, 2: 1, 3: -1}; DY = {0: -1, 1: -1, 2: 1, 3: 1}
def F(u):
    m = u % 20
    return m if m < 10 else 19 - m
def S(r): return r + 1 if r >= 4 else 9 - r
def oracle(e):
    dx, dy = DX[e.ball_dir], DY[e.ball_dir]; r, c = e.ball_y, e.ball_x
    T = F(c + dx * ((8 - r) if dy > 0 else S(r)))
    return (3 if T > e.pos else 1 if T < e.pos else 0), T

n = 0; mism = []; xerr = Counter(); verr = Counter(); minpre = 1e9
revpc = []  # reversal post-catch states
flat_up_off8 = Counter(); flat_up_off8_mis = 0
examples = []
for s in range(1000, 1040):
    env = Environment("breakout", sticky_action_prob=0.1); env.seed(s); env.reset(); e = env.env
    obs = wsp.make_obs_fn(env, "breakout"); rng = np.random.default_rng(s)
    prev_pos = None; prev_ball = None
    for t in range(10000):
        x = obs()
        pre1 = x @ net["W1"] + net["b1"]; h1 = np.tanh(pre1)
        pre2 = h1 @ net["W2"] + net["b2"]; h2 = np.tanh(pre2)
        z = h2 @ net["W3"] + net["b3"]
        minpre = min(minpre, np.abs(pre1[:10]).min(), np.abs(pre2[:8]).min())
        na = int(np.argmax(z)); na = na if na in (1, 3) else 0
        da, T = oracle(e); n += 1
        dx, dy = DX[e.ball_dir], DY[e.ball_dir]
        flat = e.ball_y == e.last_y
        st = dict(seed=s, t=t, ball=(e.ball_y, e.ball_x), trail=(e.last_y, e.last_x), dir=e.ball_dir, pos=e.pos,
                  strike=e.strike, X=int(np.sign(h1[8])), V=int(np.sign(h1[9])), oracle=da, T=T, net=na)
        if na != da: mism.append(st)
        if np.sign(h1[8]) != dx:
            kind = "rev-postcatch" if (e.ball_y == 8 and flat and dy < 0 and e.pos == e.ball_x) else "other"
            xerr[kind] += 1
            if kind == "rev-postcatch": revpc.append(st)
        if np.sign(h1[9]) != -dy:
            verr[("flat" if flat else "notflat", "row%d" % e.ball_y, "true up" if dy < 0 else "true down")] += 1
        if flat and e.ball_y != 8 and dy < 0:
            flat_up_off8[e.ball_y] += 1
            if na != da: flat_up_off8_mis += 1
        if s == 1006 and t == 3999: examples.append(st)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p)); r, done = env.act(a)
        if done: break
print("states", n, "min|preact| L1 units0-9 / L2 units0-7:", round(float(minpre), 4))
print("action mismatches (net vs true-dir oracle):", len(mism))
for m in mism: print("   ", m)
print("X wrong:", dict(xerr), " V wrong:", dict(verr))
print("flat states off row 8 with true dir up, by row:", dict(flat_up_off8), " net/oracle mismatches among them:", flat_up_off8_mis)
print("reversal post-catch states (X reads old dir):", len(revpc))
for m in revpc: print("   ", m)
print("seed1006 t3999:", examples)
