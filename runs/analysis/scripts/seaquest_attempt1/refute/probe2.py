import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
np.set_printoptions(precision=2, suppress=True)
S = [
 ("facing R (cells5-6), fish col4 moving R (behind, adjacent)", dict(sub=(4,6,'R'), fish=[(4,4,'R')])),
 ("facing R (cells5-6), fish col3 moving R (behind)", dict(sub=(4,6,'R'), fish=[(4,3,'R')])),
 ("facing L (cells5-6), fish col7 moving L (behind, adjacent)", dict(sub=(4,5,'L'), fish=[(4,7,'L')])),
 ("facing R (cells5-6), lone foreign trail at col7", dict(sub=(4,6,'R'), trails=[(4,7)])),
 ("facing R (cells5-6), diver col8 moving R (trail col7)", dict(sub=(4,6,'R'), divers=[(4,8,'R')])),
 ("facing L (cells5-6), fish col9 moving L + diver col2", dict(sub=(4,5,'L'), fish=[(4,9,'L')], divers=[(4,2,'R')])),
 ("facing R (cells5-6), fish col1 moving R + diver col8", dict(sub=(4,6,'R'), fish=[(4,1,'R')], divers=[(4,8,'L')])),
 ("facing L (cells5-6), fish col6 (back cell) moving L, trail col7", dict(sub=(4,5,'L'), fish=[(4,6,'L')])),
 ("cells8-9 facing R, fish col7 moving R (behind)", dict(sub=(4,9,'R'), fish=[(4,7,'R')])),
 ("cells7-8 facing L (front7), empty", dict(sub=(4,7,'L'))),
]
for name, kw in S:
    x = obs(**kw); h1, h2, z, p = fwd(CL, x)
    pre = x @ CL["W1"] + CL["b1"]
    print(f"{name:62s} Tpre={pre[11]:+.2f} E={h1[18]:+.2f} TURN_R={h2[2]:+.2f} TURN_L={h2[3]:+.2f} CL={h2[4]:+.2f} CR={h2[5]:+.2f} argmax={ACT[int(np.argmax(z))]:5s} p={p}")
