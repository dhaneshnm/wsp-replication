import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
np.set_printoptions(precision=2, suppress=True)
S = [
 ("start row0 facing L", dict(sub=(0,5,'L'))),
 ("row1 empty", dict(sub=(1,5,'L'))),
 ("row2 empty", dict(sub=(2,5,'L'))),
 ("row4 empty", dict(sub=(4,5,'L'))),
 ("row8 empty", dict(sub=(8,5,'L'))),
 ("row4 diver row7", dict(sub=(4,5,'L'), divers=[(7,0,'R')])),
 ("row4 diver row2", dict(sub=(4,5,'L'), divers=[(2,9,'L')])),
 ("row4 fish row6 col1 (left, shootable)", dict(sub=(4,5,'L'), fish=[(6,1,'R')])),
 ("row4 fish row6 col9 (right)", dict(sub=(4,5,'L'), fish=[(6,9,'L')])),
 ("row4 fish own row col1 (left)", dict(sub=(4,5,'L'), fish=[(4,1,'R')])),
 ("row4 fish own row col9 (right, behind)", dict(sub=(4,5,'L'), fish=[(4,9,'L')])),
 ("row4 fish own row col7 (behind, close)", dict(sub=(4,5,'L'), fish=[(4,7,'L')])),
 ("row4 fish own row col6 (at back cell)", dict(sub=(4,5,'L'), fish=[(4,6,'L')])),
 ("row4 fish own row col4 (adjacent front)", dict(sub=(4,5,'L'), fish=[(4,4,'R')])),
 ("row4 bullet own row col8", dict(sub=(4,5,'L'), bullets=[(4,8)])),
 ("row4 bullet own row col3", dict(sub=(4,5,'L'), bullets=[(4,3)])),
 ("row4 fish row5 col5 (below, at column)", dict(sub=(4,5,'L'), fish=[(5,5,'L')])),
 ("row4 diver row5 + fish row5 col5", dict(sub=(4,5,'L'), divers=[(5,0,'R')], fish=[(5,5,'L')])),
 ("row4 oxy50 ndiv1", dict(sub=(4,5,'L'), oxy=50, ndiv=1)),
 ("row4 oxy50 ndiv0", dict(sub=(4,5,'L'), oxy=50, ndiv=0)),
 ("row2 oxy50 ndiv1", dict(sub=(2,5,'L'), oxy=50, ndiv=1)),
 ("row1 oxy50 ndiv1", dict(sub=(1,5,'L'), oxy=50, ndiv=1)),
 ("row4 oxy50 ndiv1 fish row3 col5", dict(sub=(4,5,'L'), oxy=50, ndiv=1, fish=[(3,5,'L')])),
 ("row2 oxy200 ndiv1", dict(sub=(2,5,'L'), oxy=200, ndiv=1)),
]
for name, kw in S:
    x = obs(**kw); h1, h2, z, p = fwd(AS, x)
    top = np.argsort(-h2[:24])[:2]
    print(f"{name:42s} top cand={[(int(i), round(float(h2[i]),2)) for i in top]} surf={h1[24]:+.2f} | argmax={ACT[int(np.argmax(z))]:5s} p={p}")
