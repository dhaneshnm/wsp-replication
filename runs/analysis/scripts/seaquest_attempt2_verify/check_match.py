import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
for nm, net in (("claude", CL), ("astra", AS)):
    res = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"instr_{nm}_0_200.json")))
    mism = 0
    for s in range(0, 200, 10):
        sc, steps, _ = wsp.play_episode(net, "seaquest", s)
        if sc != res[s]['score'] or steps != res[s]['steps']: mism += 1
    print(nm, "checked 20 seeds vs wsp.play_episode, mismatches:", mism)
