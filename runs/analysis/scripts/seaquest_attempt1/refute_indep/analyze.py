import os, pickle, sys
import numpy as np
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__))
A = ["noop", "left", "up", "right", "down", "fire"]
C = pickle.load(open(os.path.join(H, "roll_claude_200.pkl"), "rb"))
S = pickle.load(open(os.path.join(H, "roll_astra_200.pkl"), "rb"))


def cells(x, right):
    return frozenset((x - 1, x) if right else (x, x + 1))


def death_class(ep):
    d = ep["death"]
    if d is None:
        return "cap"
    st = ep["steps"][-1]
    if d["pre_y"] > 0 and d["post_y"] == 0 and d["pre_dc"] == 0:
        return "empty_surface"
    if d["pre_oxy"] <= 0:
        return "oxygen"
    return "collision"


def summary(name, R):
    print(f"===== {name}")
    sc = np.array([e["score"] for e in R]); L = np.array([e["length"] for e in R])
    print("mean score", sc.mean(), "mean len", L.mean())
    cls = Counter(death_class(e) for e in R); print("death classes", dict(cls))
    # surfacings
    surf_ok = []; pick = []
    kills = 0; bonus = 0
    for e in R:
        n_s = 0; n_p = 0
        for s in e["steps"]:
            if s["y"] > 0 and s["ny"] == 0 and not s["done"]:
                n_s += 1
                if s["dc"] == 6: bonus += s["r"]
                else: kills += s["r"]
            else:
                kills += s["r"]
            if s["ndc"] > s["dc"] and s["ny"] > 0:
                n_p += s["ndc"] - s["dc"]
        surf_ok.append(n_s); pick.append(n_p)
    print("successful surfacings/ep", np.mean(surf_ok), " pickups/ep", np.mean(pick), " eps with >=1 pickup", np.mean(np.array(pick) > 0))
    print("kills per 100 steps", 100 * kills / L.sum(), " surface bonus total", bonus)
    # surfacing-request onsets and their outcome
    onsets = sum(len(e["surf_onsets"]) for e in R)
    ok = 0; died = 0; other = 0
    for e in R:
        st = e["steps"]
        for t0 in e["surf_onsets"]:
            res = None
            for s in st[t0:]:
                if s["done"]:
                    res = "died"; break
                if s["ny"] == 0 and s["y"] > 0:
                    res = "ok"; break
            if res == "ok": ok += 1
            elif res == "died": died += 1
            else: other += 1
    print(f"surf-request onsets/ep {onsets/len(R):.3f}  -> surfaced {ok} died {died} other {other}  success {ok/max(1,onsets):.3f}",
          f" surfacings/requests ratio {np.sum(surf_ok)/max(1,onsets):.3f}")
    # collision deaths: same-row vs vertical
    sr = vt = vt_sticky = 0
    for e in R:
        if death_class(e) != "collision": continue
        d = e["death"]
        if d["post_y"] != d["pre_y"]:
            vt += 1; vt_sticky += d["ea"] != d["a"]
        else:
            sr += 1
    print("collision deaths: same-row", sr, " vertical", vt, f"(sticky {vt_sticky})")
    return dict(sc=sc, L=L)


cs = summary("claude", C)
ss = summary("astra", S)
