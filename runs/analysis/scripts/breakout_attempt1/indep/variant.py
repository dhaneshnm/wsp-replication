# Claim 5: build my own same-direction variant (descending target = ball's column at row 8),
# compare with the analyst's variant file, and evaluate it with the harness (200 eps, 4 workers).
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

base = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz")


def fold(u):
    u = u % 20
    return u if u <= 9 else 19 - u


if __name__ == "__main__":
    v = {k: a.copy() for k, a in base.items()}
    for r in range(9):
        for c in range(10):
            v["W1"][(r * 10 + c) * 6 + 3, 0] = fold(c + (8 - r))
            v["W1"][(r * 10 + c) * 6 + 3, 1] = fold(c - (8 - r))
    print("entries changed vs Claude net:", int((v["W1"] != base["W1"]).sum()))
    an = wsp.load_npz("/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt1/variant_samedir.npz")
    print("max |my variant - analyst variant_samedir.npz|:", max(float(np.abs(v[k] - an[k]).max()) for k in v))
    wsp.save_npz(v, "my_samedir.npz")
    print("harness 200 eps:", wsp.evaluate(v, "breakout", episodes=200, workers=4))
