"""What-if edits to a COPY of Claude's network (originals untouched), 200 episodes each (seeds 0..199).
A1 sticky lookahead: up-unit of row r also sees danger of row r-2 (down: r+2), weight w, baseline-compensated.
A2 gold horizon: up-unit of row r also sees gold-arrival of row r-2 (down: r+2).
A4 edge rows: stronger penalty on target rows 1 and 8.
"""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy
import numpy as np
import wsp

BASE = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
D0, G0 = np.tanh(-1.2), np.tanh(-1.0)   # D and G of an empty row


def variant(sticky_w=0.0, gold_w=0.0, edge=None):
    n = copy.deepcopy(BASE)
    for r in range(1, 9):
        up_k, dn_k = 3 * (r - 1) + 1, 3 * (r - 1) + 2
        if r >= 3:
            n["W2"][r - 3, up_k] += sticky_w;        n["b2"][up_k] -= sticky_w * D0
            n["W2"][16 + r - 3, up_k] += -gold_w;    n["b2"][up_k] -= -gold_w * G0
        if r <= 6:
            n["W2"][r + 1, dn_k] += sticky_w;        n["b2"][dn_k] -= sticky_w * D0
            n["W2"][16 + r + 1, dn_k] += -gold_w;    n["b2"][dn_k] -= -gold_w * G0
    if edge is not None:
        for k in [0, 1, 4, 20, 21, 23]:
            n["b2"][k] = edge
    return n


if __name__ == "__main__":
    runs = {
        "base (as scored)": variant(),
        "A1 sticky lookahead w=0.3": variant(sticky_w=0.3),
        "A2 gold rows r+-2 w=0.15": variant(gold_w=0.15),
        "A1+A2": variant(sticky_w=0.3, gold_w=0.15),
        "A4 edge penalty b2=-2.6": variant(edge=-2.6),
    }
    sel = sys.argv[1:] or list(runs)
    for name in sel:
        r = wsp.evaluate(runs[name], "asterix", episodes=200, workers=4)
        print(f"{name:30s} mean {r['mean']:.2f} (se {r['se']:.2f}) len {r['mean_length']:.1f} max {r['max']}", flush=True)
