"""Claim 1, part B: on real visited states, compare layer-1 units 0-7 (D_r) and 16-23 (G_r) with the
reply's table / description, using the game's entity list (not the observation) to label each row."""
import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1/indep_verify")
from collections import defaultdict
import numpy as np
import common, wsp


def table_S(ent):
    """Reply's table: score S for an entity in a row (None = empty row)."""
    if ent is None:
        return 0.0, "empty"
    x, y, right, gold = ent
    if gold:
        return None, "treasure"
    approaching = (right and x < 5) or ((not right) and x > 5)
    if x == 5:
        return 4.0, "enemy c5"
    if (x == 4 and right) or (x == 6 and not right):
        return 4.0, "enemy c4/c6 approaching"
    if x in (3, 7) and approaching:
        return 2.0, "enemy c3/c7 approaching"
    if x in (2, 8):
        return 1.0, "enemy c2/c8"
    if x in (3, 4, 6, 7) and not approaching:
        return 0.0, "enemy moving away"
    return 0.0, f"enemy c{x} (not in table)"


def gold_cat(ent):
    if ent is None:
        return "empty"
    x, y, right, gold = ent
    if not gold:
        return "enemy row"
    if x == 5:
        return "gold c5"
    approaching = (right and x < 5) or ((not right) and x > 5)
    if x in (4, 6):
        return "gold c4/c6 " + ("approaching" if approaching else "away")
    if x in (3, 7):
        return "gold c3/c7 " + ("approaching" if approaching else "away")
    return f"gold other col"


def check(x, a1, E):
    out = []
    ents = {e[1]: e for e in E.entities if e is not None}
    for r in range(1, 9):
        e = ents.get(r)
        S, cat = table_S(e)
        D = float(a1[r - 1])
        G = float(a1[16 + r - 1])
        out.append((cat, S, D, gold_cat(e), G))
    return out


if __name__ == "__main__":
    net = wsp.load_npz(common.CLAUDE)
    n_states = 0
    derr = defaultdict(float)
    dcount = defaultdict(int)
    treasure_Dmax = -9.0
    gstats = defaultdict(list)
    mism = 0
    for seed in range(20):
        res = common.run(net, seed, check=check)
        mism += res["mismatch"]
        for rows in res["chk"]:
            n_states += 1
            for cat, S, D, gc, G in rows:
                if S is None:
                    treasure_Dmax = max(treasure_Dmax, D)
                else:
                    err = abs(D - np.tanh(0.6 * S - 1.2))
                    derr[cat] = max(derr[cat], err)
                    dcount[cat] += 1
                gstats[gc].append(G)
    print("states:", n_states, "episodes: 20 (seeds 0-19)", "collision-model mismatches:", mism)
    print("D_r vs tanh(0.6*S_table - 1.2), by table row (count, max abs err):")
    for k in sorted(dcount):
        print(f"  {k:28s} n={dcount[k]:7d} maxerr={derr[k]:.3e}")
    print(f"  treasure rows: max D = {treasure_Dmax:.4f} (table: S<=0 -> D<= {np.tanh(-1.2):.4f})")
    print("G_r by situation (n, min, mean, max):")
    for k in sorted(gstats):
        v = np.array(gstats[k])
        print(f"  {k:28s} n={len(v):7d} min={v.min():+.4f} mean={v.mean():+.4f} max={v.max():+.4f}")
