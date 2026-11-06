"""Claims 1/8/11 on played frames (Claude, sticky 0.1, seeds 0-199):
 - network action distribution vs the reply's stated policy (formula H,V signs -> table -> move)
 - every misread frame classified by the event that produced it."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from collections import Counter

CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"
DX = {0: -1, 1: 1, 2: 1, 3: -1}
DOWN = {0: False, 1: False, 2: True, 3: True}
TUP = {0: 9, 1: 10, 2: 9, 3: 8, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11}


def fold(u):
    m = u % 20
    return 19 - m if m >= 10 else m


def ep(seed):
    net = wsp.load_npz(CL)
    env = wsp._make_env("breakout", seed)
    obs = wsp.make_obs_fn(env, "breakout"); g = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    stats = Counter(); kinds = Counter()
    prev = None
    for t in range(wsp.MAX_STEPS):
        x = obs()
        z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        bx, by, lx, ly, d, pos = g.ball_x, g.ball_y, g.last_x, g.last_y, g.ball_dir, g.pos
        # reply formula policy
        H = 8 * (bx - lx) + (4 if bx == 0 else 0) - (4 if bx == 9 else 0)
        V = 8 * (by - ly) + (4 if by <= 7 else -4)
        hdx = 1 if H > 0 else -1
        down = V > 0
        L = fold(bx + hdx * ((8 - by) if down else TUP[by]))
        want = 3 if L > pos else 1 if L < pos else None
        pm = {1: p[1], 3: p[3]}
        if want is None:
            stats["stay_frames"] += 1
            stats["stay_maxmoveprob<1e-6"] += int(max(p[1], p[3]) < 1e-6)
        else:
            stats["move_frames"] += 1
            stats["move_prob>0.9999"] += int(pm[want] > 0.9999)
        stats["frames"] += 1
        # misread classification
        hm = (H > 0) != (DX[d] > 0); vm = (V > 0) != DOWN[d]
        if hm or vm:
            pb = prev  # state before previous step
            if vm and by == ly and by <= 2:
                k = ("V", "flat row %d" % by, "prev dir down=%s" % DOWN[pb["d"]], "prev reward=%s" % pb["r"], "now rising=%s" % (not DOWN[d]))
            elif hm and by == 8 and ly == 8:
                k = ("H", "flat row 8", "paddle(after prev act)==ball new col=%s" % (pb["pa"] == bx), "paddle==old col=%s" % (pb["pa"] == lx))
            else:
                k = ("other", "H" if hm else "", "V" if vm else "", by, ly, bx, lx)
            kinds[k] += 1
        a = int(rng.choice(6, p=p))
        u = env.random.rand(); st = u < env.sticky_action_prob
        ae = env.last_action if st else a; env.last_action = ae
        r, done = g.act(ae)
        prev = dict(d=d, r=r, pa=g.pos, by=by)
        if done:
            break
    return stats, kinds


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    S = Counter(); K = Counter()
    with ProcessPoolExecutor(4) as ex:
        for s, k in ex.map(ep, range(200), chunksize=5):
            S.update(s); K.update(k)
    print(dict(S))
    for k, v in sorted(K.items(), key=lambda kv: -kv[1]):
        print(v, k)
    print("total misread frames", sum(K.values()))
