import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
for w in ("claude","astra"):
    res=pickle.load(open(f"inst_{w}_200.pkl","rb"))
    h=np.sum([R["rows"] for R in res],axis=0)[1:9]; h=h/h.sum()
    L=np.array([R["steps"] for R in res]); S=np.array([R["score"] for R in res])
    # deaths per 1000 steps by move_speed phase
    steps_by_ms={}; deaths_by_ms={}
    for R in res:
        for (t,py,ex,a,stk,r,ms,ramp) in R["full"]: steps_by_ms[ms]=steps_by_ms.get(ms,0)+1
        deaths_by_ms[R["full"][-1][6]]=deaths_by_ms.get(R["full"][-1][6],0)+1
    print(w,"row occupancy rows1..8:",np.round(h,3))
    print("   hazard (deaths per 1000 steps) by move_speed:", {ms: round(1000*deaths_by_ms.get(ms,0)/steps_by_ms[ms],2) for ms in sorted(steps_by_ms)})
    print("   steps spent by move_speed:", {ms: steps_by_ms[ms] for ms in sorted(steps_by_ms)})
    print("   episode length quantiles 10/50/90:", np.percentile(L,[10,50,90]), " score/step %.4f"%(S.sum()/L.sum()))
