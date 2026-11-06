import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/"
net = wsp.load_npz(A + "net.npz")
text = open(A + "answer.md").read()
res = wsp.apply_edits(text)
net2 = res[0] if isinstance(res, tuple) else res
print("apply_edits returned", type(res), [type(r) for r in res] if isinstance(res, tuple) else "")
for k in net:
    print(k, net[k].shape, "max|diff| =", float(np.abs(net[k] - net2[k]).max()), "nonzero", int((net[k] != 0).sum()))
used1 = np.where(np.abs(net["W1"]).sum(0) + np.abs(net["b1"]) > 0)[0]
used2 = np.where(np.abs(net["W2"]).sum(0) + np.abs(net["b2"]) > 0)[0]
print("layer1 units used", used1.tolist()); print("layer2 units used", used2.tolist())
# channels touched by W1
for ch in range(6):
    print("channel", ch, "nonzero W1 rows:", int((np.abs(net["W1"][ch::6]).sum(1) > 0).sum()))
print("b3", net["b3"]); print("W3 nonzero", [(i, j, float(net["W3"][i, j])) for i, j in zip(*np.nonzero(net["W3"]))])
