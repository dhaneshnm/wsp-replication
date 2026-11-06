import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
from collections import Counter
net=wsp.load_npz(A)
def obs_from(ball,trail,pad,bricks=None):
    o=np.zeros((10,10,6),np.float32); o[9,pad,0]=1; o[ball[0],ball[1],3]=1; o[trail[0],trail[1],4]=1
    if bricks is not None: o[...,2]=bricks
    return o.reshape(600)
print("--- hand-built observations ---")
cases=[("down-right mid, paddle left", (5,3),(4,2),0),
       ("down-right mid, paddle on target F(3+3)=6",(5,3),(4,2),6),
       ("down-left near wall: (6,1) from (5,2): target F(1-2)=F(-1)=0",(6,1),(5,2),3),
       ("wall clamp (7,0) trail (6,0): next dx=+1, target F(0+1)=1",(7,0),(6,0),1),
       ("post-catch flat row8 (8,5) trail (8,4): up, dx+1, target F(5+9)=5",(8,5),(8,4),4),
       ("brick bounce flat row4 (4,6) trail (4,5): down, dx+1, target F(6+4)=9",(4,6),(4,5),9),
       ("ascending (5,4) from (6,3): U+ target F(4+6)=9",(5,4),(6,3),2),
       ("reset (3,0)/(3,0): down-right target F(0+5)=5",(3,0),(3,0),4),
       ("reset (3,9)/(3,9): down-left target F(9-5)=4",(3,9),(3,9),4),
       ]
for name,b,tr,p in cases:
    h1,h2,z=hidden(net,obs_from(b,tr,p))
    print(f"{name}: paddle={p}  L1[0:8]={np.round(h1[:8]).astype(int).tolist()} X={h1[8]:+.2f} V={h1[9]:+.2f} L2[0:8]={np.round(h2[:8]).astype(int).tolist()} logits={np.round(z,1).tolist()} argmax={int(np.argmax(z))}")
# brick channel is ignored?
h_a=hidden(net,obs_from((5,3),(4,2),0))[2]; h_b=hidden(net,obs_from((5,3),(4,2),0,bricks=np.ones((10,10))))[2]
print("brick channel effect on logits:",np.abs(h_a-h_b).max())

print("--- real states: net argmax vs design oracle, X/V vs env direction ---")
mism=Counter(); n=0; xv=Counter(); minmargin=1e9; pmax_other=0
for s in range(1000,1040):
    env=Environment("breakout",sticky_action_prob=0.1); env.seed(s); env.reset(); e=env.env
    obs=wsp.make_obs_fn(env,"breakout"); rng=np.random.default_rng(s)
    for t in range(10000):
        x=obs(); h1,h2,z=hidden(net,x)
        da,T=design_action(e); na=int(np.argmax(z))
        na3 = na if na in (1,3) else 0
        n+=1
        if na3!=da: mism[(da,na3)]+=1
        dx=DX[e.ball_dir]; dy=DY[e.ball_dir]
        if np.sign(h1[8])!=dx: xv["X wrong"]+=1
        if np.sign(h1[9])!=-dy: xv["V wrong"]+=1
        # min |pre-activation| margin of units 0..9 and 0..7 layer2
        pre1=x@net["W1"][:,:10]+net["b1"][:10]; pre2=h1@net["W2"][:,:8]+net["b2"][:8]
        minmargin=min(minmargin,np.abs(pre1).min(),np.abs(pre2).min())
        p=np.exp(z-z.max()); p/=p.sum()
        intended = [3] if da==3 else [1] if da==1 else [0,2,4,5]
        pmax_other=max(pmax_other,1-sum(p[i] for i in intended))
        a=int(rng.choice(6,p=p)); r,done=env.act(a)
        if done: break
print("states",n,"action mismatches",dict(mism),"X/V errors",dict(xv),"min |preact| L1/L2",minmargin,"max prob on non-intended action",pmax_other)
