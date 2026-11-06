"""Probes built by setting the real MinAtar env state (not hand-built arrays) and reading wsp.make_obs_fn."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

D = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt1/"
NET = wsp.load_npz(D + "net.npz")
A = ["noop", "left", "up", "right", "down", "fire"]


def state(row, front, right, fish=(), subs=(), divers=(), bullets=(), oxy=200, ndiv=0):
    """fish/subs/divers: (row, col, moving_right); bullets: (row, col, moving_right)."""
    env = wsp._make_env("seaquest", 0)
    g = env.env
    g.sub_y, g.sub_x, g.sub_or = row, front, right
    g.e_fish = [[c, r, d, 3] for (r, c, d) in fish]
    g.e_subs = [[c, r, d, 3, 5] for (r, c, d) in subs]
    g.divers = [[c, r, d, 3] for (r, c, d) in divers]
    g.e_bullets = [[c, r, d] for (r, c, d) in bullets]
    g.oxygen, g.diver_count = oxy, ndiv
    return wsp.make_obs_fn(env, "seaquest")()


def run(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    pre1 = x @ net["W1"] + net["b1"]
    return pre1, h1, h2, z, p


def show(label, x, net=NET):
    pre1, h1, h2, z, p = run(net, x)
    row = None
    g = x.reshape(10, 10, 6)
    for r in range(9):
        if g[r, :, 0].any() and r >= 2:
            row = r
    tpre = pre1[9 + row - 2] if row is not None else float("nan")
    top = {A[i]: round(float(p[i]), 3) for i in np.argsort(-p)[:3] if p[i] > 0.005}
    print(f"{label:62s} Tpre={tpre:+.2f} L2[D,U,TR,TL,CL,CR]={np.round(h2[:6], 2).tolist()} p={top}")
    return p
