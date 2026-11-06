import json, os, collections
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
for nm in ("claude", "astra"):
    ins = json.load(open(os.path.join(D, f"instr_{nm}_0_200.json")))
    dth = json.load(open(os.path.join(D, f"deaths2_{nm}.json")))
    steps = sum(r['steps'] for r in ins)
    col = [r for r in dth if r['cause'] == 'collision']
    sticky = sum(1 for r in col if r['hist'][-1]['a'] != r['hist'][-1]['ax'])
    print(f"{nm}: steps {steps}, collisions {len(col)}, sticky-step collisions {sticky}; "
          f"policy-step collision hazard {100*(len(col)-sticky)/steps:.3f}/100 steps, sticky-step hazard {100*sticky/steps:.3f}/100 steps; "
          f"points/step {sum(r['score'] for r in ins)/steps:.4f}")
    colsteps = np.sum([r['cols'] for r in ins], axis=0)
    dcol = collections.Counter(r['hist'][-1]['sx'] for r in col)   # front column at the start of the fatal step
    cen = sum(colsteps[3:7]); off = colsteps.sum() - cen
    dc = sum(dcol[c] for c in range(3,7)); do = len(col) - dc
    print(f"   front col 3..6 at fatal step: {dc} deaths / {cen} steps ({100*dc/cen:.3f} per 100);  front col 0-2,7-9: {do} deaths / {off} steps ({100*do/max(off,1):.3f} per 100)")
