import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Diagnostic counterfactuals on copies of Claude's network (not part of the scored reply).
from common import *
import copy
from minatar import Environment
from concurrent.futures import ProcessPoolExecutor

def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m

def cf_catchset(net):
    """Descent units 0-3: compare paddle with the midpoint of both catch cells {x8, next x}, threshold 0.75, scale 10."""
    n = copy.deepcopy(net)
    for (uR, uL, dx) in [(0, 1, 1), (2, 3, -1)]:
        for y in range(9):
            for x in range(10):
                Lm = (fold(x + dx*(8-y)) + fold(x + dx*(9-y))) / 2
                i = (y*10+x)*6+3
                n["W1"][i, uR] = 10*Lm; n["W1"][i, uL] = -10*Lm
        for p in range(10):
            n["W1"][(90+p)*6, uR] = -10*p; n["W1"][(90+p)*6, uL] = 10*p
        n["b1"][uR] = n["b1"][uL] = -7.5
    return n

def cf_uptable(net, T=(9, 10, 7, 6, 5, 6, 7, 8, 9)):
    """Up units 4-7: earliest-brick-bounce return times (Astra's assumption)."""
    n = copy.deepcopy(net)
    for (uR, uL, dx) in [(4, 5, 1), (6, 7, -1)]:
        for y in range(9):
            for x in range(10):
                L = fold(x + dx*T[y]); i = (y*10+x)*6+3
                n["W1"][i, uR] = 5*L; n["W1"][i, uL] = -5*L
    return n

def run_nosticky(args):
    net, seeds = args
    out = []
    for s in seeds:
        env = Environment("breakout", sticky_action_prob=0.0); env.seed(s); env.reset()
        obs = wsp.make_obs_fn(env, "breakout"); rng = np.random.default_rng(s + 1_000_003); sc = 0
        for t in range(wsp.MAX_STEPS):
            z = wsp.logits(net, obs()); p = np.exp(z - z.max()); p /= p.sum()
            r, d = env.act(int(rng.choice(6, p=p))); sc += r
            if d: break
        out.append((sc, t+1))
    return out

if __name__ == "__main__":
    base = wsp.load_npz(CLAUDE)
    # sanity: modified units reproduce intended decisions on hand-built frames
    nets = {"original": base, "A: descent accepts either catch cell": cf_catchset(base),
            "B: up tables use earliest-bounce T": cf_uptable(base), "A+B": cf_uptable(cf_catchset(base))}
    for k, n in nets.items():
        r = wsp.evaluate(n, "breakout", episodes=200, workers=4)
        print(f"{k:42s} mean {r['mean']:.1f} se {r['se']:.1f} mean_len {r['mean_length']:.0f} max {r['max']:.0f}")
    seeds = list(range(200))
    with ProcessPoolExecutor(4) as ex:
        res = [e for part in ex.map(run_nosticky, [(base, seeds[i::4]) for i in range(4)]) for e in part]
    sc = np.array([a for a, b in res]); ln = np.array([b for a, b in res])
    print(f"original, sticky prob 0: mean {sc.mean():.1f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.1f} mean_len {ln.mean():.0f} capped {(ln>=10000).sum()}/200 misses {(ln<10000).sum()}")
