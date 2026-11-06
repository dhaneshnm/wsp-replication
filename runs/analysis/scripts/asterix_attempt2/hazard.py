import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import copy, collections, pickle
import numpy as np
import wsp
from common import *

def row_status(inner, r):
    e = inner.entities[r - 1]
    if e is None: return "empty"
    x, _, lr, g = e
    d = (5 - x) if lr else (x - 5)
    if g: return "gold-approach" if d >= 0 else "gold-passed"
    if d < 0: return "enemy-passed"
    if d == 0: return "enemy@5"
    if d == 1: return "enemy-d1"
    if d <= 3: return "enemy-d2-3"
    return "enemy-far"

def run(net, seed):
    env = wsp._make_env("asterix", seed); inner = env.env
    obsf = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    st = collections.Counter(); hz = collections.defaultdict(float)
    moves_by_status = collections.Counter(); steps_by_status = collections.Counter()
    score = 0
    for t in range(wsp.MAX_STEPS):
        x = obsf(); z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        L = env.last_action
        L0 = 0 if L == 5 else L
        F = {b: try_action(inner, b)[1] for b in range(5)}
        pf = sum(p[b] for b in range(5) if F[b]) + (p[5] if F[0] else 0)
        ms = inner.move_speed
        hz[("sticky", ms)] += 0.1 * F[L0]
        hz[("policy", ms)] += 0.9 * pf
        hz[("steps", ms)] += 1
        s = row_status(inner, inner.player_y)
        steps_by_status[s] += 1
        r, done = env.act(a)
        eff = env.last_action
        st["steps"] += 1
        if eff in (2, 4): st["eff_move"] += 1; moves_by_status[s] += 1
        if a in (2, 4): st["chosen_move"] += 1
        score += r
        if done: break
    return dict(score=score, steps=t + 1, st=st, hz=dict(hz), mbs=moves_by_status, sbs=steps_by_status)

def worker(args):
    which, seeds, mod = args
    net = load(which)
    if mod: net = mod(net)
    return [run(net, s) for s in seeds]

def summarize(res, label):
    st = sum((r["st"] for r in res), collections.Counter())
    hz = collections.defaultdict(float)
    for r in res:
        for k, v in r["hz"].items(): hz[k] += v
    mbs = sum((r["mbs"] for r in res), collections.Counter()); sbs = sum((r["sbs"] for r in res), collections.Counter())
    sc = np.array([r["score"] for r in res]); ln = np.array([r["steps"] for r in res])
    print(f"== {label}: n={len(res)} mean score {sc.mean():.2f} (se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f}) mean len {ln.mean():.1f}")
    print(f"  effective vertical move share {st['eff_move']/st['steps']:.3f}; chosen move share {st['chosen_move']/st['steps']:.3f}")
    tot_s = sum(v for (k, m), v in hz.items() if k == "sticky"); tot_p = sum(v for (k, m), v in hz.items() if k == "policy")
    print(f"  expected deaths: sticky {tot_s:.1f}, policy-sampling {tot_p:.1f} (sum {tot_s+tot_p:.1f} vs {len(res)} episodes)")
    for m in sorted({m for (k, m) in hz}):
        n = hz[("steps", m)]
        print(f"   move_speed {m}: steps {int(n)}, sticky hazard/step {hz[('sticky', m)]/n:.5f}, policy hazard/step {hz[('policy', m)]/n:.5f}")
    print("  share of steps by own-row status / P(effective move | status):",
          {k: (round(sbs[k]/st['steps'], 3), round(mbs[k]/sbs[k], 3)) for k in sorted(sbs)})

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    which = sys.argv[1]; n = int(sys.argv[2])
    seeds = list(range(n)); chunks = [seeds[i::4] for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        res = [r for part in ex.map(worker, [(which, c, None) for c in chunks]) for r in part]
    pickle.dump(res, open(f"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/hz_{which}_{n}.pkl", "wb"))
    summarize(res, which)
