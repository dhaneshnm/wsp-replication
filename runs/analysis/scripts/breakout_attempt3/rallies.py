import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Real-play instrumentation: split each episode into rallies (paddle bounce -> next landing), measure
# slack, per-step waste and its cause (policy / sticky / sampling), direction-classification errors,
# and a greedy no-sticky counterfactual replay of every missed rally.
from common import *
from play_log import run_episode
import json
from concurrent.futures import ProcessPoolExecutor

def obs_from(by, bx, ly, lx, pos, bricks=None):
    x = np.zeros(600, np.float32)
    x[(by*10+bx)*6+3] = 1; x[(ly*10+lx)*6+4] = 1; x[(90+pos)*6+0] = 1
    if bricks is not None:
        x[2::6] = bricks.reshape(-1)
    return x

def eff_of(a):
    return {1: "L", 3: "R"}.get(a, "S")
def modal_eff(r):
    pS = 1 - r["pL"] - r["pR"]
    return max([("L", r["pL"]), ("R", r["pR"]), ("S", pS)], key=lambda t: t[1])[0]

def analyse(args):
    path, seeds = args
    hv = (8, 9) if path == CLAUDE else (4, 5)
    net = wsp.load_npz(path)
    uses_bricks = bool(np.abs(net["W1"][2::6]).sum() > 0)
    out = []
    for s in seeds:
        ep = run_episode(net, s, hv=hv)
        log = ep["log"]
        # rally boundaries: frame after a catch
        starts = [0] + [i+1 for i, r in enumerate(log) if r["by"] == 8 and r["d"] in (2, 3) and not r["done"]]
        rallies = []
        for j, st in enumerate(starts):
            if st >= len(log): continue
            en = starts[j+1]-1 if j+1 < len(starts) else len(log)-1
            seg = log[st:en+1]
            last = seg[-1]
            missed = bool(last["done"]) and last["by"] == 8
            if not (last["by"] == 8 and last["d"] in (2, 3)):
                continue  # truncated by step cap
            x8, nx8 = last["bx"], last["nx8"]
            dist = lambda p: min(abs(p - x8), abs(p - nx8))
            N = len(seg)
            d0 = dist(seg[0]["pos"])
            waste = {"policy": 0, "sticky": 0, "sampling": 0}
            dirwrong = 0
            for r in seg:
                db, da = dist(r["pos"]), dist(r["pos_after"])
                e = da - max(db - 1, 0)
                tdx, tdy = DXY[r["d"]]
                if np.sign(r["H"]) != tdx or np.sign(r["V"]) != tdy: dirwrong += 1
                if e > 0:
                    if r["eff"] != r["a"]: waste["sticky"] += e
                    elif eff_of(r["a"]) != modal_eff(r): waste["sampling"] += e
                    else: waste["policy"] += e
            # first frame of the rally where the ball truly moves down for the final descent
            fd = next(i for i in range(N) if all(seg[k]["d"] in (2, 3) for k in range(i, N)))
            rec = dict(seed=s, N=N, d0=d0, slack0=N - d0, missed=missed, waste=waste, dirwrong=dirwrong,
                       desc_len=N - fd, desc_dist=dist(seg[fd]["pos"]), desc_slack=(N - fd) - dist(seg[fd]["pos"]),
                       desc_row=seg[fd]["by"], x8=x8, bricks=last["bricks"])
            if missed:
                # greedy, no-sticky counterfactual from rally start: ball path is paddle-independent
                pos = seg[0]["pos"]
                for r in seg:
                    _, _, z = fwd(net, obs_from(r["by"], r["bx"], r["ly"], r["lx"], pos))
                    g = int(np.argmax(z))
                    if g == 1: pos = max(0, pos-1)
                    elif g == 3: pos = min(9, pos+1)
                rec["greedy_catch"] = pos in (x8, nx8) if not uses_bricks else None
                rec["final_dist"] = dist(last["pos_after"])
                rec["path"] = [(r["by"], r["bx"], r["ly"], r["lx"], r["d"], r["pos"], r["a"], r["eff"], round(r["H"],2), round(r["V"],2), round(r["pL"],3), round(r["pR"],3)) for r in seg]
                rec["desc_first"] = dict(row=seg[fd]["by"], col=seg[fd]["bx"], trail=(seg[fd]["ly"], seg[fd]["lx"]), pos=seg[fd]["pos"])
            rallies.append(rec)
        out.append(dict(seed=s, score=ep["score"], steps=ep["steps"], done=ep["done"], rallies=rallies,
                        dirwrong_frames=sum(1 for r in log if np.sign(r["H"]) != DXY[r["d"]][0] or np.sign(r["V"]) != DXY[r["d"]][1]),
                        sticky_changed=sum(1 for r in log if r["eff"] != r["a"]), frames=len(log)))
    return out

if __name__ == "__main__":
    which = sys.argv[1]; n = int(sys.argv[2])
    path = CLAUDE if which == "claude" else ASTRA
    seeds = list(range(n)); W = 4
    with ProcessPoolExecutor(W) as ex:
        res = [e for part in ex.map(analyse, [(path, seeds[i::W]) for i in range(W)]) for e in part]
    json.dump(res, open(f"rallies_{which}.json", "w"))
    sc = np.array([e["score"] for e in res]); ln = np.array([e["steps"] for e in res])
    print(which, "episodes", len(res), "mean score", sc.mean(), "se", sc.std(ddof=1)/np.sqrt(len(sc)), "mean len", ln.mean(),
          "hit cap", int((ln >= 10000).sum()), "terminal", sum(e["done"] for e in res))
