import json, numpy as np, sys
from collections import Counter
for tag in sys.argv[1:]:
    res=json.load(open(f"fl_{tag}.json"))
    F=[f for r in res for f in r["flights"]]
    M=[f for f in F if not f["caught"]]
    print(f"===== {tag}: flights {len(F)} misses {len(M)} ({len(M)/len(F)*100:.3f}%)")
    # flight slack = n - d (Claude's straight target) and n - d_any
    print(" flight slack (actions - |paddle_start - x8|): bin: flights / misses / miss%")
    for s in sorted(set(f["n"]-f["d"] for f in F)):
        a=[f for f in F if f["n"]-f["d"]==s]; m=[f for f in a if not f["caught"]]
        if len(a)>=50 or m: print(f"   slack {s:3d}: {len(a):6d} / {len(m):3d} / {100*len(m)/len(a):.3f}%")
    # classify misses
    cls=Counter()
    for f in M:
        if f["at_catch_before"] and f["landing_sticky"]: c="A: paddle on a catch column before landing step, sticky repeat moved it off"
        elif f["landing_sticky"]: c="B: landing-step sticky, paddle not on catch column before"
        elif f["n"]-f["d_any"]<0: c="C: unreachable from post-catch position (n < distance)"
        else: c="D: reachable, no landing-step sticky (lost moves earlier)"
        cls[c]+=1
    for k,v in sorted(cls.items()): print("  ",k,":",v)
    print("  misses: sticky events in flight:",dict(sorted(Counter(f["sticky"] for f in M).items())), " sticky delays:",dict(sorted(Counter(f["sticky_delay"] for f in M).items())))
    print("  misses: non-sticky moves away from x8:",dict(sorted(Counter(f["away"] for f in M).items())))
    print("  all flights: non-sticky moves away from x8:",dict(sorted(Counter(f["away"] for f in F).items())))
    print("  misses: flight slack:",dict(sorted(Counter(f["n"]-f["d"] for f in M).items())))
    print("  misses: (start_bx, x8) top-5:",Counter((f["start_bx"],f["x8"]) for f in M).most_common(6))
    print("  misses: x8 col:",dict(sorted(Counter(f["x8"] for f in M).items())))
    print("  misses: top row reached:",dict(sorted(Counter(f["top"] for f in M).items())), " first flight of episode:",sum(f["first"] for f in M))
    lowslack=[f for f in F if f["n"]-f["d"]<=1]
    print("  flights with slack<=1: %d (%.2f%% of flights), misses among them %d" % (len(lowslack),100*len(lowslack)/len(F),sum(1 for f in lowslack if not f['caught'])))
