import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
det = pickle.load(open("deaths_claude.pkl","rb"))
res = {R["seed"]:R for R in pickle.load(open("inst_claude_200.pkl","rb"))}
def build_obs(py, ents):
    o=np.zeros((10,10,6),np.float32); o[py,5,0]=1
    for e in ents:
        if e is None: continue
        o[e[1],e[0],2 if e[3] else 1]=1
        b=e[0]-1 if e[2] else e[0]+1
        if 0<=b<=9: o[e[1],b,4]=1
    return o.reshape(600)
for cat in ("stayed: sticky repeat overrode a dodge","stayed: no safe neighbour (trapped)"):
    ds=[d for d in det if d["cat"]==cat]
    print(cat, len(ds), "rows:",dict(Counter(d["y0"] for d in ds)), "move_speed:",dict(Counter(d["ms"] for d in ds)))
    hist=Counter()
    for d in ds:
        L=res[d["seed"]]["log"]
        # walk back while in same row: what happened at the previous step(s) when threat was on
        seq=[]
        for s in reversed(L[:-1]):
            if s["py_after"]!=d["y0"]: break
            h1,h2,z,p=fwd(NET,build_obs(s["py"],s["ents"]))
            S=h2[s["py"]-1]
            seq.append(("T" if S>0.5 else "-") + ("s" if (s["sticky"] and s["exec"]!=s["a"]) else "") + ACT[s["exec"]][0] + ("" if s["py"]==d["y0"] else "*entered"))
        hist[" ".join(reversed(seq[:3]))]+=1
    for k,v in hist.most_common(8): print("   ",v," prior steps (oldest->newest, T=threat on, s=sticky changed, letter=executed action):",k)
