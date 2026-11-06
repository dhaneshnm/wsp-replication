"""Claims 6/9/10: my own counterfactual edits to Claude's net, evaluated with
wsp.evaluate on seeds 0-199 (4 workers).
  catch-set fix : descent units 0-3 target the midpoint of both catch cells
                  {fold(u8), fold(u8+dx)}, comparator tanh(10*(M-p-0.75)) / tanh(10*(p-M-0.75))
  catch-set fix (rows 6-8 only, Astra-style) : same but only for ball rows 6-8
  T fix         : rising units 4-7 use T=[9,10,7,6,5,6,7,8,9]
"""
import sys, copy, json
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

C = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz")
A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")


def fold(u):
    m = u % 20
    return 19 - m if m >= 10 else m


def catch_fix(net, rows=range(9)):
    n = copy.deepcopy(net)
    for (uR, uL, dx) in ((0, 1, +1), (2, 3, -1)):
        for y in range(9):
            for x in range(10):
                i = (y * 10 + x) * 6 + 3
                if y in rows:
                    u8 = x + dx * (8 - y)
                    M = (fold(u8) + fold(u8 + dx)) / 2
                    n["W1"][i, uR] = 10 * M
                    n["W1"][i, uL] = -10 * M
                else:  # keep exact x8 target, rescaled to the new comparator
                    L = fold(x + dx * (8 - y))
                    n["W1"][i, uR] = 10 * L
                    n["W1"][i, uL] = -10 * L
        n["W1"][540:600:6, uR] = -10 * np.arange(10)
        n["W1"][540:600:6, uL] = 10 * np.arange(10)
        n["b1"][uR] = n["b1"][uL] = -7.5
    return n


def T_fix(net, T=(9, 10, 7, 6, 5, 6, 7, 8, 9)):
    n = copy.deepcopy(net)
    for (uR, uL, dx) in ((4, 5, +1), (6, 7, -1)):
        for y in range(9):
            for x in range(10):
                i = (y * 10 + x) * 6 + 3
                L = fold(x + dx * T[y])
                n["W1"][i, uR] = 5 * L
                n["W1"][i, uL] = -5 * L
    return n


def check_fix(n):
    """Exhaustive check of the new descent comparators: right fires iff p < M-0.75,
    left fires iff p > M+0.75, with |pre| >= 2.5."""
    bad = 0; mn = 1e9
    for (uR, uL, dx) in ((0, 1, +1), (2, 3, -1)):
        for y in range(9):
            for x in range(10):
                u8 = x + dx * (8 - y); M = (fold(u8) + fold(u8 + dx)) / 2
                for p in range(10):
                    v = np.zeros(600, np.float32); v[(y * 10 + x) * 6 + 3] = 1; v[540 + 6 * p] = 1
                    pre = v @ n["W1"] + n["b1"]
                    bad += (pre[uR] > 0) != (p < M - 0.75)
                    bad += (pre[uL] > 0) != (p > M + 0.75)
                    mn = min(mn, abs(pre[uR]), abs(pre[uL]))
    return int(bad), float(mn)


if __name__ == "__main__":
    nets = {
        "original": C,
        "catch_fix_all_rows": catch_fix(C),
        "catch_fix_rows6-8": catch_fix(C, rows=(6, 7, 8)),
        "T_fix": T_fix(C),
        "both(all rows)": T_fix(catch_fix(C)),
        "both(rows6-8)": T_fix(catch_fix(C, rows=(6, 7, 8))),
        "astra": A,
    }
    print("check catch_fix_all_rows (mismatches, min|pre|):", check_fix(nets["catch_fix_all_rows"]))
    res = {}
    for k, n in nets.items():
        r = wsp.evaluate(n, "breakout", episodes=200, base_seed=0, workers=4)
        res[k] = r
        print(k, json.dumps(r), flush=True)
