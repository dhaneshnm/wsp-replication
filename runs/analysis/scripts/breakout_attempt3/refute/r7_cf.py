# Counterfactual copies of Claude's net (diagnostic only). Each evaluated on seeds 0..199, 4 workers.
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp, copy
CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m

def set_desc(net, rows_mid):
    """Descent units 0-3 at scale 10, threshold 0.75; target = x8 for rows not in rows_mid, midpoint of the two catch cells for rows in rows_mid."""
    n = copy.deepcopy(net)
    for (uR, uL, dx) in [(0, 1, 1), (2, 3, -1)]:
        for y in range(9):
            for x in range(10):
                L = (fold(x+dx*(8-y)) + fold(x+dx*(9-y)))/2 if y in rows_mid else fold(x+dx*(8-y))
                i = (y*10+x)*6+3; n["W1"][i, uR] = 10*L; n["W1"][i, uL] = -10*L
        for p in range(10):
            n["W1"][(90+p)*6, uR] = -10*p; n["W1"][(90+p)*6, uL] = 10*p
        n["b1"][uR] = n["b1"][uL] = -7.5
    return n

def set_up(net, T):
    n = copy.deepcopy(net)
    for (uR, uL, dx) in [(4, 5, 1), (6, 7, -1)]:
        for y in range(9):
            for x in range(10):
                L = fold(x+dx*T[y]); i = (y*10+x)*6+3; n["W1"][i, uR] = 5*L; n["W1"][i, uL] = -5*L
    return n

T_ASTRA = [9, 10, 7, 6, 5, 6, 7, 8, 9]
if __name__ == "__main__":
    C = wsp.load_npz(CLAUDE); A = wsp.load_npz(ASTRA)
    variants = {
        "original": C,
        "midpoint all rows 0-8 (analyst catch-set fix)": set_desc(C, set(range(9))),
        "Astra T only": set_up(C, T_ASTRA),
        "midpoint all rows + Astra T (analyst both)": set_up(set_desc(C, set(range(9))), T_ASTRA),
        "Astra desc tables (mid rows 6-8 only)": set_desc(C, {6, 7, 8}),
        "Astra desc tables + Astra T (Astra's two tables)": set_up(set_desc(C, {6, 7, 8}), T_ASTRA),
        "Astra net": A,
    }
    which = sys.argv[1:] or list(variants)
    for k in variants:
        if k not in which and not any(w in k for w in which): continue
        r = wsp.evaluate(variants[k], "breakout", episodes=200, workers=4)
        print(f"{k:52s} mean {r['mean']:.2f} se {r['se']:.1f} mean_len {r['mean_length']:.0f} max {r['max']:.0f}", flush=True)
