import json, numpy as np, sys
from collections import Counter
MOVE={1:-1,3:1}
for tag in sys.argv[1:]:
    res=json.load(open(f"fl_{tag}.json"))
    F=[f for r in res for f in r["flights"]]
    M=[f for f in F if not f["caught"]]
    A=[f for f in M if f["at_catch_before"] and f["landing_sticky"]]
    c=Counter()
    for f in A:
        rel=(f["pre_pos"]-f["x8"])*f["dx"]  # 0 = on straight column, +1 = on reversal column
        ch=MOVE.get(f["chosen"],0)*f["dx"]; ex=MOVE.get(f["exec"],0)*f["dx"]
        c[(f"paddle at x8{'+dx' if rel==1 else ''}", f"chose {'noop' if ch==0 else ('+dx' if ch>0 else '-dx')}", f"sticky exec {'+dx' if ex>0 else '-dx' if ex<0 else 'noop'}")]+=1
    print(tag, "category A misses:",len(A))
    for k,v in c.most_common(): print("   ",k,v)
    # How often the paddle sits on each catch column before the landing step, among all flights, and the chosen action
    c2=Counter()
    for f in F:
        rel=(f["pre_pos"]-f["x8"])*f["dx"]; ch=MOVE.get(f["chosen"],0)*f["dx"]
        c2[(rel, 'noop' if ch==0 else ('+dx' if ch>0 else '-dx'))]+=1
    print("  all landings: (paddle pos before landing-step action relative to x8, signed by dx; chosen action):")
    for k,v in sorted(c2.items()): print("     ",k,v)
