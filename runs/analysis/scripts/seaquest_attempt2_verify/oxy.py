import json, os, collections
import numpy as np
D = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(D, "deaths2_claude.json")))
for r in res:
    if r['cause'] != 'oxygen': continue
    h = r['hist']
    print(f"seed {r['seed']} t={r['t']} dc={h[-1]['dc']} last rows/cols:", [(x['sy'], x['sx']) for x in h], "on:", h[-1].get('on'), "V=%.2f" % h[-1].get('V', float('nan')))
# collision death time distribution (hazard)
ins = json.load(open(os.path.join(D, "instr_claude_0_200.json")))
T = np.array([r['steps'] for r in ins]); dead = np.array([r['death']=='collision' for r in ins])
for lo, hi in [(0,100),(100,200),(200,300),(300,500),(500,1000),(1000,10000)]:
    at_risk = np.clip(T, lo, hi) - lo
    ev = ((T > lo) & (T <= hi) & dead).sum()
    print(f"steps [{lo},{hi}): collision deaths {ev}, exposure {at_risk.sum()}, hazard per 100 steps {100*ev/max(at_risk.sum(),1):.2f}")
