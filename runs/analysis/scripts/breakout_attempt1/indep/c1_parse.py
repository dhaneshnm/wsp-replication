# Claim 1: independent re-parse of the edits block (numpy exec, not wsp.apply_edits)
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import re
import numpy as np
import wsp

A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/answer.md"
N = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"
txt = open(A).read()
start = txt.index("```edits")
block = txt[start + len("```edits"):]
block = block[: block.index("```")]
print("number of ```edits blocks:", txt.count("```edits"))

arrs = {"W1": np.zeros((600, 32)), "b1": np.zeros(32), "W2": np.zeros((32, 32)),
        "b2": np.zeros(32), "W3": np.zeros((32, 6)), "b3": np.zeros(6)}
n_stmt, n_ok, errs = 0, 0, []
for line in block.split("\n"):
    s = line.split("#")[0].strip()
    if not s:
        continue
    n_stmt += 1
    lhs, rhs = s.split("=", 1)
    name = lhs.strip().split("[")[0]
    idx = lhs.strip()[len(name):]
    try:
        tgt = eval("arrs['%s']%s" % (name, idx))
        val = np.array(eval(rhs), dtype=float)
        if val.ndim and np.shape(tgt) != val.shape:
            raise ValueError(f"shape {np.shape(tgt)} vs {val.shape}")
        exec("arrs['%s']%s = val" % (name, idx))
        n_ok += 1
    except Exception as e:
        errs.append((s, repr(e)))
print("statements", n_stmt, "ok", n_ok, "errors", errs)

net = wsp.load_npz(N)
raw = np.load(N)
print("npz keys:", raw.files)
for k in arrs:
    print(k, "shape", net[k].shape, "max|indep - npz| =", float(np.abs(arrs[k] - net[k]).max()))
W = net["W1"].reshape(10, 10, 6, 32)
for ch in range(6):
    print("channel", ch, "nonzero W1 entries:", int(np.count_nonzero(W[:, :, ch, :])))
print("total nonzero weights in npz:", sum(int(np.count_nonzero(net[k])) for k in net))
print("CHANNEL_MAP breakout:", wsp.CHANNEL_MAP["breakout"])
