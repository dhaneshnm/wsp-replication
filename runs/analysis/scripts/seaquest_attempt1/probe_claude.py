import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
np.set_printoptions(precision=2, suppress=True)
S = [
 ("start row0 cols5-6 facing L, empty", dict(sub=(0,5,'L'))),
 ("row1, empty", dict(sub=(1,5,'L'))),
 ("row1, fish row2 col5", dict(sub=(1,5,'L'), fish=[(2,5,'L')])),
 ("row2, empty", dict(sub=(2,5,'L'))),
 ("row3, empty", dict(sub=(3,5,'L'))),
 ("row4, empty", dict(sub=(4,5,'L'))),
 ("row5, empty", dict(sub=(5,5,'L'))),
 ("row6, empty", dict(sub=(6,5,'L'))),
 ("row8, empty", dict(sub=(8,5,'L'))),
 ("row4, diver row7 col0", dict(sub=(4,5,'L'), divers=[(7,0,'R')])),
 ("row4, diver row2 col0", dict(sub=(4,5,'L'), divers=[(2,0,'R')])),
 ("row4, fish row7 col0", dict(sub=(4,5,'L'), fish=[(7,0,'R')])),
 ("row4, fish row2 col0", dict(sub=(4,5,'L'), fish=[(2,0,'R')])),
 ("row4, fish row1 col0 (row1 excluded)", dict(sub=(4,5,'L'), fish=[(1,0,'R')])),
 ("row4, fish row5 col4 (adj danger near col)", dict(sub=(4,5,'L'), fish=[(5,4,'R')])),
 ("row4, fish own row col0 R-moving, facing L", dict(sub=(4,5,'L'), fish=[(4,0,'R')])),
 ("row4, fish own row col9 L-moving, facing L", dict(sub=(4,5,'L'), fish=[(4,9,'L')])),
 ("row4, fish own row col9 L-moving, facing R (front6)", dict(sub=(4,6,'R'), fish=[(4,9,'L')])),
 ("row4, fish own row col0, facing R (front6)", dict(sub=(4,6,'R'), fish=[(4,0,'R')])),
 ("row4, fish own row col8, facing L", dict(sub=(4,5,'L'), fish=[(4,8,'L')])),
 ("row4, fish own row col7, facing L", dict(sub=(4,5,'L'), fish=[(4,7,'L')])),
 ("row4, 2 fish own row col8,9, facing R", dict(sub=(4,6,'R'), fish=[(4,8,'L'),(4,9,'L')])),
 ("row4, bullet own row col9", dict(sub=(4,5,'L'), bullets=[(4,9)])),
 ("row4, bullet own row col2", dict(sub=(4,5,'L'), bullets=[(4,2)])),
 ("row4, esub+bullet own row right", dict(sub=(4,5,'L'), esub=[(4,9,'L')], bullets=[(4,8)])),
 ("row4, diver own row col9 L-moving", dict(sub=(4,5,'L'), divers=[(4,9,'L')])),
 ("row4 oxy 50 ndiv 1", dict(sub=(4,5,'L'), oxy=50, ndiv=1)),
 ("row4 oxy 50 ndiv 0", dict(sub=(4,5,'L'), oxy=50, ndiv=0)),
 ("row2 oxy 50 ndiv 1", dict(sub=(2,5,'L'), oxy=50, ndiv=1)),
 ("row1 oxy 50 ndiv 1", dict(sub=(1,5,'L'), oxy=50, ndiv=1)),
 ("row1 oxy 200 ndiv 1", dict(sub=(1,5,'L'), oxy=200, ndiv=1)),
 ("row4 oxy 50 ndiv1, fish row3 col5 above", dict(sub=(4,5,'L'), oxy=50, ndiv=1, fish=[(3,5,'L')])),
 ("row4 cols6-7 facing L (drift right)", dict(sub=(4,6,'L'))),
 ("row4 cols7-8 facing L", dict(sub=(4,7,'L'))),
 ("row4 cols4-5 facing R (front5)", dict(sub=(4,5,'R'))),
 ("row4 cols3-4 facing R (front4)", dict(sub=(4,4,'R'))),
 ("row4 cols6-7 facing R (front7)", dict(sub=(4,7,'R'))),
]
for name, kw in S:
    x = obs(**kw)
    h1, h2, z, p = fwd(CL, x)
    r = kw['sub'][0]
    V = h1[r]
    T = h1[9 + r - 2] if r >= 2 else np.nan
    E = h1[16 + r - 2] if r >= 2 else np.nan
    pre = x @ CL["W1"] + CL["b1"]
    Tpre = pre[9 + r - 2] if r >= 2 else np.nan
    print(f"{name:52s} V={V:+.2f} Tpre={Tpre:+.2f} E={E:+.2f} R01={h1[23]:+.2f} SURF={h1[24]:+.2f} XR={h1[25]:+.2f} XL={h1[26]:+.2f} | h2={h2[:6]} | argmax={ACT[int(np.argmax(z))]:5s} p={p}")
