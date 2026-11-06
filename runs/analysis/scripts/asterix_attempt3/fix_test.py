import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import copy
net = copy.deepcopy(NET)
w=float(sys.argv[1]) if len(sys.argv)>1 else 1.25
for y in range(3,9):   # U_y (col 8+y-1): also look at row y-2
    col=8+y-1; net["W2"][16+(y-3),col]+=w; net["W2"][8+(y-3),col]+=w; net["b2"][col]+=2*w
for y in range(1,7):   # D_y (col 16+y-1): also look at row y+2
    col=16+y-1; net["W2"][16+(y+1),col]+=w; net["W2"][8+(y+1),col]+=w; net["b2"][col]+=2*w
E=lambda r,c,right: (r,c,right,False); G=lambda r,c,right: (r,c,right,True)
for name,pr,ents in [("empty r5",5,[]),("gold 1 above, enemy c5 in row 2-above",5,[G(4,3,True),E(3,5,True)]),
                     ("threat own, only up open but 2-up has enemy c5",5,[E(5,4,True),E(6,5,True),E(3,5,True)]),
                     ("threat own, 2-up enemy c4-> (Bk&T both)",5,[E(5,4,True),E(6,5,True),E(3,4,True)]),
                     ("gold 1 above, clear",5,[G(4,3,True)])]:
    _,_,z,p=fwd(net,obs(pr,ents)); _,_,z0,p0=fwd(NET,obs(pr,ents))
    print(f"{name:50s} orig: {fmtp(p0):40s} patched: {fmtp(p)}")
if __name__=="__main__":
    r=wsp.evaluate(net,"asterix",episodes=200,workers=4); print("patched w=%.2f"%w, r)
