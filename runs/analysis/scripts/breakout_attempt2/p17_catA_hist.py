import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
import json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
MOVE={1:-1,3:1}
def one(seed):
    net=wsp.load_npz(A)
    score,steps,L=run(net,seed,log=True)
    if not L[-1]["done"]: return None
    x=L[-1]; x8=x["bx"]; dx=DX[x["dir"]]
    if not (x["pos"]==x8 and x["exec"]!=x["a"] and MOVE.get(x["exec"],0)*dx<0): return None
    # positions relative to x8 (signed by dx) over last 5 steps, and whether each step was sticky
    hist=tuple(((L[k]["pos"]-x8)*dx, "S" if L[k]["exec"]!=L[k]["a"] else "-", MOVE.get(L[k]["exec"],0)*dx, L[k]["by"]) for k in range(len(L)-5,len(L)))
    return hist
if __name__=="__main__":
    with ProcessPoolExecutor(4) as ex: out=[h for h in ex.map(one,range(200)) if h]
    print("category-A misses (paddle on x8, sticky -dx at landing):",len(out))
    # where the paddle was 2 steps before landing and how it got to x8
    c=Counter((h[-3][0],h[-3][1],h[-2][0],h[-2][1],h[-2][2]) for h in out)
    print("(rel pos 2 steps before, sticky?, rel pos 1 step before, sticky?, exec move(+dx/-dx) 1 step before):")
    for k,v in c.most_common(): print("   ",k,v)
    c3=Counter(h[-3][3] for h in out); print("ball row at step landing-2:",dict(c3))
    # what put the paddle on the +dx side: sticky overshoot in the last 5 steps?
    print("misses with a sticky +dx push in the 4 steps before landing:",sum(1 for h in out if any(s=='S' and m>0 for (_,s,m,_) in h[:-1])))
