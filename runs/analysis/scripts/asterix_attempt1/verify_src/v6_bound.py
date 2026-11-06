"""Upper bound on p(left)+p(right) for Claude's net over ANY input with the player in rows 1..8 (one P unit active).
Layer-1 D,G units lie in (-1,1); P_r = tanh(3) for the player row, tanh(-3) otherwise. Grid over D,G corners is exact
because each gated unit is monotone in its D and G inputs."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import itertools, numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
W2, b2, W3, b3 = net["W2"], net["b2"], net["W3"], net["b3"]
worst = 1e9
for r in range(8):
    # maximise every active unit (worst case for n,u,d logits since W3 weights are -25): D=+1, G=-1 everywhere
    h1 = np.zeros(32); h1[0:8] = 1.0; h1[16:24] = -1.0; h1[8:16] = np.tanh(-3); h1[8 + r] = np.tanh(3)
    h2 = np.tanh(h1 @ W2 + b2); z = h2 @ W3 + b3
    worst = min(worst, max(z[0], z[2], z[4]))
    print("player row", r + 1, "worst-case logits", np.round(z, 2))
print("lowest possible max(noop,up,down) logit:", round(worst, 2), " left/right logit fixed at", b3[1], b3[3])
print("upper bound p(left)+p(right) per step:", 2 * np.exp(-60 - worst))
