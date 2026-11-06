import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import json, collections
A = wsp.load_npz(ASTRA); C = wsp.load_npz(CLAUDE)
def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m
names = {0: "desc-right", 1: "desc-left", 2: "asc-right", 3: "asc-left"}
for u in range(4):
    tab = np.array([[A["W1"][(y*10+x)*6+3, u] / 0.02 for x in range(10)] for y in range(9)])
    print(f"Astra unit {u} ({names[u]}) decoded target = W1/0.02, rows 0..8:")
    for y in range(9): print("   row", y, np.round(tab[y], 1).tolist())
# implied return time T for ascending tables (which T in 0..20 reproduces the row, for x where unique)
for u, dx in [(2, 1), (3, -1)]:
    Ts = []
    for y in range(9):
        row = [A["W1"][(y*10+x)*6+3, u] / 0.02 for x in range(10)]
        cands = [T for T in range(0, 20) if all(abs(fold(x + dx*T) - row[x]) < 1e-6 for x in range(10))]
        Ts.append(cands)
    print(f"Astra unit {u}: return times T(y) consistent with the table:", Ts)
# Behavioural check on normal diagonal frames: where does each policy stop (no move)?
def stop_set(net, by, bx, ty, tx):
    s = []
    for p in range(10):
        o = np.zeros(600, np.float32); o[(by*10+bx)*6+3] = 1; o[(ty*10+tx)*6+4] = 1; o[(90+p)*6] = 1
        z = wsp.logits(net, o); pr = np.exp(z-z.max()); pr /= pr.sum()
        if pr[1] < .5 and pr[3] < .5: s.append(p)
    return s
for nm, net in [("claude", C), ("astra", A)]:
    cnt = collections.Counter()
    for dx in (1, -1):
        for by in range(1, 9):
            for bx in range(10):
                tx = bx - dx
                if not 0 <= tx <= 9: continue
                x8, nx8 = fold(bx + dx*(8-by)), fold(bx + dx*(9-by))
                st = stop_set(net, by, bx, by-1, tx)
                kind = "stops only at x8" if st == [x8] else ("stops at both catch cells" if sorted(st) == sorted({x8, nx8}) else f"other")
                cnt[(by >= 6, kind)] += 1
    print(nm, "descending frames, (ball row>=6, stopping set):", dict(cnt))
