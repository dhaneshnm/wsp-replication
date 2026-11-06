import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
det = pickle.load(open("deaths_astra.pkl","rb"))
res = {R["seed"]:R for R in pickle.load(open("inst_astra_200.pkl","rb"))}
def board(py, ents):
    g=[["." for _ in range(10)] for _ in range(10)]
    for e in ents:
        if e is None: continue
        g[e[1]][e[0]] = ("G" if e[3] else "E")
        b=e[0]-1 if e[2] else e[0]+1
        if 0<=b<=9: g[e[1]][b]="-"
    g[py][5]="P" if g[py][5]=="." else "X"
    return "\n".join("   "+"".join(r) for r in g)
pc=[d for d in det if d["cat"]=="moved into deadly row: policy choice"]
print("Astra policy-choice deaths:",len(pc))
print(" rows:",Counter(d["y0"] for d in pc), " move_speed:",Counter(d["ms"] for d in pc))
print(" sampled action prob of the fatal move: quantiles", np.percentile([d["p"][d["a"]] for d in pc],[10,25,50,75,90]))
print(" stay was safe:", sum(1 for d in pc), "(by construction)")
for d in pc[:3]:
    s=res[d["seed"]]["log"][-1]
    h1,h2,z,p=fwd(AST, wsp.make_obs_fn.__globals__['np'].zeros(600) if False else None) if False else (None,None,None,None)
    print("seed",d["seed"],"t",d["t"],"row",d["y0"],"action",ACT[d["a"]],"p",d["p"], "move_timer0",d["em"])
    print(board(s["py"], s["ents"]))
