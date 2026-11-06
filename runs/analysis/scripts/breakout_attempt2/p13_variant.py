import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
net=wsp.load_npz(A)
def o(b,t,p):
    x=np.zeros((10,10,6),np.float32); x[9,p,0]=1; x[b[0],b[1],3]=1; x[t[0],t[1],4]=1; return x.reshape(600)
def acts(n,b,t): return [int(np.argmax(wsp.logits(n,o(b,t,p)))) for p in range(10)]
def margin(n,b,t):
    m=1e9
    for p in range(10):
        x=o(b,t,p); pre=x@n["W1"][:,:10]+n["b1"][:10]; m=min(m,np.abs(pre).min())
    return m
print("orig  DR (7,4)<-(6,3) x8=5 acts by paddle col:",acts(net,(7,4),(6,3)),"  DL (7,5)<-(6,6) x8=4:",acts(net,(7,5),(6,6)))
for rows,name in [((6,7,8),"cf2_rows678"),((8,),"cf2_row8")]:
    n2={k:v.copy() for k,v in net.items()}
    for r in rows:
        for c in range(10):
            i=(r*10+c)*6+3
            n2["W1"][i,1]-=10   # L_D+ fires only when paddle >= x8+2  (accepts x8 and x8+1)
            n2["W1"][i,2]-=10   # R_D- fires only when paddle <= x8-2  (accepts x8 and x8-1)
    wsp.save_npz(n2,f"{name}.npz")
    print(name,"DR x8=5:",acts(n2,(7,4),(6,3)),"DL x8=4:",acts(n2,(7,5),(6,6)),"row8 DR (8,5)<-(7,4):",acts(n2,(8,5),(7,4)),"min|preact| on probes:",margin(n2,(7,4),(6,3)),margin(n2,(7,5),(6,6)))
