import os, pickle
import numpy as np
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__))
A = ["noop", "left", "up", "right", "down", "fire"]
R = pickle.load(open(os.path.join(H, "roll_claude_200.pkl"), "rb"))


def cells(x, right):
    return frozenset((x - 1, x) if right else (x, x + 1))


print("##### Claim 4: horizontal movement")
mv_all, mv_r2 = Counter(), Counter()
front = Counter(); centred_cells = 0; n_r2 = 0
for e in R:
    for s in e["steps"]:
        if s["y"] >= 2:
            front[s["x"]] += 1; n_r2 += 1
            centred_cells += cells(s["x"], s["right"]) == frozenset((5, 6))
        if s["ea"] in (1, 3):
            c0, c1 = cells(s["x"], s["right"]), cells(s["nx"], s["nright"])
            k = "shift" if c0 != c1 else ("turn_in_place" if s["right"] != s["nright"] else "no_effect")
            mv_all[k] += 1
            if s["y"] >= 2: mv_r2[k] += 1
print("executed left/right outcomes, all rows:", dict(mv_all), " rows>=2:", dict(mv_r2))
print("front col distribution rows>=2:", {k: round(v / n_r2, 3) for k, v in sorted(front.items())})
print("fraction rows>=2 steps with front col outside 5-6:", round(1 - (front[5] + front[6]) / n_r2, 4),
      " fraction with occupied cells != {5,6}:", round(1 - centred_cells / n_r2, 4))

print("##### Claims 5/6: deaths")
tax = Counter(); caus = Counter(); lr = Counter()
for e in R:
    d = e["death"]
    if d is None: continue
    if d["pre_y"] > 0 and d["post_y"] == 0 and d["pre_dc"] == 0:
        tax["empty_surface"] += 1; continue
    surf = d["pre_oxy"] < 60 and d["pre_dc"] >= 1
    sticky = d["ea"] != d["a"]
    vert = d["post_y"] != d["pre_y"]
    tax[(("surf" if surf else "nosurf"), A[d["ea"]], ("sticky" if sticky else "chosen"), ("vert" if vert else "samerow"))] += 1
    stay_ok = (not d["alt_terminal"][5]) or (not d["alt_terminal"][0])
    any_ok = any(not v for v in d["alt_terminal"].values())
    if d["ea"] == 2 and surf and not sticky:
        caus["surf_up_chosen"] += 1
        caus["surf_up_chosen & fire-or-noop survives"] += stay_ok
    if d["ea"] in (1, 3):
        lr["left/right executed at death step"] += 1
        lr["  of which sticky"] += sticky
        lr["  of which fire-or-noop would survive the step"] += stay_ok
        lr["  of which moved cells"] += cells(d["pre_x"], d["pre_right"]) != cells(d["post_x"], (d["ea"] == 3))
    caus["avoidable by some action"] += any_ok
    if not d["exec_reproduced"]: caus["WARNING exec not reproduced"] += 1
for k, v in tax.most_common(): print(f"  {v:4d} {k}")
print(dict(caus)); print(dict(lr))
agg = Counter()
for k, v in tax.items():
    if k == "empty_surface": continue
    agg[(k[0], k[1], k[2])] += v
print("aggregated (surf, executed, sticky):", agg.most_common(6))
agg2 = Counter()
for k, v in tax.items():
    if k == "empty_surface": continue
    agg2[k[1]] += v
print("by executed action:", agg2.most_common())
