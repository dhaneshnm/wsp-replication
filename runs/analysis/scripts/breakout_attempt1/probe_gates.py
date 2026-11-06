import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
N = nets()
cases = [
 ("start, ball (3,0) trail same, true down-right", (3,0), (3,0), (1,1)),
 ("start, ball (3,9) trail same, true down-left", (3,9), (3,9), (-1,1)),
 ("brick hit from below at row 4 (moved (4,3)->(4,4)), true down-right", (4,4), (4,3), (1,1)),
 ("brick hit from ABOVE at row 0 (moved (0,3)->(0,4)), true up-right", (0,4), (0,3), (1,-1)),
 ("brick hit from ABOVE at row 2 in cleared hole, true up-right", (2,4), (2,3), (1,-1)),
 ("ceiling bounce (0,3)->(0,4), true down-right", (0,4), (0,3), (1,1)),
 ("paddle reverse catch: (8,4)->(8,5) true up-left", (8,5), (8,4), (-1,-1)),
 ("paddle same-dir catch: (8,4)->(8,5) true up-right", (8,5), (8,4), (1,-1)),
 ("left wall clip (5,0)->(6,0), true down-right", (6,0), (5,0), (1,1)),
 ("left wall arrive (5,1)->(6,0), true down-left (clip next)", (6,0), (5,1), (-1,1)),
 ("right wall clip ascending (5,9)->(4,9), true up-left", (4,9), (5,9), (-1,-1)),
 ("corner (1,1)->(0,0) ascending, true up-left", (0,0), (1,1), (-1,-1)),
 ("corner after double flip (0,0)->(0,0)?? trail (0,0) ball (0,0) true down-right", (0,0), (0,0), (1,1)),
]
for name, net in N.items():
    print("=====", name)
    for desc, ball, trail, (vx, vy) in cases:
        h1, h2, z, p = forward(net, make_obs(ball, trail, 4))
        gH, gV = h1[4], h1[5]
        ok = (np.sign(gH) == vx) and (np.sign(gV) == vy)
        print(f"  gH={gH:+.3f} gV={gV:+.3f} {'OK ' if ok else 'ERR'} {desc}")
    # no-op margin when on target vs at row 8
    x = make_obs((8, 2), (7, 3), 1)
    h1, h2, z, p = forward(net, x)
    print("  ball (8,2) desc-left, paddle 1 (on Claude target): logits", np.round(z, 2), "probs", np.round(p, 4))
    x = make_obs((8, 2), (7, 3), 2)
    h1, h2, z, p = forward(net, x)
    print("  ball (8,2) desc-left, paddle 2: logits", np.round(z, 2), "probs", np.round(p, 4))
    x = make_obs((5, 2), (4, 3), 7)
    h1, h2, z, p = forward(net, x)
    print("  ball (5,2) desc-left, paddle 7 (far right of target): logits", np.round(z, 2), "probs", np.round(p, 4))
