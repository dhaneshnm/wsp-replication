import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
C = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz")
A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
Ap, rep = wsp.apply_edits(open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md").read())
print("Astra parse", rep.statements, rep.applied, rep.errors, "max|hand.npz - parse|:", max(float(np.abs(A[k]-Ap[k]).max()) for k in A))
def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m
# Claude tables (unit 0 DR, 2 DL, 4 UR, 6 UL), divided by 5; Astra units 0 DR,1 DL,2 UR,3 UL divided by 0.02
pairs = [("desc-right", 0, 0, 1), ("desc-left", 2, 1, -1), ("asc-right", 4, 2, 1), ("asc-left", 6, 3, -1)]
for nm, cu, au, dx in pairs:
    ct = np.array([[C["W1"][(y*10+x)*6+3, cu]/5 for x in range(10)] for y in range(9)])
    at = np.array([[A["W1"][(y*10+x)*6+3, au]/0.02 for x in range(10)] for y in range(9)])
    eq = [bool(np.allclose(ct[y], at[y], atol=1e-4)) for y in range(9)]
    print(nm, "rows equal Claude:", eq)
    if nm.startswith("desc"):
        for y in range(6, 9):
            mid = [(fold(x+dx*(8-y)) + fold(x+dx*(9-y)))/2 for x in range(10)]
            print(f"   row {y} astra == midpoint(fold(x+dx*(8-y)), fold(x+dx*(9-y))):", bool(np.allclose(at[y], mid, atol=1e-4)))
    else:
        Ts = [[T for T in range(20) if np.allclose([fold(x+dx*T) for x in range(10)], at[y], atol=1e-4)] for y in range(9)]
        print("   Astra T per row:", Ts)
used = lambda n, L: np.where(np.abs(n["W1"]).sum(0) + np.abs(n["b1"]) > 0)[0].tolist()
print("Astra layer1 units used:", used(A, 1), "layer2 used:", np.where(np.abs(A["W2"]).sum(0) + np.abs(A["b2"]) > 0)[0].tolist())
print("Astra brick channel nonzero:", int((A["W1"][2::6] != 0).sum()), "; Astra b1:", A["b1"][:6].tolist())
print("Astra b3:", A["b3"].tolist(), "W3 nonzero:", [(int(i), int(j), float(A["W3"][i, j])) for i, j in zip(*np.nonzero(A["W3"]))])
