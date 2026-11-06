import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt2/"
net = wsp.load_npz(A+"net.npz")
net2, rep = wsp.apply_edits(open(A+"answer.md").read())
print("statements", rep.statements, "applied", rep.applied, "errors", rep.errors)
for k in ["W1","b1","W2","b2","W3","b3"]:
    print(k, net[k].shape, float(np.abs(net[k]-net2[k]).max()))
print("nnz total", sum(int((net[k]!=0).sum()) for k in net))
# O unit weights row 2
W1=net["W1"]
print("O row2 ch0 cols0-9:", [W1[(20+c)*6+0,7] for c in range(10)])
print("O row2 ch4 cols0-9:", [W1[(20+c)*6+4,7] for c in range(10)])
print("b1[7]", net["b1"][7])
print("D row2 ch0:", [round(float(W1[(20+c)*6+0,14]),2) for c in range(10)])
print("D row2 ch1:", [W1[(20+c)*6+1,14] for c in range(10)])
print("D row2 ch2:", [W1[(20+c)*6+2,14] for c in range(10)])
print("Y row2 ch0/1/2:", W1[120,21], W1[121,21], W1[122,21], "b", net["b1"][21])
print("V row4 (unit2) ch0 own row:", [W1[(40+c)*6,2] for c in range(10)])
print("V unit2 danger row3 ch1:", [W1[(30+c)*6+1,2] for c in range(10)], "danger row5 ch1:", [W1[(50+c)*6+1,2] for c in range(10)])
print("V unit2 reward ch2 rows:", {r: W1[(r*10)*6+2,2] for r in range(10)})
print("b1[0:7]", net["b1"][0:7])
