import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import pickle
# real env check: step a real env with the net, and at each state find gold at spawn column moving inward; read G for that row
cnt=0; Gvals=[]; appr=0; appr_on=0
for seed in range(20):
    env=wsp._make_env("asterix",seed); ob=wsp.make_obs_fn(env,"asterix"); rng=np.random.default_rng(seed+1_000_003)
    for t in range(wsp.MAX_STEPS):
        x=ob(); h1=np.tanh(x@NET["W1"]+NET["b1"])
        for e in env.env.entities:
            if e is None or not e[3]: continue
            approaching = (e[2] and e[0]<=5) or ((not e[2]) and e[0]>=5)
            if approaching:
                appr+=1; appr_on += h1[24+e[1]-1]>0
            if (e[2] and e[0]==0) or ((not e[2]) and e[0]==9):
                cnt+=1; Gvals.append(float(h1[24+e[1]-1]))
        z=wsp.logits(NET,x); p=np.exp(z-z.max()); p/=p.sum(); a=int(rng.choice(6,p=p))
        r,d=env.act(a)
        if d: break
print("20 real episodes: gold-states approaching-or-at-c5:",appr,"with G_r>0:",int(appr_on))
print("gold at spawn column moving inward (approaching):",cnt,"G_r values: max %.4f min %.4f"%(max(Gvals),min(Gvals)))
