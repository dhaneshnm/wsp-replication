# Claim 9: layer-2/output weights vs the reply's stated design; all nonzeros accounted for
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
n = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz")
modes = [(+1, +1), (-1, +1), (+1, -1), (-1, -1)]  # (gH sign, gV sign) for D+, D-, A+, A-
W2 = np.zeros((32, 32)); b2 = np.zeros(32)
for m, (sh, sv) in enumerate(modes):
    for k, sd in ((m, +6), (m + 4, -6)):      # right unit m, left unit m+4
        W2[m, k] = sd; W2[4, k] = 10 * sh; W2[5, k] = 10 * sv; b2[k] = -2.28 - 20
W3 = np.zeros((32, 6)); W3[0:4, 3] = 8; W3[4:8, 1] = 8
b3 = np.array([6, 32, -10, 32, -10, -10])
print("max|W2-design|", np.abs(n["W2"] - W2).max(), " max|b2-design|", np.abs(n["b2"] - b2).max(),
      " max|W3-design|", np.abs(n["W3"] - W3).max(), " max|b3-design|", np.abs(n["b3"] - b3).max())
print("nonzero W1 columns", sorted(set(np.nonzero(n["W1"])[1])), " nonzero b1", np.nonzero(n["b1"])[0], n["b1"][5])
