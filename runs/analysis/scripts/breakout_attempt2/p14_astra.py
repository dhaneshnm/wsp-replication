import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2")
from common import *
from collections import Counter
na=wsp.load_npz(ASTRA); nc=wsp.load_npz(A)
W1=na["W1"]
print("Astra nonzero W1 cols:",np.nonzero(np.abs(W1).sum(0))[0], "b1 nz:",{int(i):float(na['b1'][i]) for i in np.nonzero(na['b1'])[0]})
print("W2 nz rows:",np.nonzero(np.abs(na['W2']).sum(1))[0],"b2:",na['b2'][:8],"W3 nz:",[(int(i),int(j),float(na['W3'][i,j])) for i,j in zip(*np.nonzero(na['W3']))],"b3:",na['b3'])
names=["D+ (unit0)","D- (unit1)","U+ (unit2)","U- (unit3)"]
for u in range(4):
    T=W1[3::6,u].reshape(10,10)/0.02
    print(names[u],"paddle wts/0.02:",(W1[540:600:6,u]/0.02).round(2).tolist())
    dx=1 if u in (0,2) else -1
    for r in range(10):
        k=(8-r) if u<2 else S(r)
        exp=[F(c+dx*k) for c in range(10)]
        print(f"   row {r}: astra T={np.round(T[r],2).tolist()}   claude-formula={exp}")
