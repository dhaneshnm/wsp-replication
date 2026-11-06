import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
N = nets()
for name, net in N.items():
    for s in range(6):
        a = episode(net, s, instrument=True)
        b = wsp.play_episode(net, "asterix", s)
        print(name, s, "mine", a["score"], a["steps"], "wsp", b[0], b[1], "MATCH" if (a["score"], a["steps"]) == (b[0], b[1]) else "DIFF")
