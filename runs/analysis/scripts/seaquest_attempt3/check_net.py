import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/"
net = wsp.load_npz(A+"net.npz")
txt = open(A+"answer.md").read()
re_net, rep = wsp.apply_edits(txt)
print("parse:", rep.statements, rep.applied, rep.errors)
for k in net: print(k, net[k].shape, "max diff vs reparse", float(np.abs(net[k]-re_net[k]).max()), "nnz", int((net[k]!=0).sum()))
W1=net["W1"]
used = np.where(np.abs(W1).sum(0)>0)[0]; print("L1 units used:", used)
W2=net["W2"]; print("L2 units used (cols):", np.where(np.abs(W2).sum(0)+np.abs(net['b2'])>0)[0])
print("W3 rows used:", np.where(np.abs(net['W3']).sum(1)>0)[0])
print("b3", net["b3"])
