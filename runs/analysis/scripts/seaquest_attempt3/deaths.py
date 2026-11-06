import sys, pickle, numpy as np
from collections import Counter
D = sys.argv[1]
for name in ["claude", "astra"]:
    res = pickle.load(open(f"{D}/{name}_200.pkl", "rb"))
    print("===", name)
    for cause in ["oxygen", "fish", "enemy_sub", "enemy_bullet", "surface_no_diver"]:
        rs = [r for r in res if r["cause"] == cause]
        if not rs: continue
        print(f" {cause} n={len(rs)}")
        print("   divers aboard at death:", dict(Counter(r["post"]["d"] for r in rs)))
        print("   row at death:", dict(sorted(Counter(r["post"]["y"] for r in rs).items())))
        print("   col at death:", dict(sorted(Counter(r["post"]["x"] for r in rs).items())))
        # last executed action and whether sticky in the final step
        print("   final executed action:", dict(Counter(h[2] for h in [r["last_hist"][-1] for r in rs])),
              " final step sticky-overridden:", sum(r["last_hist"][-1][4] for r in rs))
        # vertical move in the final step
        mv = Counter()
        for r in rs:
            h = r["last_hist"][-1]; pre = h[3]
            mv[("up" if r["post"]["y"] < pre["y"] else "down" if r["post"]["y"] > pre["y"] else "same row")] += 1
        print("   final-step vertical move:", dict(mv))
