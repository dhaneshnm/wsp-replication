import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
def run(seed):
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    c = Counter()
    for t in range(wsp.MAX_STEPS):
        x = ob(); h1, h2, z, p = fwd(CL, x)
        a = int(rng.choice(6, p=p))
        py = g.sub_y
        centered = (g.sub_x == 5 and not g.sub_or) or (g.sub_x == 6 and g.sub_or)
        if py >= 2 and centered:
            facing_L = not g.sub_or
            ens = [e for e in g.e_fish + g.e_subs if e[1] == py]
            # approaching enemy behind the sub, inside the T window
            behind = [e for e in ens if (facing_L and e[0] >= 7 and not e[2]) or ((not facing_L) and e[0] <= 3 and e[2])]
            ahead = [e for e in ens if (facing_L and e[0] <= 4) or ((not facing_L) and e[0] >= 7)]
            if behind and not ahead:
                turned = h2[2] > 0 if facing_L else h2[3] > 0
                if turned: c["turn_unit_on"] += 1
                else:
                    grid = x.reshape(10, 10, 6)[py]
                    fw = range(0, 4) if facing_L else range(7, 10)
                    dv = any(grid[cc, 2] and not grid[cc, 1] for cc in fw)
                    bl = any(grid[cc, 1] and not grid[cc, 2] for cc in fw)
                    c["missed:" + ("diver_on_facing_side" if dv else ("bullet_on_facing_side" if bl else "other"))] += 1
        r, done = env.act(a)
        if done: break
    return c
if __name__ == "__main__":
    n = int(sys.argv[1])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, range(n), chunksize=10))
    tot = Counter(); [tot.update(r) for r in res]
    s = sum(tot.values()); print("steps with approaching enemy behind a centred sub (no enemy ahead):", s)
    for k, v in tot.most_common(): print(f"  {k:35s} {v:6d} ({v/s:.1%})")
