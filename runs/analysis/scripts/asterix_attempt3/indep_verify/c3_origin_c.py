import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from collections import Counter
C = nets()["claude"]
res = pickle.load(open("my_inst_claude.pkl", "rb"))
c = Counter()
for R in res:
    L = R["log"]; s = L[-1]
    if not (R["done"] and s["sticky"] and s["ex"] != s["a"] and s["ex"] in (2, 4)): continue
    m = s["ex"]; k = len(L) - 2
    while L[k]["sticky"] and L[k]["a"] != L[k]["ex"]: k -= 1
    o = L[k]; chain = len(L) - 1 - k
    g = type("G", (), {})(); g.player_y = o["py"]; g.player_x = o["px"]; g.entities = o["ents"]
    _, a2, z, p = layers(C, obs_from_game(g)); y = o["py"] - 1
    vchase = a2[y] <= 0.5 and ((m == 2 and a2[24+y] > 0.5) or (m == 4 and a2[24+y] < -0.5))
    c[(f"chain{chain}", "V-chase" if vchase else ("S>0.5 dodge" if a2[y] > 0.5 else "other"))] += 1
for k_, v in sorted(c.items()): print(v, k_)
