import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/net.npz")
W1,b1,W2,b2,W3,b3 = (net[k] for k in ["W1","b1","W2","b2","W3","b3"])
def I(r,c,ch): return (r*10+c)*6+ch
def ob(player=(5,5), ents=()):
    o = np.zeros((10,10,6),np.float32); o[player[0],player[1],0]=1
    for r,c,lr,g in ents:
        o[r,c,2 if g else 1]=1; bx=c-1 if lr else c+1
        if 0<=bx<=9: o[r,bx,4]=1
    return o.reshape(600)
def fwd(x):
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); z=h2@W3+b3; return h1,h2,z
print("b3", b3, "W3 nonzero rows/cols:", [(i,j,float(W3[i,j])) for i,j in zip(*np.nonzero(W3)) if i in (0,8,16,24)])
print("b2", b2)
# up_y connections from H1 units (8..15): which target rows does each up unit read?
for y in range(1,9):
    up=7+y; dn=15+y; st=y-1
    print(f"player row {y}: stay reads H1 rows {[r for r in range(1,9) if W2[7+r,st]!=0]}, up reads H1 rows {[r for r in range(1,9) if W2[7+r,up]!=0]}, down reads H1 rows {[r for r in range(1,9) if W2[7+r,dn]!=0]}; up reads H2 rows {[r for r in range(1,9) if W2[15+r,up]!=0]}")
# gold-direction unit values
for y in [2,4,6]:
    for desc, ents in [("none",[]),("1 gold above",[(y-1,2,True,True)]),("1 gold below",[(y+1,2,True,True)]),("2 above",[(1,2,True,True),(y-1,2,True,True)] if y>2 else [(1,2,True,True)]),("1 above 1 below",[(y-1,2,True,True),(y+1,2,True,True)])]:
        h1,h2,z=fwd(ob((y,5),ents)); 
        print(f"row {y} {desc:16s} goldDir={h2[23+y]:+.3f} z_u-z_d contribution from goldDir units={(h2[24:32]@W3[24:32,2] + b3[2]) - (h2[24:32]@W3[24:32,4] + b3[4]) - (b3[2]-b3[4]):+.3f}  logits n,u,d={z[0]:.2f},{z[2]:.2f},{z[4]:.2f}")
# stay unit readings in player row 4
y=4
for desc, ents in [("neutral",[]),("immediate E@4->",[(4,4,True,False)]),("near E@3->",[(4,3,True,False)]),("far E@1->",[(4,1,True,False)]),("gold",[(4,2,True,True)])]:
    h1,h2,z=fwd(ob((y,5),ents)); print(f"stay unit, {desc:16s}: {h2[y-1]:+.3f}; n logit {z[0]:.2f}")
h1,h2,z=fwd(ob((4,5))); print("empty board logits", z.round(2), "gap n - max(l,r,f)=", round(float(z[0]-max(z[1],z[3],z[5])),2), "u - max(l,r,f)=", round(float(z[2]-max(z[1],z[3],z[5])),2))
