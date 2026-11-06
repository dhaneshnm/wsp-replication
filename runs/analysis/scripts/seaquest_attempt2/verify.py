import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt2/"
net = wsp.load_npz(A+"net.npz")
text = open(A+"answer.md").read()
res = wsp.apply_edits(text)
net2, rep = res if isinstance(res, tuple) else (res, None)
print("parse report:", rep)
for k in net:
    print(k, net[k].shape, "max|diff| vs re-parse:", float(np.abs(net[k]-net2[k]).max()), "nnz", int((net[k]!=0).sum()))
# which h1 units are used
print("h1 units with nonzero W1 col:", [j for j in range(32) if np.any(net['W1'][:,j]!=0)])
print("h2 units with nonzero W2 col:", [j for j in range(32) if np.any(net['W2'][:,j]!=0) or net['b2'][j]!=0])
print("h2 units used by W3:", [j for j in range(32) if np.any(net['W3'][j]!=0)])
print("b3", net['b3'])
