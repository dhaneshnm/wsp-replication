import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
from minatar import Environment
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz"
ASTRA="/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
DX={0:-1,1:1,2:1,3:-1}; DY={0:-1,1:-1,2:1,3:1}
def F(u):
    m=u%20; return m if m<10 else 19-m
def S(r): return r+1 if r>=4 else 9-r

def hidden(net,x):
    h1=np.tanh(x@net["W1"]+net["b1"]); h2=np.tanh(h1@net["W2"]+net["b2"]); return h1,h2,h2@net["W3"]+net["b3"]

def design_action(e):
    """Claude reply's intended action from true env state (e = inner Env)."""
    dx=DX[e.ball_dir]; dy=DY[e.ball_dir]; r,c=e.ball_y,e.ball_x
    if dy>0: k=8-r
    else: k=S(r)
    T=F(c+dx*k)
    return (3 if T>e.pos else 1 if T<e.pos else 0), T

def run(net, seed, sticky=0.1, log=False, policy=None):
    env=Environment("breakout", sticky_action_prob=sticky); env.seed(seed); env.reset()
    e=env.env
    obs=wsp.make_obs_fn(env,"breakout")
    rng=np.random.default_rng(seed+1_000_003)
    score=0.0; L=[]
    for t in range(wsp.MAX_STEPS):
        x=obs()
        rec=None
        if log:
            rec=dict(t=t,bx=e.ball_x,by=e.ball_y,dir=e.ball_dir,lx=e.last_x,ly=e.last_y,pos=e.pos,
                     nbricks=int(np.count_nonzero(e.brick_map)),strike=e.strike, prev_exec=env.last_action)
        if policy is None:
            z=wsp.logits(net,x); p=np.exp(z-z.max()); p/=p.sum(); a=int(rng.choice(6,p=p))
        else:
            a=policy(e,x); rng.random()
        r,done=env.act(a)
        if log:
            rec.update(a=a,exec=env.last_action,r=r,done=done,pos_after=e.pos); L.append(rec)
        score+=r
        if done: return score,t+1,L
    return score,wsp.MAX_STEPS,L
