import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
net=wsp.load_npz(A)
n=0; row1up=0; diff=0; tot=0
for s in range(100):
    score,steps,L=run(net,s,log=True)
    for x in L:
        tot+=1
        if x["by"]==1 and DY[x["dir"]]<0 and x["ly"]==2:
            row1up+=1
            dx=DX[x["dir"]]; c=x["bx"]; p=x["pos"]
            t8=F(c+dx*8); t10=F(c+dx*10)
            a8=np.sign(t8-p); a10=np.sign(t10-p)
            if a8!=a10: diff+=1
print("steps",tot,"states with ball at row 1 moving up:",row1up,"of which design S(1)=8 vs true S(1)=10 gives a different move:",diff)
