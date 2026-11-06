import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, sys.argv[1])
import pickle, numpy as np, wsp, trace as T
from collections import Counter
D = sys.argv[1]
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz")
res = pickle.load(open(f"{D}/claude_200.pkl", "rb"))
ox = [r for r in res if r["cause"] == "oxygen"]
print("oxygen deaths:", len(ox), " divers aboard:", dict(Counter(r["post"]["d"] for r in ox)))
tot = Counter(); rows_at_onset = []; surf_steps = []
for r in ox:
    info = T.run(net, r["seed"], keep_frames=True)
    fr = info["frames"]
    on = None
    c = Counter()
    for t, f in enumerate(fr):
        x = f.reshape(600)
        h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
        if h1[26] > 0:
            if on is None: on = t; rows_at_onset.append([rr for rr in range(9) if f[rr, :, 0].any()][0])
            row = [rr for rr in range(9) if f[rr, :, 0].any()][0]
            up_on = h2[row - 1] > 0 if 1 <= row <= 8 else False
            dn_on = h2[8 + row] > 0 if row <= 7 else False
            if row == 0: c["at row 0"] += 1
            elif up_on and not dn_on: c["up chosen"] += 1
            elif up_on and dn_on: c["up/down tie (own-row danger)"] += 1
            elif dn_on: c["pushed down (own-row danger, row above unsafe)"] += 1
            elif row >= 2 and h1[17 + row - 2] > 0: c["up vetoed: danger cols 6-9 in row above"] += 1
            elif row == 1 and h1[25] < 0: c["row1 blocked: HD off"] += 1
            else: c["other"] += 1
        elif on is not None:
            c["SURF went off again"] += 1
    if on is None: c["SURF never on"] += 1
    else: surf_steps.append(len(fr) - on)
    tot.update(c)
print("SURF-on steps classified (all oxygen deaths):", dict(tot))
print("row at SURF onset:", dict(Counter(rows_at_onset)), " mean SURF-on steps before death:", np.mean(surf_steps))
