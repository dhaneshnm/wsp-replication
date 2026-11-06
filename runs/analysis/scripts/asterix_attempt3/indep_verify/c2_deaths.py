# Classify every death using counterfactual replays of the pre-death game state (all 6 actions).
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
from collections import Counter
NM = ["noop","left","up","right","down","fire"]
for name in sys.argv[1:]:
    res = pickle.load(open(f"my_inst_{name}.pkl", "rb"))
    cat = Counter(); rows = Counter(); detail = []
    for R in res:
        if not R["done"]: continue
        s = R["log"][-1]; cf = R["cf"]
        a, ex = s["a"], s["ex"]
        assert cf[ex], "executed action must be fatal in replay"
        safe = [k for k in (0, 2, 4) if not cf[k]]
        moved = s["py1"] != s["py"]
        override = s["sticky"] and ex != a
        if override:
            c = f"sticky override: executed {NM[ex]} (policy sampled {NM[a]}, sampled {'safe' if not cf[a] else 'FATAL'})"
            c += "; moved" if moved else "; did not move"
        else:
            kind = "sticky-but-same" if s["sticky"] else "policy"
            if not safe: c = f"{kind}: {NM[ex]} chosen, no safe action among noop/up/down (trapped)"
            else: c = f"{kind}: {NM[ex]} chosen while {[NM[k] for k in safe]} safe"
        cat[c] += 1
        detail.append(dict(seed=R["seed"], c=c, row=s["py"], row1=s["py1"], a=a, ex=ex))
    n = sum(cat.values())
    print(f"== {name}: deaths {n}")
    for k, v in cat.most_common(): print(f"  {v:4d}  {k}")
    pickle.dump(detail, open(f"my_deaths_{name}.pkl", "wb"))
