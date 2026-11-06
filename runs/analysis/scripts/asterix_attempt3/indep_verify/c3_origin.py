# For each Claude death where a sticky repeat executed up/down, walk back through the sticky chain to the step
# where the POLICY sampled that move; check the fatal row at that step, and why the move was chosen.
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from collections import Counter
C = nets()["claude"]
res = pickle.load(open("my_inst_claude.pkl", "rb"))
NM = ["noop","left","up","right","down","fire"]
def state_obs(s, drop_gold=False):
    g = type("G", (), {})(); g.player_y = s["py"]; g.player_x = s["px"]
    g.entities = [e for e in s["ents"] if e is not None and not (drop_gold and e[3])]
    return obs_from_game(g)
def danger(ents, row):
    for e in ents:
        if e is None or e[3] or e[1] != row: continue
        x, right = e[0], e[2]
        if x == 5 or (right and x in (3, 4)) or ((not right) and x in (6, 7)): return True
    return False
def own_threat(ents, row):
    return danger(ents, row)
n = 0; n_moved = 0; vis = Counter(); vis_moved = Counter(); why = Counter(); chainlen = Counter(); gap = Counter()
for R in res:
    if not R["done"]: continue
    L = R["log"]; s = L[-1]
    if not (s["sticky"] and s["ex"] != s["a"] and s["ex"] in (2, 4)): continue
    n += 1
    m = s["ex"]; fatal_row = s["py1"]; moved = s["py1"] != s["py"]
    k = len(L) - 2
    while True:
        q = L[k]
        assert q["ex"] == m
        if not (q["sticky"] and q["a"] != q["ex"]): break   # policy sampled m here
        k -= 1
    o = L[k]
    chainlen[len(L) - 1 - k] += 1
    d = danger(o["ents"], fatal_row)
    vis[d] += 1
    if moved: vis_moved[d] += 1; n_moved += 1
    # reason for original move
    _, a2, z, p = layers(C, state_obs(o)); _, _, z0, p0 = layers(C, state_obs(o, drop_gold=True))
    if own_threat(o["ents"], o["py"]): r = "dodge: own row had enemy at c5/approaching<=2"
    elif p0[m] < 0.5 and p[m] >= 0.5: r = "gold chase: move prob >=0.5 with gold, <0.5 with gold removed"
    else: r = f"other (p={p[m]:.2f}, p_nogold={p0[m]:.2f})"
    why[r.split(" (")[0]] += 1
print("sticky up/down-repeat deaths:", n, " (of which player actually moved:", n_moved, ")")
print("steps between policy's original move and death:", sorted(chainlen.items()))
print("fatal row held enemy at c5 or approaching within 2 cols at the original step:", dict(vis))
print("  restricted to deaths where player moved:", dict(vis_moved))
for k, v in why.most_common(): print("  original move:", v, k)
