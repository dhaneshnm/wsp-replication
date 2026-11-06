import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/"
AST = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
AST_TXT = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md"
net = wsp.load_npz(A + "net.npz")
txt = open(A + "answer.md").read()
re_net, rep = wsp.apply_edits(txt)
print("parse report:", rep)
for k in ["W1", "b1", "W2", "b2", "W3", "b3"]:
    print(k, "array_equal(npz, reparse) =", np.array_equal(net[k], re_net[k].astype(np.float32)))
ast = wsp.load_npz(AST)
ast_re, rep2 = wsp.apply_edits(open(AST_TXT).read())
print("astra parse:", rep2.statements, rep2.applied, len(rep2.errors), all(np.array_equal(ast[k], ast_re[k].astype(np.float32)) for k in ast))

def F(u):
    m = u % 20
    return m if m < 10 else 19 - m
def S(r): return r + 1 if r >= 4 else 9 - r

W1 = net["W1"]
names = ["D+", "D-", "U+", "U-"]
for t in range(4):
    R, L = 2 * t, 2 * t + 1
    ballR = W1[3::6, R].reshape(10, 10); ballL = W1[3::6, L].reshape(10, 10)
    padR = W1[540:600:6, R]; padL = W1[540:600:6, L]
    T = ballR / 10
    dx = 1 if t in (0, 2) else -1
    exp = np.array([[F(c + dx * ((8 - r) if t < 2 else S(r))) for c in range(10)] for r in range(10)])
    mism = [(r, c, T[r, c], exp[r, c]) for r in range(9) for c in range(10) if T[r, c] != exp[r, c]]
    other_nz = [(i, float(W1[i, R])) for i in np.nonzero(W1[:, R])[0] if (i % 6 != 3) and not (540 <= i < 600 and i % 6 == 0)]
    print(names[t], "rows0-8 mismatches:", mism, "| row9 T:", T[9].tolist(),
          "| padR==-10*col:", np.array_equal(padR, -10 * np.arange(10)), "| L unit == -R unit:", np.array_equal(ballL, -ballR) and np.array_equal(padL, -padR),
          "| b1:", net["b1"][R], net["b1"][L], "| other nonzero W1 in R:", other_nz[:5])

# Exhaustive: net argmax vs stated-design oracle computed from observation alone (ball, trail, paddle)
def a_x(c): return 1 if c == 0 else c
def a_v(r): return 7 if r == 8 else r
def design_obs(br, bc, lr, lc, p):
    X = 1 if a_x(bc) - lc >= 1 else -1
    up = (lr - a_v(br)) >= 1
    k = S(br) if up else 8 - br
    T = F(bc + X * k)
    return (3 if T >= p + 1 else 1 if T <= p - 1 else 0), X, up, T
def obs(br, bc, lr, lc, p):
    o = np.zeros((10, 10, 6), np.float32); o[9, p, 0] = 1; o[br, bc, 3] = 1; o[lr, lc, 4] = 1
    return o.reshape(600)
n = 0; bad = []
for br in range(9):
    for bc in range(10):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                lr, lc = br + dr, bc + dc
                if not (0 <= lr <= 9 and 0 <= lc <= 9): continue
                for p in range(10):
                    z = wsp.logits(net, obs(br, bc, lr, lc, p)); na = int(np.argmax(z)); na = na if na in (1, 3) else 0
                    da = design_obs(br, bc, lr, lc, p)[0]; n += 1
                    if na != da: bad.append((br, bc, lr, lc, p, da, na))
print("exhaustive ball rows 0-8 x 9 trail offsets x 10 paddle:", n, "states; net!=obs-design oracle:", len(bad), bad[:10])

# V unit on flat states (ball row == trail row), rows 0-8
h = lambda x: np.tanh(x @ net["W1"] + net["b1"])
flat = {}
for r in range(9):
    vs = set()
    for bc in range(10):
        for lc in (bc - 1, bc, bc + 1):
            if 0 <= lc <= 9:
                vs.add(int(np.sign(h(obs(r, bc, r, lc, 0))[9])))
    flat[r] = sorted(vs)
print("V sign on flat states by row (+1=up):", flat)
# X on post-catch reversal states: ball (8, x8+dx), trail (8, x8)
for x8, dx in [(1, 1), (3, 1), (4, 1), (5, 1), (8, -1), (5, -1)]:
    bc = x8 + dx
    X = np.sign(h(obs(8, bc, 8, x8, bc))[8])
    print(f"reversal post-catch ball(8,{bc}) trail(8,{x8}) pos={bc}: X={X:+.0f} (true new dx={-dx:+d}); read target F({bc}+{dx}*9)={F(bc+dx*9)}, true target F({bc}-{dx}*9)={F(bc-dx*9)}")
