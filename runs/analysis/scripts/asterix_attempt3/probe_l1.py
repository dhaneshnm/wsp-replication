import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
# Layer-1 per-row detectors for an entity in row 3 (unit index r-1), player in row 6
r=3
print("Row-3 entity sweep; player in row 6. Columns: T_3(unit10) Bk_3(unit18) G_3(unit26)")
for gold in (False, True):
  for right in (True, False):
    line=[]
    for c in range(10):
        trail = not ((right and c==0) or ((not right) and c==9))
        h1,_,_,_ = fwd(NET, obs(6, [(r,c,right,gold,trail)]))
        line.append(f"c{c}:{h1[8+r-1]:+.2f}/{h1[16+r-1]:+.2f}/{h1[24+r-1]:+.2f}")
    print(("GOLD " if gold else "ENEMY")+(" ->right " if right else " <-left  "), " ".join(line))
# also spawn without trail at col 0/9 already included. Player units
for pr in range(1,9):
    h1,_,_,_=fwd(NET, obs(pr,[]))
    print("player row",pr,"P units:",np.round(h1[0:8],3))
