import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
RUN = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1"
net = wsp.load_npz(f"{RUN}/net.npz")
re_net, rep = wsp.apply_edits(open(f"{RUN}/answer.md").read())
print("parse", rep.statements, rep.applied, rep.errors)
print("equal per tensor:", {k: bool(np.array_equal(net[k], re_net[k])) for k in net})
print("nonzero total:", sum(int((net[k]!=0).sum()) for k in net))
W1, W2, W3, b3 = net["W1"], net["W2"], net["W3"], net["b3"]
# output columns
for a in range(6):
    print("W3 col", a, "nonzero rows:", np.nonzero(W3[:, a])[0].tolist(), "b3", b3[a])
# For each gated layer-2 unit k<24, list layer-1 inputs
names = {}
for i in range(8): names[i] = f"D{i+1}"; names[8+i] = f"P{i+1}"; names[16+i] = f"G{i+1}"
for k in range(24):
    nz = np.nonzero(W2[:, k])[0]
    print(f"k{k:2d}", [(names.get(i, i), float(W2[i, k])) for i in nz], "b2", float(net["b2"][k]))
# D unit input channels / columns for row 3 (unit 2)
for u in [2, 18]:
    nz = np.nonzero(W1[:, u])[0]
    print("unit", u, [((i//6)//10, (i//6)%10, i%6, float(W1[i, u])) for i in nz])
