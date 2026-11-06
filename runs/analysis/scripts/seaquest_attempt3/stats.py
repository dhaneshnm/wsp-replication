import sys, pickle, numpy as np
from collections import Counter
D = sys.argv[1]
for name in ["claude", "astra"]:
    res = pickle.load(open(f"{D}/{name}_200.pkl", "rb"))
    sc = np.array([r["score"] for r in res]); st = np.array([r["steps"] for r in res])
    kills = np.array([r["kills"] for r in res]); pk = np.array([r["pickups"] for r in res])
    nsurf = np.array([len(r["surf"]) for r in res])
    bonus = np.array([sum(s[2] for s in r["surf"]) for r in res])
    full6 = np.array([sum(1 for s in r["surf"] if s[0] == 6) for r in res])
    print(f"=== {name}: mean score {sc.mean():.2f}  median {np.median(sc)}  max {sc.max()}  mean steps {st.mean():.0f}")
    print(f"  kills/ep {kills.mean():.2f}  bonus/ep {bonus.mean():.2f}  pickups/ep {pk.mean():.2f}  surfacings/ep {nsurf.mean():.2f}  6-diver surfacings/ep {full6.mean():.2f}")
    print("  kills per 100 steps", 100*kills.sum()/st.sum())
    c = Counter(r["cause"] for r in res); print("  death causes:", dict(c))
    for cause in c:
        m = np.array([r["cause"] == cause for r in res])
        print(f"    {cause:16s} n={m.sum():3d}  mean score {sc[m].mean():6.1f}  mean steps {st[m].mean():6.0f}  share of lost score? ")
    print("  episodes with 0 surfacings:", (nsurf == 0).sum(), " their mean score", sc[nsurf == 0].mean() if (nsurf==0).any() else None)
    print("  episodes ending before first surfacing by cause:", dict(Counter(r["cause"] for r in res if len(r["surf"]) == 0)))
    rows = Counter(); cols = Counter(); acts = Counter(); ex = Counter()
    for r in res:
        rows.update(r["rows"]); cols.update(r["cols"]); acts.update(r["acts"]); ex.update(r["exec_acts"])
    tot = sum(rows.values())
    print("  row occupancy %:", {k: round(100*v/tot, 1) for k, v in sorted(rows.items())})
    print("  col occupancy %:", {k: round(100*v/tot, 1) for k, v in sorted(cols.items())})
    print("  sampled action %:", {k: round(100*v/tot, 2) for k, v in sorted(acts.items())})
    print("  ramp index at end: mean", np.mean([r["ramp"] for r in res]), "max", max(r["ramp"] for r in res))
    # oxygen at surfacing (pre)
    so = [s[1] for r in res for s in r["surf"]]; sd = [s[0] for r in res for s in r["surf"]]
    if so: print("  oxygen at surfacing: mean", np.mean(so), "min", min(so), "max", max(so), "; divers at surfacing", dict(Counter(sd)))
