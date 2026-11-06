import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/"
net=wsp.load_npz(A+"net.npz")
txt=open(A+"answer.md").read()
net2,rep=wsp.apply_edits(txt)
print("statements",rep.statements if hasattr(rep,'statements') else rep)
for k in ["W1","b1","W2","b2","W3","b3"]:
    print(k, net[k].shape, "nonzero",int((net[k]!=0).sum()), "max|.|",float(np.abs(net[k]).max()), "equal_to_reparse", np.array_equal(net[k],net2[k]))
print("b1[:12]",net["b1"][:12]); print("b2[:10]",net["b2"][:10]); print("b3",net["b3"])
print("W3 nonzero:", [(i,j,float(net["W3"][i,j])) for i,j in zip(*np.nonzero(net["W3"]))])
print("W2 nonzero:", [(i,j,float(net["W2"][i,j])) for i,j in zip(*np.nonzero(net["W2"]))])
used=np.nonzero(np.abs(net["W1"]).sum(0))[0]; print("W1 used cols",used)
# channels used per unit
W1=net["W1"].reshape(10,10,6,32)
for u in used:
    print(u, "channels with nonzero:", [c for c in range(6) if np.any(W1[:,:,c,u]!=0)])
