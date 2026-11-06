import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
from collections import Counter
d = np.load("rec_claude_0_0.1.npz"); R = d["rec"]; ep = d["ep"]
g = lambda c: R[:, CI[c]]
by, bx, ly, dr, pos, done = g("by"), g("bx"), g("ly"), g("dir"), g("pos"), g("done")
land = (by == 8) & np.isin(dr, (2, 3))
sel = ep < 100
print("seeds 0-99 total steps:", int(sel.sum()))
up_trail = sel & (by == 1) & (ly == 2)                 # moving up: trail one row below
up_dir = sel & (by == 1) & np.isin(dr, (0, 1))         # env direction up (includes flat brick-from-above states)
print("ball row 1 & trail row 2:", int(up_trail.sum()), "; ball row 1 & env dir up:", int(up_dir.sum()), "; overlap", int((up_trail & up_dir).sum()))
# steps from such a state to the next landing state (ball on row 8 moving down) in the same episode
L = np.where(land)[0]
def ret(i):
    j = L[np.searchsorted(L, i)] if np.searchsorted(L, i) < len(L) else None
    return (j - i) if j is not None and ep[j] == ep[i] else None
for nm, m in (("trail-row-2", up_trail), ("all row1 up", up_dir)):
    rt = Counter(ret(i) for i in np.where(m)[0])
    print(f"  {nm}: steps until ball is on row 8 moving down: {dict(sorted((k if k is not None else -1, v) for k, v in rt.items()))}")
# all seeds 0-199: minimum return time for ball on row r moving up (trail row r+1), r=0..8
sel2 = np.ones(len(R), bool)
for r in range(0, 9):
    m = (by == r) & (ly == r + 1)
    rt = [ret(i) for i in np.where(m)[0]]; rt = [x for x in rt if x is not None]
    print(f"  seeds0-199 ball row {r} moving up: n={len(rt)} min return {min(rt) if rt else None}  design S(r)={S(r)}  count==S(r): {sum(x==S(r) for x in rt)}")
# move difference S=8 vs S=10 targets at row 1 moving up
T = design_tables()
diffs = 0; n = 0
for i in np.where(up_trail)[0]:
    dx = 1 if dr[i] == 1 else -1
    t8 = T["U+" if dx == 1 else "U-"][1, bx[i]]; t10 = fold(bx[i] + 10 * dx)
    m8 = np.sign(t8 - pos[i]); m10 = np.sign(t10 - pos[i]); n += 1
    diffs += int(m8 != m10)
print(f"row-1 moving-up states (trail row 2, seeds 0-99): {n}; move differs S=8 vs S=10: {diffs}")
diffs = 0; n = 0
for i in np.where(up_dir)[0]:
    dx = 1 if dr[i] == 1 else -1
    t8 = T["U+" if dx == 1 else "U-"][1, bx[i]]; t10 = fold(bx[i] + 10 * dx)
    n += 1; diffs += int(np.sign(t8 - pos[i]) != np.sign(t10 - pos[i]))
print(f"row-1 env-dir-up states (seeds 0-99): {n}; move differs S=8 vs S=10: {diffs}")
print("brick rows ever nonzero: source sets brick_map[1:4,:]=1 at reset and refill (see breakout.py)")
