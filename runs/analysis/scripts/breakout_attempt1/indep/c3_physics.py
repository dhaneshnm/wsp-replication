# Claims 3, 8, 9 (synthetic part): generate frames with the real game code, compare net targets/gates
# against simulated physics; check gate pre-activations against the reply's stated formulas.
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from minatar.environments.breakout import Env as RawEnv

CL = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz")
AS = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
DV = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}


def mk(bx, by, d, bricks=(), pos=0):
    e = RawEnv()
    e.ball_x, e.ball_y, e.ball_dir = bx, by, d
    e.last_x, e.last_y = bx, by
    e.pos = pos
    e.brick_map = np.zeros((10, 10))
    for (r, c) in bricks:
        e.brick_map[r, c] = 1
    e.strike = False
    e.terminal = False
    return e


def obs(e, pos=None):
    x = np.zeros(600, np.float32)
    x[(e.ball_y * 10 + e.ball_x) * 6 + 3] = 1
    x[(e.last_y * 10 + e.last_x) * 6 + 4] = 1
    x[(90 + (e.pos if pos is None else pos)) * 6] = 1
    return x


def run_net(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    return h1, z


def landing(e):
    """continue a copy with no bricks; return (row-8 column, column at row 9 step)"""
    f = mk(e.ball_x, e.ball_y, e.ball_dir)
    for _ in range(100):
        if f.ball_y == 8 and DV[f.ball_dir][1] == 1:
            bx8 = f.ball_x
            nx = bx8 + DV[f.ball_dir][0]
            nx = min(max(nx, 0), 9)
            return bx8, nx
        f.pos = 0 if f.ball_x > 4 else 9  # keep paddle away (irrelevant above row 9)
        f.act(0)
    raise RuntimeError


# ---- generate frames: every (row 0..8, col, dir), one real game step with no bricks, paddle far away
frames = []
for r in range(0, 9):
    for c in range(10):
        for d in range(4):
            e = mk(c, r, d, pos=(0 if c > 4 else 9))
            if r == 8 and DV[d][1] == 1:
                continue  # would hit row 9
            e.act(0)
            if e.terminal or e.ball_y > 8:
                continue
            frames.append(("free", e))
# brick-from-below: ascending ball hits a brick right above -> dy=0, now descending
for r in range(2, 5):  # bricks live in rows 1-3
    for c in range(10):
        for d in (0, 1):
            nx = c + DV[d][0]
            if not 0 <= nx <= 9:
                continue
            e = mk(c, r, d, bricks=[(r - 1, nx)], pos=(0 if c > 4 else 9))
            e.act(0)
            frames.append(("brick-below", e))
# brick-from-above: descending ball hits a brick right below -> dy=0, now ascending
for r in range(0, 3):  # bricks live in rows 1-3
    for c in range(10):
        for d in (2, 3):
            nx = c + DV[d][0]
            if not 0 <= nx <= 9:
                continue
            e = mk(c, r, d, bricks=[(r + 1, nx)], pos=(0 if c > 4 else 9))
            e.act(0)
            frames.append(("brick-above", e))

from collections import Counter
cnt = Counter(); err = Counter(); exs = {}
tgt_tot = Counter(); tgt_bad = Counter(); bad_examples = []
for kind, e in frames:
    vx, vy = DV[e.ball_dir]
    for name, net in (("claude", CL), ("astra", AS)):
        h1, _ = run_net(net, obs(e))
        okH = np.sign(h1[4]) == vx
        okV = np.sign(h1[5]) == vy
        cnt[(name, kind)] += 1
        if not okH:
            err[(name, kind, "gH")] += 1
        if not okV:
            err[(name, kind, "gV")] += 1
            exs.setdefault((name, kind), ((e.last_y, e.last_x), (e.ball_y, e.ball_x), e.ball_dir, round(float(h1[5]), 4)))
    # descending target exactness (Claude): paddle columns where argmax is no-op vs true landing column
    if vy == 1 and kind != "brick-above":
        bx8, nx = landing(e)
        noop = []
        for p in range(10):
            _, z = run_net(CL, obs(e, pos=p))
            if int(np.argmax(z)) == 0:
                noop.append(p)
        tgt_tot[kind] += 1
        if noop != [nx]:
            tgt_bad[kind] += 1
            if len(bad_examples) < 5:
                bad_examples.append(((e.last_y, e.last_x), (e.ball_y, e.ball_x), e.ball_dir, noop, nx))
print("frames per kind/net:", dict(cnt))
print("gate errors:", dict(err))
print("first gV error example per (net, kind): (trail, ball, true dir, h1[5])", exs)
print("descending frames checked:", dict(tgt_tot), " no-op column != simulated landing column:", dict(tgt_bad), bad_examples)

# specific frames named in claim 8
for (r0, c0) in [(0, 3), (2, 3)]:
    e = mk(c0, r0, 2, bricks=[(r0 + 1, c0 + 1)])
    e.act(0)
    for name, net in (("claude", CL), ("astra", AS)):
        h1, _ = run_net(net, obs(e))
        print(f"descending ball at ({r0},{c0}) hits brick ({r0+1},{c0+1}): next frame trail ({e.last_y},{e.last_x}) ball ({e.ball_y},{e.ball_x}) dir {e.ball_dir} {DV[e.ball_dir]}; {name} gV={h1[5]:+.4f} gH={h1[4]:+.4f}")
    # what happens next for the row-0 case
    e.act(0)
    print(f"   one more step: ball ({e.ball_y},{e.ball_x}) dir {e.ball_dir} {DV[e.ball_dir]}")

# ---- gate pre-activations vs stated formulas over all ball rows 0..8 x trail cells
W1, b1 = CL["W1"], CL["b1"]
mH = mV = 0
for br in range(9):
    for bc in range(10):
        for tr in range(10):
            for tc in range(10):
                pre = W1[(br * 10 + bc) * 6 + 3] + W1[(tr * 10 + tc) * 6 + 4] + b1
                fH = 4 * (2 * (bc - tc) + (bc == 0) - (bc == 9))
                fV = 8 * ((br - tr) + 0.5 - (br == 8))
                mH = max(mH, abs(pre[4] - fH)); mV = max(mV, abs(pre[5] - fV))
print("max |unit4 pre - 4(2dx+[c=0]-[c=9])| =", mH, "; max |unit5 pre - 8(dy+0.5-[r=8])| =", mV)


def fold(u):
    u = u % 20
    return u if u <= 9 else 19 - u


Wb = W1.reshape(10, 10, 6, 32)[:, :, 3, :]
Dp = max(abs(Wb[r, c, 0] - fold(c + (9 - r))) for r in range(9) for c in range(10))
Dm = max(abs(Wb[r, c, 1] - fold(c - (9 - r))) for r in range(9) for c in range(10))
T = {0: 10, 1: 11, 2: 10, 3: 9}
Ap = max(abs(Wb[r, c, 2] - fold(c + (r + 2 if r >= 4 else T[r]))) for r in range(9) for c in range(10))
Am = max(abs(Wb[r, c, 3] - fold(c - (r + 2 if r >= 4 else T[r]))) for r in range(9) for c in range(10))
print("max dev D+ vs fold(c+(9-r)):", Dp, " D- vs fold(c-(9-r)):", Dm)
print("max dev A+/A- vs fold(c +/- T), T=r+2 for r>=4 (turn at row 4), T=10,11,10,9 for rows 0-3:", Ap, Am)
print("A+ row 8:", Wb[8, :, 2], " A- row 8:", Wb[8, :, 3])
print("paddle weights unit0..3 equal -col:", all(np.allclose(W1[(90 + p) * 6, :4], -p) for p in range(10)))
