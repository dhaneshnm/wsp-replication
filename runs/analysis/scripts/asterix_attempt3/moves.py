import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
which=sys.argv[1]
res = pickle.load(open(f"inst_{which}_200.pkl","rb"))
DY={0:0,1:0,2:-1,3:0,4:1,5:0}
tot_steps=0; moves=0; eff_moves=0; sticky_moves=0; sticky_any=0
gold_spawn=0; gold_got=0
for R in res:
    full=R["full"]; tot_steps+=len(full)
    for (t,py,ex,a,stk,r,ms,ramp) in full:
        y1=min(8,max(1,py+DY[ex]))
        if ex in (2,4): moves+=1
        if y1!=py: eff_moves+=1
        if stk and ex!=a: sticky_any+=1
        if stk and ex!=a and ex in (2,4): sticky_moves+=1
    # gold spawns: slot transitions None/other -> gold at col 0/9 with no previous
    tr=R["ents_trace"]; prev=[None]*8
    for ents in tr+[None]:
        if ents is None: break
        for i,e in enumerate(ents):
            if e is not None and e[3] and (prev[i] is None or not prev[i][3] or prev[i][0]!=e[0] and abs(prev[i][0]-e[0])>1):
                if e[0] in (0,9): gold_spawn+=1
        prev=ents
    gold_got+=R["score"]
print(which, "steps",tot_steps,"executed up/down actions per 100 steps: %.2f"%(100*moves/tot_steps),
      "effective row changes per 100 steps: %.2f"%(100*eff_moves/tot_steps))
print("  sticky-changed actions per 100 steps: %.2f; sticky-changed that were moves: %.2f"%(100*sticky_any/tot_steps,100*sticky_moves/tot_steps))
print("  gold spawned (seen in pre-step states):",gold_spawn,"collected:",gold_got,"capture rate %.3f"%(gold_got/gold_spawn))
