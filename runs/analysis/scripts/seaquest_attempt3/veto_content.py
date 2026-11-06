"""What occupies cols 6-9 of the row above while SURF is on and the up move is vetoed (oxygen-death episodes)."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, sys.argv[1])
import pickle, numpy as np, wsp, trace as T
from collections import Counter
D = sys.argv[1]
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
res = pickle.load(open(f"{D}/claude_200.pkl", "rb"))
ox = [r for r in res if r["cause"] == "oxygen" and r["post"]["d"] >= 1]
kinds = Counter(); harmless_only = 0; n = 0
def classify(g, row, c):
    enemy = g[row, c, 2] > 0
    tl = c - 1 >= 0 and g[row, c - 1, 4] > 0; tr = c + 1 <= 9 and g[row, c + 1, 4] > 0
    d = "R" if tl and not tr else "L" if tr and not tl else "?"
    return ("enemy" if enemy else "bullet"), d
for r in ox:
    info = T.run(net, r["seed"], keep_frames=True); fr = info["frames"]
    for f in fr:
        x = f.reshape(600); h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
        if h1[26] <= 0: continue
        row = [rr for rr in range(9) if f[rr, :, 0].any()][0]
        if row < 2 or h2[row - 1] > 0 or h1[17 + row - 2] <= 0: continue
        n += 1; above = row - 1; harmless = True
        for c in range(6, 10):
            if f[above, c, 1] > 0:
                k, d = classify(f, above, c); kinds[(k, c, d)] += 1
                # harmless if it is moving left and already at col <= 7 (receding, ahead of a sub at col 8 facing left),
                # or moving right at col 9 (about to leave)
                if not ((d == "L" and c <= 7) or (d == "R" and c == 9)): harmless = False
        harmless_only += harmless
print("veto steps:", n, " steps where every danger cell in cols 6-9 of the row above was moving away from col 8:", harmless_only)
print("danger cells by (kind, col, direction):")
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]): print("  ", k, v)
