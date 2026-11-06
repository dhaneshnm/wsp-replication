# Claim 4/5: deterministic (argmax, no sticky) play; find first exact state repeat, period, bricks left,
# catch types inside the cycle. Uses the raw game Env with a forced start side.
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from minatar.environments.breakout import Env as RawEnv

DV = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}


def obs_from(e):
    x = np.zeros(600, dtype=np.float32)
    x[(e.ball_y * 10 + e.ball_x) * 6 + 3] = 1
    x[(90 + e.pos) * 6] = 1
    x[(e.last_y * 10 + e.last_x) * 6 + 4] = 1
    return x  # brick channel has zero weights in both nets tested here (checked in c1_parse.py)


def act_argmax(net, e):
    x = obs_from(e)
    h = np.tanh(np.tanh(x @ net["W1"] + net["b1"]) @ net["W2"] + net["b2"])
    return int(np.argmax(h @ net["W3"] + net["b3"]))


for path in sys.argv[1:]:
    net = wsp.load_npz(path)
    for side in (0, 1):
        e = RawEnv()
        e.random = np.random.RandomState(0)
        e.reset()
        e.ball_x, e.ball_dir = [(0, 2), (9, 3)][side]
        e.last_x = e.ball_x
        seen = {}
        score = 0
        hist = []
        rep = None
        for t in range(10000):
            key = (e.ball_x, e.ball_y, e.ball_dir, e.last_x, e.last_y, e.pos, e.strike, e.brick_map.tobytes())
            if rep is None and key in seen:
                rep = (seen[key], t, score, int(e.brick_map.sum()))
            seen.setdefault(key, t)
            y0, d0, x0 = e.ball_y, e.ball_dir, e.ball_x
            r, done = e.act(act_argmax(net, e))
            score += r
            if y0 == 8 and DV[d0][1] == 1 and not done:
                hist.append((t, "under-ball" if e.pos == x0 else "landing-col", "same-vx" if DV[e.ball_dir][0] == DV[d0][0] else "reversed-vx", x0))
            if done:
                break
        print(f"{path.split('/')[-1]} start side {side}: steps {t+1} score {score} terminal {e.terminal}")
        if rep:
            a, b, s, nb = rep
            cyc = [h for h in hist if a <= h[0] < b]
            print(f"   first repeat: state at t={b} == state at t={a} (period {b-a}); score then {s}; bricks left {nb}; catches in cycle: {cyc}")
