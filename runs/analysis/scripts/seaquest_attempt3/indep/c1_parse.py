"""Claim 1: independent re-parse of answer.md's edits block (own parser, not wsp.apply_edits), compared to net.npz."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import re
import numpy as np
import wsp

A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/"
text = open(A + "answer.md").read()
blocks = text.split("```edits")
print("number of ```edits fences:", len(blocks) - 1)
body = blocks[-1].split("```")[0]

net = {"W1": np.zeros((600, 32)), "b1": np.zeros(32), "W2": np.zeros((32, 32)), "b2": np.zeros(32),
       "W3": np.zeros((32, 6)), "b3": np.zeros(6)}
SAFE = re.compile(r"^(W1|b1|W2|b2|W3|b3)\[[0-9:, ]+\] *= *[-0-9., \[\]]+$")
n_stmt = n_ok = 0
bad = []
for line in body.splitlines():
    s = line.split("#")[0].strip()
    if not s:
        continue
    n_stmt += 1
    if not SAFE.match(s):
        bad.append(s); continue
    lhs, rhs = s.split("=", 1)
    name = lhs[:2]
    idx = lhs[lhs.index("[") + 1: lhs.rindex("]")]
    key = tuple(slice(*[int(b) if b.strip() else None for b in p.split(":")]) if ":" in p else int(p) for p in idx.split(","))
    val = np.array(eval(rhs.strip(), {"__builtins__": {}}), dtype=np.float64)  # only digits/brackets pass SAFE
    net[name][key] = val
    n_ok += 1
print("my parser: statements", n_stmt, "applied", n_ok, "unparsed", bad)

saved = wsp.load_npz(A + "net.npz")
print("npz keys:", sorted(saved))
for k in ["W1", "b1", "W2", "b2", "W3", "b3"]:
    d = np.abs(saved[k].astype(np.float64) - net[k])
    print(f"{k} shape {saved[k].shape} max|npz - myparse| = {d.max()}  nnz npz {int((saved[k]!=0).sum())} nnz mine {int((net[k]!=0).sum())}")
_, rep = wsp.apply_edits(text)
print("wsp.apply_edits report:", rep.statements, rep.applied, rep.errors)
print("total nonzero weights in npz:", sum(int((saved[k] != 0).sum()) for k in saved))
