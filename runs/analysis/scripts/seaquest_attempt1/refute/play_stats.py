import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import copy, json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

def run(args):
    which, seed = args
    net = CL if which == "claude" else AS
    env = wsp._make_env("seaquest", seed)
    g = env.env
    ob = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0
    st = dict(seed=seed, kills=0, surf_ok=0, surf6=0, pickups=0, rows=Counter(), acts=Counter(), exec_acts=Counter(),
              cause=None, steps=0, row1_steps=0, max_div=0, oxy_low_no_div=0, first_pickup=None)
    prev_dc = 0
    for t in range(wsp.MAX_STEPS):
        x = ob()
        z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        pre = dict(x=g.sub_x, y=g.sub_y, orr=g.sub_or, oxy=g.oxygen, dc=g.diver_count,
                   fish=copy.deepcopy(g.e_fish), subs=copy.deepcopy(g.e_subs), bul=copy.deepcopy(g.e_bullets),
                   surface=g.surface)
        st["rows"][g.sub_y] += 1
        st["acts"][a] += 1
        r, done = env.act(a)
        ea = env.last_action
        st["exec_acts"][ea] += 1
        score += r
        # events
        if g.sub_y == 0 and pre["y"] > 0 and not done:
            st["surf_ok"] += 1
            if pre["dc"] == 6: st["surf6"] += 1
        if g.diver_count > pre["dc"]:
            st["pickups"] += g.diver_count - pre["dc"]
            if st["first_pickup"] is None: st["first_pickup"] = t
        st["max_div"] = max(st["max_div"], g.diver_count)
        if done:
            sx, sy = g.sub_x, g.sub_y
            cause = None
            if sy == 0 and pre["y"] > 0 and pre["dc"] == 0:
                cause = "surfaced_no_diver"
            else:
                hit = None
                for f in g.e_fish:
                    if f[0] == sx and f[1] == sy: hit = ("fish", f[2])
                for s in g.e_subs:
                    if s[0] == sx and s[1] == sy: hit = ("enemy_sub", s[2])
                if hit is None:
                    for b in pre["bul"]:
                        nb = b[0] + (1 if b[2] else -1)
                        if b[1] == sy and (b[0] == sx or nb == sx): hit = ("bullet", b[2])
                if hit is not None:
                    kind, edir = hit
                    # edir True = moving right (came from the left)
                    facing_right = g.sub_or
                    from_front = (edir and not facing_right) or ((not edir) and facing_right)
                    mv = {2: "up", 4: "down", 1: "left", 3: "right"}.get(ea, "stay")
                    cause = f"{kind}|player_{'vert' if mv in ('up','down') else ('horiz' if mv in ('left','right') else 'stay')}|{'front' if from_front else 'behind'}"
                elif pre["oxy"] <= 0:
                    cause = "oxygen"
                else:
                    cause = "unknown"
            st["cause"] = cause
            st["death_row"] = sy
            st["death_dc"] = pre["dc"]
            st["death_oxy"] = pre["oxy"]
            st["steps"] = t + 1
            break
    else:
        st["steps"] = wsp.MAX_STEPS; st["cause"] = "cap"
    st["score"] = score
    st["rows"] = dict(st["rows"]); st["acts"] = dict(st["acts"]); st["exec_acts"] = dict(st["exec_acts"])
    return st

if __name__ == "__main__":
    which = sys.argv[1]; n = int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(which, s) for s in range(n)], chunksize=10))
    json.dump(res, open(f"stats_{which}_{n}.json", "w"))
    sc = np.array([r["score"] for r in res]); L = np.array([r["steps"] for r in res])
    print(which, "mean score", sc.mean(), "se", sc.std(ddof=1)/np.sqrt(n), "median", np.median(sc), "max", sc.max(), "mean len", L.mean())
    c = Counter(r["cause"] for r in res)
    print("causes:"); [print(f"  {k:40s} {v:4d} ({v/n:.1%})") for k, v in c.most_common()]
    c2 = Counter(r["cause"].split("|")[0] for r in res)
    print("cause kinds:", dict(c2))
    print("mean pickups", np.mean([r["pickups"] for r in res]), "eps with >=1 pickup", np.mean([r["pickups"]>0 for r in res]))
    print("mean successful surfacings", np.mean([r["surf_ok"] for r in res]), "eps with >=1 surfacing", np.mean([r["surf_ok"]>0 for r in res]), "surf with 6 divers total", sum(r["surf6"] for r in res))
    print("death diver count dist", Counter(r.get("death_dc") for r in res))
    rows = Counter(); [rows.update({int(k): v for k, v in r["rows"].items()}) for r in res]
    tot = sum(rows.values()); print("row occupancy", {k: round(v/tot, 3) for k, v in sorted(rows.items())})
    acts = Counter(); [acts.update({int(k): v for k, v in r["exec_acts"].items()}) for r in res]
    tot = sum(acts.values()); print("executed actions", {ACT[k]: round(v/tot, 3) for k, v in sorted(acts.items())})
    dr = Counter(r.get("death_row") for r in res); print("death row", dict(sorted(dr.items())))
    print("score of oxygen deaths", np.mean([r["score"] for r in res if r["cause"]=="oxygen"]) if any(r["cause"]=="oxygen" for r in res) else None,
          "steps of oxygen deaths", np.mean([r["steps"] for r in res if r["cause"]=="oxygen"]) if any(r["cause"]=="oxygen" for r in res) else None)
