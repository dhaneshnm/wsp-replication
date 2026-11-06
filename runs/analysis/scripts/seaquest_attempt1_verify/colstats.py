import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
def run(args):
    which, seed = args
    net = CL if which == "claude" else AS
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    cols = Counter(); moves = Counter(); kills = 0; bonus = 0; surf_attempts = 0; prev_req = False
    for t in range(wsp.MAX_STEPS):
        x = ob(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        if g.sub_y >= 2: cols[g.sub_x] += 1
        req = g.oxygen < 60 and g.diver_count >= 1
        if req and not prev_req: surf_attempts += 1
        prev_req = req
        px, py, po, pdc = g.sub_x, g.sub_y, g.sub_or, g.diver_count
        r, done = env.act(a)
        ea = env.last_action
        if g.sub_y == 0 and py > 0 and not done and pdc == 6: bonus += r
        else: kills += r
        if ea in (1, 3):
            cells = lambda x, o: frozenset((x - 1, x) if o else (x, x + 1))
            if cells(g.sub_x, g.sub_or) == cells(px, po): moves["turn_in_place" if g.sub_or != po else "noeffect"] += 1
            else: moves["shift_" + ("same_dir" if po == g.sub_or else "??")] += 1
        if done: break
    return dict(cols=dict(cols), moves=dict(moves), kills=kills, bonus=bonus, steps=t + 1, surf_attempts=surf_attempts)
if __name__ == "__main__":
    which = sys.argv[1]; n = int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(which, s) for s in range(n)], chunksize=10))
    cols = Counter(); [cols.update(r["cols"]) for r in res]; tot = sum(cols.values())
    print(which, "front col distribution (rows>=2):", {k: round(v / tot, 3) for k, v in sorted(cols.items())})
    mv = Counter(); [mv.update(r["moves"]) for r in res]; print("left/right executions:", dict(mv), "per episode:", {k: v / n for k, v in mv.items()})
    print("mean kills", np.mean([r["kills"] for r in res]), "mean surface bonus", np.mean([r["bonus"] for r in res]), "mean steps", np.mean([r["steps"] for r in res]))
    print("kills per 100 steps", 100 * sum(r["kills"] for r in res) / sum(r["steps"] for r in res))
    print("surfacing requests per episode", np.mean([r["surf_attempts"] for r in res]))
