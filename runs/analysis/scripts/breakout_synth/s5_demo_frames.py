import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
a2 = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz")
A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
np.set_printoptions(precision=3, suppress=True, linewidth=150)
def obs(ball, trail, pad):
    o = np.zeros((10, 10, 6), np.float32); o[9, pad, 0] = 1; o[1:4, :, 2] = 1
    o[ball[0], ball[1], 3] = 1; o[trail[0], trail[1], 4] = 1; return o.reshape(600)
def show(tag, net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"]); z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    print(f"  {tag}: h1[0:10]={h1[:10]} h2[0:8]={h2[:8]} logits={z} P(L,R,stay)=({p[1]:.4f},{p[3]:.4f},{p[[0,2,4,5]].sum():.4f})")
for pad in (4, 5):
    print(f"ball (7,3) from (6,2) descending right; x8=4, second catch cell 5; paddle {pad}")
    x = obs((7, 3), (6, 2), pad); show("attempt2", a2, x); show("astra   ", A, x)
# brick channel sensitivity: same frame with all bricks removed
x1 = obs((5, 3), (4, 2), 0); x2 = x1.copy().reshape(10, 10, 6); x2[..., 2] = 0
print("attempt2 max|logit change| when bricks removed:", float(np.abs(wsp.logits(a2, x1) - wsp.logits(a2, x2.reshape(600))).max()))
