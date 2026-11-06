# Materiality test: re-weight only the G_r units' gold/trail inputs so freshly spawned edge gold counts as approaching
# (the behaviour answer.md states), leave everything else untouched, and score seeds 0..199.
import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from concurrent.futures import ProcessPoolExecutor
base = nets()["claude"]
F = copy.deepcopy(base)
gold = [6, 6, 12, 12, 18, 18, 18, 12, 12, 6]; trail = [0, -6, -6, -12, -12, -18, -12, -12, -6, 0]
for r in range(1, 9):
    u = 23 + r
    for c in range(10):
        F["W1"][(r*10 + c)*6 + 2, u] = gold[c]; F["W1"][(r*10 + c)*6 + 4, u] = trail[c]
bad = 0
for r in range(1, 9):
    for k in "EG":
        for c in range(10):
            for d in (1, -1):
                a1 = layers(F, board(5, [dict(r=r, c=c, kind=k, dir=d)]))[0]
                want = k == "G" and (c == 5 or (d == 1 and c < 5) or (d == -1 and c > 5))
                bad += (a1[23 + r] > 0) != want
                bad += int(((layers(F, board(5, [dict(r=r, c=c, kind=k, dir=d)]))[0][:24]) != (layers(base, board(5, [dict(r=r, c=c, kind=k, dir=d)]))[0][:24])).any())
print("fixed G: mismatches vs rule (and any change to P/T/Bk units):", bad)
def job(args):
    which, seed = args
    o = episode(F if which == "fixG" else base, seed); return o["score"], o["steps"]
if __name__ == "__main__":
    for which in ("fixG",):
        with ProcessPoolExecutor(4) as ex:
            r = list(ex.map(job, [(which, s) for s in range(200)], chunksize=5))
        sc = np.array([x[0] for x in r]); L = np.array([x[1] for x in r])
        print(f"{which} seeds 0..199: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(200):.3f} mean_len {L.mean():.1f}")
