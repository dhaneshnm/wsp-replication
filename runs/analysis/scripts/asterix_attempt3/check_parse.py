import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt3/"
net = wsp.load_npz(A+"net.npz")
txt = open(A+"answer.md").read()
re_net, rep = wsp.apply_edits(txt)
print("parse errors:", rep.errors if hasattr(rep,'errors') else rep)
for k in net: print(k, net[k].shape, "max|diff| vs re-parse:", float(np.abs(net[k]-re_net[k]).max()), "nnz", int((net[k]!=0).sum()))
ast = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")
atxt=open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/asterix/reply/answer.md").read()
an, arep = wsp.apply_edits(atxt)
print("astra parse errors:", arep.errors)
for k in ast: print("astra", k, "max|diff| vs re-parse:", float(np.abs(ast[k]-an[k]).max()), "nnz", int((ast[k]!=0).sum()))
