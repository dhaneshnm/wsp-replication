import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
which=sys.argv[1]
net = NET if which=="claude" else AST
res = pickle.load(open(f"inst_{which}_200.pkl","rb"))
DY={0:0,1:0,2:-1,3:0,4:1,5:0}
def build_obs(py, ents):
    o=np.zeros((10,10,6),np.float32); o[py,5,0]=1
    for e in ents:
        if e is None: continue
        o[e[1],e[0],2 if e[3] else 1]=1
        b=e[0]-1 if e[2] else e[0]+1
        if 0<=b<=9: o[e[1],b,4]=1
    return o.reshape(600)
reason=Counter(); visible=Counter(); n=0
for R in res:
    if not R["done"]: continue
    L=R["log"]; s=L[-1]
    if not (s["sticky"] and s["exec"]!=s["a"] and s["exec"] in (2,4)): continue
    q=L[-2]  # previous step: the move that was repeated
    n+=1
    assert q["exec"]==s["exec"]
    y=q["py"]; d=DY[q["exec"]]
    # why did it move at t-1? policy sample vs sticky
    if q["sticky"] and q["exec"]!=q["a"]: why="t-1 move was itself sticky"
    else:
        if which=="claude":
            h1,h2,z,p=fwd(net, build_obs(y,q["ents"]))
            S=h2[y-1]; V=h2[24+y-1]
            if S>0.5: why="dodge (own-row threat)"
            elif (d<0 and V>0.5) or (d>0 and V<-0.5): why="gold chase"
            else: why="drift/other (p=%.2f)"%q["p"][q["exec"]]
            why = why if not why.startswith("drift") else "drift/other"
        else:
            why="policy move"
    reason[why]+=1
    # was the row two away (y+2d) already dangerous at t-1 (enemy within 2 columns of col 5 approaching, or at 5)?
    r2=y+2*d
    dang=False
    for e in q["ents"]:
        if e is None or e[3] or e[1]!=r2: continue
        if e[0]==5 or (e[2] and e[0] in (3,4)) or ((not e[2]) and e[0] in (6,7)): dang=True
    visible["row y+2d had enemy at c5 or approaching within 2 cols at t-1" if dang else "not visible at t-1 (spawned/far)"]+=1
print(which,"sticky-move deaths:",n)
for k,v in reason.most_common(): print("  reason for t-1 move:",v,k)
for k,v in visible.most_common(): print("  ",v,k)
