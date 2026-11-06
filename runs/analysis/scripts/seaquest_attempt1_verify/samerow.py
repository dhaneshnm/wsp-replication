import json, sys
from collections import Counter
res = json.load(open(sys.argv[1]))
col = [r for r in res if r["kind"] in ("fish", "enemy_sub", "bullet")]
sr = [r for r in col if not r["moved_vert"]]
def cells(x, f): return frozenset((x, x + 1) if f == "L" else (x - 1, x))
cat = Counter()
for r in sr:
    pre = r["last"][-1]  # (t,row,front,face,act,...)
    px, pf, ea = pre[2], pre[3], r["ea"]
    if ea in ("left", "right"):
        nf = "L" if ea == "left" else "R"
        nx = max(0, px - 1) if ea == "left" else min(9, px + 1)
        kind = "turn_in_place_into_killer" if cells(nx, nf) == cells(px, pf) else "shift_into_killer"
    else:
        kind = "stationary(" + ea + ")"
    off = px not in (5, 6)
    cat[(kind, "off_center" if off else "cols5-6", "facing_killer" if r["facing_killer_pre"] else "killer_behind")] += 1
for k, v in cat.most_common(): print(f"{v:4d}  {k}")
print("same-row deaths:", len(sr), " pre-step front col:", Counter(r["last"][-1][2] for r in sr))
