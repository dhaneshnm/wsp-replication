import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
R = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt%d/net.npz"
nets = {f"a{k}": wsp.load_npz(R % k) for k in (1, 2, 3)}
nets["astra"] = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")

def obs(ball, trail, pad, bricks=True):
    o = np.zeros((10, 10, 6), np.float32)
    o[9, pad, 0] = 1
    if bricks: o[1:4, :, 2] = 1
    o[ball[0], ball[1], 3] = 1
    o[trail[0], trail[1], 4] = 1
    return o.reshape(600)

def acts(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"]); z = h2 @ net["W3"] + net["b3"]
    return h1, h2, z

def F(u):
    m = u % 20
    return 19 - m if m >= 10 else m

np.set_printoptions(precision=3, suppress=True, linewidth=150)
n = nets["a2"]
print("attempt2 nonzero L1 units:", np.nonzero(np.abs(n["W1"]).sum(0) + np.abs(n["b1"]))[0].tolist(),
      "L2 units:", np.nonzero(np.abs(n["W2"]).sum(0) + np.abs(n["b2"]))[0].tolist(),
      "brick-channel nonzero W1:", int((n["W1"].reshape(10, 10, 6, 32)[:, :, 2, :] != 0).sum()))
print("b3:", n["b3"])
scenes = [
    ("descending DR ball(5,3) trail(4,2), paddle 0", (5, 3), (4, 2), 0),
    ("same, paddle 6 = F(3+3)", (5, 3), (4, 2), 6),
    ("same, paddle 7 (on reversal col x8+1)", (5, 3), (4, 2), 7),
    ("ascending UR ball(6,3) trail(7,2), paddle 0", (6, 3), (7, 2), 0),
    ("start state ball(3,0)=trail, paddle 4", (3, 0), (3, 0), 4),
    ("post-catch flat row 8: ball(8,5) trail(8,4), paddle 4", (8, 5), (8, 4), 4),
]
for name, b, t, p in scenes:
    h1, h2, z = acts(n, obs(b, t, p))
    pz = np.exp(z - z.max()); pz /= pz.sum()
    print(f"\n[{name}]\n  h1[0:10]={h1[:10]}\n  h2[0:8] ={h2[:8]}\n  logits={z}  P(left)={pz[1]:.4f} P(right)={pz[3]:.4f} P(stay-class)={pz[[0,2,4,5]].sum():.4f}")

# Expected targets under the stated design for scene 4 (ascending, S(6)=7): F(3+7)=9 ; start state: X reads +1 (a(0)=1), V reads down -> D+ target F(0+5)=5
print("\nS(6)=7 -> U+ target F(3+7) =", F(10), "; start D+ target F(0+8-3) =", F(5))

# Exhaustive diagonal-state decision comparison
def cls(z):
    a = int(np.argmax(z)); return {1: "L", 3: "R"}.get(a, "S")
diffs = {}
tot = 0
for r in range(0, 9):
    for c in range(10):
        for vy in (-1, 1):
            for vx in (-1, 1):
                tr, tc = r - vy, c - vx
                if not (0 <= tr <= 8 and 0 <= tc <= 9): continue
                for p in range(10):
                    x = obs((r, c), (tr, tc), p); tot += 1
                    k = {nm: cls(acts(nt, x)[2]) for nm, nt in nets.items()}
                    for a_, b_ in (("a2", "a3"), ("a2", "astra"), ("a1", "a2"), ("a3", "astra")):
                        if k[a_] != k[b_]:
                            key = (a_, b_, "down" if vy == 1 else "up", r)
                            diffs[key] = diffs.get(key, 0) + 1
print("\ndiagonal states checked:", tot)
for pair in (("a2", "a3"), ("a2", "astra"), ("a3", "astra"), ("a1", "a2")):
    sub = {k[2:]: v for k, v in sorted(diffs.items()) if k[:2] == pair}
    print(pair, "decision differences by (dir,row):", sub, "total", sum(sub.values()))
