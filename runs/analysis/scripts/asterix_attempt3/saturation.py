import sys,os,itertools; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
# brute force: every subset of rows holding approaching gold (c3->) for each player row; plus real-play states
worst=-2; worst_cfg=None
for pr in range(1,9):
    for mask in range(256):
        ents=[(r+1,3,True,True) for r in range(8) if mask>>r&1 and r+1!=pr]
        h1,h2,z,p=fwd(NET,obs(pr,ents))
        inactive=[u for u in range(32) if u%8!=pr-1]
        m=h2[inactive].max()
        if m>worst: worst=m; worst_cfg=(pr,mask)
print("max inactive layer-2 unit over all gold subsets:",worst,worst_cfg)
import pickle
res=pickle.load(open("inst_claude_200.pkl","rb"))
from move_reasons import build_obs
X=[];P=[]
for R in res[:50]:
    for k,f in enumerate(R["full"]): X.append(build_obs(f[1],R["ents_trace"][k])); P.append(f[1])
X=np.stack(X); P=np.array(P)
h1=np.tanh(X@NET["W1"]+NET["b1"]); h2=np.tanh(h1@NET["W2"]+NET["b2"])
mask=np.ones_like(h2,bool)
for i,pr in enumerate(P): mask[i,[pr-1,8+pr-1,16+pr-1,24+pr-1]]=False
print("real play (50 episodes, %d states): max inactive layer-2 unit %.6f; min %.6f"%(len(P),h2[mask].max(),h2[mask].min()))
