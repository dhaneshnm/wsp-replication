# Claim 7/9: logits and probabilities at real on-target frames (argmax == no-op) for both nets
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import pickle
from collections import Counter
import numpy as np
import wsp

for name, pk, path in [
    ("claude", "claude_softmax_0.1.pkl", "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"),
    ("astra", "astra_softmax_0.1_40.pkl", "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"),
]:
    net = wsp.load_npz(path)
    res = pickle.load(open(pk, "rb"))
    zc = Counter(); n_on = 0; p0s = []; gaps = []
    for r in res:
        for i in np.nonzero(r["amax"] == 0)[0][::7]:  # subsample every 7th on-target frame
            x = np.zeros(600, np.float32)
            x[(r["by"][i] * 10 + r["bx"][i]) * 6 + 3] = 1; x[(90 + r["pos"][i]) * 6] = 1; x[(r["ly"][i] * 10 + r["lx"][i]) * 6 + 4] = 1
            z = (np.tanh(np.tanh(x @ net["W1"] + net["b1"]) @ net["W2"] + net["b2"]) @ net["W3"] + net["b3"]).astype(np.float64)
            p = np.exp(z - z.max()); p /= p.sum()
            zc[tuple(np.round(z, 2))] += 1; n_on += 1; p0s.append(p[0]); gaps.append(z[0] - max(z[1], z[3]))
    p0s = np.array(p0s); gaps = np.array(gaps)
    print(f"{name}: on-target frames sampled {n_on}; most common logits {zc.most_common(3)}")
    print(f"   p(noop) min {p0s.min():.6f} max {p0s.max():.15f}; 1-p(noop) min {1-p0s.max():.3e} max {1-p0s.min():.3e}; noop-minus-best-move gap min {gaps.min():.3f} max {gaps.max():.3f}")
