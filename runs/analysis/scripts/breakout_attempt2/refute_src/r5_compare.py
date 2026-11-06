import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
from collections import Counter
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz"
cl = wsp.load_npz(A)
ast = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
v678 = wsp.load_npz("v_rows678.npz")
def obs(br, bc, lr, lc, p):
    o = np.zeros((10, 10, 6), np.float32); o[9, p, 0] = 1; o[br, bc, 3] = 1; o[lr, lc, 4] = 1
    return o.reshape(600)
cls = lambda q: q if q in (1, 3) else 0
def act(n, x): return cls(int(np.argmax(wsp.logits(n, x))))
# Astra X/V signs vs Claude X/V signs
def h1(n, x): return np.tanh(x @ n["W1"] + n["b1"])
diff = Counter(); diff_v = Counter(); xv = Counter(); n = 0
for br in range(9):
    for bc in range(10):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                lr, lc = br + dr, bc + dc
                if not (0 <= lr <= 9 and 0 <= lc <= 9): continue
                hc = h1(cl, obs(br, bc, lr, lc, 0)); ha = h1(ast, obs(br, bc, lr, lc, 0))
                Xc, Vc_up = np.sign(hc[8]), hc[9] > 0
                Xa, Va_down = np.sign(ha[4]), ha[5] > 0
                if Xc != Xa or Vc_up == Va_down: xv[(br, bc, lr, lc)] += 1
                for p in range(10):
                    x = obs(br, bc, lr, lc, p); n += 1
                    ac, aa, av = act(cl, x), act(ast, x), act(v678, x)
                    key = ("up" if Vc_up else "down", "row%d" % br)
                    if ac != aa: diff[key] += 1
                    if av != aa: diff_v[key] += 1
print("states", n)
print("X/V classification differs (Claude vs Astra) at:", len(xv), list(xv)[:10])
print("Claude vs Astra action differs, by (Claude V class, ball row):", dict(sorted(diff.items())))
print("rows678-variant vs Astra action differs:", dict(sorted(diff_v.items())))
