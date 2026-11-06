import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
from collections import Counter
cl = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz")
ast = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
v678 = wsp.load_npz("v_rows678.npz")
def obs(br, bc, lr, lc, p):
    o = np.zeros((10, 10, 6), np.float32); o[9, p, 0] = 1; o[br, bc, 3] = 1; o[lr, lc, 4] = 1
    return o.reshape(600)
cls = lambda q: q if q in (1, 3) else 0
def act(n, x): return cls(int(np.argmax(wsp.logits(n, x))))
def h1(n, x): return np.tanh(x @ n["W1"] + n["b1"])
def valid(br, bc, lr, lc):
    dr, dc = br - lr, bc - lc
    if abs(dr) == 1 and abs(dc) == 1: return "diag"
    if dr == 0 and abs(dc) == 1: return "flat"
    if dc == 0 and abs(dr) == 1 and bc in (0, 9): return "wallvert"
    if dr == 0 and dc == 0 and bc in (0, 9): return "same@wall"
    return None
diff = Counter(); diffv = Counter(); xvd = Counter(); n = 0
for br in range(9):
    for bc in range(10):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                lr, lc = br + dr, bc + dc
                if not (0 <= lr <= 9 and 0 <= lc <= 9): continue
                kind = valid(br, bc, lr, lc)
                if kind is None: continue
                hc = h1(cl, obs(br, bc, lr, lc, 0)); ha = h1(ast, obs(br, bc, lr, lc, 0))
                up = hc[9] > 0
                if np.sign(hc[8]) != np.sign(ha[4]) or (hc[9] > 0) == (ha[5] > 0): xvd[(kind, br, bc, lr, lc)] += 1
                for p in range(10):
                    x = obs(br, bc, lr, lc, p); n += 1
                    ac, aa, av = act(cl, x), act(ast, x), act(v678, x)
                    key = ("up" if up else "down", br, kind)
                    if ac != aa: diff[key] += 1
                    if av != aa: diffv[key] += 1
print("valid-shaped states", n)
print("X/V class differs Claude vs Astra:", dict(xvd))
print("Claude vs Astra action differs (Claude V class, ball row, trail kind):", dict(sorted(diff.items())))
print("rows678 variant vs Astra differs:", dict(sorted(diffv.items())))
