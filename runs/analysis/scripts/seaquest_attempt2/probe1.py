import sys; sys.path.insert(0, sys.argv[1])
from common import *
P = lambda lab, **kw: print(describe_cl(make_state(**kw), lab))
print("=== start / top rows ===")
P("start row0 col5 facing L, oxy200 dc0", sub=(0,5,False))
P("row1 col5 L, dc0", sub=(1,5,False))
P("row1 col5 L, oxy50 dc1", sub=(1,5,False), oxygen=50, dc=1)
P("row0 col5 L, oxy200 dc1 (just surfaced)", sub=(0,5,False), oxygen=200, dc=1)
print("=== idle in row 4 ===")
for c, f in [(5,False),(4,True),(5,True),(4,False),(6,True),(7,True),(3,False),(2,False),(8,True),(1,False),(6,False),(3,True)]:
    P(f"row4 front col{c} facing {'R' if f else 'L'} empty", sub=(4,c,f))
print("=== enemy in own row (sub row4 col5) ===")
for fr in [True, False]:
    for ec, ed in [(8,False),(9,False),(6,False),(1,True),(0,True),(3,True)]:
        P(f"sub row4 col5 facing {'R' if fr else 'L'}; fish row4 col{ec} moving {'R' if ed else 'L'}", sub=(4,5,fr), fish=[(4,ec,ed)])
