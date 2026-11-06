import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
for name, ans, npz in [("claude", "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/answer.md", CL),
                       ("astra", "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md", AS)]:
    net, rep = wsp.apply_edits(open(ans).read())
    ref = wsp.load_npz(npz)
    diffs = {k: float(np.abs(net[k] - ref[k]).max()) for k in net}
    print(name, "statements", rep.statements, "applied", rep.applied, "errors", rep.errors[:3])
    print("  max |parsed - npz| per tensor:", diffs)
    print("  nonzero W1 cols:", sorted(set(np.nonzero(ref["W1"])[1].tolist())), "nonzero W2 cols:", sorted(set(np.nonzero(ref["W2"])[1].tolist())))
    W1 = ref["W1"]
    for ch in range(6):
        print(f"  channel {ch}: nonzero W1 entries {int((W1.reshape(10,10,6,32)[:,:,ch,:]!=0).sum())}")
