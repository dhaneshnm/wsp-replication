import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
from collections import Counter
for name in sys.argv[1:]:
    d = np.load(f"rec_{name}_0_0.1.npz"); R = d["rec"]; ep = d["ep"]
    g = lambda c: R[:, CI[c]]
    by, bx, dr, pos, done = g("by"), g("bx"), g("dir"), g("pos"), g("done")
    land = (by == 8) & np.isin(dr, (2, 3)); miss = land & (done == 1)
    starts = set(np.r_[0, np.where(np.diff(ep) != 0)[0] + 1].tolist()) | set((np.where(land & (done == 0))[0] + 1).tolist())
    rows = []; s = 0
    for i in range(len(R)):
        if i in starts: s = i
        if land[i]:
            N = i - s + 1; dxv = 1 if dr[i] == 2 else -1; nx = min(9, max(0, bx[i] + dxv))
            rows.append((N - abs(pos[s] - bx[i]), N - min(abs(pos[s] - bx[i]), abs(pos[s] - nx)), bool(miss[i])))
    A = np.array(rows)
    k = A[:, 0] == 1
    print(f"{name}: slack-to-x8 == 1: flights {k.sum()}, misses {(k & (A[:,2]==1)).sum()}, rate {100*(k & (A[:,2]==1)).sum()/k.sum():.3f}%;"
          f" cross-tab (slack_x8, slack_nearest) for slack_x8==1: {Counter(map(int, A[k,1]))}; misses by slack_x8 {dict(sorted(Counter(map(int, A[A[:,2]==1,0])).items()))}")
