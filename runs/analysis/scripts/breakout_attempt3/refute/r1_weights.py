import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp, json
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/"
net = wsp.load_npz(A + "net.npz")
parsed, rep = wsp.apply_edits(open(A + "answer.md").read())
print("parse report:", rep.statements, rep.applied, rep.errors)
for k in net:
    print(k, "max|diff| net.npz vs parse:", float(np.abs(net[k] - parsed[k]).max()))
print("run.json parse:", json.load(open(A + "run.json"))["parse"])

def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m
W1, b1 = net["W1"], net["b1"]
T_up = [9, 10, 9, 8, 7, 8, 9, 10, 11]
specs = {0: (1, "down"), 1: (1, "down"), 2: (-1, "down"), 3: (-1, "down"),
         4: (1, "up"), 5: (1, "up"), 6: (-1, "up"), 7: (-1, "up")}
bad = 0
for u, (dx, ph) in specs.items():
    sgn = 5 if u % 2 == 0 else -5
    for y in range(10):
        for x in range(10):
            w = W1[(y*10+x)*6+3, u]
            if y == 9:
                exp = 0.0
            else:
                T = (8 - y) if ph == "down" else T_up[y]
                exp = sgn * fold(x + dx*T)
            if w != exp: bad += 1
    for p in range(10):
        if W1[(90+p)*6, u] != -sgn*p: bad += 1
    if b1[u] != -2.5: bad += 1
    # nothing else
    mask = np.zeros(600, bool); mask[3::6] = True; mask[540::6] = True
    if np.any(W1[~mask, u] != 0): bad += 1; print("unit", u, "extra weights")
print("table/paddle/bias mismatches vs fold(x+dx*T) formula, units 0-7:", bad)
# H: 8*(bx - tx) + 4[bx==0] - 4[bx==9], over ball ch3 and trail ch4, any row
badH = 0
for y in range(10):
    for x in range(10):
        wb = W1[(y*10+x)*6+3, 8]; wt = W1[(y*10+x)*6+4, 8]
        eb = 8*x + (4 if x == 0 else 0) - (4 if x == 9 else 0); et = -8*x
        badH += (wb != eb) + (wt != et)
others = [c for c in range(6) if c not in (3, 4)]
print("H mismatches:", badH, "H other-channel nonzero:", int(sum(np.abs(W1[c::6, 8]).sum() > 0 for c in others)), "b1[8]", b1[8])
badV = 0
for y in range(10):
    for x in range(10):
        wb = W1[(y*10+x)*6+3, 9]; wt = W1[(y*10+x)*6+4, 9]
        if y <= 7: eb = 8*y + 4
        elif y == 8: eb = 8*8 - 4
        else: eb = 0
        et = -8*y if y <= 8 else 0
        badV += (wb != eb) + (wt != et)
print("V mismatches:", badV, "V other-channel nonzero:", int(sum(np.abs(W1[c::6, 9]).sum() > 0 for c in others)), "b1[9]", b1[9])
print("W1 brick channel (2) nonzero count:", int((W1[2::6] != 0).sum()))
print("layer1 used units:", np.where(np.abs(W1).sum(0) + np.abs(b1) > 0)[0].tolist())
W2, b2 = net["W2"], net["b2"]
print("W2 nonzero:", [(int(i), int(j), float(W2[i, j])) for i, j in zip(*np.nonzero(W2))])
print("b2 nonzero:", {int(i): float(b2[i]) for i in np.nonzero(b2)[0]})
W3, b3 = net["W3"], net["b3"]
print("W3 nonzero:", [(int(i), int(j), float(W3[i, j])) for i, j in zip(*np.nonzero(W3))])
print("b3:", b3.tolist())
