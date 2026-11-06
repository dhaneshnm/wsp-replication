import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
D = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt1/"
net = wsp.load_npz(D+"net.npz")
txt = open(D+"answer.md").read()
n2, rep = wsp.apply_edits(txt)
print("statements", rep.statements, "applied", rep.applied, "errors", rep.errors)
for k in ["W1","b1","W2","b2","W3","b3"]:
    print(k, net[k].shape, net[k].dtype, float(np.abs(net[k]-n2[k]).max()), int((net[k]!=0).sum()))
print("total nonzero", sum(int((net[k]!=0).sum()) for k in net))
print("keys", list(net.keys()))
print("num edits blocks", txt.count("```edits"))
