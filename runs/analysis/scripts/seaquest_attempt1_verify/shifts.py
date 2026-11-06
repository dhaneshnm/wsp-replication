import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
def cells(x, o): return frozenset((x - 1, x) if o else (x, x + 1))
def run(seed):
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    out = Counter()
    for t in range(wsp.MAX_STEPS):
        x = ob(); h1, h2, z, p = fwd(CL, x)
        a = int(rng.choice(6, p=p))
        px, py, po = g.sub_x, g.sub_y, g.sub_or
        r, done = env.act(a); ea = env.last_action
        if ea in (1, 3) and py >= 2 and cells(g.sub_x, g.sub_or) != cells(px, po):
            grid = x.reshape(10, 10, 6)[py]
            sub_cells = cells(px, po)
            enemy = lambda cs: sum(1 for c in cs if grid[c, 1] and grid[c, 2])
            diver = lambda cs: sum(1 for c in cs if grid[c, 2] and not grid[c, 1])
            bul = lambda cs: sum(1 for c in cs if grid[c, 1] and not grid[c, 2])
            side = (7, 8, 9) if ea == 3 else (0, 1, 2, 3)
            other = (0, 1, 2, 3) if ea == 3 else (7, 8, 9)
            trail_poll = [c for c in (4, 6, 7) if grid[c, 4] and c not in sub_cells]
            src = "sticky" if ea != a else ("TURN" if h2[2 if ea == 3 else 3] > 0 else ("CENTER" if h2[4 if ea == 1 else 5] > 0 else "sampled_low_p"))
            reasons = []
            if px not in (5, 6): reasons.append("off_center_start")
            if enemy(side) >= 2: reasons.append(">=2 enemies that side")
            if enemy(side) + 0.5 * (diver(side) + bul(side)) >= 1.5 and enemy(side) < 2: reasons.append("enemy+diver/bullet that side")
            if trail_poll: reasons.append("foreign trail in facing window")
            if not reasons: reasons.append("other")
            out[(src, "+".join(reasons))] += 1
        if done: break
    return out
if __name__ == "__main__":
    n = int(sys.argv[1])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, range(n), chunksize=10))
    tot = Counter(); [tot.update(r) for r in res]
    print("shift events (rows>=2):", sum(tot.values()))
    for k, v in tot.most_common(20): print(f"{v:5d}  {k}")
