import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import copy, json
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor

def run(args):
    which, seed = args
    net = CL if which == "claude" else AS
    env = wsp._make_env("seaquest", seed)
    g = env.env
    ob = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    hist = deque(maxlen=12)
    score = 0
    for t in range(wsp.MAX_STEPS):
        x = ob()
        z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        pre = dict(t=t, x=g.sub_x, y=g.sub_y, orr=g.sub_or, oxy=g.oxygen, dc=g.diver_count, shot=g.shot_timer,
                   fish=copy.deepcopy(g.e_fish), subs=copy.deepcopy(g.e_subs), bul=copy.deepcopy(g.e_bullets),
                   fb=copy.deepcopy(g.f_bullets), a=a, p=p.round(2).tolist(), surf_req=bool(g.oxygen < 60 and g.diver_count >= 1))
        nfb = len(g.f_bullets)
        r, done = env.act(a)
        score += r
        pre["ea"] = env.last_action
        hist.append(pre)
        if done:
            sx, sy = g.sub_x, g.sub_y
            d = dict(seed=seed, t=t, score=score, row=sy, prev_row=pre["y"], dc=pre["dc"], oxy=pre["oxy"], ea=ACT[pre["ea"]],
                     sampled=ACT[a], sticky=(pre["ea"] != a), surf_req=pre["surf_req"])
            if sy == 0 and pre["y"] > 0 and pre["dc"] == 0:
                d["kind"] = "surfaced_no_diver"
            else:
                killer = None
                for kind, lst in (("fish", pre["fish"]), ("enemy_sub", pre["subs"])):
                    for e in lst:
                        if e[1] != sy: continue
                        nx = e[0] + (1 if e[2] else -1)
                        if e[0] == sx or (e[3] == 0 and nx == sx): killer = (kind, e[0], e[2])
                if killer is None:
                    for b in pre["bul"]:
                        nb = b[0] + (1 if b[2] else -1)
                        if b[1] == sy and (b[0] == sx or nb == sx): killer = ("bullet", b[0], b[2])
                if killer is None:
                    d["kind"] = "oxygen" if pre["oxy"] <= 0 else "unknown"
                else:
                    kind, kx, kdir = killer
                    d["kind"] = kind
                    d["killer_pre_col"] = kx
                    # side relative to pre-step front, facing before step
                    side = "right" if kx > pre["x"] else ("left" if kx < pre["x"] else "same")
                    d["killer_side"] = side
                    d["pre_facing"] = "R" if pre["orr"] else "L"
                    d["post_facing"] = "R" if g.sub_or else "L"
                    d["moved_vert"] = sy != pre["y"]
                    d["moved_col"] = sx != pre["x"]
                    # how many of the recorded previous steps was the sub in this row with killer-kind entity present
                    same_row_steps = sum(1 for h in hist if h["y"] == sy)
                    d["steps_in_row_before"] = same_row_steps
                    d["facing_killer_pre"] = (side == "right" and pre["orr"]) or (side == "left" and not pre["orr"])
            d["last"] = [(h["t"], h["y"], h["x"], "R" if h["orr"] else "L", ACT[h["ea"]], h["shot"],
                          [(f[0], f[1]) for f in h["fish"] if abs(f[1]-h["y"])<=1],
                          [(s[0], s[1]) for s in h["subs"] if abs(s[1]-h["y"])<=1],
                          [(b[0], b[1]) for b in h["bul"] if abs(b[1]-h["y"])<=1],
                          [(b[0], b[1]) for b in h["fb"] if b[1]==h["y"]]) for h in list(hist)[-6:]]
            return d
    return dict(seed=seed, kind="cap", score=score)

if __name__ == "__main__":
    which = sys.argv[1]; n = int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(which, s) for s in range(n)], chunksize=10))
    json.dump(res, open(f"deaths_{which}_{n}.json", "w"))
    print("mean score", np.mean([r["score"] for r in res]))
    print("kind:", Counter(r["kind"] for r in res).most_common())
    col = [r for r in res if r["kind"] in ("fish", "enemy_sub", "bullet")]
    print("collisions:", len(col))
    print(" moved vertically into it:", sum(r["moved_vert"] for r in col), " of which surfacing-request on:", sum(r["moved_vert"] and r["surf_req"] for r in col))
    sr = [r for r in col if not r["moved_vert"]]
    print(" same-row (no vertical move):", len(sr))
    print("   by kind:", Counter(r["kind"] for r in sr))
    print("   killer side vs pre facing: facing it", sum(r["facing_killer_pre"] for r in sr), " behind", sum(not r["facing_killer_pre"] for r in sr))
    print("   moved column this step:", sum(r["moved_col"] for r in sr), " executed action:", Counter(r["ea"] for r in sr))
    print("   death row:", Counter(r["row"] for r in sr))
    print("   killer pre-col rel front:", Counter(r["killer_pre_col"] - 0 for r in sr))
    print(" vertical-move deaths: executed:", Counter(r["ea"] for r in col if r["moved_vert"]), " sticky:", sum(r["sticky"] for r in col if r["moved_vert"]), " rows from->to:", Counter((r["prev_row"], r["row"]) for r in col if r["moved_vert"]).most_common(8))
    print(" all deaths with surf_req on:", sum(r.get("surf_req", False) for r in res))
