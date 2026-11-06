import sys, itertools
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
A = wsp.load_npz(ASTRA); C = wsp.load_npz(CLAUDE)
txt = open(ASTRA_ANSWER).read()
na, rep = wsp.apply_edits(txt)
print("astra re-parse == hand.npz:", all(np.array_equal(na[k], A[k]) for k in A), rep.statements, rep.applied, len(rep.errors))
def tab(net, u, scale):
    return np.array([[net["W1"][(r*10+c)*6+3, u] for c in range(10)] for r in range(10)]) / scale
ast = {"D+": tab(A, 0, 0.02), "D-": tab(A, 1, 0.02), "U+": tab(A, 2, 0.02), "U-": tab(A, 3, 0.02)}
cl = {"D+": tab(C, 0, 10), "D-": tab(C, 2, 10), "U+": tab(C, 4, 10), "U-": tab(C, 6, 10)}
print("astra paddle weights /0.02 units0-3:", [ (np.array([A['W1'][(90+c)*6, u] for c in range(10)])/0.02).round(3).tolist() == [-c for c in range(10)] for u in range(4)])
for k in ast:
    diff_rows = [r for r in range(10) if not np.allclose(ast[k][r], cl[k][r], atol=1e-4)]
    print(f"{k}: rows where Astra != Claude: {diff_rows}")
    for r in diff_rows:
        print(f"    row {r}: astra {np.round(ast[k][r],2).tolist()}  claude {cl[k][r].astype(int).tolist()}")
# rows 6-8 descent: Astra == midpoint of the two catch columns?
for k, dx in (("D+", 1), ("D-", -1)):
    for r in (6, 7, 8):
        mid = [(fold(c + dx*(8-r)) + fold(c + dx*(9-r))) / 2 for c in range(10)]
        print(f"{k} row {r}: astra == midpoint(F(c+dx(8-r)), F(c+dx(9-r))): {np.allclose(ast[k][r], mid, atol=1e-4)}")
for k, dx in (("U+", 1), ("U-", -1)):
    print(f"{k} row 1 astra == F(c+dx*10): {np.allclose(ast[k][1], [fold(c+dx*10) for c in range(10)], atol=1e-4)}")
# my v678 vs astra: induced no-op sets for every (row, col, paddle) for rows 6-8 descent
V = wsp.load_npz("my_v678.npz")
bad = 0
for (ru, lu, au, k) in ((0, 1, 0, "D+"), (2, 3, 1, "D-")):
    for r in range(10):
        for c in range(10):
            for p in range(10):
                i = (r*10+c)*6+3
                mv = (V["W1"][i, ru]/10 - p - 0.5 > 0) - (-(V["W1"][i, lu])/10 - p + 0.5 < 0) * 0
                R = V["W1"][i, ru]/10 - p >= 1; L = p - (-(V["W1"][i, lu])/10) >= 1
                diff = ast[k][r, c] - p
                aR = diff > 0.75; aL = diff < -0.75
                if (R, L) != (aR, aL): bad += 1
print("my v678 vs Astra: (row,col,paddle) descent cases with different move decision:", bad)
# direction units: compare sign of Claude X/V and Astra unit4/-unit5 on all (ball cell, trail cell) pairs
dis = 0; n = 0
for br, bc, lr, lc in itertools.product(range(10), range(10), range(10), range(10)):
    x = np.zeros(600, np.float32); x[(br*10+bc)*6+3] = 1; x[(lr*10+lc)*6+4] = 1; x[(9*10+4)*6] = 1
    a1c = x @ C["W1"] + C["b1"]; a1a = x @ A["W1"] + A["b1"]
    n += 1
    if (a1c[8] > 0) != (a1a[4] > 0) or (a1c[9] > 0) != (a1a[5] < 0): dis += 1
print("direction/vertical unit sign disagreements over all ball/trail cell pairs:", dis, "of", n)
print("layer-1 units used: claude", int((np.abs(C['W1']).sum(0) > 0).sum()), "astra", int((np.abs(A['W1']).sum(0) > 0).sum()),
      "; layer-2 units: claude", int((np.abs(C['W2']).sum(0) > 0).sum()), "astra", int((np.abs(A['W2']).sum(0) > 0).sum()))
