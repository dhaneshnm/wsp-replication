"""Claim 7: my own implementation of the two 'missing features' as edits to copies of Claude's net.
Layer-2 unit (r, k) index = 3*(r-1)+k, k: 0 stay, 1 up, 2 down. D_r = unit r-1, G_r = unit 16+r-1.
Feature 'danger2': up unit of row r also reads D_{r-2}; down unit reads D_{r+2} (only if that row exists).
Feature 'treas2': up unit of row r also reads -G_{r-2}; down reads -G_{r+2}.
comp=True adds a b2 offset so that an EMPTY row r+-2 leaves the unit unchanged (D_empty=tanh(-1.2), G_empty=tanh(-1)).
Scored with wsp.evaluate, seeds 0-199, 4 workers."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy
import numpy as np
import wsp

CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz"
D_EMPTY = np.tanh(-1.2)
G_EMPTY = np.tanh(-1.0)


def edit(net, wd=0.0, wg=0.0, comp=True):
    n = copy.deepcopy(net)
    for r in range(1, 9):
        for k, r2 in ((1, r - 2), (2, r + 2)):
            if not (1 <= r2 <= 8):
                continue
            u = 3 * (r - 1) + k
            if wd:
                n["W2"][r2 - 1, u] += wd
                if comp:
                    n["b2"][u] -= wd * D_EMPTY
            if wg:
                n["W2"][16 + r2 - 1, u] += -wg
                if comp:
                    n["b2"][u] -= -wg * G_EMPTY
    return n


if __name__ == "__main__":
    base = wsp.load_npz(CLAUDE)
    cfgs = [c for c in sys.argv[1:] if not c.startswith("seed=")]
    bs = int(([c for c in sys.argv[1:] if c.startswith("seed=")] or ["seed=0"])[0][5:])
    print("base_seed", bs, "episodes 200", flush=True)
    table = {
        "base": dict(),
        "danger2_0.6": dict(wd=0.6), "treas2_0.3": dict(wg=0.3), "both_0.6_0.3": dict(wd=0.6, wg=0.3),
        "danger2_0.3": dict(wd=0.3), "treas2_0.15": dict(wg=0.15), "both_0.3_0.15": dict(wd=0.3, wg=0.15),
        "both_0.6_0.3_nocomp": dict(wd=0.6, wg=0.3, comp=False),
        "danger2_0.6_nocomp": dict(wd=0.6, comp=False), "treas2_0.3_nocomp": dict(wg=0.3, comp=False),
        "danger2_1.2": dict(wd=1.2), "danger2_2.4": dict(wd=2.4), "both_1.2_0.3": dict(wd=1.2, wg=0.3),
        "treas2_0.6": dict(wg=0.6), "both_1.2_0.6": dict(wd=1.2, wg=0.6),
        "astra": "astra",
    }
    for c in cfgs:
        if table[c] == "astra":
            net = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")
        else:
            net = edit(base, **table[c])
        r = wsp.evaluate(net, "asterix", episodes=200, base_seed=bs, workers=4)
        print(f"{c:22s} mean {r['mean']:.2f} se {r['se']:.2f} len {r['mean_length']:.1f}", flush=True)
