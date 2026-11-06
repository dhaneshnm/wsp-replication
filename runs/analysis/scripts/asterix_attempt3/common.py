import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt3/"
NET = wsp.load_npz(A+"net.npz")
AST = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")
ACT = ["noop","left","up","right","down","fire"]
def obs(prow, ents, pcol=5):
    """ents: list of (row, col, moving_right, is_gold, has_trail=True)"""
    o = np.zeros((10,10,6), np.float32)
    o[prow, pcol, 0] = 1
    for e in ents:
        r,c,right,gold = e[:4]; trail = e[4] if len(e)>4 else True
        o[r,c,2 if gold else 1] = 1
        b = c-1 if right else c+1
        if trail and 0<=b<=9: o[r,b,4] = 1
    return o.reshape(600)
def fwd(net, x):
    h1 = np.tanh(x@net["W1"]+net["b1"]); h2=np.tanh(h1@net["W2"]+net["b2"]); z=h2@net["W3"]+net["b3"]
    p=np.exp(z-z.max()); p/=p.sum(); return h1,h2,z,p
def fmtp(p): return " ".join(f"{ACT[i]}={p[i]:.3f}" for i in range(6) if p[i]>=0.001)
