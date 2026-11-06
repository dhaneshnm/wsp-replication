import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
D = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt1/"
CL = wsp.load_npz(D + "net.npz")
AS = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz")
ACT = ["noop", "left", "up", "right", "down", "fire"]
def I(r, c, ch): return (r * 10 + c) * 6 + ch
def fwd(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]; p = np.exp(z - z.max()); p /= p.sum()
    return h1, h2, z, p
def obs(sub=(4, 5, 'L'), fish=(), esub=(), bullets=(), divers=(), oxy=200, ndiv=0, trails=()):
    """sub=(row, front_col, 'L'|'R'). fish/esub/divers: (row,col,dir 'L'|'R') moving dir; trail drawn behind.
    bullets: (row,col). Builds the 6-channel obs like wsp.make_obs_fn."""
    x = np.zeros(600, np.float32)
    r, c, f = sub
    back = c + 1 if f == 'L' else c - 1
    x[I(r, c, 0)] = 1; x[I(r, back, 0)] = 1; x[I(r, back, 4)] = 1
    def trail(rr, cc, d):
        b = cc + 1 if d == 'L' else cc - 1
        if 0 <= b <= 9: x[I(rr, b, 4)] = 1
    for (rr, cc, d) in fish:
        x[I(rr, cc, 1)] = 1; x[I(rr, cc, 2)] = 1; trail(rr, cc, d)
    for (rr, cc, d) in esub:
        x[I(rr, cc, 1)] = 1; x[I(rr, cc, 2)] = 1; trail(rr, cc, d)
    for (rr, cc) in bullets:
        x[I(rr, cc, 1)] = 1
    for (rr, cc, d) in divers:
        x[I(rr, cc, 2)] = 1; trail(rr, cc, d)
    for (rr, cc) in trails:
        x[I(rr, cc, 4)] = 1
    for cc in range(oxy * 10 // 200): x[I(9, cc, 5)] = 1
    for cc in range(9 - ndiv, 9): x[I(9, cc, 5)] = 1
    return x
