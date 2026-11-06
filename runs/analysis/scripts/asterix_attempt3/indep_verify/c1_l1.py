# Exhaustive single-entity sweep of every layer-1 detector against answer.md's stated rules.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
net = nets()["claude"]
def exp_T(k,c,d): return k=="E" and ((d==1 and c in (3,4)) or (d==-1 and c in (6,7)))
def exp_B(k,c,d): return k=="E" and (c==5 or (d==1 and c==4) or (d==-1 and c==6))
def exp_G(k,c,d): return k=="G" and (c==5 or (d==1 and c<5) or (d==-1 and c>5))
mism = []; minsat = 9
for prow in range(1, 9):
    for r in range(1, 9):
        for k in "EG":
            for c in range(10):
                for d in (1, -1):
                    if (d == 1 and c == 9) or (d == -1 and c == 0):
                        pass  # entity would have left; still test for completeness
                    a1, _, _, _ = layers(net, board(prow, [dict(r=r, c=c, kind=k, dir=d)]))
                    for u in range(32):
                        grp, row = divmod(u, 8); row += 1
                        if grp == 0: e = (row == prow)
                        elif row != r: e = False
                        elif grp == 1: e = exp_T(k, c, d)
                        elif grp == 2: e = exp_B(k, c, d)
                        else: e = exp_G(k, c, d)
                        got = a1[u] > 0
                        minsat = min(minsat, abs(a1[u]))
                        if got != e:
                            mism.append((prow, r, k, c, d, ["P","T","Bk","G"][grp], row, round(float(a1[u]), 3)))
print("single-entity configs x 32 units checked; min |activation| =", round(float(minsat), 4))
print("mismatches vs answer.md rule:", len(mism))
from collections import Counter
print(Counter((m[2], m[3], m[4], m[5]) for m in mism))
for m in mism[:6]: print("  prow,r,kind,col,dir,unit,row,act =", m)
