"""Claim 6: decode Astra's lookup tables from hand.npz and compare with Claude's."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
C = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz")


def fold(u):
    m = u % 20
    return 19 - m if m >= 10 else m


print("Astra b1[0:4]", A["b1"][:4], "paddle w unit0", np.round(A["W1"][540:600:6, 0], 3))
print("Astra extra row-9 ball weights unit0 (fallback):", np.round(A["W1"][543:600:6, 0] / 0.02, 3))
# Astra: unit0 DR, unit1 DL, unit2 UR, unit3 UL ; Claude: R units 0 (DR), 2 (DL), 4 (UR), 6 (UL), weights 5*L
pairs = {"DR": (0, 0, +1), "DL": (1, 2, -1), "UR": (2, 4, +1), "UL": (3, 6, -1)}
for name, (ua, uc, dx) in pairs.items():
    print("==", name)
    for y in range(9):
        ta = A["W1"][(y * 10 + np.arange(10)) * 6 + 3, ua] / 0.02
        tc = C["W1"][(y * 10 + np.arange(10)) * 6 + 3, uc] / 5
        same = np.allclose(ta, tc)
        extra = ""
        if name in ("DR", "DL"):
            u8 = np.arange(10) + dx * (8 - y)
            mid = np.array([(fold(u) + fold(u + dx)) / 2 for u in u8])
            extra = "midpoint-of-catch-cells: %s" % np.allclose(ta, mid)
        else:
            Ts = [T for T in range(0, 25) if np.allclose(ta, [fold(x + dx * T) for x in range(10)])]
            extra = "Astra T fits: %s" % Ts
        print(" row", y, "Astra==Claude:", same, extra, "Astra:", np.round(ta, 2).tolist() if not same else "")
