import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlib import *
for net, nm in ((CL, 'claude'), (AS, 'astra')):
    for s in range(0, 12):
        a = wsp.play_episode(net, "seaquest", s)[:2]
        b = episode(net, s)
        assert a[0] == b[0] and a[1] == b[1], (nm, s, a, b)
    print(nm, "replay matches wsp.play_episode on seeds 0-11")
