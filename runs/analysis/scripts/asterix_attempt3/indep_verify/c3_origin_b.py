# Sensitivity of claim-3 counts to definitions: t-1 vs true original step; several 'gold chase' definitions.
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c3_origin import *   # reruns base analysis and reuses helpers
print("----- sensitivity")
cnt = Counter(); rows = []
for R in res:
    if not R["done"]: continue
    L = R["log"]; s = L[-1]
    if not (s["sticky"] and s["ex"] != s["a"] and s["ex"] in (2, 4)): continue
    m = s["ex"]; fatal_row = s["py1"]
    k = len(L) - 2
    while L[k]["sticky"] and L[k]["a"] != L[k]["ex"]: k -= 1
    o = L[k]; prev = L[-2]
    cnt["danger@orig"] += danger(o["ents"], fatal_row)
    cnt["danger@t-1"] += danger(prev["ents"], fatal_row)
    sgn = -1 if m == 2 else 1
    # gold present in the move's direction, approaching (or at c5), own row not threatened
    gdir = any(e is not None and e[3] and (e[1] - o["py"]) * sgn > 0 and (e[0] == 5 or (e[2] and e[0] < 5) or ((not e[2]) and e[0] > 5)) for e in o["ents"])
    thr = own_threat(o["ents"], o["py"])
    _, a2, z, p = layers(C, state_obs(o)); _, _, z0, p0 = layers(C, state_obs(o, drop_gold=True))
    y = o["py"] - 1
    S, V = a2[y], a2[24 + y]
    cnt["V points along move & S<=0.5"] += (S <= 0.5) and ((m == 2 and V > 0.5) or (m == 4 and V < -0.5))
    cnt["approaching gold in move dir & own row unthreatened"] += gdir and not thr
    cnt["argmax w/o gold != move & argmax with gold == move"] += (int(np.argmax(z0)) != m) and (int(np.argmax(z)) == m)
    cnt["p(move)>=.5 with gold, <.5 without"] += (p[m] >= .5) and (p0[m] < .5)
    if not danger(o["ents"], fatal_row):
        rows.append((R["seed"], len(L)-1-k, o["py"], fatal_row, [e for e in o["ents"] if e is not None and e[1] == fatal_row],
                     [e for e in prev["ents"] if e is not None and e[1] == fatal_row], [e for e in s["ents"] if e is not None and e[1] == fatal_row]))
for k_, v in cnt.items(): print(f"  {v:4d}  {k_}")
print("cases with no visible danger in fatal row at the original step (seed, chain, orig row, fatal row, fatal-row ents at orig / t-1 / death-step):")
for r in rows: print("  ", r)
