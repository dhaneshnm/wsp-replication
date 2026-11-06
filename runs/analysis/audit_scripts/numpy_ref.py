import numpy as np
W2 = np.zeros((32, 32), np.float32); W1 = np.zeros((600, 32), np.float32)
for desc, f in [("W2[0:2,0:3] = 3x2 list", lambda: W2.__setitem__((slice(0,2), slice(0,3)), np.asarray([[1,0],[-1,2],[0.5,0]], np.float32))),
                ("W1[0:6,0:4] = 4x6 list", lambda: W1.__setitem__((slice(0,6), slice(0,4)), np.asarray([[1]*6,[2]*6,[3]*6,[4]*6], np.float32))),
                ("W1[0:6,3]  = 2x3 list", lambda: W1.__setitem__((slice(0,6), 3), np.asarray([[1,0,-1],[0,2,0]], np.float32))),
                ("W2[0:2,0:3] = flat 6", lambda: W2.__setitem__((slice(0,2), slice(0,3)), np.asarray([1,-1,.5,0,2,0], np.float32)))]:
    try: f(); print("numpy:", desc, "-> accepted")
    except Exception as e: print("numpy:", desc, "->", type(e).__name__, e)
