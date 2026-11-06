import json, numpy as np, sys
from collections import defaultdict
for tag in sys.argv[1:]:
    res=json.load(open(f"fl_{tag}.json"))
    F=[f for r in res for f in r["flights"]]
    d=defaultdict(list)
    for f in F: d[f["top"]].append(f)
    tot_steps=sum(f["n"] for f in F); tot_r=sum(f["reward"] for f in F)
    print(f"{tag}: flights {len(F)} bricks/flight {tot_r/len(F):.3f} steps/flight {tot_steps/len(F):.2f}")
    for k in sorted(d):
        a=d[k]; print(f"   top row {k}: {len(a):6d} flights ({100*len(a)/len(F):5.1f}%)  mean steps {np.mean([f['n'] for f in a]):5.2f}  mean bricks {np.mean([f['reward'] for f in a]):.3f}  share of steps {100*sum(f['n'] for f in a)/tot_steps:.1f}%")
    print("   flights with 0 bricks: %.1f%%" % (100*np.mean([f['reward']==0 for f in F])))
