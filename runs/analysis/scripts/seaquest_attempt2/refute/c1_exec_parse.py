# Independent check of claim 1: rebuild the net by exec-ing each edits line as numpy code (not wsp.apply_edits),
# then compare with net.npz.
import sys, re
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt2/"
txt = open(A + "answer.md").read()
starts = [m.end() for m in re.finditer(r"```edits\n", txt)]
print("edits blocks found:", len(starts))
blk = txt[starts[-1]: txt.index("```", starts[-1])]
ns = {k: np.zeros(s, dtype=np.float32) for k, s in wsp.SHAPES.items()}
n_ok = n_lines = 0
for line in blk.splitlines():
    line = line.split("#")[0].strip()
    if not line: continue
    n_lines += 1
    lhs, rhs = line.split("=", 1)
    exec(f"{lhs.strip()} = np.asarray({rhs.strip()}, dtype=np.float32)", {"np": np}, ns)
    n_ok += 1
print("statements", n_lines, "executed", n_ok)
net = wsp.load_npz(A + "net.npz")
for k in wsp.SHAPES:
    print(k, net[k].shape, net[k].dtype, "max|diff| =", float(np.abs(net[k] - ns[k]).max()), "nonzero", int((ns[k] != 0).sum()))
print("total nonzero", sum(int((ns[k] != 0).sum()) for k in ns))
