import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
txt = open(D + "answer.md").read()
net, rep = wsp.apply_edits(txt)
print("statements", rep.statements, "applied", rep.applied, "errors", rep.errors)
for k in net: print(k, np.abs(net[k] - CL[k]).max(), (CL[k] != 0).sum())
