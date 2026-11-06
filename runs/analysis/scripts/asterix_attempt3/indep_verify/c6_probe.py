# Probe Astra (and Claude) on hand-built boards.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
N = nets(); NM = ["noop","left","up","right","down","fire"]
E = lambda r, c, d: dict(r=r, c=c, kind="E", dir=d)
G = lambda r, c, d: dict(r=r, c=c, kind="G", dir=d)
def show(label, prow, items, which=("astra",)):
    for w in which:
        a1, a2, z, p = layers(N[w], board(prow, items))
        top = " ".join(f"{NM[i]}={p[i]:.3f}" for i in np.argsort(-p)[:3] if p[i] > 1e-3)
        extra = f" L2 up/down/wait={a2[0]:+.2f}/{a2[1]:+.2f}/{a2[2]:+.2f}" if w == "astra" else ""
        print(f"  [{w:6s}] {label:55s} z n/u/d={z[0]:+8.2f}/{z[2]:+8.2f}/{z[4]:+8.2f}{extra} | {top}")
print("-- Astra: danger two rows ahead (player row 5)")
for c, d in ((5, 1), (5, -1), (4, 1), (6, -1), (3, 1)):
    show(f"enemy row 3 (2 above) c{c} {'->' if d>0 else '<-'}", 5, [E(3, c, d)])
    show(f"enemy row 7 (2 below) c{c} {'->' if d>0 else '<-'}", 5, [E(7, c, d)])
show("enemy row 3 c5 + gold row 4 c3->", 5, [E(3, 5, 1), G(4, 3, 1)], ("astra", "claude"))
show("gold row 4 c3-> only", 5, [G(4, 3, 1)], ("astra", "claude"))
print("-- Astra edge rows: own-row enemy 2 cols away + adjacent row enemy at c5 / c4-> / c6<-")
for (pr, own, nb) in ((1, E(1, 3, 1), E(2, 5, 1)), (1, E(1, 3, 1), E(2, 5, -1)), (1, E(1, 3, 1), E(2, 4, 1)),
                      (1, E(1, 7, -1), E(2, 5, 1)), (1, E(1, 4, 1), E(2, 5, -1)),
                      (8, E(8, 7, -1), E(7, 5, 1)), (8, E(8, 7, -1), E(7, 6, -1)), (8, E(8, 3, 1), E(7, 5, -1)),
                      (1, E(1, 3, 1), None), (8, E(8, 7, -1), None), (2, E(2, 3, 1), E(3, 5, 1)), (5, E(5, 3, 1), E(6, 5, 1))):
    items = [own] + ([nb] if nb else [])
    lab = f"row{pr}: own c{own['c']}{'->' if own['dir']>0 else '<-'}" + (f", row{nb['r']} c{nb['c']}{'->' if nb['dir']>0 else '<-'}" if nb else ", nothing adjacent")
    show(lab, pr, items)
