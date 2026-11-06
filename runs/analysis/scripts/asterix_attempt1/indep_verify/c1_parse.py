"""Claim 1, part A: independent parse of the reply's edits by executing each line as numpy code.
Does NOT use wsp.apply_edits. Compares to net.npz loaded with plain np.load."""
import re
import numpy as np

ATT = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1"
text = open(f"{ATT}/answer.md").read()
start = text.rindex("```edits")
body = text[start + len("```edits"):]
body = body[: body.index("```")]
ns = {"W1": np.zeros((600, 32), np.float32), "b1": np.zeros(32, np.float32),
      "W2": np.zeros((32, 32), np.float32), "b2": np.zeros(32, np.float32),
      "W3": np.zeros((32, 6), np.float32), "b3": np.zeros(6, np.float32)}
n_stmt = 0
n_ok = 0
for line in body.splitlines():
    s = line.split("#")[0].strip()
    if not s:
        continue
    n_stmt += 1
    try:
        exec(s, {"__builtins__": {}}, ns)
        n_ok += 1
    except Exception as e:
        print("FAILED:", s, e)
print("statements:", n_stmt, "executed ok:", n_ok)

d = np.load(f"{ATT}/net.npz")
print("npz keys:", d.files)
key = {"W1": "actor/dense1/kernel", "b1": "actor/dense1/bias", "W2": "actor/dense2/kernel",
       "b2": "actor/dense2/bias", "W3": "actor/logits/kernel", "b3": "actor/logits/bias"}
allsame = True
nnz = 0
for k, v in ns.items():
    a = d[key[k]] if key[k] in d.files else d[k]
    same = a.shape == v.shape and np.array_equal(a.astype(np.float32), v)
    allsame &= same
    nnz += int(np.count_nonzero(a))
    print(k, a.shape, "equal:", same, "nonzero:", int(np.count_nonzero(a)))
print("ALL EQUAL:", allsame, "total nonzero in npz:", nnz)
