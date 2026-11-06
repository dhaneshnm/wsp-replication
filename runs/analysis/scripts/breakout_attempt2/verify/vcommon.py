"""Independent verification helpers (written separately from the analyst's p*.py scripts)."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz"
ANSWER = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/answer.md"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
ASTRA_ANSWER = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md"


def fold(u):
    m = u % 20
    return m if m < 10 else 19 - m


def S(r):
    return r + 1 if r >= 4 else 9 - r


def design_tables(s_row1=None):
    """Tables as stated in answer.md prose: D(r,c)=F(c+dx(8-r)), U(r,c)=F(c+dx S(r))."""
    T = {}
    for name, dx, up in (("D+", 1, False), ("D-", -1, False), ("U+", 1, True), ("U-", -1, True)):
        t = np.zeros((10, 10), int)
        for r in range(10):
            k = (S(r) if (s_row1 is None or r != 1) else s_row1) if up else 8 - r
            for c in range(10):
                t[r, c] = fold(c + dx * k)
        T[name] = t
    return T


# columns of a step record
COLS = ["t", "by", "bx", "ly", "lx", "dir", "pos", "strike", "a", "exe", "sticky", "r", "done",
        "nby", "nbx", "npos"]
CI = {c: i for i, c in enumerate(COLS)}


def run_episode(net, seed, sticky=0.1, cap=10_000):
    """Same RNG streams and order of operations as wsp.play_episode, plus a per-step record."""
    from minatar import Environment
    env = Environment("breakout", sticky_action_prob=sticky)
    env.seed(seed)
    env.reset()
    e = env.env
    obs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed + 1_000_003)
    rows = []
    score = 0.0
    steps = cap
    for t in range(cap):
        pre = (t, e.ball_y, e.ball_x, e.last_y, e.last_x, e.ball_dir, e.pos, int(e.strike))
        x = obs()
        z = wsp.logits(net, x)
        p = np.exp(z - z.max())
        p /= p.sum()
        a = int(rng.choice(6, p=p))
        st = env.random.get_state()
        u = env.random.rand()
        env.random.set_state(st)
        stk = int(u < env.sticky_action_prob)
        r, done = env.act(a)
        score += r
        rows.append(pre + (a, env.last_action, stk, int(r), int(done), e.ball_y, e.ball_x, e.pos))
        if done:
            steps = t + 1
            break
    return score, steps, np.array(rows, dtype=np.int32)


def _w(args):
    net, seeds, sticky, keep = args
    out = []
    for s in seeds:
        sc, n, rec = run_episode(net, s, sticky)
        out.append((s, sc, n, rec if keep else None))
    return out


def run_many(net, seeds, sticky=0.1, keep=True, workers=4):
    from concurrent.futures import ProcessPoolExecutor
    seeds = list(seeds)
    chunks = [seeds[i::workers] for i in range(workers)]
    with ProcessPoolExecutor(workers) as ex:
        res = [r for part in ex.map(_w, [(net, c, sticky, keep) for c in chunks]) for r in part]
    res.sort(key=lambda r: r[0])
    return res


def layers(net, x):
    a1 = x @ net["W1"] + net["b1"]
    h1 = np.tanh(a1)
    a2 = h1 @ net["W2"] + net["b2"]
    h2 = np.tanh(a2)
    return a1, h1, a2, h2, h2 @ net["W3"] + net["b3"]


def move_class(z):
    """0 = no-op class, 1 = left, 3 = right (argmax over the three effective classes)."""
    nz = max(z[0], z[2], z[4], z[5])
    cand = [(nz, 0), (z[1], 1), (z[3], 3)]
    return max(cand)[1]
