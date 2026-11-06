import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import Counter
def cells(x, f): return frozenset((x, x + 1) if f == "L" else (x - 1, x))
def cellstr(grid, c):
    s = ""
    if grid[c, 0]: s += "S"
    if grid[c, 1] and grid[c, 2]: s += "E"
    elif grid[c, 1]: s += "b"
    elif grid[c, 2]: s += "D"
    if grid[c, 4]: s += "t"
    if grid[c, 3]: s += "f"
    return s or "."
res = json.load(open("deaths_claude_200.json"))
sel = []
for r in res:
    if r["kind"] not in ("fish", "enemy_sub", "bullet") or r["moved_vert"]: continue
    pre = r["last"][-1]; px, pf, ea = pre[2], pre[3], r["ea"]
    if ea in ("left", "right"):
        nf = "L" if ea == "left" else "R"; nx = max(0, px - 1) if ea == "left" else min(9, px + 1)
        if cells(nx, nf) == cells(px, pf) and not r["facing_killer_pre"]: sel.append(r)
print("turn-in-place into killer from behind:", len(sel))
# classify: how many steps before death was the sub in this row; was the killer in cols 7-9 / 0-3 visible while facing away
summary = Counter()
for i, r in enumerate(sel):
    seed, tdeath = r["seed"], r["t"]
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest"); rng = np.random.default_rng(seed + 1_000_003)
    rows = []
    for t in range(tdeath + 1):
        x = ob(); h1, h2, z, p = fwd(CL, x)
        a = int(rng.choice(6, p=p))
        if t >= tdeath - 7:
            py = g.sub_y; grid = x.reshape(10, 10, 6)[py]
            pre = x @ CL["W1"] + CL["b1"]
            rows.append((t, py, g.sub_x, "R" if g.sub_or else "L", (pre[9 + py - 2] if py >= 2 else float('nan')), ' '.join(cellstr(grid, c) for c in range(10)), ACT[a]))
        env.act(a)
    same = 0
    for rr in reversed(rows):
        if rr[1] == r["row"]: same += 1
        else: break
    summary["steps_in_row<=2" if same <= 2 else "steps_in_row>2"] += 1
    if i < 7:
        print(f"--- seed {seed} death t={tdeath} kind={r['kind']} steps in row (of last 8)={same}")
        for rr in rows: print(f"   t={rr[0]} row={rr[1]} front={rr[2]} face={rr[3]} Tpre={rr[4]:+.2f} [{rr[5]}] a={rr[6]}")
print(summary)
