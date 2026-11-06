import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
from collections import Counter
C = wsp.load_npz(CLAUDE); V1 = wsp.load_npz("my_vrow1.npz")
d = np.load("rec_claude_0_0.1.npz"); R = d["rec"]; ep = d["ep"]
g = lambda c: R[:, CI[c]]
by, bx, ly, lx, dr, pos = g("by"), g("bx"), g("ly"), g("lx"), g("dir"), g("pos")
idx = np.where((ep < 100) & (by == 1) & (ly == 2))[0]
T = design_tables(); res = Counter(); ex = []
for i in idx:
    x = np.zeros(600, np.float32); x[(by[i]*10+bx[i])*6+3] = 1; x[(ly[i]*10+lx[i])*6+4] = 1; x[(90+pos[i])*6] = 1
    mc = move_class(layers(C, x)[4]); mv = move_class(layers(V1, x)[4])
    dx = 1 if dr[i] == 1 else -1
    res[(int(mc), int(mv))] += 1
    if mc != mv and len(ex) < 5: ex.append((int(ep[i]), int(R[i,0]), (int(by[i]), int(bx[i])), (int(ly[i]), int(lx[i])), int(dr[i]), int(pos[i]), int(T['U+' if dx==1 else 'U-'][1,bx[i]]), fold(bx[i]+10*dx)))
print("(claude move, row1-fix move) at the 539 row-1 moving-up states (bricks omitted from obs; they carry no weight):", dict(res))
print("examples (seed,t,ball,trail,dir,pos,T_S8,T_S10):", ex)
