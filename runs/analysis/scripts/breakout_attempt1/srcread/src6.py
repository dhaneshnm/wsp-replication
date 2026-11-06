import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"
AS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
cl = wsp.load_npz(CL); asn = wsp.load_npz(AS)
def idx(r, c, ch): return (r * 10 + c) * 6 + ch
def obs(ball, trail, pad):
    x = np.zeros(600, np.float32)
    x[idx(9, pad, 0)] = 1; x[idx(ball[0], ball[1], 3)] = 1; x[idx(trail[0], trail[1], 4)] = 1
    return x
def fold(u):
    if 0 <= u <= 9: return u
    if u >= 10: return 19 - u
    return -1 - u
def noop_cols(net, b, t):
    return [p for p in range(10) if int(np.argmax(wsp.logits(net, obs(b, t, p)))) == 0]

# Descending states of every kind (true dir vx, down). Landing column ignoring bricks, simulated with game rules.
def land(r, c, vx):
    x, y = c, r
    while True:
        nx = x + vx; ny = y + 1
        if nx < 0 or nx > 9:
            nx = min(max(nx, 0), 9); vx = -vx
        if ny == 9: return nx
        x, y = nx, ny
bad = []; n = 0
for vx in (1, -1):
    for r in range(0, 9):
        for c in range(10):
            trails = []
            if r >= 1 and 0 <= c - vx <= 9: trails.append(("diag", (r - 1, c - vx)))
            # wall clip arrival: ball moved vertically only at wall (dir already flipped to vx)
            if r >= 1 and ((c == 0 and vx == 1) or (c == 9 and vx == -1)): trails.append(("wallclip", (r - 1, c)))
            # ceiling bounce / brick from below: same row, moved by vx
            if 0 <= c - vx <= 9: trails.append(("dy0", (r, c - vx)))
            if (c == 0 and vx == 1) or (c == 9 and vx == -1): trails.append(("dy0-wall", (r, c)))
            for kind, t in trails:
                if r == 8 and kind.startswith("dy0"): continue  # row 8 dy=0 is a paddle bounce (ascending)
                n += 1
                L = land(r, c, vx)
                T = noop_cols(cl, (r, c), t)
                if T != [L]: bad.append((kind, (r, c), t, vx, L, T))
print("claude descending states checked:", n, "no-op column != exact landing column:", len(bad))
for b in bad[:20]: print("  ", b)

# gH error at row 8 after a reverse paddle catch: does flipping gH change the logits?
maxd = 0.0
for c in range(10):
    for dx in (1, -1):
        tc = c - dx
        if not 0 <= tc <= 9: continue
        for p in range(10):
            x = obs((8, c), (8, tc), p)
            h1 = np.tanh(x @ cl["W1"] + cl["b1"])
            z = np.tanh(h1 @ cl["W2"] + cl["b2"]) @ cl["W3"] + cl["b3"]
            h1f = h1.copy(); h1f[4] = -h1f[4]
            zf = np.tanh(h1f @ cl["W2"] + cl["b2"]) @ cl["W3"] + cl["b3"]
            maxd = max(maxd, float(np.abs(z - zf).max()))
print("claude row-8 dy=0 frames: max |logit change| when gH sign is flipped:", maxd)

# Astra on-target (its own no-op column): no-op probability over diag-trail states
p0 = []
for vx in (1, -1):
    for vy in (1, -1):
        for r in range(1, 9):
            for c in range(10):
                t = (r - vy, c - vx)
                if not (0 <= t[0] <= 9 and 0 <= t[1] <= 9): continue
                for pp in range(10):
                    z = wsp.logits(asn, obs((r, c), t, pp))
                    if int(np.argmax(z)) == 0:
                        pr = np.exp(z - z.max()); pr /= pr.sum(); p0.append(pr[0])
print("astra: states with argmax no-op:", len(p0), "min p(no-op)", float(min(p0)))
p0 = []
for vx in (1, -1):
    for vy in (1, -1):
        for r in range(1, 9):
            for c in range(10):
                t = (r - vy, c - vx)
                if not (0 <= t[0] <= 9 and 0 <= t[1] <= 9): continue
                for pp in range(10):
                    z = wsp.logits(cl, obs((r, c), t, pp))
                    if int(np.argmax(z)) == 0:
                        pr = np.exp(z - z.max()); pr /= pr.sum(); p0.append(pr[0])
print("claude: states with argmax no-op:", len(p0), "min/max p(no-op)", float(min(p0)), float(max(p0)))
