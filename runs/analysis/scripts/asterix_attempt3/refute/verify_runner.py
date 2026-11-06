import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instrument import *
for s in range(5):
    a = wsp.play_episode(NET,"asterix",s)[:2]; b = run(("claude",s))
    print(s, "wsp:",a, "mine:",(b["score"],b["steps"]))
