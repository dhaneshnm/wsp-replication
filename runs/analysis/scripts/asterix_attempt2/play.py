import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import copy, itertools
import numpy as np
import wsp
from common import *

VERT = [0, 2, 4]

def survives(inner, seq):
    e = copy.deepcopy(inner)
    for a in seq:
        r, t = e.act(a)
        if t:
            return False
    return True

def run_episode(net, seed):
    """Exact replica of wsp.play_episode with instrumentation."""
    env = wsp._make_env("asterix", seed)
    inner = env.env
    obsf = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0
    hist = []  # ring of last pre-states
    cols = set(); rows = np.zeros(10, int)
    gold_t = []
    n_sticky_diff = 0
    for t in range(wsp.MAX_STEPS):
        x = obsf()
        z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        pre = copy.deepcopy(inner)
        prev_last = env.last_action
        hist.append((pre, a, p, x)); hist = hist[-4:]
        cols.add(inner.player_x); rows[inner.player_y] += 1
        r, done = env.act(a)
        eff = env.last_action
        if eff != a: n_sticky_diff += 1
        if r: gold_t.append(t)
        score += r
        if done:
            return dict(seed=seed, score=score, steps=t+1, died=True, hist=hist, eff=eff, a=a, prev_last=prev_last,
                        cols=sorted(cols), rows=rows, gold_t=gold_t, n_sticky_diff=n_sticky_diff)
    return dict(seed=seed, score=score, steps=wsp.MAX_STEPS, died=False, cols=sorted(cols), rows=rows,
                gold_t=gold_t, n_sticky_diff=n_sticky_diff)

def classify(ep):
    pre, a, p, x = ep["hist"][-1]
    eff = ep["eff"]
    fatal = {b: try_action(pre, b)[1] for b in range(5)}
    safe_vert = [b for b in VERT if not fatal[b]]
    safe_any = [b for b in range(5) if not fatal[b]]
    # new player pos under effective action
    px, py = pre.player_x, pre.player_y
    if eff == 1: px = max(0, px-1)
    elif eff == 3: px = min(9, px+1)
    elif eff == 2: py = max(1, py-1)
    elif eff == 4: py = min(8, py+1)
    stepped_onto = any(e is not None and not e[3] and e[0:2] == [px, py] for e in pre.entities)
    moved = (eff in (1, 2, 3, 4)) and ((px, py) != (pre.player_x, pre.player_y))
    if stepped_onto:
        mech = "player stepped onto enemy cell"
    else:
        mech = "enemy moved into player (player " + ("moved into its row" if moved else "stayed") + ")"
    # lookahead: from state 1 and 2 steps earlier, could a vertical-only sequence survive through death step?
    look = {}
    for k in (1, 2, 3):
        if len(ep["hist"]) > k:
            s = ep["hist"][-1-k][0]
            look[k] = any(survives(s, seq) for seq in itertools.product(VERT, repeat=k+1))
            look[str(k)+"_any"] = any(survives(s, seq) for seq in itertools.product(range(5), repeat=k+1))
    pf = sum(p[b] for b in range(5) if fatal[b]) + (p[5] if fatal[0] else 0)
    n_enemies = sum(1 for e in pre.entities if e is not None and not e[3])
    n_gold = sum(1 for e in pre.entities if e is not None and e[3])
    return dict(chosen=ACT[a], eff=ACT[eff], sticky=(eff != a), chosen_fatal=fatal[a if a < 5 else 0],
                safe_vert=[ACT[b] for b in safe_vert], safe_any=[ACT[b] for b in safe_any],
                p_fatal=float(pf), mech=mech, look=look, move_speed=pre.move_speed, spawn_speed=pre.spawn_speed,
                ramp=pre.ramp_index, n_enemies=n_enemies, n_gold=n_gold, player=(pre.player_y, pre.player_x),
                prev_last=ACT[ep["prev_last"]])

def worker(args):
    which, seeds = args
    net = load(which)
    out = []
    for s in seeds:
        ep = run_episode(net, s)
        if ep["died"]:
            ep["cls"] = classify(ep)
        ep.pop("hist", None)
        out.append(ep)
    return out

if __name__ == "__main__":
    import pickle
    from concurrent.futures import ProcessPoolExecutor
    which = sys.argv[1]; n = int(sys.argv[2])
    seeds = list(range(n))
    chunks = [seeds[i::4] for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        eps = [e for part in ex.map(worker, [(which, c) for c in chunks]) for e in part]
    eps.sort(key=lambda e: e["seed"])
    pickle.dump(eps, open(f"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/eps_{which}_{n}.pkl", "wb"))
    sc = np.array([e["score"] for e in eps]); ln = np.array([e["steps"] for e in eps])
    print(which, "episodes", n, "mean score", sc.mean(), "se", sc.std(ddof=1)/np.sqrt(n), "mean len", ln.mean())
