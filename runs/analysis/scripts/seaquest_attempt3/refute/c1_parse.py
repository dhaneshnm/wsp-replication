import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A="/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/"
net = wsp.load_npz(A+"net.npz")
txt = open(A+"answer.md").read()
re_net, rep = wsp.apply_edits(txt)
print("parse:", rep.statements, rep.applied, rep.errors)
print("keys net", sorted(net), "keys reparse", sorted(re_net))
for k in sorted(net):
    print(k, net[k].shape, re_net[k].shape, "max abs diff", float(np.abs(net[k]-re_net[k]).max()), "array_equal", np.array_equal(net[k], re_net[k]))
# count statements in edits block manually
blk = wsp.last_edits_block(txt)
lines=[l for l in blk.splitlines() if l.strip() and not l.strip().startswith('#')]
print("non-comment nonblank lines in edits block:", len(lines))
