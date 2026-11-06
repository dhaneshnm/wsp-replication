import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from minatar import Environment

def net_target(h1):
    # recover the direction the network believes in and its table target (tables are linear in ball cell)
    return int(np.sign(h1[8])), int(np.sign(h1[9]))

def run_episode(net, seed, keep_frames=False, hv=(8, 9)):
    env = wsp._make_env("breakout", seed); g = env.env
    obs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0; log = []; pred_mismatch = 0; n_land = 0; pending = None
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1, h2, z = fwd(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        greedy = int(np.argmax(z))
        k, x8, nx8 = sim_landing(g.ball_x, g.ball_y, g.ball_dir, g.brick_map, g.strike)
        rec = dict(t=t, by=g.ball_y, bx=g.ball_x, ly=g.last_y, lx=g.last_x, d=g.ball_dir, pos=g.pos,
                   bricks=int(g.brick_map.sum()), strike=g.strike, a=a, pmax=float(p.max()),
                   amax_prob=float(p[a]), H=float(h1[hv[0]]), V=float(h1[hv[1]]), k=k, x8=x8, nx8=nx8,
                   pR=float(p[3]), pL=float(p[1]))
        if pending is None or rec["t"] >= pending[0]:
            pending = (t + k, x8)
        r, done = env.act(a)
        rec["eff"] = env.last_action; rec["r"] = r; rec["pos_after"] = g.pos; rec["done"] = done
        log.append(rec)
        score += r
        if g.ball_y == 8 and g.last_y == 8 and not done:  # caught this step
            pass
        if done:
            break
    # validate predictions: for frames where ball sits at row 8 moving down, check earlier predictions
    land_frames = {r["t"]: r["bx"] for r in log if r["by"] == 8 and r["d"] in (2, 3)}
    for r in log:
        tt = r["t"] + r["k"]
        if tt in land_frames:
            n_land += 1; pred_mismatch += land_frames[tt] != r["x8"]
    return dict(score=score, steps=len(log), log=log, pred_mismatch=pred_mismatch, n_landings=n_land, done=log[-1]["done"])
