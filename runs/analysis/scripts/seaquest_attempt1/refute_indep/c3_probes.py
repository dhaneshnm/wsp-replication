import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from envprobe import *

W1 = NET["W1"]
def I(r, c, ch): return (r * 10 + c) * 6 + ch
print("T unit 11 (row 4) weights by col:")
for ch in range(6):
    print(" ch", ch, np.round([W1[I(4, c, ch), 11] for c in range(10)], 2).tolist())
print(" b1[11]", NET["b1"][11])
print("ch4 weights col 4/6/7 in all T units:", [[float(W1[I(r, c, 4), 9 + r - 2]) for c in (4, 6, 7)] for r in range(2, 9)])

R = 5
print("== trail reading ==")
show("facing R cells 5-6 (x=6), nothing else", state(R, 6, True))
x = state(R, 6, True); x[I(R, 7, 4)] = 1
show("facing R cells 5-6, injected lone trail ch4 col7", x)
show("facing R cells 5-6, diver col8 moving R (trail col7)", state(R, 6, True, divers=[(R, 8, True)]))
show("facing R cells 5-6, fish col8 moving R (trail col7), passed", state(R, 6, True, fish=[(R, 8, True)]))
show("facing L cells 5-6, fish col8 moving R (passed)", state(R, 5, False, fish=[(R, 8, True)]))
show("facing R cells 5-6, diver col5? n/a; diver col7 moving L (trail col8)", state(R, 6, True, divers=[(R, 7, False)]))
show("facing L cells 5-6, diver col3 moving R (trail col2)", state(R, 5, False, divers=[(R, 3, True)]))
show("facing R cells 5-6, diver col3 moving L (trail col4)", state(R, 6, True, divers=[(R, 3, False)]))
print("== divers in the turn sum ==")
show("facing L, fish col9 moving L (behind), no diver", state(R, 5, False, fish=[(R, 9, False)]))
show("facing L, fish col9 moving L + diver col2 moving R", state(R, 5, False, fish=[(R, 9, False)], divers=[(R, 2, True)]))
show("facing L, fish col9 moving L + diver col2 moving L", state(R, 5, False, fish=[(R, 9, False)], divers=[(R, 2, False)]))
show("facing L, fish col8 moving L + diver col2 moving R", state(R, 5, False, fish=[(R, 8, False)], divers=[(R, 2, True)]))
show("facing R, fish col0 moving R (behind), no diver", state(R, 6, True, fish=[(R, 0, True)]))
show("facing R, fish col0 moving R + diver col8 moving L", state(R, 6, True, fish=[(R, 0, True)], divers=[(R, 8, False)]))
show("facing R, fish col4 moving R (adjacent behind)", state(R, 6, True, fish=[(R, 4, True)]))
show("facing R, fish col3 moving R", state(R, 6, True, fish=[(R, 3, True)]))
print("== off-centre ==")
show("cells 7-8 facing L (x=7) empty", state(R, 7, False))
show("cells 7-8 facing R (x=8) empty", state(R, 8, True))
show("cells 8-9 facing R (x=9) empty", state(R, 9, True))
show("cells 8-9 facing R (x=9), fish col7 moving R (behind)", state(R, 9, True, fish=[(R, 7, True)]))
show("cells 8-9 facing R (x=9), fish col6 moving R (behind)", state(R, 9, True, fish=[(R, 6, True)]))
show("cells 8-9 facing L (x=8), fish col7 moving R (ahead)", state(R, 8, False, fish=[(R, 7, True)]))
show("cells 3-4 facing L (x=3) empty", state(R, 3, False))
