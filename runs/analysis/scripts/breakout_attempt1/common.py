import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"
AS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
def nets():
    return {"claude": wsp.load_npz(CL), "astra": wsp.load_npz(AS)}

def idx(r, c, ch):
    return (r * 10 + c) * 6 + ch

def make_obs(ball, trail, pad, bricks=None):
    x = np.zeros(600, np.float32)
    x[idx(9, pad, 0)] = 1
    if ball is not None:
        x[idx(ball[0], ball[1], 3)] = 1
    if trail is not None:
        x[idx(trail[0], trail[1], 4)] = 1
    if bricks is not None:
        for (r, c) in zip(*np.nonzero(bricks)):
            x[idx(r, c, 2)] = 1
    return x

def forward(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    return h1, h2, z, p

def fold(u):
    if 0 <= u <= 9: return u
    if u >= 10: return 19 - u
    return -1 - u
