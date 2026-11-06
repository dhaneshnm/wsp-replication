import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import numpy as np
from common import *
net = load("claude")
np.set_printoptions(precision=2, suppress=True)
# player in row 7 col 5; entity in row 3 (unit index row-1)
r = 3
print("P units, player row 7:", forward(net, obs((7,5)))[0][0:8])
print("empty board H1,H2,G row3:", [round(float(v),2) for v in forward(net, obs((7,5)))[0][[8+r-1,16+r-1,24+r-1]]])
for g in [False, True]:
    for lr in [True, False]:
        row = []
        for c in range(10):
            h1 = forward(net, obs((7,5), [(r, c, lr, g)]))[0]
            row.append((c, round(float(h1[8+r-1]),2), round(float(h1[16+r-1]),2), round(float(h1[24+r-1]),2)))
        print(("GOLD " if g else "ENEMY"), ("moving right" if lr else "moving left "), "(col,H1,H2,G):", row)
