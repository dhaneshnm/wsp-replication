import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"

def idx(r, c, ch): return (r * 10 + c) * 6 + ch
if __name__ == "__main__":
    net = wsp.load_npz(CL)
    sharp = {k: v.copy() for k, v in net.items()}
    sharp["W3"] *= 5; sharp["b3"] *= 5   # same argmax everywhere, 5x larger logit gaps (on-target gap ~29)
    x = np.zeros(600, np.float32); x[idx(9, 1, 0)] = 1; x[idx(8, 2, 3)] = 1; x[idx(7, 3, 4)] = 1
    for n, m in [("orig", net), ("x5", sharp)]:
        z = wsp.logits(m, x); p = np.exp(z - z.max()); p /= p.sum()
        print(n, "on-target logits", np.round(z, 3), "p(no-op)", p[0])
    print("x5-sharpened output, harness eval 200 eps:", wsp.evaluate(sharp, "breakout", episodes=200, workers=4))
