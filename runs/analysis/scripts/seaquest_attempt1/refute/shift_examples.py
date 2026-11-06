import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
def cells(x, o): return frozenset((x - 1, x) if o else (x, x + 1))
def cellstr(grid, c):
    s = ""
    if grid[c, 0]: s += "S"
    if grid[c, 1] and grid[c, 2]: s += "E"
    elif grid[c, 1]: s += "b"
    elif grid[c, 2]: s += "D"
    if grid[c, 4]: s += "t"
    if grid[c, 3]: s += "f"
    return s or "."
shown = Counter()
for seed in range(40):
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    for t in range(wsp.MAX_STEPS):
        x = ob(); h1, h2, z, p = fwd(CL, x)
        a = int(rng.choice(6, p=p))
        px, py, po = g.sub_x, g.sub_y, g.sub_or
        fish = [(f[0], "R" if f[2] else "L") for f in g.e_fish if f[1] == py]
        subs = [(f[0], "R" if f[2] else "L") for f in g.e_subs if f[1] == py]
        dv = [(f[0], "R" if f[2] else "L") for f in g.divers if f[1] == py]
        r, done = env.act(a); ea = env.last_action
        if ea in (1, 3) and ea == a and py >= 2 and cells(g.sub_x, g.sub_or) != cells(px, po) and px in (5, 6):
            grid = x.reshape(10, 10, 6)[py]
            pre = x @ CL["W1"] + CL["b1"]
            if shown["x"] < 8:
                shown["x"] += 1
                print(f"seed {seed} t {t} row {py} front {px} face {'R' if po else 'L'} -> {ACT[ea]}; Tpre={pre[9+py-2]:+.2f}; row: {' '.join(cellstr(grid, c) for c in range(10))}; fish(col,dir)={fish} esub={subs} divers={dv}; died={done}")
        if done: break
