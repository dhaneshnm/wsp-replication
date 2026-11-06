import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
import json
from concurrent.futures import ProcessPoolExecutor
MOVE={1:-1,3:1}
def flights(args):
    path,seed,sticky=args
    net=wsp.load_npz(path)
    score,steps,L=run(net,seed,sticky=sticky,log=True)
    out=[]; start=0
    for i,rec in enumerate(L):
        if rec["by"]==8 and DY[rec["dir"]]>0:   # landing step
            x8=rec["bx"]; dx=DX[rec["dir"]]; nx=min(9,max(0,x8+dx))
            p0=L[start]["pos"]; n=i-start+1
            seg=L[start:i+1]
            st=[m for m in seg if m["exec"]!=m["a"]]
            sticky_delay=sum(1 for m in st if MOVE.get(m["a"],0)!=0 and MOVE.get(m["exec"],0)==0)
            sticky_push=sum(1 for m in st if MOVE.get(m["exec"],0)!=0 and MOVE.get(m["exec"],0)!=MOVE.get(m["a"],0))
            # chosen moves that go away from x8 (not sticky)
            away=sum(1 for m in seg if m["exec"]==m["a"] and MOVE.get(m["a"],0)!=0 and abs(m["pos_after"]-x8)>abs(m["pos"]-x8))
            top=min(m["by"] for m in seg)
            pre=rec["pos"]; prev_exec=rec["prev_exec"]
            at_catch_before = pre in (x8,nx)
            out.append(dict(caught=not rec["done"], n=n, d=abs(p0-x8), d_any=min(abs(p0-x8),abs(p0-nx)), sticky=len(st),
                            sticky_delay=sticky_delay, sticky_push=sticky_push, away=away, top=top, x8=x8, dx=dx, start_bx=L[start]["bx"],
                            pre_pos=pre, final_pos=rec["pos_after"], landing_sticky=rec["exec"]!=rec["a"], chosen=rec["a"], exec=rec["exec"],
                            at_catch_before=at_catch_before, first=(start==0), reward=sum(m["r"] for m in seg)))
            start=i+1
    return dict(seed=seed,score=score,steps=steps,flights=out)
if __name__=="__main__":
    path=sys.argv[1]; tag=sys.argv[2]; sticky=float(sys.argv[3]); n=int(sys.argv[4])
    with ProcessPoolExecutor(4) as ex:
        res=list(ex.map(flights,[(path,s,sticky) for s in range(n)],chunksize=5))
    json.dump(res,open(f"fl_{tag}.json","w"))
    print(tag, np.mean([r["score"] for r in res]))
