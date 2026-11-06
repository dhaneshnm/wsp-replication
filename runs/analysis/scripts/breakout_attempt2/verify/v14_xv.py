import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
from collections import Counter
C = wsp.load_npz(CLAUDE); T = design_tables()
d = np.load("rec_claude_0_0.1.npz"); R = d["rec"]; ep = d["ep"]
g = lambda c: R[:, CI[c]]
by, bx, ly, lx, dr, pos, nby, done = g("by"), g("bx"), g("ly"), g("lx"), g("dir"), g("pos"), g("nby"), g("done")
aa = np.where(bx == 0, 1, bx)
Xd = (aa - lx >= 1); Xt = np.isin(dr, (1, 2))
xw = np.where(Xd != Xt)[0]
print("seeds 0-199 states:", len(R), "X wrong:", len(xw), "breakdown (ball row, trail row, paddle==ball col):", Counter((int(by[i]), int(ly[i]), bool(pos[i]==bx[i])) for i in xw))
# reversal catches: landing steps not done where executed paddle (npos) == new ball col and npos != old ball col
land = (by == 8) & np.isin(dr, (2, 3))
rev = np.where(land & (done == 0) & (g("npos") != bx))[0]
print("reversal catches:", len(rev), "; next state X wrong:", sum(1 for i in rev if Xd[i+1] != Xt[i+1]), "; two states later X wrong:", sum(1 for i in rev if i+2 < len(R) and ep[i+2]==ep[i] and Xd[i+2] != Xt[i+2]))
def obs(i):
    x = np.zeros(600, np.float32); x[(by[i]*10+bx[i])*6+3] = 1; x[(ly[i]*10+lx[i])*6+4] = 1; x[(90+pos[i])*6] = 1; return x
def oracle(i):
    up = dr[i] in (0, 1); xp = dr[i] in (1, 2); t = T[("U" if up else "D") + ("+" if xp else "-")][by[i], bx[i]]
    return 3 if t > pos[i] else (1 if t < pos[i] else 0)
print("X-wrong states where net move != oracle move:", sum(1 for i in xw if move_class(layers(C, obs(i))[4]) != oracle(i)))
print("max |F(u)-F(u+2)| over u:", max(abs(fold(u) - fold(u+2)) for u in range(-40, 40)))
# V: flat states off row 8 with env direction up
fu = np.where((by == ly) & (by != 8) & np.isin(dr, (0, 1)))[0]
print("flat off-row-8 env-dir-up states:", len(fu), "by ball row:", Counter(map(int, by[fu])), "; next ball row == row-1:", sum(1 for i in fu if nby[i] == by[i]-1), "; next ball row == same row:", sum(1 for i in fu if nby[i] == by[i]))
prev_row0 = sum(1 for i in fu if by[i] >= 1 and any(by[j] == 0 for j in range(i-by[i]-1, i) if ep[j] == ep[i]))
print("  of row>=1 ones, ball was on row 0 within the preceding steps:", prev_row0, "of", int((by[fu] >= 1).sum()))
print("  net move != oracle move at these states:", sum(1 for i in fu if move_class(layers(C, obs(i))[4]) != oracle(i)))
fd = np.where((by == ly) & (by != 8) & np.isin(dr, (2, 3)))[0]
print("flat off-row-8 env-dir-down states (V correct):", len(fd))
