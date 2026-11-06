import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"
AS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
N = {"claude": wsp.load_npz(CL), "astra": wsp.load_npz(AS)}

def idx(r, c, ch): return (r * 10 + c) * 6 + ch
def obs(ball, trail, pad):
    x = np.zeros(600, np.float32)
    x[idx(9, pad, 0)] = 1; x[idx(ball[0], ball[1], 3)] = 1; x[idx(trail[0], trail[1], 4)] = 1
    return x
def fwd(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    z = wsp.logits(net, x)
    p = np.exp(z - z.max()); p /= p.sum()
    return h1, z, p

np.set_printoptions(precision=5, suppress=True)
# On-target logits for Claude across every descending ball cell (diagonal trail) with paddle at exact landing col
def fold(u):
    if 0 <= u <= 9: return u
    if u >= 10: return 19 - u
    return -1 - u
for name, net in N.items():
    gaps = []; p0s = []
    for vx in (1, -1):
        for r in range(1, 9):
            for c in range(10):
                tc = c - vx
                if not 0 <= tc <= 9: continue
                L = fold(c + vx * (9 - r))
                h1, z, p = fwd(net, obs((r, c), (r - 1, tc), L))
                gaps.append(z[0] - max(z[1], z[3])); p0s.append(p[0])
    print(name, "descending diag cells, paddle at exact landing col: no-op logit gap min/max",
          float(min(gaps)), float(max(gaps)), " p(no-op) min/max", float(min(p0s)), float(max(p0s)))
# specific probe from probe_gates
for name, net in N.items():
    for pad in (1, 2):
        h1, z, p = fwd(net, obs((8, 2), (7, 3), pad))
        print(name, "ball (8,2) trail (7,3) paddle", pad, "logits", z, "probs", p, "gap", float(z[0] - max(z[1], z[3])))
    h1, z, p = fwd(net, obs((5, 2), (4, 3), 7))
    print(name, "ball (5,2) trail (4,3) paddle 7 logits", z, "probs", p)

# Gate probes
cases = [
 ("brick from ABOVE row0 (0,3)->(0,4), true up-right", (0, 4), (0, 3), (1, -1)),
 ("brick from ABOVE row2 (2,3)->(2,4), true up-right", (2, 4), (2, 3), (1, -1)),
 ("brick from below (4,3)->(4,4), true down-right", (4, 4), (4, 3), (1, 1)),
 ("ceiling (0,3)->(0,4) true down-right", (0, 4), (0, 3), (1, 1)),
 ("paddle reverse (8,4)->(8,5) true up-left", (8, 5), (8, 4), (-1, -1)),
 ("paddle same (8,4)->(8,5) true up-right", (8, 5), (8, 4), (1, -1)),
]
for name, net in N.items():
    for d, b, t, (vx, vy) in cases:
        h1, z, p = fwd(net, obs(b, t, 4))
        print(f"{name}: gH={h1[4]:+.4f} gV={h1[5]:+.4f} {'OK ' if (np.sign(h1[4])==vx and np.sign(h1[5])==vy) else 'ERR'} {d}")
