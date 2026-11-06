import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import numpy as np
from common import *
for which in ["astra", "claude"]:
    net = load(which)
    y = 5
    print("=====", which, "player row", y, "col 5; single enemy; P(noop,up,down) by enemy row offset and (col,dir)")
    base = forward(net, obs((y, 5)))[3]
    print("empty board: P(n,u,d)=(%.3f,%.3f,%.3f)" % (base[0], base[2], base[4]))
    for dr in [-2, -1, 0, 1, 2]:
        line = []
        for lr in [True, False]:
            for c in range(10):
                if dr == 0 and c == 5: continue
                p = forward(net, obs((y, 5), [(y + dr, c, lr, False)]))[3]
                line.append(f"{c}{'>' if lr else '<'}:{p[0]:.2f}/{p[2]:.2f}/{p[4]:.2f}")
        print(f"row offset {dr:+d}: " + " ".join(line))
    if which == "astra":
        h1, h2, z, p = forward(net, obs((y, 5)))
        print("astra empty board h2[0:3] (up/down/wait hazard OR):", h2[0:3].round(3), "logits", z.round(2))
        for dr, c, lr in [(-1, 5, True), (-2, 5, True), (-1, 4, True), (-2, 4, True), (0, 4, True), (0, 3, True), (0, 2, True), (-1, 3, True)]:
            h1, h2, z, p = forward(net, obs((y, 5), [(y + dr, c, lr, False)]))
            print(f"  enemy row{dr:+d} col{c} {'right' if lr else 'left'}: h2[0:3]={h2[0:3].round(2)} P(n,u,d)=({p[0]:.3f},{p[2]:.3f},{p[4]:.3f})")
