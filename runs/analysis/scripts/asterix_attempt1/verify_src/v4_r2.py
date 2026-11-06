import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
C = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")
def obs(py, ents):
    o = np.zeros((10, 10, 6), np.float32); o[py, 5, 0] = 1
    for (r, c, k, d) in ents:
        o[r, c, 1 if k == "e" else 2] = 1
        b = c - 1 if d > 0 else c + 1
        if 0 <= b <= 9: o[r, b, 4] = 1
    return o.reshape(600)
def P(net, x):
    z = wsp.logits(net, x); p = np.exp(z - z.max()); return (p / p.sum())
np.set_printoptions(precision=4, suppress=True)
for py in range(3, 9):
    e = P(C, obs(py, [])); 
    for c, d in [(5, +1), (4, +1), (6, -1)]:
        x = obs(py, [(py - 2, c, "e", d)])
        pc, pa = P(C, x), P(A, x)
        print(f"player row {py}, enemy row {py-2} c{c}{'R' if d>0 else 'L'}: Claude p(up)={pc[2]:.4f} (empty {e[2]:.4f})  Astra p(up)={pa[2]:.4f}")
for py in range(1, 7):
    e = P(C, obs(py, []))
    x = obs(py, [(py + 2, 5, "e", +1)])
    print(f"player row {py}, enemy row {py+2} c5: Claude p(down)={P(C,x)[4]:.4f} (empty {e[4]:.4f})  Astra p(down)={P(A,x)[4]:.4f}")
