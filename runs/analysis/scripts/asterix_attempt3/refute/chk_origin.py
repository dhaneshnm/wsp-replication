import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import pickle
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
def dang(ents,r):
    return any(e is not None and not e[3] and e[1]==r and (e[0]==5 or (e[2] and e[0] in (3,4)) or ((not e[2]) and e[0] in (6,7))) for e in ents)
n=0; vis_t1=0; vis_orig=0; why=Counter(); lag=Counter()
for R in res:
    if not R["done"]: continue
    L=R["log"]; s=L[-1]
    if not (s["sticky"] and s["exec"]!=s["a"] and s["exec"] in (2,4) and s["py_after"]!=s["py"]): continue
    n+=1; fatal=s["py_after"]
    # walk back to the policy-chosen original move
    k=len(L)-2
    while k>=0 and L[k]["sticky"] and L[k]["exec"]!=L[k]["a"]: k-=1
    q=L[k]; lag[len(L)-1-k]+=1
    vis_t1 += dang(L[-2]["ents"], fatal)
    vis_orig += dang(q["ents"], fatal)
    y=q["py"]; d=DY[q["exec"]]
    h1,h2,z,p=fwd(NET, build_obs(y,q["ents"])); S=h2[y-1]; V=h2[24+y-1]
    why["dodge" if S>0.5 else ("gold" if (d<0 and V>0.5) or (d>0 and V<-0.5) else "drift")]+=1
print("true sticky-move deaths (row changed):",n)
print("fatal row dangerous at t-1:",vis_t1,"; at the step the original move was policy-chosen:",vis_orig)
print("steps between original choice and death:",sorted(lag.items()))
print("reason for original policy move:",why)
# network at the step of the sticky repeat: does U/D inspect the fatal row? probe: player row 4, enemy c5 in row 3
h1,h2,z,p=fwd(NET,obs(4,[(3,5,True,False)]))
print("probe player row 4, enemy c5 row 3: U_4=%+.3f (unit 11), Bk_3=%+.3f (unit 18) | %s"%(h2[11],h1[18],fmtp(p)))
# BUG1 residual decomposition
P=np.tanh(np.float64(5)); T=np.tanh(np.float64(-9)); G=np.tanh(np.float64(-3))
print("S pre-act parts: 10P-10=%.6f  1.5T+1.5=%.2e  -1.5G-1.5=%.6f"%(10*P-10, 1.5*T+1.5, -1.5*G-1.5))
