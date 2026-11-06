import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/"
net=wsp.load_npz(A+"net.npz"); W1=net["W1"]
def F(u):
    m=u%20; return m if m<10 else 19-m
def S(r): return r+1 if r>=4 else 9-r
names=["D+","D-","U+","U-"]
for t in range(4):
    u=2*t
    ball=W1[3::6,u].reshape(10,10)/10.0
    pad=W1[540:600:6,u]/10.0
    pad2=-W1[540:600:6,u+1]/10.0; ball2=-W1[3::6,u+1].reshape(10,10)/10.0
    dx=+1 if t in (0,2) else -1
    exp=np.zeros((10,10))
    for r in range(10):
        for c in range(10):
            k=(8-r) if t<2 else S(r)
            if t<2 and r==9: k=0
            exp[r,c]=F(c+dx*k)
    diff=[(r,c,ball[r,c],exp[r,c]) for r in range(10) for c in range(10) if ball[r,c]!=exp[r,c]]
    print(names[t],"paddle wts ok:",np.allclose(pad,-np.arange(10)),"pair identical:",np.allclose(ball,ball2) and np.allclose(pad,pad2),
          "mismatches vs formula (rows 0-8):",[d for d in diff if d[0]<9], "row9:", [d for d in diff if d[0]==9][:3])
    # other channels nonzero?
    other=[c for c in range(6) if c not in (0,3) and np.any(W1[c::6,u]!=0)]
    print("   other channels:",other, " b1:",net["b1"][u],net["b1"][u+1])
# X and V units
X=W1[:,8].reshape(10,10,6); V=W1[:,9].reshape(10,10,6)
print("X ball wt by col (rows equal?)", X[0,:,3], all(np.allclose(X[r,:,3],X[0,:,3]) for r in range(10)))
print("X trail wt by col", X[0,:,4], all(np.allclose(X[r,:,4],X[0,:,4]) for r in range(10)))
print("V ball wt by row", V[:,0,3], all(np.allclose(V[:,c,3],V[:,0,3]) for c in range(10)))
print("V trail wt by row", V[:,0,4], all(np.allclose(V[:,c,4],V[:,0,4]) for c in range(10)))
