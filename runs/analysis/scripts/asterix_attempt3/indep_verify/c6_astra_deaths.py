# Astra: policy-chosen fatal moves while a safe action existed -- rows, killer geometry, own-row state.
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from collections import Counter
NM = ["noop","left","up","right","down","fire"]
res = {R["seed"]: R for R in pickle.load(open("my_inst_astra.pkl", "rb"))}
det = pickle.load(open("my_deaths_astra.pkl", "rb"))
pm = [d for d in det if d["c"].startswith("policy:") and "safe" in d["c"] and "no safe" not in d["c"] and d["ex"] in (2, 4)]
print("policy-chosen fatal moves with a safe alternative:", len(pm))
print(" from-row:", sorted(Counter(d["row"] for d in pm).items()), " to-row:", sorted(Counter(d["row1"] for d in pm).items()))
geo = Counter(); own = Counter(); ptab = []
for d in pm:
    s = res[d["seed"]]["log"][-1]
    tgt = [e for e in s["ents"] if e is not None and e[1] == d["row1"] and not e[3]]
    geo[tuple((e[0], "->" if e[2] else "<-") for e in tgt)] += 1
    o = [e for e in s["ents"] if e is not None and e[1] == d["row"] and not e[3]]
    own[tuple((e[0], "->" if e[2] else "<-") for e in o)] += 1
    ptab.append(s["p"][d["ex"]])
print(" enemy in target row (col,dir):", geo.most_common(8))
print(" enemy in own row (col,dir):", own.most_common(10))
print(" prob policy gave the fatal move: quantiles 10/50/90", np.round(np.percentile(ptab, [10, 50, 90]), 3))
print(" move_timer==0 at death:", Counter(res[d['seed']]['log'][-1]['mt'] == 0 for d in pm))
# does Astra ever leave column 5?
cols = Counter(); 
for R in res.values():
    for s in R["log"]: cols[s["px"]] += 1
print(" astra player column occupancy:", dict(cols))
