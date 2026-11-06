import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import math, json, time, numpy as np, wsp
from concurrent.futures import ProcessPoolExecutor
R = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt%d/net.npz"
a2, a3 = wsp.load_npz(R % 2), wsp.load_npz(R % 3)
A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
bi = lambda r, c: (r * 10 + c) * 6 + 3   # ball channel index

# Graft 1: attempt 3 with its rising-ball tables (units 4-7) replaced by attempt 2's (attempt-3 scale is 5, attempt-2 scale is 10)
g3 = {k: v.copy() for k, v in a3.items()}
chg = 0
for r in range(10):
    for c in range(10):
        for u in (4, 5, 6, 7):
            new = a2["W1"][bi(r, c), u] / 2.0
            if g3["W1"][bi(r, c), u] != new: chg += 1
            g3["W1"][bi(r, c), u] = new
print("graft1 (a3 + a2 rising tables): W1 entries changed", chg)

# Graft 2: attempt 2 with Astra's rows 6-8 descending catch sets. Astra unit 0 = D+, unit 1 = D-; Astra accepts |T - p| <= 0.75.
g2 = {k: v.copy() for k, v in a2.items()}
chg = 0
for au, (ru, lu) in ((0, (0, 1)), (1, (2, 3))):
    for r in (6, 7, 8):
        for c in range(10):
            T = A["W1"][bi(r, c), au] / 0.02
            lo, hi = math.ceil(T - 0.75 - 1e-9), math.floor(T + 0.75 + 1e-9)
            for u, val in ((ru, 10.0 * lo), (lu, -10.0 * hi)):
                if g2["W1"][bi(r, c), u] != np.float32(val): chg += 1
                g2["W1"][bi(r, c), u] = val
print("graft2 (a2 + Astra rows 6-8 catch sets): W1 entries changed", chg)
np.savez("graft1_a3_with_a2_rising.npz", **g3); np.savez("graft2_a2_with_astra_rows678.npz", **g2)

def obs(ball, trail, pad):
    o = np.zeros((10, 10, 6), np.float32); o[9, pad, 0] = 1; o[1:4, :, 2] = 1
    o[ball[0], ball[1], 3] = 1; o[trail[0], trail[1], 4] = 1; return o.reshape(600)
def cls(net, x):
    a = int(np.argmax(wsp.logits(net, x))); return {1: "L", 3: "R"}.get(a, "S")
def cmp(n1, n2):
    d = {}
    for r in range(9):
        for c in range(10):
            for vy in (-1, 1):
                for vx in (-1, 1):
                    tr, tc = r - vy, c - vx
                    if not (0 <= tr <= 8 and 0 <= tc <= 9): continue
                    for p in range(10):
                        x = obs((r, c), (tr, tc), p)
                        if cls(n1, x) != cls(n2, x):
                            k = ("down" if vy == 1 else "up", r); d[k] = d.get(k, 0) + 1
    return d
print("diag decision diffs graft1 vs a2:", cmp(g3, a2))
print("diag decision diffs graft2 vs astra:", cmp(g2, A))

def per_episode(net, seeds, workers=4):
    chunks = [seeds[i::workers] for i in range(workers)]
    with ProcessPoolExecutor(workers) as ex:
        parts = list(ex.map(wsp._worker, [(net, "breakout", ch) for ch in chunks]))
    out = {}
    for ch, res in zip(chunks, parts):
        for s, (sc, st) in zip(ch, res): out[s] = (sc, st)
    return [out[s] for s in seeds]

if __name__ == "__main__":
    seeds = list(range(200)); res = {}
    for name, net in (("a2", a2), ("graft1", g3), ("graft2", g2)):
        t = time.time(); r = per_episode(net, seeds); res[name] = r
        sc = np.array([x[0] for x in r]); ln = np.array([x[1] for x in r])
        print(f"{name}: seeds 0-199 mean {sc.mean():.3f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f} mean_len {ln.mean():.2f} capped {(ln==10000).sum()} ({time.time()-t:.0f}s)", flush=True)
    same = sum(1 for x, y in zip(res["a2"], res["graft1"]) if x == y)
    print("per-episode (score, steps) identical, a2 vs graft1:", same, "of 200")
    json.dump(res, open("s3_results.json", "w"))
