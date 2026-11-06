import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import numpy as np
from common import *
net = load("claude")
TYPES = {"empty": None, "immediate(E@5)": (5, True, False), "immediate(E@4->)": (4, True, False),
         "near(E@3->)": (3, True, False), "far(E@0->)": (0, True, False), "passed(E@6->)": (6, True, False),
         "gold(G@2->)": (2, True, True)}
y = 4
print("player row", y, "; badness units stay_y/up_y/down_y and logits n,u,d (others) and probs")
for where, row in [("current", y), ("above", y-1), ("below", y+1)]:
    for tname, t in TYPES.items():
        if where == "current" and t is not None and t[0] == 5 and not t[2]:
            continue  # player would be dead
        ents = [] if t is None else [(row, t[0], t[1], t[2])]
        h1, h2, z, p = forward(net, obs((y, 5), ents))
        print(f"{where:8s} {tname:17s} stay={h2[y-1]:+.2f} up={h2[7+y]:+.2f} down={h2[15+y]:+.2f} "
              f"logits n={z[0]:.2f} u={z[2]:.2f} d={z[4]:.2f} l/r/f={z[1]:.1f}/{z[3]:.1f}/{z[5]:.1f}  "
              f"P(n,u,d)=({p[0]:.3f},{p[2]:.3f},{p[4]:.3f})")
print()
# edge rows, empty board
for yy in range(1, 9):
    h1, h2, z, p = forward(net, obs((yy, 5)))
    print(f"empty board, player row {yy}: P(n,u,d)=({p[0]:.3f},{p[2]:.3f},{p[4]:.3f}) gold-dir unit={h2[23+yy]:+.2f}")
print()
# gold direction: gold 2-3 rows away
for desc, ents in [("gold row 1 (approaching)", [(1, 2, True, True)]), ("gold row 7 (approaching)", [(7, 2, True, True)]),
                   ("gold row1 + gold row 7 + gold row 8", [(1, 2, True, True), (7, 2, True, True), (8, 8, False, True)])]:
    h1, h2, z, p = forward(net, obs((4, 5), ents))
    print(f"player row 4, {desc}: gold-dir={h2[27]:+.2f} P(n,u,d)=({p[0]:.3f},{p[2]:.3f},{p[4]:.3f})")
