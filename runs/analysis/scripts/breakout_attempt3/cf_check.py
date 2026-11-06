import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from cf import cf_catchset, fold
net = cf_catchset(wsp.load_npz(CLAUDE))
bad = tot = 0
for dx in (1, -1):
    for y in range(9):
        for x in range(10):
            tx = x - dx; ty = y - 1
            if not (0 <= tx <= 9 and ty >= 0): continue
            a, b = fold(x + dx*(8-y)), fold(x + dx*(9-y))
            for p in range(10):
                o = np.zeros(600, np.float32); o[(y*10+x)*6+3] = 1; o[(ty*10+tx)*6+4] = 1; o[(90+p)*6] = 1
                z = wsp.logits(net, o); pr = np.exp(z-z.max()); pr /= pr.sum()
                got = 3 if pr[3] > .5 else (1 if pr[1] > .5 else 0)
                want = 0 if p in (a, b) else (3 if p < min(a, b) else 1)
                tot += 1; bad += got != want
print("CF-A descent frames checked", tot, "mismatches", bad)
