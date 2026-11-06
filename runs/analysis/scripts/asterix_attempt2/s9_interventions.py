import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import copy, json
import numpy as np, wsp
from common import *

def lookahead(net, w=2.0, use_h2=False):
    n = {k: v.copy() for k, v in net.items()}
    for y in range(3, 9):   # up_y (unit 7+y) also sees H1 of row y-2 (unit 7+y-2)
        n["W2"][7 + y - 2, 7 + y] += w
        if use_h2: n["W2"][15 + y - 2, 7 + y] += w / 4
    for y in range(1, 7):   # down_y (unit 15+y) also sees H1 of row y+2 (unit 7+y+2)
        n["W2"][7 + y + 2, 15 + y] += w
        if use_h2: n["W2"][15 + y + 2, 15 + y] += w / 4
    return n

def noop_bias(net, b):
    n = {k: v.copy() for k, v in net.items()}; n["b3"][0] = b; return n

def scale_out(net, s):
    n = {k: v.copy() for k, v in net.items()}; n["W3"][0:24] *= s; return n

VARIANTS = {
    "claude": ("claude", None, 0.1),
    "claude_nosticky": ("claude", None, 0.0),
    "astra_nosticky": ("astra", None, 0.0),
    "claude_lookahead_H1": ("claude", lambda n: lookahead(n, 2.0), 0.1),
    "claude_lookahead_H1H2": ("claude", lambda n: lookahead(n, 2.0, True), 0.1),
    "claude_noop4": ("claude", lambda n: noop_bias(n, 4.0), 0.1),
    "claude_W3x2": ("claude", lambda n: scale_out(n, 2.0), 0.1),
}

def play(net, seed, sticky):
    from minatar import Environment
    env = Environment("asterix", sticky_action_prob=sticky); env.seed(seed); env.reset()
    obsf = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0
    for t in range(wsp.MAX_STEPS):
        z = wsp.logits(net, obsf()); p = np.exp(z - z.max()); p /= p.sum()
        r, d = env.act(int(rng.choice(6, p=p))); score += r
        if d: return score, t + 1
    return score, wsp.MAX_STEPS

def worker(args):
    name, seeds = args
    which, mod, sticky = VARIANTS[name]
    net = load(which)
    if mod: net = mod(net)
    return [play(net, s, sticky) for s in seeds]

def _main():
    from concurrent.futures import ProcessPoolExecutor
    n = int(sys.argv[1])
    for name in sys.argv[2:]:
        seeds = list(range(n)); chunks = [seeds[i::4] for i in range(4)]
        with ProcessPoolExecutor(4) as ex:
            res = [r for part in ex.map(worker, [(name, c) for c in chunks]) for r in part]
        sc = np.array([r[0] for r in res]); ln = np.array([r[1] for r in res])
        print(f"{name:24s} n={n} mean {sc.mean():6.2f} se {sc.std(ddof=1)/np.sqrt(n):5.2f} mean_len {ln.mean():7.1f} max {sc.max():.0f}", flush=True)

VARIANTS["claude_lookH1H2_noop4"] = ("claude", lambda n: noop_bias(lookahead(n, 2.0, True), 4.0), 0.1)
VARIANTS["claude_lookH1H2_noop4_nosticky"] = ("claude", lambda n: noop_bias(lookahead(n, 2.0, True), 4.0), 0.0)

if __name__ == "__main__":
    _main()
