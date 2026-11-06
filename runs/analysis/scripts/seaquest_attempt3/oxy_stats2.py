import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, sys.argv[1])
import pickle, numpy as np, wsp, trace as T
from collections import Counter
D = sys.argv[1]
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
res = pickle.load(open(f"{D}/claude_200.pkl", "rb"))
ox = [r for r in res if r["cause"] == "oxygen"]
tot = Counter(); onset_rows = []; wins = []; per_ep = []
for r in ox:
    info = T.run(net, r["seed"], keep_frames=True); fr = info["frames"]
    H = []
    for f in fr:
        x = f.reshape(600); h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
        H.append((h1, h2, [rr for rr in range(9) if f[rr, :, 0].any()][0]))
    # final contiguous window with SURF on
    t = len(H) - 1
    if H[t][0][26] <= 0:
        per_ep.append((r["seed"], r["post"]["d"], "SURF off at death")); continue
    while t > 0 and H[t - 1][0][26] > 0: t -= 1
    onset_rows.append(H[t][2]); wins.append(len(H) - t)
    c = Counter()
    for h1, h2, row in H[t:]:
        up_on = h2[row - 1] > 0 if row >= 1 else False
        dn_on = h2[8 + row] > 0 if row <= 7 else False
        if row == 0: c["at row 0"] += 1
        elif up_on and not dn_on: c["up chosen"] += 1
        elif up_on and dn_on: c["up/down tie"] += 1
        elif dn_on: c["pushed down"] += 1
        elif row >= 2 and h1[17 + row - 2] > 0: c["up vetoed by U(row above)"] += 1
        elif row == 1 and h1[25] < 0: c["row1 blocked (HD off)"] += 1
        else: c["other"] += 1
    tot.update(c); per_ep.append((r["seed"], r["post"]["d"], H[t][2], len(H) - t, dict(c)))
print("aggregate over final SURF window:", dict(tot))
print("SURF onset row:", dict(sorted(Counter(onset_rows).items())), " window length mean", np.mean(wins), "min", min(wins), "max", max(wins))
for p in per_ep: print(" ", p)
