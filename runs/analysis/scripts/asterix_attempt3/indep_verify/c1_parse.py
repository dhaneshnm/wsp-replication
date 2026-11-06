# Independent re-parse: execute every edits statement as numpy code (not wsp.apply_edits).
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import *
txt = open(RUN + "answer.md").read()
blocks = re.findall(r"```edits\n(.*?)```", txt, re.S)
print("edits blocks found:", len(blocks))
ns = {k: np.zeros(s, np.float32) for k, s in wsp.SHAPES.items()}
nstmt = 0; fails = 0
for line in blocks[-1].splitlines():
    line = line.split("#")[0].strip()
    if not line: continue
    nstmt += 1
    try:
        lhs, rhs = line.split("=", 1)
        val = np.array(eval(rhs, {}), dtype=np.float32)
        exec(f"{lhs} = val", {"val": val}, ns)
    except Exception as e:
        fails += 1; print("FAIL", line, e)
print("statements", nstmt, "failures", fails)
net = nets()["claude"]
for k in wsp.SHAPES:
    print(k, "max|npz - exec-parse| =", float(np.abs(net[k] - ns[k]).max()), "nonzero", int((ns[k] != 0).sum()))
