# Hand-built observations: check each unit against the reply's stated formulas.
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/"
net = wsp.load_npz(A + "net.npz")
def obs(by, bx, ty, tx, p, bricks=None):
    x = np.zeros(600, np.float32)
    x[(by*10+bx)*6+3] = 1; x[(ty*10+tx)*6+4] = 1; x[(9*10+p)*6+0] = 1
    if bricks is not None:
        for (r, c) in bricks: x[(r*10+c)*6+2] = 1
    return x
def fwd(x):
    h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]; return h1, h2, z
def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m
T = [9, 10, 9, 8, 7, 8, 9, 10, 11]
def target(by, bx, dx, down):
    return fold(bx + dx*(8-by)) if down else fold(bx + dx*T[by])
names = {(1,1):"DR",(-1,1):"DL",(1,-1):"UR",(-1,-1):"UL"}
# (1) Normal diagonal frames: ball at (by,bx), trail at (by-dy, bx-dx)
bad = 0; tot = 0; minmargin = 9
hsign_bad = vsign_bad = 0
for (dx, dy), nm in names.items():
    for by in range(0, 9):
        for bx in range(10):
            ty, tx = by - dy, bx - dx
            if not (0 <= ty <= 8 and 0 <= tx <= 9): continue
            down = dy == 1
            for p in range(10):
                h1, h2, z = fwd(obs(by, bx, ty, tx, p))
                L = target(by, bx, dx, down)
                want = 3 if L > p else (1 if L < p else 0)
                pr = np.exp(z - z.max()); pr /= pr.sum()
                got = 3 if pr[3] > 0.5 else (1 if pr[1] > 0.5 else 0)
                tot += 1; bad += got != want
                if np.sign(h1[8]) != dx: hsign_bad += 1
                if np.sign(h1[9]) != dy: vsign_bad += 1
                minmargin = min(minmargin, abs(z[3]-z[1]) if want else 30)
print(f"normal diagonal frames: {tot} (ball,trail,paddle) cases, network move != reply formula in {bad}; H sign wrong {hsign_bad}, V sign wrong {vsign_bad}")
# (2) Special frames and how the net classifies them
def show(desc, by, bx, ty, tx, p=4):
    h1, h2, z = fwd(obs(by, bx, ty, tx, p))
    pr = np.exp(z - z.max()); pr /= pr.sum()
    print(f"{desc:55s} H={h1[8]:+.3f} V={h1[9]:+.3f} h2={np.round(h2[:8],2).tolist()} P(left)={pr[1]:.3f} P(right)={pr[3]:.3f}")
show("start: ball=trail=(3,0) (true dir DR) paddle 4", 3, 0, 3, 0)
show("start: ball=trail=(3,9) (true dir DL) paddle 4", 3, 9, 3, 9)
show("left-wall stall ball (5,0) trail (4,0) true DR, p=4", 5, 0, 4, 0)
show("right-wall stall ball (5,9) trail (4,9) true DL, p=4", 5, 9, 4, 9)
show("top-wall bounce ball(0,3) trail(0,2) true DR", 0, 3, 0, 2)
show("brick hit from below ball(4,3) trail(4,2) true DR", 4, 3, 4, 2)
show("brick hit from above ball(0,3) trail(0,2) true UR", 0, 3, 0, 2)
show("paddle bounce same col: ball(8,5) trail(8,4) true UR", 8, 5, 8, 4, p=4)
show("paddle bounce next col: ball(8,5) trail(8,4) true UL", 8, 5, 8, 4, p=5)
# (3) unit pre-activation margins for the comparison units
pre = []
for (dx, dy), nm in names.items():
    for by in range(9):
        for bx in range(10):
            for p in range(10):
                x = obs(by, bx, max(0,min(8,by-dy)), max(0,min(9,bx-dx)), p)
                pre.append(np.abs(x @ net["W1"][:, :8] + net["b1"][:8]).min())
print("min |pre-activation| over comparison units 0-7:", float(np.min(pre)))
