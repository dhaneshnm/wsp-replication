# Counterfactual for the 83 same-row deaths on an executed left/right step:
# at the fatal step, execute 'fire' instead (sticky RNG draw still consumed), then let the policy continue.
import sys, os, copy, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
res = json.load(open("deaths_claude_200.json"))
def cells(x, f): return frozenset((x, x + 1) if f == "L" else (x - 1, x))
sel = []
for r in res:
    if r["kind"] in ("fish", "enemy_sub", "bullet") and not r["moved_vert"] and r["ea"] in ("left", "right"):
        pre = r["last"][-1]; px, pf, ea = pre[2], pre[3], r["ea"]
        nf = "L" if ea == "left" else "R"; nx = max(0, px - 1) if ea == "left" else min(9, px + 1)
        k = "turn" if cells(nx, nf) == cells(px, pf) else "shift"
        sel.append((r["seed"], r["t"], k, r["facing_killer_pre"]))
def run(item):
    seed, tdeath, k, fk = item
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    for t in range(tdeath):
        x = ob(); z = wsp.logits(CL, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p)); env.act(a)
    # step tdeath: draw the policy sample as in the real run, then override to fire
    x = ob(); z = wsp.logits(CL, x); p = np.exp(z - z.max()); p /= p.sum(); a = int(rng.choice(6, p=p))
    env.random.rand(); env.last_action = 5; r, done = env.env.act(5)
    if done: return (k, fk, 0)
    ob2 = wsp.make_obs_fn(env, "seaquest")
    for s in range(1, 61):
        x = ob2(); z = wsp.logits(CL, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p)); r, done = env.act(a)
        if done: return (k, fk, s)
    return (k, fk, None)
if __name__ == "__main__":
    with ProcessPoolExecutor(4) as ex:
        out = list(ex.map(run, sel))
    print("n", len(out))
    c = Counter()
    for k, fk, s in out:
        b = "died same step anyway" if s == 0 else ("died within 5 steps" if s is not None and s <= 5 else ("died within 6-60" if s is not None else "alive after 60"))
        c[(k, "facing" if fk else "behind", b)] += 1
    for kk, v in sorted(c.items()): print(v, kk)
    tot = Counter()
    for k, fk, s in out:
        tot["same step" if s == 0 else ("<=5" if s is not None and s <= 5 else (">5..60" if s is not None else "survived 60"))] += 1
    print(dict(tot))
