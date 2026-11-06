import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import numpy as np, wsp
from common import *
for name, ans, npz in [("claude", "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/answer.md", CLAUDE),
                       ("astra", "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/asterix/reply/answer.md", ASTRA)]:
    net, rep = wsp.apply_edits(open(ans).read())
    ld = wsp.load_npz(npz)
    diffs = {k: float(np.abs(net[k]-ld[k]).max()) for k in net}
    print(name, "statements", rep.statements, "applied", rep.applied, "errors", rep.errors, "maxdiff", diffs,
          "nonzero", sum(int((ld[k]!=0).sum()) for k in ld))
