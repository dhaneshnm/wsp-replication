import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from move_reasons import build_obs
from collections import Counter
det = pickle.load(open("deaths_astra.pkl","rb"))
res = {R["seed"]:R for R in pickle.load(open("inst_astra_200.pkl","rb"))}
pc=[d for d in det if d["cat"]=="moved into deadly row: policy choice"]
kk=Counter(); pat=Counter(); rows=Counter()
for d in pc:
    s=res[d["seed"]]["log"][-1]
    h1,h2,z,p=fwd(AST, build_obs(s["py"], s["ents"]))
    hz=tuple(int(v>0) for v in h2[0:3])  # up, down, wait hazards on?
    kk[(d["y0"], d["killer"][0] if d["killer"] else None)]+=1
    pat[(d["y0"] in (1,8), hz, ACT[d["a"]])]+=1
    if d["y0"] not in (1,8): print("non-edge:", d, "hazards up/down/wait", np.round(h2[0:3],2), "logits", np.round(z[[0,2,4]],2))
print("killer kind by row:", kk)
print("(edge, hazards(up,down,wait) on, action):")
for k,v in pat.most_common(): print("  ",v,k)
