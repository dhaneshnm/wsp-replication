import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/verify")
from vcommon import *

def tolerant(net, rows):
    """R units aim at min(catch cols), L units at max(catch cols) for descent rows in `rows`."""
    out = {k: v.copy() for k, v in net.items()}
    for (ru, lu, dx) in ((0, 1, 1), (2, 3, -1)):
        for r in rows:
            for c in range(10):
                b8 = fold(c + dx * (8 - r)); nx = fold(c + dx * (9 - r))
                i = (r * 10 + c) * 6 + 3
                out["W1"][i, ru] = 10 * min(b8, nx)
                out["W1"][i, lu] = -10 * max(b8, nx)
    return out

def row1(net):
    out = {k: v.copy() for k, v in net.items()}
    for (ru, lu, dx) in ((4, 5, 1), (6, 7, -1)):
        for c in range(10):
            T = fold(c + dx * 10); i = (10 + c) * 6 + 3
            out["W1"][i, ru] = 10 * T; out["W1"][i, lu] = -10 * T
    return out

if __name__ == "__main__":
    base = wsp.load_npz(CLAUDE)
    for name, v in (("v678", tolerant(base, [6, 7, 8])), ("v8", tolerant(base, [8])), ("vrow1", row1(base))):
        ch = sum(int((v[k] != base[k]).sum()) for k in base)
        print(name, "changed weights:", ch)
        wsp.save_npz(v, f"my_{name}.npz")
