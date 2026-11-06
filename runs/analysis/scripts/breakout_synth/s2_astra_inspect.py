import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
C = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz")
np.set_printoptions(precision=2, suppress=True, linewidth=160)
W = A["W1"].reshape(10, 10, 6, 32); Wc = C["W1"].reshape(10, 10, 6, 32)
print("astra b1[0:6]", A["b1"][:6]); print("astra paddle w (row9,ch0) units0-3:\n", W[9, :, 0, :4].T)
for u in range(4):
    print("astra unit", u, "ball/0.02 rows 0..8:\n", W[:9, :, 3, u] / 0.02)
for u in (0, 2, 4, 6):
    print("claude a2 unit", u, "ball/10 rows 5..8:\n", Wc[5:9, :, 3, u] / 10)
print("astra W2 nonzero rows/cols:", [(i, j, round(float(A['W2'][i, j]), 2)) for i, j in zip(*np.nonzero(A['W2'])) if i < 6][:40])
print("astra b2", A["b2"][:10]); print("astra W3 nz", [(i, j, float(A['W3'][i, j])) for i, j in zip(*np.nonzero(A['W3']))]); print("astra b3", A["b3"])
