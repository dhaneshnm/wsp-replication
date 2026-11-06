import os, pickle
import numpy as np
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__))
A = ["noop", "left", "up", "right", "down", "fire"]
R = pickle.load(open(os.path.join(H, "roll_claude_200.pkl"), "rb"))
def cells(x, right): return frozenset((x - 1, x) if right else (x, x + 1))

print("##### Claim 5 detail: surfacing-up deaths")
pu = []; killer = Counter()
for e in R:
    d = e["death"]
    if d is None or d["ea"] != 2 or d["a"] != 2: continue
    if not (d["pre_oxy"] < 60 and d["pre_dc"] >= 1): continue
    s = e["steps"][-1]
    pu.append(s["pa"][2])
    ny, nx = d["post_y"], d["post_x"]
    k = []
    for f in d["fish"]:
        if f[1] == ny and (f[0] == nx or (f[3] == 0 and f[0] + (1 if f[2] else -1) == nx)): k.append("fish")
    for f in d["subs"]:
        if f[1] == ny and (f[0] == nx or (f[3] == 0 and f[0] + (1 if f[2] else -1) == nx)): k.append("sub")
    for b in d["bul"]:
        if b[1] == ny and (b[0] == nx or b[0] + (1 if b[2] else -1) == nx): k.append("bullet")
    killer[tuple(sorted(set(k))) or ("none-found",)] += 1
print("n", len(pu), "p(up) at death step: min", min(pu), "median", np.median(pu), " killers", dict(killer))

print("##### Claim 9/10: shift events (rows>=2)")
src = Counter(); trail_any = Counter(); trail_caused = Counter(); offc = Counter()
n = 0
for e in R:
    for s in e["steps"]:
        if s["ea"] not in (1, 3) or s["y"] < 2: continue
        c0, c1 = cells(s["x"], s["right"]), cells(s["nx"], s["nright"])
        if c0 == c1: continue
        n += 1
        tu = 2 if s["ea"] == 3 else 3      # TURN_R unit -> right, TURN_L unit -> left
        cu = 5 if s["ea"] == 3 else 4      # center units: CL(4)->left, CR(5)->right
        if s["ea"] != s["a"]: k = "sticky"
        elif s["h2"][tu] > 0: k = "TURN"
        elif s["h2"][cu] > 0: k = "CENTER"
        else: k = "low_p_sample"
        src[k] += 1
        ft = [c for c in s["foreign_trail_cols"] if c in (4, 6, 7)]
        trail_any[(k, bool(ft))] += 1
        if k == "TURN":
            trail_caused["TURN shift; turn unit off once foreign trails removed"] += s["h2_notrail"][tu] <= 0
        if k == "sticky":
            # previous step's chosen action drove it: was the previous step's turn unit trail-driven?
            pass
        offc[("front_not_5_6" if s["x"] not in (5, 6) else "front_5_6", "cells_not_56" if c0 != frozenset((5, 6)) else "cells_56")] += 1
print("shift events rows>=2:", n, " by source:", dict(src))
print("with foreign trail in cols 4/6/7:", dict(trail_any))
tt = sum(v for (k, f), v in trail_any.items() if k in ("TURN", "sticky") and f)
print("TURN-or-sticky shifts:", src["TURN"] + src["sticky"], " of which foreign trail in 4/6/7:", tt)
print(dict(trail_caused))
print("off-centre starts:", dict(offc))

print("##### Claim 11: approaching enemy behind a centred sub, nothing ahead")
for window in ("analyst(behind=cols7-9 / 0-3)", "full(behind=cols7-9 / 0-4)"):
    cnt = Counter()
    for e in R:
        for s in e["steps"]:
            if s["y"] < 2 or cells(s["x"], s["right"]) != frozenset((5, 6)): continue
            row = s["y"]; fl = not s["right"]
            ens = [o for o in s["fish"] + s["subs"] if o[1] == row]
            lo = 3 if window.startswith("analyst") else 4
            if fl:
                behind = [o for o in ens if o[0] >= 7 and not o[2]]
                ahead = [o for o in ens if o[0] <= 4]
            else:
                behind = [o for o in ens if o[0] <= lo and o[2]]
                ahead = [o for o in ens if o[0] >= 7]
            if not behind or ahead: continue
            tu = 2 if fl else 3
            if s["h2"][tu] > 0:
                cnt["turn on"] += 1; continue
            div_face = any(d[1] == row and ((fl and d[0] <= 3) or ((not fl) and d[0] >= 7)) for d in s["divers"])
            fixed = s["h2_nodiver"][tu] > 0
            cnt["missed"] += 1
            cnt["missed & diver on facing side"] += div_face
            cnt["missed & turn fires once own-row divers removed"] += fixed
            if not fl and any(o[0] == 4 for o in behind): cnt["missed with enemy at col4 (facing R)"] += 1
    print(window, dict(cnt))
