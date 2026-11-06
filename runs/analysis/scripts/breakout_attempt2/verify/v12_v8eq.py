import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
mine = wsp.load_npz("my_v8.npz"); theirs = wsp.load_npz("../cf2_row8.npz"); base = wsp.load_npz(CLAUDE)
print("analyst row8 variant changed weights:", sum(int((theirs[k] != base[k]).sum()) for k in base), "; mine:", sum(int((mine[k] != base[k]).sum()) for k in base))
dif = 0
for u in range(8):
    for r in range(10):
        for c in range(10):
            for p in range(10):
                i = (r*10+c)*6+3; j = (90+p)*6
                if (mine["W1"][i,u] + mine["W1"][j,u] + mine["b1"][u] > 0) != (theirs["W1"][i,u] + theirs["W1"][j,u] + theirs["b1"][u] > 0): dif += 1
print("comparator-unit sign differences between my row-8 variant and analyst's over all (unit,row,col,paddle):", dif)
