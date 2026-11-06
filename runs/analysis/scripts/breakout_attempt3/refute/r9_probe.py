import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(1, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt3/refute")
import numpy as np, wsp, collections
from r2_play import episode, CLAUDE, fold
from r7_cf import set_desc
net = wsp.load_npz(CLAUDE)
T_UP = [9, 10, 9, 8, 7, 8, 9, 10, 11]
def ob(by, bx, ty, tx, p):
    x = np.zeros(600, np.float32); x[(by*10+bx)*6+3] = 1; x[(ty*10+tx)*6+4] = 1; x[(90+p)*6] = 1; return x
# (1) all diagonal frames: greedy move vs reply formula; H/V signs; min |pre| of units 0-7
tot = bad = hb = vb = 0; minpre = 1e9
for dx in (1, -1):
    for dy in (1, -1):
        for by in range(9):
            for bx in range(10):
                ty, tx = by - dy, bx - dx
                if not (0 <= ty <= 8 and 0 <= tx <= 9): continue
                for p in range(10):
                    x = ob(by, bx, ty, tx, p)
                    pre = x @ net["W1"] + net["b1"]; h1 = np.tanh(pre)
                    L = fold(bx + dx*(8-by)) if dy == 1 else fold(bx + dx*T_UP[by])
                    want = 3 if L > p else (1 if L < p else 0)
                    z = wsp.logits(net, x); g = int(np.argmax(z))
                    got = g if g in (1, 3) else 0
                    tot += 1; bad += got != want; hb += np.sign(h1[8]) != dx; vb += np.sign(h1[9]) != dy
                    minpre = min(minpre, float(np.abs(pre[:8]).min()))
print(f"diagonal frames {tot}: greedy move != reply formula {bad}; H sign wrong {hb}; V sign wrong {vb}; min|pre| units0-7 {minpre}")
# (2) midpoint-all-rows variant: stop exactly on both catch cells in descending diagonal frames
cf = set_desc(net, set(range(9))); tot = bad = 0
for dx in (1, -1):
    for y in range(1, 9):
        for x in range(10):
            tx = x - dx
            if not 0 <= tx <= 9: continue
            a, b = fold(x + dx*(8-y)), fold(x + dx*(9-y))
            for p in range(10):
                g = int(np.argmax(wsp.logits(cf, ob(y, x, y-1, tx, p)))); got = g if g in (1, 3) else 0
                want = 0 if p in (a, b) else (3 if p < min(a, b) else 1)
                tot += 1; bad += got != want
print(f"midpoint variant descending frames {tot}: mismatches {bad}")
# (3) mechanism of in-play direction misreads, seeds 0..39
ctx = collections.Counter()
for s in range(40):
    _, _, F = episode(net, s, (8, 9))
    for i, f in enumerate(F):
        by, bx, ly, lx, d, pos, a, hs, vs, eff, posa, done, r = f
        DX, DY = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}[d]
        if vs != DY:
            pf = F[i-1]
            ctx[("V", f"flat={by==ly}", f"row{by}", f"prev_dir_down={pf[4] in (2,3)}", f"now_up={d in (0,1)}", f"brick_reward_prev_step={pf[12]}")] += 1
        if hs != DX:
            pf = F[i-1]
            ctx[("H", f"flat={by==ly}", f"row{by}", f"prev_row8_down={pf[0]==8 and pf[4] in (2,3)}", f"paddle_after_prev==new_col={pf[10]==bx and pf[1]!=bx}")] += 1
for k, v in sorted(ctx.items()): print(v, k)
