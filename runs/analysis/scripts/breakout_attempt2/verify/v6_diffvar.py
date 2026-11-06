import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
base = wsp.load_npz(CLAUDE)
theirs = wsp.load_npz("../cf2_rows678.npz"); mine = wsp.load_npz("my_v678.npz")
for k in base:
    d = np.argwhere(theirs[k] != base[k])
    print(k, "analyst changed", len(d))
W = theirs["W1"]; M = mine["W1"]; B = base["W1"]
idx = np.argwhere((W != B) | (M != B))
for i, u in idx:
    r, c, ch = i // 60, (i // 6) % 10, i % 6
    print(f"unit {u} row {r} col {c} ch {ch}: base {B[i,u]:6.1f} analyst {W[i,u]:6.1f} mine {M[i,u]:6.1f}")
