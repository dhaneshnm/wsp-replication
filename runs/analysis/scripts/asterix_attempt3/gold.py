import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
from collections import Counter
which=sys.argv[1]
res = pickle.load(open(f"inst_{which}_200.pkl","rb"))
DY={0:0,1:0,2:-1,3:0,4:1,5:0}
spawn=0; got=0; missed_dist=Counter(); enemies=0
for R in res:
    tr=R["ents_trace"]; full=R["full"]
    prev=[None]*8
    for k,ents in enumerate(tr):
        for i,e in enumerate(ents):
            if prev[i] is None and e is not None:
                if e[3]: spawn+=1
                else: enemies+=1
        # gold crossing col 5 uncollected: gold at col 5 in pre-state k and slot still holds it (not collected) next state with col moved past
        prev=ents
    got+=R["score"]
    # misses: a gold that was in the trace at col 5 at some snapshot, compare player row at that moment
    for k,ents in enumerate(tr[:-1]):
        nxt=tr[k+1]
        for i,e in enumerate(ents):
            if e is None or not e[3]: continue
            n=nxt[i]
            # gold passed col5 uncollected: was at col 4->/6<- or 5, and next snapshot it's at 6->/4<- (moved past) 
            if n is not None and n[3] and ((e[2] and e[0]==5 and n[0]==6) or ((not e[2]) and e[0]==5 and n[0]==4)):
                py_after=min(8,max(1,full[k][1]+DY[full[k][2]]))
                missed_dist[abs(py_after-e[1])]+=1
print(which,"gold spawned",spawn,"enemies spawned",enemies,"collected",got,"capture rate %.3f"%(got/spawn))
print("  gold that left col 5 uncollected, by |player row - gold row| at that step:", sorted(missed_dist.items()), "total",sum(missed_dist.values()))
