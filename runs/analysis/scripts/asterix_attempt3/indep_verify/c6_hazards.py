# For each Astra policy-chosen fatal move, read Astra's layer-2 hazard units in the actual pre-death state.
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from collections import Counter
A = nets()["astra"]
res = {R["seed"]: R for R in pickle.load(open("my_inst_astra.pkl", "rb"))}
det = pickle.load(open("my_deaths_astra.pkl", "rb"))
pm = [d for d in det if d["c"].startswith("policy:") and "no safe" not in d["c"] and d["ex"] in (2, 4)]
pat = Counter()
for d in pm:
    s = res[d["seed"]]["log"][-1]
    g = type("G", (), {})(); g.player_y = s["py"]; g.player_x = s["px"]; g.entities = s["ents"]
    a1, a2, z, p = layers(A, obs_from_game(g))
    assert abs(p[d["ex"]] - s["p"][d["ex"]]) < 1e-5
    mv = a2[0] if d["ex"] == 2 else a2[1]
    pat[(f"row{d['row']}", "wait>0" if a2[2] > 0 else "wait<=0", "movehaz>0" if mv > 0 else "movehaz<=0",
         "|z_move - z_noop|<5" if abs(z[d['ex']] - z[0]) < 5 else "|dz|>=5")] += 1
for k, v in pat.most_common(): print(v, k)
