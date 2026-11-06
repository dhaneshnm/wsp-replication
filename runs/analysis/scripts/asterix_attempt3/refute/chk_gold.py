import pickle, numpy as np
for w in ("claude","astra"):
    res=pickle.load(open(f"inst_{w}_200.pkl","rb"))
    spawn=0; got=0; inflight=0
    for R in res:
        prev=[None]*8
        for ents in R["ents_trace"]:
            for i,e in enumerate(ents):
                if prev[i] is None and e is not None and e[3]: spawn+=1
            prev=ents
        inflight+=sum(1 for e in R["ents_trace"][-1] if e is not None and e[3])
        got+=R["score"]
    L=np.array([R["steps"] for R in res])
    print(w,"gold spawned",spawn,"collected",got,"in flight at last snapshot",inflight,"rate %.3f, excl in-flight %.3f"%(got/spawn, got/(spawn-inflight)),"len mean %.1f median %.1f"%(L.mean(),np.median(L)))
