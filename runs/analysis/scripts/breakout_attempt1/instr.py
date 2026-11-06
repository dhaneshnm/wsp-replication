import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import pickle

DIRV = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}  # dir -> (vx, vy)

def sim_landing(e):
    """Simulate ball only (paddle ignored) until it reaches row 9. Return (ball_x_at_row8, new_x, steps)."""
    bx, by, d = e.ball_x, e.ball_y, e.ball_dir
    bm = e.brick_map.copy(); strike = e.strike
    for k in range(1, 200):
        lx, ly = bx, by
        vx, vy = DIRV[d]
        nx, ny = bx + vx, by + vy
        st = False
        if nx < 0 or nx > 9:
            nx = min(max(nx, 0), 9); d = [1, 0, 3, 2][d]
        if ny < 0:
            ny = 0; d = [3, 2, 1, 0][d]
        elif bm[ny, nx] == 1:
            st = True
            if not strike:
                strike = True; bm[ny, nx] = 0; ny = ly; d = [3, 2, 1, 0][d]
        elif ny == 9:
            return bx, nx, k
        if not st: strike = False
        bx, by = nx, ny
    return None

def run(args):
    net, seed, keep_trace = args
    env = wsp._make_env("breakout", seed)
    obs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed + 1_000_003)
    e = env.env
    score = 0.0
    trace = []
    rewards_t = []
    refills = 0
    seen = {}
    loop_info = None
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1, h2, z, p = forward(net, x)
        a = int(rng.choice(6, p=p))
        st = dict(t=t, bx=e.ball_x, by=e.ball_y, d=e.ball_dir, lx=e.last_x, ly=e.last_y, pos=e.pos,
                  strike=e.strike, nbricks=int(e.brick_map.sum()), a=a, amax=int(np.argmax(p)),
                  h1=h1[:6].copy(), land=sim_landing(e))
        nb_before = int(e.brick_map.sum())
        r, done = env.act(a)
        st["exec"] = env.last_action
        st["pos_after"] = e.pos
        st["r"] = r
        if int(e.brick_map.sum()) > nb_before: refills += 1
        trace.append(st)
        if len(trace) > 400 and not keep_trace:
            trace = trace[-60:]
        score += r
        if r: rewards_t.append(t)
        # loop detection on full env state (ignoring stochastic action state)
        if loop_info is None and t % 1 == 0:
            key = (e.ball_x, e.ball_y, e.ball_dir, e.pos, e.last_x, e.last_y, e.strike, e.brick_map.tobytes())
            if key in seen:
                loop_info = (seen[key], t)
            elif t >= 0:
                seen[key] = t
        if done:
            return dict(seed=seed, score=score, steps=t + 1, done=True, trace=trace, refills=refills,
                        rewards_t=rewards_t, loop=loop_info, bricks_end=int(e.brick_map.sum()))
    return dict(seed=seed, score=score, steps=wsp.MAX_STEPS, done=False, trace=trace if keep_trace else trace[-60:], refills=refills,
                rewards_t=rewards_t, loop=loop_info, bricks_end=int(e.brick_map.sum()))

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    which = sys.argv[1]; n = int(sys.argv[2])
    net = nets()[which]
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(net, s, False) for s in range(n)], chunksize=5))
    pickle.dump(res, open(f"episodes_{which}_{n}.pkl", "wb"))
    sc = np.array([r["score"] for r in res]); ln = np.array([r["steps"] for r in res])
    print(which, "episodes", n, "mean score", sc.mean(), "max", sc.max(), "mean len", ln.mean(),
          "cap-hit", int((~np.array([r['done'] for r in res])).sum()))
