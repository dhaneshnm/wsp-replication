import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
res = pickle.load(open("inst_claude_200.pkl","rb"))
DY={0:0,1:0,2:-1,3:0,4:1,5:0}
def build_obs(py, ents):
    o=np.zeros((10,10,6),np.float32); o[py,5,0]=1
    for e in ents:
        if e is None: continue
        o[e[1],e[0],2 if e[3] else 1]=1
        b=e[0]-1 if e[2] else e[0]+1
        if 0<=b<=9: o[e[1],b,4]=1
    return o.reshape(600)
moves=Counter(); fatal=Counter(); twoaway=Counter()
for R in res:
    full=R["full"]; tr=R["ents_trace"]
    X=np.stack([build_obs(f[1],tr[k]) for k,f in enumerate(full)])
    h1=np.tanh(X@NET["W1"]+NET["b1"]); h2=np.tanh(h1@NET["W2"]+NET["b2"])
    for k,(t,py,ex,a,stk,r,ms,ramp) in enumerate(full):
        if ex not in (2,4) or (stk and ex!=a): continue
        y1=min(8,max(1,py+DY[ex]))
        if y1==py: continue
        S=h2[k,py-1]; V=h2[k,24+py-1]; d=DY[ex]
        why = "dodge" if S>0.5 else ("gold" if (d<0 and V>0.5) or (d>0 and V<-0.5) else "drift")
        moves[why]+=1
        # danger two rows away in move direction at decision time (enemy at c5 or within 2 cols approaching)
        r2=py+2*d
        dang=any(e is not None and not e[3] and e[1]==r2 and (e[0]==5 or (e[2] and e[0] in (3,4)) or ((not e[2]) and e[0] in (6,7))) for e in tr[k])
        if dang: twoaway[why]+=1
        # fatal sticky repeat next step?
        if k==len(full)-2 and R["done"]:
            s=full[k+1]
            if s[4] and s[2]==ex and s[3]!=ex: fatal[why]+=1
tot=sum(moves.values())
for w in ("gold","dodge","drift"):
    print(f"{w:6s} policy moves {moves[w]:6d} ({100*moves[w]/tot:4.1f}%), with danger 2 rows ahead {twoaway[w]:5d} ({100*twoaway[w]/max(1,moves[w]):4.1f}%), followed by fatal sticky repeat {fatal[w]:4d} ({100*fatal[w]/max(1,moves[w]):.2f}% per move)")
