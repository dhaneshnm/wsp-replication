import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

CL_ANS = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/answer.md"
CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"
AS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"

txt = open(CL_ANS).read()
print("number of ```edits blocks:", txt.count("```edits"))
net, rep = wsp.apply_edits(txt)
ref = wsp.load_npz(CL)
print("statements", rep.statements, "applied", rep.applied, "errors", rep.errors)
print("keys parsed", sorted(net), "keys npz", sorted(ref))
for k in net:
    print(" ", k, net[k].shape, ref[k].shape, "max|diff|", float(np.abs(net[k] - ref[k]).max()), "array_equal", np.array_equal(net[k], ref[k]))
W = ref["W1"].reshape(10, 10, 6, 32)
for ch in range(6):
    print(f"channel {ch}: nonzero W1 entries {int((W[:, :, ch, :] != 0).sum())}")
print("nonzero W1 columns:", sorted(set(np.nonzero(ref['W1'])[1].tolist())))
print("nonzero total:", sum(int((v != 0).sum()) for v in ref.values()))

def fold(u):
    if 0 <= u <= 9: return u
    if u >= 10: return 19 - u
    return -1 - u

# descending tables vs exact landing column
for unit, vx in [(0, 1), (1, -1)]:
    bad = [(r, c, float(W[r, c, 3, unit]), fold(c + vx * (9 - r))) for r in range(9) for c in range(10) if W[r, c, 3, unit] != fold(c + vx * (9 - r))]
    print(f"desc unit {unit}: mismatches vs fold(c+vx*(9-r)) rows 0-8: {bad}")
    print(f"  row 9 ball weights unit {unit}:", W[9, :, 3, unit])
# ascending tables vs stated rule rows 4..8: T = y + 2
for unit, vx in [(2, 1), (3, -1)]:
    bad = [(r, c, float(W[r, c, 3, unit]), fold(c + vx * (r + 2))) for r in range(4, 9) for c in range(10) if W[r, c, 3, unit] != fold(c + vx * (r + 2))]
    print(f"asc unit {unit}: rows 4-8 mismatches vs fold(c+vx*(r+2)): {bad}")
    for r in range(4):
        print(f"  row {r}:", W[r, :, 3, unit].astype(int).tolist())
print("A+ row8 == A- row8:", np.array_equal(W[8, :, 3, 2], W[8, :, 3, 3]), W[8, :, 3, 2].astype(int).tolist(), "9-c:", [9 - c for c in range(10)])
print("paddle weights units0-3 (row9, ch0):", W[9, :, 0, 0:4].T.astype(int).tolist())
# gates
gH_ball = W[:, :, 3, 4]; gH_tr = W[:, :, 4, 4]
print("gH ball weights all rows identical:", all(np.array_equal(gH_ball[r], gH_ball[0]) for r in range(10)), gH_ball[0].tolist())
print("gH trail weights all rows identical:", all(np.array_equal(gH_tr[r], gH_tr[0]) for r in range(10)), gH_tr[0].tolist())
print("expected gH ball 4*(2c+[c=0]-[c=9]):", [4 * (2 * c + (c == 0) - (c == 9)) for c in range(10)], "trail -8c:", [-8 * c for c in range(10)])
print("b1[4]", ref["b1"][4], "b1[5]", ref["b1"][5], "b1 nonzero:", np.nonzero(ref['b1'])[0].tolist())
gV_ball = W[:, :, 3, 5]; gV_tr = W[:, :, 4, 5]
print("gV ball weights per row (col-constant?):", [(r, sorted(set(gV_ball[r].tolist()))) for r in range(10)])
print("gV trail weights per row:", [(r, sorted(set(gV_tr[r].tolist()))) for r in range(10)])
print("expected gV ball 8*(r - [r=8]):", [8 * (r - (r == 8)) for r in range(10)], "trail -8r")
# Layer 2/3
print("W2 nonzero:", [(int(i), int(j), float(ref['W2'][i, j])) for i, j in zip(*np.nonzero(ref['W2']))])
print("b2:", ref["b2"][:10].tolist())
print("W3 nonzero:", [(int(i), int(j), float(ref['W3'][i, j])) for i, j in zip(*np.nonzero(ref['W3']))])
print("b3:", ref["b3"].tolist())
