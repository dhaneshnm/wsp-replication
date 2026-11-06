import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
np.set_printoptions(precision=2, suppress=True)
S = [
 ("row4, diver row7 col0 + fish row5 col5 (danger below, target below)", dict(sub=(4,5,'L'), divers=[(7,0,'R')], fish=[(5,5,'L')])),
 ("row4, diver row2 col0 + fish row3 col5 (danger above, target above)", dict(sub=(4,5,'L'), divers=[(2,0,'R')], fish=[(3,5,'L')])),
 ("row4, bullet own row col9 + fish row3 col5 (dodge, danger above)", dict(sub=(4,5,'L'), bullets=[(4,9)], fish=[(3,5,'L')])),
 ("row4, bullet own row col9 + fish row5 col5 (dodge, danger below)", dict(sub=(4,5,'L'), bullets=[(4,9)], fish=[(5,5,'L')])),
 ("row4 SURF (oxy50 ndiv1) + fish row3 col5 above", dict(sub=(4,5,'L'), oxy=50, ndiv=1, fish=[(3,5,'L')])),
 ("row4 SURF (oxy50 ndiv1) + fish row3 col6 above", dict(sub=(4,5,'L'), oxy=50, ndiv=1, fish=[(3,6,'L')])),
 ("row2 SURF (oxy50 ndiv1) + esub row1 col5 above", dict(sub=(2,5,'L'), oxy=50, ndiv=1, esub=[(1,5,'L')])),
 ("row4 SURF + fish in own row col9 (hold?)", dict(sub=(4,5,'L'), oxy=50, ndiv=1, fish=[(4,9,'L')])),
 ("cells7-8 facing L + bullet own row col1 (centering w/ bullet?)", dict(sub=(4,7,'L'), bullets=[(4,1)])),
]
for name, kw in S:
    x = obs(**kw); h1, h2, z, p = fwd(CL, x)
    r = kw['sub'][0]
    E = h1[16 + r - 2] if r >= 2 else float('nan')
    print(f"{name:70s} V={h1[r]:+.2f} E={E:+.2f} SURF={h1[24]:+.2f} h2(D,U,TR,TL,CL,CR)={h2[:6]} argmax={ACT[int(np.argmax(z))]:5s} p={p}")
