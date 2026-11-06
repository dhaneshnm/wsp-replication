# What are the S-unit sign mismatches?
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from collections import Counter
C = nets()["claude"]
res = pickle.load(open("my_inst_claude.pkl", "rb"))
cnt = Counter()
for R in res:
    for s in R["log"]:
        y = s["py"]
        own = [e for e in s["ents"] if e is not None and e[1] == y]
        if not own: continue
        e = own[0]; x, _, right, gold = e
        g = type("G", (), {})(); g.player_y = y; g.player_x = s["px"]; g.entities = s["ents"]
        a1, a2, z, p = layers(C, obs_from_game(g)); S = a2[y-1]
        if gold:
            want = -1 if (x == 5 or (right and x < 5) or ((not right) and x > 5)) else 0
        else:
            want = 1 if ((right and x in (3, 4)) or ((not right) and x in (6, 7))) else 0
        bad = (want == 1 and S < 0.5) or (want == -1 and S > -0.5) or (want == 0 and abs(S) > 0.5)
        if bad: cnt[("gold" if gold else "enemy", x, "->" if right else "<-", f"want {want}", f"S~{S:+.2f}")] += 1
for k, v in cnt.most_common(): print(v, k)
