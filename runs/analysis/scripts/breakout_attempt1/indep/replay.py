# Independent instrumented replay of the harness loop (own obs builder from env internals,
# own catch/miss bookkeeping, own counterfactual miss attribution).
# usage: replay.py NET_PATH POLICY(softmax|argmax) STICKY N OUT.pkl
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import pickle
import numpy as np
import wsp
from minatar import Environment
from minatar.environments.breakout import Env as RawEnv

DV = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}  # dir -> (vx, vy)


def obs_from(e):
    x = np.zeros(600, dtype=np.float32)
    x[(e.ball_y * 10 + e.ball_x) * 6 + 3] = 1
    x[(90 + e.pos) * 6 + 0] = 1
    x[(e.last_y * 10 + e.last_x) * 6 + 4] = 1
    br = np.argwhere(e.brick_map == 1)
    for (r, c) in br:
        x[(r * 10 + c) * 6 + 2] = 1
    return x


def fwd(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max())
    p /= p.sum()
    return h1, z, p


def snap(e):
    return (e.ball_x, e.ball_y, e.ball_dir, e.last_x, e.last_y, e.pos, e.strike, e.brick_map.copy())


def cf_argmax_catches(net, s):
    """From snapshot s (state before an action), play pure argmax with no sticky until the ball
    reaches row 9. Return True if caught."""
    e = RawEnv()
    e.ball_x, e.ball_y, e.ball_dir, e.last_x, e.last_y, e.pos, e.strike, bm = s
    e.brick_map = bm.copy()
    e.terminal = False
    for _ in range(200):
        y0, d0 = e.ball_y, e.ball_dir
        _, _, p = fwd(net, obs_from(e))
        e.act(int(np.argmax(p)))
        if e.terminal:
            return False
        if y0 == 8 and DV[d0][1] == 1:
            return True
    raise RuntimeError("no landing within 200 steps")


def episode(args):
    net, seed, policy, sticky = args
    env = Environment("breakout", sticky_action_prob=sticky)
    env.seed(seed)
    env.reset()
    e = env.env
    hobs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed + 1_000_003)
    rec = {k: [] for k in ("by", "bx", "ly", "lx", "d", "pos", "amax", "asamp", "aexec",
                           "r", "h4", "h5", "p0", "pL", "pR", "catch", "nb")}
    score = 0.0
    rally = []  # (snapshot, amax, asamp, aexec) for steps since last catch
    done = False
    obs_mismatch = 0
    for t in range(wsp.MAX_STEPS):
        x = obs_from(e)
        if t < 30 and not np.array_equal(x, hobs()):
            obs_mismatch += 1
        h1, z, p = fwd(net, x)
        amax = int(np.argmax(p))
        a = int(rng.choice(6, p=p)) if policy == "softmax" else amax
        s = snap(e)
        by, bx, d, pos_before = e.ball_y, e.ball_x, e.ball_dir, e.pos
        rec["by"].append(by); rec["bx"].append(bx); rec["ly"].append(e.last_y); rec["lx"].append(e.last_x)
        rec["d"].append(d); rec["pos"].append(pos_before); rec["amax"].append(amax); rec["asamp"].append(a)
        rec["h4"].append(h1[4]); rec["h5"].append(h1[5]); rec["p0"].append(p[0]); rec["pL"].append(p[1]); rec["pR"].append(p[3])
        rec["nb"].append(int(e.brick_map.sum()))
        r, done = env.act(a)
        ex = env.last_action
        rec["aexec"].append(ex); rec["r"].append(r)
        rally.append((s, amax, a, ex))
        score += r
        c = 0
        if by == 8 and DV[d][1] == 1 and not done:
            # caught: branch 1 = paddle under ball's row-8 column, 2 = paddle at new column
            c = 1 if e.pos == bx else 2
            rally = []
        rec["catch"].append(c)
        if done:
            break
    out = {k: np.array(v) for k, v in rec.items()}
    out.update(seed=seed, score=score, steps=t + 1, done=bool(done), obs_mismatch=obs_mismatch)
    if done:
        # miss attribution
        cf0 = cf_argmax_catches(net, rally[0][0])
        decisive = None
        if cf0:
            cfs = [cf_argmax_catches(net, st[0]) for st in rally]
            last_ok = max(i for i, v in enumerate(cfs) if v)
            _, am, sa, exa = rally[last_ok]
            if sa != am and exa == sa:
                kind = "sampling"
            elif exa != sa:
                kind = "sticky"
            else:
                kind = "no-deviation(?)"
            decisive = dict(i=last_ok, n=len(rally), amax=am, asamp=sa, aexec=exa, kind=kind)
        out["miss"] = dict(cf_rally_start_catches=cf0, decisive=decisive, rally_len=len(rally))
    return out


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    path, policy, sticky, n, outp = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    net = wsp.load_npz(path)
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(episode, [(net, s, policy, sticky) for s in range(n)], chunksize=5))
    pickle.dump(res, open(outp, "wb"))
    sc = np.array([r["score"] for r in res]); ln = np.array([r["steps"] for r in res])
    print(f"{path.split('/')[-1]} {policy} sticky={sticky} n={n}: mean {sc.mean():.4f} se {sc.std(ddof=1)/np.sqrt(n):.4f} "
          f"mean_len {ln.mean():.2f} misses {sum(r['done'] for r in res)} max {sc.max()} obs_mismatch {sum(r['obs_mismatch'] for r in res)}")
