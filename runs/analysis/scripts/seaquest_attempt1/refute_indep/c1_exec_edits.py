"""Claim 1: rebuild the net by executing each edits statement as numpy code (no wsp.apply_edits), compare to net.npz."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import re
import numpy as np
import wsp

D = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt1/"
text = open(D + "answer.md").read()
start = text.rindex("```edits")
body = text[start + len("```edits"):]
body = body[: body.index("```")]
ns = {"W1": np.zeros((600, 32)), "b1": np.zeros(32), "W2": np.zeros((32, 32)), "b2": np.zeros(32),
      "W3": np.zeros((32, 6)), "b3": np.zeros(6)}
n_ok = n_bad = 0
for line in body.splitlines():
    s = line.split("#")[0].strip()
    if not s:
        continue
    try:
        exec(s, {"__builtins__": {}}, ns)
        n_ok += 1
    except Exception as e:
        n_bad += 1
        print("FAILED:", s, e)
print("statements executed", n_ok, "failed", n_bad)
raw = np.load(D + "net.npz")
print("npz keys", raw.files)
net = wsp.load_npz(D + "net.npz")
for k in ["W1", "b1", "W2", "b2", "W3", "b3"]:
    print(k, net[k].shape, "max|diff| vs float32(exec)", float(np.abs(net[k] - ns[k].astype(np.float32)).max()),
          "nonzero", int((net[k] != 0).sum()))
print("total nonzero", sum(int((net[k] != 0).sum()) for k in net))
