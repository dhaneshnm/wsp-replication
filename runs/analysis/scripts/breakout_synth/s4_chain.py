import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import json, time, numpy as np, wsp
from concurrent.futures import ProcessPoolExecutor
bi = lambda r, c: (r * 10 + c) * 6 + 3

def per_episode(net, seeds, workers=4):
    chunks = [seeds[i::workers] for i in range(workers)]
    with ProcessPoolExecutor(workers) as ex:
        parts = list(ex.map(wsp._worker, [(net, "breakout", ch) for ch in chunks]))
    out = {}
    for ch, res in zip(chunks, parts):
        for s, r in zip(ch, res): out[s] = tuple(r)
    return [out[s] for s in seeds]

if __name__ == "__main__":
    R = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt%d/net.npz"
    A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
    g2 = wsp.load_npz("graft2_a2_with_astra_rows678.npz")
    g3 = {k: v.copy() for k, v in g2.items()}; chg = 0
    for au, (ru, lu) in ((2, (4, 5)), (3, (6, 7))):   # Astra unit 2 = U+, unit 3 = U-
        for c in range(10):
            T = A["W1"][bi(1, c), au] / 0.02
            for u, val in ((ru, 10 * T), (lu, -10 * T)):
                if g3["W1"][bi(1, c), u] != np.float32(val): chg += 1
                g3["W1"][bi(1, c), u] = val
    print("graft3 = graft2 + Astra rising row 1: extra W1 entries changed", chg)
    seeds = list(range(200)); res = {}
    for name, net in (("a1", wsp.load_npz(R % 1)), ("a3", wsp.load_npz(R % 3)), ("astra", A), ("graft3", g3)):
        t = time.time(); r = per_episode(net, seeds); res[name] = r
        sc = np.array([x[0] for x in r]); ln = np.array([x[1] for x in r])
        print(f"{name}: seeds 0-199 mean {sc.mean():.3f} se {sc.std(ddof=1)/np.sqrt(200):.2f} mean_len {ln.mean():.2f} capped {(ln==10000).sum()} ({time.time()-t:.0f}s)", flush=True)
    print("per-episode identical graft3 vs astra:", sum(x == y for x, y in zip(res["graft3"], res["astra"])), "of 200")
    json.dump(res, open("s4_results.json", "w"))
