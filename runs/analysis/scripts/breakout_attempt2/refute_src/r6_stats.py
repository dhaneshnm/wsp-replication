import json, numpy as np
from collections import Counter
for tag in ["claude_s01", "astra_s01", "v678_s01", "v8_s01"]:
    res = json.load(open(f"tr_{tag}.json"))
    Fl = [f for r in res for f in r["flights"]]; M = [f for f in Fl if not f["caught"]]
    sc = np.array([r["score"] for r in res]); st = np.array([r["steps"] for r in res])
    print(f"== {tag}: mean {sc.mean():.2f} capped {sum(1 for r in res if not r['done'])}/200 landings {len(Fl)} misses {len(M)} "
          f"miss% {100*len(M)/len(Fl):.4f} steps/landing {st.sum()/len(Fl):.3f} bricks/step {sc.sum()/st.sum():.4f}")
    # check: each non-capped episode ends in exactly one miss
    print("   episodes done:", sum(1 for r in res if r["done"]), " episodes whose last flight is a miss:", sum(1 for r in res if r["flights"] and not r["flights"][-1]["caught"]))
    A = [f for f in M if f["catA"]]
    print("   catA (paddle on x8 before landing step, chose noop-class, sticky exec -dx):", len(A), f"= {100*len(A)/max(1,len(M)):.1f}% of misses")
    if A:
        print("   catA prev-step (rel pos to x8 signed by dx, sticky?, exec move signed, chosen move signed):",
              Counter((f["prev"]["rel"], f["prev"]["sticky"], f["prev"]["exmove"], f["prev"]["amove"]) for f in A).most_common())
        print("   catA ball row 2 steps before landing:", Counter(f["by_minus2"] for f in A), " sticky +dx push in prior 4 steps:", sum(f["push4"] for f in A))
    # slack
    sl = Counter(f["n"] - f["d"] for f in Fl); slm = Counter(f["n"] - f["d"] for f in M)
    s1 = [f for f in Fl if f["n"] - f["d"] == 1]; s1m = [f for f in s1 if not f["caught"]]
    print(f"   slack-1 flights {len(s1)} misses {len(s1m)} ({100*len(s1m)/max(1,len(s1)):.3f}%) = {100*len(s1m)/max(1,len(M)):.1f}% of misses")
    print("   slack-1 misses (n,d):", Counter((f["n"], f["d"]) for f in s1m), " (p0,x8):", Counter((f["p0"], f["x8"]) for f in s1m).most_common(4),
          " (start_bx,x8):", Counter((f["start_bx"], f["x8"]) for f in s1m).most_common(4))
    print("   slack-1 flights (n,d):", Counter((f["n"], f["d"]) for f in s1))
    print("   slack-1 misses by sticky no-op delays:", dict(sorted(Counter(f["delays"] for f in s1m).items())))
    print("   min flight n (non-first flights):", min(f["n"] for f in Fl if not f["first"]), " misses slack dist:", dict(sorted(slm.items())))
    print("   catA & slack-1 overlap:", sum(1 for f in A if f["n"] - f["d"] == 1))
