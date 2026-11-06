import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import numpy as np
import s9_interventions as S
from common import *

def astra_no_lookahead(net):
    n = {k: v.copy() for k, v in net.items()}
    rows = list(range(90, 570, 60))  # player at col 5, rows 1..8
    blk = n["W1"][rows][:, 0:16]
    print("weight-3 entries zeroed (player row, unit):", [(i + 1, j) for i in range(8) for j in range(16) if blk[i, j] == 3])
    for i, r in enumerate(rows):
        for j in range(16):
            if n["W1"][r, j] == 3: n["W1"][r, j] = 0
    return n

S.VARIANTS["astra"] = ("astra", None, 0.1)
S.VARIANTS["astra_no_lookahead"] = ("astra", astra_no_lookahead, 0.1)
if __name__ == "__main__":
    astra_no_lookahead(load("astra"))
    # verify probe: enemy two rows above at col 5 no longer blocks 'up'
    n = astra_no_lookahead(load("astra"))
    p = forward(n, obs((5, 5), [(3, 5, True, False)]))[3]; print("ablated astra, enemy 2 rows up at col5: P(n,u,d)=(%.3f,%.3f,%.3f)" % (p[0], p[2], p[4]))
    sys.argv = ["x", "200", "astra_no_lookahead"]
    S._main()
