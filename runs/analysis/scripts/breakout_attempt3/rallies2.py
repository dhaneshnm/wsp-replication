import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Extra per-rally features: turn row, paddle error at turn, catch-set occupancy during the final descent,
# last-frame exposure, and direction-classification error types.
from common import *
from play_log import run_episode
import json, collections
from concurrent.futures import ProcessPoolExecutor

def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m
T = [9, 10, 9, 8, 7, 8, 9, 10, 11]

def analyse(args):
    path, seeds = args
    net = wsp.load_npz(path); hv = (8, 9) if path == CLAUDE else (4, 5)
    out = []
    for s in seeds:
        ep = run_episode(net, s, hv=hv); log = ep["log"]
        # direction error types
        derr = collections.Counter()
        for i, r in enumerate(log):
            tdx, tdy = DXY[r["d"]]
            if np.sign(r["H"]) != tdx or np.sign(r["V"]) != tdy:
                kind = []
                if np.sign(r["H"]) != tdx: kind.append("H")
                if np.sign(r["V"]) != tdy: kind.append("V")
                flat = r["by"] == r["ly"]; same = r["bx"] == r["lx"]
                ctx = "row8-paddle-bounce" if (r["by"] == 8 and flat) else ("flat-row%d" % r["by"] if flat else ("stall-col%d" % r["bx"] if same else "diag-row%d" % r["by"]))
                derr["+".join(kind) + ":" + ctx] += 1
        starts = [0] + [i+1 for i, r in enumerate(log) if r["by"] == 8 and r["d"] in (2, 3) and not r["done"]]
        rallies = []
        for j, st in enumerate(starts):
            if st >= len(log): continue
            en = starts[j+1]-1 if j+1 < len(starts) else len(log)-1
            seg = log[st:en+1]; last = seg[-1]
            if not (last["by"] == 8 and last["d"] in (2, 3)): continue
            missed = bool(last["done"])
            x8, nx8 = last["bx"], last["nx8"]; N = len(seg)
            fd = next(i for i in range(N) if all(seg[k]["d"] in (2, 3) for k in range(i, N)))
            inset = [r["pos"] in (x8, nx8) for r in seg[fd:]]
            rec = dict(missed=missed, turn_row=seg[fd]["by"], N=N, desc_len=N-fd,
                       pos_err=seg[fd]["pos"] - x8, dist=min(abs(seg[fd]["pos"]-x8), abs(seg[fd]["pos"]-nx8)),
                       ever_in_set=any(inset), in_set_before_last=last["pos"] in (x8, nx8),
                       last_sticky=last["eff"] != last["a"], last_eff=last["eff"], last_a=last["a"],
                       moves_in_desc=sum(1 for r in seg[fd:] if r["eff"] in (1, 3) and r["pos_after"] != r["pos"]),
                       left_set_by_policy=sum(1 for r in seg[fd:] if r["pos"] in (x8, nx8) and r["pos_after"] not in (x8, nx8) and r["eff"] == r["a"]),
                       left_set_by_sticky=sum(1 for r in seg[fd:] if r["pos"] in (x8, nx8) and r["pos_after"] not in (x8, nx8) and r["eff"] != r["a"]),
                       x8_to_nx8=sum(1 for r in seg[fd:] if x8 != nx8 and r["pos"] == nx8 and r["pos_after"] == x8))
            if path == CLAUDE and fd > 0:
                u = seg[fd-1]  # last frame before the final descent: net is in its up-phase
                dxn = int(np.sign(u["H"])); dyn = int(np.sign(u["V"]))
                rec["up_target_err"] = (fold(u["bx"] + dxn*T[u["by"]]) - x8) if dyn < 0 else None
            rallies.append(rec)
        out.append(dict(seed=s, derr=dict(derr), rallies=rallies))
    return out

if __name__ == "__main__":
    which = sys.argv[1]; n = int(sys.argv[2]); path = CLAUDE if which == "claude" else ASTRA
    seeds = list(range(n)); W = 4
    with ProcessPoolExecutor(W) as ex:
        res = [e for part in ex.map(analyse, [(path, seeds[i::W]) for i in range(W)]) for e in part]
    json.dump(res, open(f"rallies2_{which}.json", "w"))
    R = [r for e in res for r in e["rallies"]]; M = [r for r in R if r["missed"]]
    print(f"===== {which}: rallies {len(R)} misses {len(M)}")
    de = collections.Counter()
    for e in res: de.update(e["derr"])
    print("direction-classification errors by context:", de.most_common(12))
    tr = collections.Counter(r["turn_row"] for r in R); trm = collections.Counter(r["turn_row"] for r in M)
    print("turn row of final descent (misses/rallies):", {k: f"{trm[k]}/{tr[k]}" for k in sorted(tr)})
    pe = collections.Counter(r["pos_err"] for r in R)
    print("paddle - x8 at first descent frame:", sorted(pe.items()))
    if which == "claude":
        ue = collections.Counter(r["up_target_err"] for r in R if r.get("up_target_err") is not None)
        print("Claude up-phase table target - true x8 (last up frame):", sorted(ue.items()))
        for row in sorted(tr):
            ue_r = collections.Counter(r["up_target_err"] for r in R if r.get("up_target_err") is not None and r["turn_row"] == row)
            print(f"   turn row {row}: up-target error {sorted(ue_r.items())}")
    for nm, sel in [("all", R), ("missed", M)]:
        n_ = len(sel)
        print(f"[{nm}] n={n_}: ever in catch set during descent {sum(r['ever_in_set'] for r in sel)}; in set before last action {sum(r['in_set_before_last'] for r in sel)};"
              f" left set by policy {sum(r['left_set_by_policy']>0 for r in sel)}, by sticky {sum(r['left_set_by_sticky']>0 for r in sel)};"
              f" moved nx8->x8 {sum(r['x8_to_nx8']>0 for r in sel)}; mean moves in descent {np.mean([r['moves_in_desc'] for r in sel]):.2f}")
    lastk = collections.Counter((r["in_set_before_last"], r["last_sticky"]) for r in M)
    print("misses by (paddle in catch set before last action, last action was sticky):", dict(lastk))
