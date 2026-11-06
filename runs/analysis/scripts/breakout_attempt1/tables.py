import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
N = nets()
W = N["claude"]["W1"].reshape(10, 10, 6, 32)
T = {0: 10, 1: 11, 2: 10, 3: 9}
for y in range(4, 9): T[y] = y + 2
for unit, vx in [(2, 1), (3, -1)]:
    bad = [(y, c, W[y, c, 3, unit], fold(c + vx * T[y])) for y in range(9) for c in range(10) if W[y, c, 3, unit] != fold(c + vx * T[y])]
    print(f"claude ascending unit {unit} (vx={vx}) matches fold(c + vx*T(y)) with T={T}: mismatches {bad}")
print("claude A+ row8 == A- row8:", np.array_equal(W[8, :, 3, 2], W[8, :, 3, 3]), W[8, :, 3, 2])
Wa = N["astra"]["W1"].reshape(10, 10, 6, 32)
for unit, vx in [(0, 1), (1, -1)]:
    ok_row8col = all(abs(Wa[r, c, 3, unit] - 0.02 * fold(c + vx * (8 - r))) < 1e-6 for r in range(6) for c in range(10))
    print(f"astra descending unit {unit}: rows 0-5 weight == 0.02*fold(c+vx*(8-r)) (ball column at row 8): {ok_row8col}")
    for r in (6, 7, 8):
        mids = [0.02 * (fold(c + vx * (8 - r)) + fold(c + vx * (9 - r))) / 2 for c in range(10)]
        print(f"   row {r}: weight/0.02 =", np.round(Wa[r, :, 3, unit] / 0.02, 2), " midpoint(row8col, landing) =", np.round(np.array(mids) / 0.02, 2))
