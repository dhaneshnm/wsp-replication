"""Claim 1/8: independent parse of the edits (plain numpy exec, not wsp.apply_edits),
compare with net.npz, then check every table entry and every unit's pre-activation
against the formulas stated in answer.md over an EXHAUSTIVE enumeration of
ball cell x trail offset x paddle column (not just played frames)."""
import sys, re
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

D = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3"
txt = open(D + "/answer.md").read()
blocks = re.findall(r"```edits\n(.*?)```", txt, re.S)
print("edits blocks:", len(blocks))
ns = {k: np.zeros(s, np.float32) for k, s in wsp.SHAPES.items()}
nstmt = 0
for line in blocks[-1].splitlines():
    line = line.split("#")[0].strip()
    if not line:
        continue
    nstmt += 1
    exec(line, {}, ns)
print("statements executed:", nstmt)
net = wsp.load_npz(D + "/net.npz")
for k in wsp.SHAPES:
    print(k, "max|exec - npz| =", float(np.abs(ns[k] - net[k]).max()))


def fold(u):
    m = u % 20
    return 19 - m if m >= 10 else m

# ---- table entries vs fold(x + dx*T(y))
Tdown = lambda y: 8 - y
Tup = {0: 9, 1: 10, 2: 9, 3: 8, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11}
spec = {0: (+1, Tdown, +5), 1: (+1, Tdown, -5), 2: (-1, Tdown, +5), 3: (-1, Tdown, -5),
        4: (+1, Tup.get, +5), 5: (+1, Tup.get, -5), 6: (-1, Tup.get, +5), 7: (-1, Tup.get, -5)}
bad = 0
for u, (dx, T, sc) in spec.items():
    for y in range(9):
        for x in range(10):
            want = sc * fold(x + dx * T(y))
            got = net["W1"][(y * 10 + x) * 6 + 3, u]
            if got != want:
                bad += 1
print("table entries checked:", 8 * 90, "mismatches vs fold(x+dx*T):", bad)

# ---- paddle weights / other channels
W1 = net["W1"]
for u in range(8):
    pw = W1[540:600:6, u]
    sgn = -1 if spec[u][2] > 0 else 1
    assert np.array_equal(pw, sgn * 5 * np.arange(10)), u
print("paddle weights = -/+5p: ok")
chan_nz = {c: int(np.count_nonzero(W1[c::6, :])) for c in range(6)}
print("nonzero W1 entries per channel:", chan_nz)
print("nonzero columns of W1:", np.nonzero(np.abs(W1).sum(0))[0].tolist(),
      "| W2 nonzero rows/cols:", np.nonzero(np.abs(net['W2']).sum(1))[0].tolist(), np.nonzero(np.abs(net['W2']).sum(0))[0].tolist())

# ---- exhaustive pre-activation check against the reply's stated formulas
offs = [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]  # trail - ball
n = mism = 0
minabs = 1e9
for by in range(9):
    for bx in range(10):
        for (ox, oy) in offs:
            tx, ty = bx + ox, by + oy
            if not (0 <= tx <= 9 and 0 <= ty <= 9):
                continue
            for p in range(10):
                x = np.zeros((10, 10, 6), np.float32)
                x[by, bx, 3] = 1; x[ty, tx, 4] = 1; x[9, p, 0] = 1
                pre = x.reshape(600) @ W1 + net["b1"]
                want = []
                for u in range(8):
                    dx, T, sc = spec[u]
                    L = fold(bx + dx * T(by))
                    want.append(5 * (L - p - 0.5) if sc > 0 else 5 * (p - L - 0.5))
                Hw = 8 * (bx - tx) + (4 if bx == 0 else 0) - (4 if bx == 9 else 0)
                Vw = 8 * (by - ty) + (4 if by <= 7 else -4)
                want += [Hw, Vw]
                d = np.abs(pre[:10] - np.array(want))
                n += 1
                if d.max() > 1e-4:
                    mism += 1
                minabs = min(minabs, float(np.abs(pre[:8]).min()))
                # unused units must be exactly zero pre-activation
                assert np.all(pre[10:] == 0)
print("exhaustive configs:", n, "formula mismatches:", mism, "min |pre| units0-7:", minabs)

# ---- which configs mismatch?
from collections import Counter
cnt = Counter()
for by in range(9):
    for bx in range(10):
        for (ox, oy) in offs:
            tx, ty = bx + ox, by + oy
            if not (0 <= tx <= 9 and 0 <= ty <= 9):
                continue
            p = 0
            x = np.zeros((10, 10, 6), np.float32)
            x[by, bx, 3] = 1; x[ty, tx, 4] = 1; x[9, p, 0] = 1
            pre = x.reshape(600) @ W1 + net["b1"]
            Hw = 8 * (bx - tx) + (4 if bx == 0 else 0) - (4 if bx == 9 else 0)
            Vw = 8 * (by - ty) + (4 if by <= 7 else -4)
            if abs(pre[8] - Hw) > 1e-4: cnt[("H", by, ty)] += 1
            if abs(pre[9] - Vw) > 1e-4: cnt[("V", by, ty)] += 1
print("mismatch kinds (unit, ball row, trail row):", dict(cnt))
