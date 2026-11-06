"""Claims 5 and 6: independent no-sticky runs and weight interventions.
Usage: r5_variants.py <variant> <base_seed> <n<=200>"""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/net.npz"
AS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz"


def cp(n):
    return {k: v.copy() for k, v in n.items()}


def astra_drop_lookahead(n):
    """Zero Astra's two-rows-away hazard weights: player cell (row y, col 5) -> up-hazard unit for row y-2 and
    down-hazard unit for row y+2 (units 0..7 up hazards for rows 1..8, 8..15 down hazards for rows 1..8)."""
    n = cp(n); hits = []
    for y in range(1, 9):
        i = (y * 10 + 5) * 6 + 0
        if y - 2 >= 1:
            u = (y - 2) - 1; hits.append((y, u, float(n["W1"][i, u]))); n["W1"][i, u] = 0
        if y + 2 <= 8:
            u = 8 + (y + 2) - 1; hits.append((y, u, float(n["W1"][i, u]))); n["W1"][i, u] = 0
    return n, hits


def claude_add_lookahead(n, w_h1=2.0, w_h2=0.0):
    """Claude: let up_y (unit 7+y) also read H1/H2 of row y-2, and down_y (unit 15+y) read row y+2.
    H1_r = unit 7+r, H2_r = unit 15+r."""
    n = cp(n)
    for y in range(1, 9):
        if y - 2 >= 1:
            n["W2"][7 + (y - 2), 7 + y] += w_h1; n["W2"][15 + (y - 2), 7 + y] += w_h2
        if y + 2 <= 8:
            n["W2"][7 + (y + 2), 15 + y] += w_h1; n["W2"][15 + (y + 2), 15 + y] += w_h2
    return n


def set_noop_bias(n, b):
    n = cp(n); n["b3"][0] = b; return n


def build(v):
    c, a = wsp.load_npz(CL), wsp.load_npz(AS)
    return {
        "claude": (c, 0.1), "astra": (a, 0.1),
        "claude_nosticky": (c, 0.0), "astra_nosticky": (a, 0.0),
        "astra_nolook": (astra_drop_lookahead(a)[0], 0.1),
        "claude_look": (claude_add_lookahead(c, 2.0, 0.0), 0.1),
        "claude_look_h2": (claude_add_lookahead(c, 2.0, 0.5), 0.1),
        "claude_noop4": (set_noop_bias(c, 4.0), 0.1),
        "claude_look_h2_noop4": (set_noop_bias(claude_add_lookahead(c, 2.0, 0.5), 4.0), 0.1),
        "astra_noop_weak": (set_noop_bias(a, float(sys.argv[4]) if len(sys.argv) > 4 else 17.0), 0.1),
        "astra_nolook_nosticky": (astra_drop_lookahead(a)[0], 0.0),
    }[v]


def play(net, seed, sticky):
    from minatar import Environment
    env = Environment("asterix", sticky_action_prob=sticky); env.seed(seed); env.reset()
    inner = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    W1, b1, W2, b2, W3, b3 = (net[k].astype(np.float64) for k in ("W1", "b1", "W2", "b2", "W3", "b3"))
    tot = 0.0
    for t in range(10_000):
        s = inner.state()  # channels player0 enemy1 trail2 gold3 -> net channels 0,1,4,2
        o = np.zeros((10, 10, 6)); o[..., 0] = s[..., 0]; o[..., 1] = s[..., 1]; o[..., 2] = s[..., 3]; o[..., 4] = s[..., 2]
        h = np.tanh(np.tanh(o.reshape(600) @ W1 + b1) @ W2 + b2)
        z = (h @ W3 + b3).astype(np.float32)  # match harness dtype for identical sampling
        p = np.exp(z - z.max()); p /= p.sum()
        r, d = env.act(int(rng.choice(6, p=p)))
        tot += r
        if d:
            return tot, t + 1
    return tot, 10_000


def work(args):
    v, seeds = args
    net, sticky = build(v)
    return [play(net, s, sticky) for s in seeds]


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    v, base, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    assert n <= 200
    seeds = list(range(base, base + n)); ch = [seeds[i::4] for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        res = [x for part in ex.map(work, [(v, c) for c in ch]) for x in part]
    sc = np.array([x[0] for x in res]); ln = np.array([x[1] for x in res])
    extra = (" noop_bias=" + sys.argv[4]) if len(sys.argv) > 4 else ""
    print(f"{v}{extra} seeds {base}..{base+n-1}: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(n):.2f} mean_len {ln.mean():.1f} max {sc.max():.0f} timeouts {(ln>=10000).sum()}", flush=True)
