import json, os
D = os.path.dirname(os.path.abspath(__file__))
for nm in ("claude", "astra"):
    res = json.load(open(os.path.join(D, f"deaths2_{nm}.json")))
    for r in res:
        if r['cause'] != 'surface_no_diver': continue
        h = r['hist'][-3:]
        print(nm, "seed", r['seed'], "t", r['t'], [(x['sy'], x['dc'], x['oxy'], x['a'], x['ax'], x.get('on')) for x in h])
