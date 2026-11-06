import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *
from collections import Counter
NOOP = {0, 2, 4, 5}

def analyze(name, verbose=True):
    d = np.load(f"rec_{name}_0_0.1.npz"); R = d["rec"]; ep = d["ep"]
    g = lambda c: R[:, CI[c]]
    by, bx, dr, pos, a, exe, stk, done = g("by"), g("bx"), g("dir"), g("pos"), g("a"), g("exe"), g("sticky"), g("done")
    land = (by == 8) & np.isin(dr, (2, 3))
    miss = land & (done == 1)
    nd = int(done.sum())
    print(f"== {name}: steps {len(R)} episodes {len(d['seeds'])} mean {d['scores'].mean():.2f} capped {(d['lens']==10000).sum()} "
          f"landings {land.sum()} misses {miss.sum()} (all done steps are landing misses: {nd == miss.sum()}) miss rate {100*miss.sum()/land.sum():.3f}% "
          f"steps/landing {len(R)/land.sum():.2f} bricks/step {g('r').sum()/len(R):.4f}")
    dx = np.where(dr == 2, 1, -1)
    mv = lambda e, s: (e == 3) & (s == 1) | (e == 1) & (s == -1)  # executed move in direction s
    catA = miss & (pos == bx) & np.isin(a, list(NOOP)) & mv(exe, -dx)
    catA_st = catA & (stk == 1)
    idx = np.where(catA)[0]
    print(f"   cat A (paddle==ball col, sampled no-op class, executed -dx move): {catA.sum()} (of which sticky flag set: {catA_st.sum()}); share of misses {100*catA.sum()/miss.sum():.1f}%")
    # all landings in that configuration
    cfg = land & (pos == bx) & np.isin(a, list(NOOP)) & mv(exe, -dx)
    print(f"   landings in that configuration: {cfg.sum()}, of which missed {(cfg & miss).sum()}")
    if len(idx):
        row6 = sum(by[i-2] == 6 and ep[i-2] == ep[i] for i in idx)
        w1 = sum(any(stk[j] == 1 and mv(exe[j], dx[i]) and ep[j] == ep[i] for j in range(i-4, i)) for i in idx)
        w2 = sum(any(stk[j] == 1 and mv(exe[j], dx[i]) and ep[j] == ep[i] for j in range(i-3, i+1)) for i in idx)
        prevmove = Counter(int(exe[i-1]) for i in idx)
        print(f"   cat A history: ball row 6 two steps before {row6}/{len(idx)}; sticky +dx executed move in t-4..t-1: {w1}; in t-3..t: {w2}; exe at t-1 {dict(prevmove)}")
    # flights: from the first step after a catch (or t=0) to the next landing step inclusive
    starts = np.r_[0, np.where(np.diff(ep) != 0)[0] + 1]
    catch_next = np.where(land & (done == 0))[0] + 1
    fstart = np.zeros(len(R), bool); fstart[starts] = True; fstart[catch_next[catch_next < len(R)]] = True
    fl = []
    s = None
    for i in range(len(R)):
        if fstart[i]: s = i
        if land[i]:
            N = i - s + 1; p0 = pos[s]; b = bx[i]; nx = min(9, max(0, b + dx[i]))
            dist = min(abs(p0 - b), abs(p0 - nx))
            delays = int(sum(1 for j in range(s, i + 1) if stk[j] == 1 and exe[j] in NOOP and a[j] in (1, 3)))
            sticky_noop = int(sum(1 for j in range(s, i + 1) if stk[j] == 1 and exe[j] in NOOP))
            fl.append((N, N - dist, int(p0), int(bx[s]), int(b), bool(miss[i]), delays, sticky_noop))
    F = np.array([(f[0], f[1], f[5]) for f in fl])
    print(f"   flights {len(fl)}; slack distribution of flights: {dict(sorted(Counter(F[:,1].tolist()).items()))}")
    print(f"   misses by slack: {dict(sorted(Counter(F[F[:,2]==1,1].tolist()).items()))}")
    s1 = [f for f in fl if f[1] == 1]; s1m = [f for f in s1 if f[5]]
    print(f"   slack1 flights {len(s1)}, misses {len(s1m)} ({100*len(s1m)/max(1,len(s1)):.3f}%); share of all misses {100*len(s1m)/miss.sum():.1f}%")
    print(f"   slack1 misses by N: {dict(Counter(f[0] for f in s1m))}; by (paddle start col, landing col): {Counter((f[2], f[4]) for f in s1m).most_common(5)}")
    print(f"   slack1 misses that are N==10 and corner-to-corner (paddle start in {{0,9}}, landing the other corner): {sum(1 for f in s1m if f[0]==10 and {f[2], f[4]}=={0,9})}")
    print(f"   slack1 misses: #sticky no-op delays (net wanted a move) {dict(sorted(Counter(f[6] for f in s1m).items()))}; #sticky no-op executions {dict(sorted(Counter(f[7] for f in s1m).items()))}")
    return R, ep, land, miss

if __name__ == "__main__":
    for n in sys.argv[1:]:
        analyze(n)
