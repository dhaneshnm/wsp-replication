import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
net = {k: v.copy() for k, v in nets()["claude"].items()}
W = net["W1"].reshape(10, 10, 6, 32)
for r in range(9):
    for c in range(10):
        W[r, c, 3, 0] = fold(c + (8 - r))   # D+: column the ball occupies at row 8 (catch with ball_x == pos)
        W[r, c, 3, 1] = fold(c - (8 - r))   # D-
net["W1"] = W.reshape(600, 32)
wsp.save_npz(net, "variant_samedir.npz")
print("changed entries:", int((net["W1"] != nets()["claude"]["W1"]).sum()))
print("unit0 row 8:", W[8, :, 3, 0], " row 1:", W[1, :, 3, 0])
