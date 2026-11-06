import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
import json
from concurrent.futures import ProcessPoolExecutor

def analyse(args):
    path, seed, sticky = args
    net=wsp.load_npz(path)
    score,steps,L=run(net,seed,sticky=sticky,log=True)
    # landing events: record where ball at row 8 moving down (dir 2/3)
    lands=[]; 
    last_up=-1
    for i,rec in enumerate(L):
        dy=DY[rec["dir"]]
        if dy<0: last_up=i
        if rec["by"]==8 and dy>0:
            j0=last_up+1
            r0=L[j0]["by"]; pos0=L[j0]["pos"]
            dx_end=DX[rec["dir"]]; x8=rec["bx"]
            nx=min(9,max(0,x8+dx_end))
            n_act=i-j0+1
            # min row reached on the preceding ascent
            prev=[L[k]["by"] for k in range(max(0,j0-30),j0+1)]
            hmin=min(L[k]["by"] for k in range(j0, i+1))
            # top row of the ascent: scan back from j0 to previous landing
            k=j0; 
            while k>0 and not (L[k-1]["by"]==8 and DY[L[k-1]["dir"]]>0): k-=1
            asc_top=min(L[m]["by"] for m in range(k,j0+1)) if j0>=k else None
            sticky_desc=sum(1 for m in range(j0,i+1) if L[m]["exec"]!=L[m]["a"])
            caught=not rec["done"]
            lands.append(dict(i=i,caught=caught,r0=r0,n_act=n_act,d_straight=abs(pos0-x8),d_any=min(abs(pos0-x8),abs(pos0-nx)),
                              asc_top=asc_top,sticky_desc=sticky_desc,final_pos=rec["pos_after"],x8=x8,dx=dx_end,
                              prev_exec=rec["prev_exec"],a=rec["a"],exec=rec["exec"],pos_before=rec["pos"],
                              reversal=(caught and rec["pos_after"]!=x8)))
    sticky_steps=sum(1 for r in L if r["exec"]!=r["a"])
    return dict(seed=seed,score=score,steps=steps,capped=(steps==wsp.MAX_STEPS and not L[-1]["done"]),lands=lands,sticky_steps=sticky_steps)

if __name__=="__main__":
    path=sys.argv[1]; tag=sys.argv[2]; sticky=float(sys.argv[3]); n=int(sys.argv[4])
    with ProcessPoolExecutor(4) as ex:
        res=list(ex.map(analyse,[(path,s,sticky) for s in range(n)],chunksize=5))
    json.dump(res,open(f"eps_{tag}.json","w"))
    sc=np.array([r["score"] for r in res]); st=np.array([r["steps"] for r in res])
    print(tag,"sticky",sticky,"episodes",n,"mean score",sc.mean(),"se",sc.std(ddof=1)/np.sqrt(n),"mean len",st.mean(),"capped",sum(r["capped"] for r in res))
