import sys, re, glob, ast
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
DEC = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)$")
real = ast.literal_eval
def strict(s):
    for t in [t.strip() for t in re.split(r"[\[\],]", s) if t.strip()]:
        if not DEC.match(t): raise ValueError(f"non-decimal {t!r}")
    s2 = re.sub(r"(?<![\d.])([+-]?)0+(\d)", r"\1\2", s)  # allow leading zeros like float()
    return real(s2)
pairs = [(p, p.replace("answer.md", "net.npz")) for p in sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/*/attempt*/answer.md"))]
pairs += [(p, p.replace("runs/", "networks/").replace("/reply/answer.md", "/hand.npz")) for p in sorted(glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/*/reply/answer.md"))]
for a, n in pairs:
    text = open(a).read()
    wsp.ast.literal_eval = real; loose, r1 = wsp.apply_edits(text)
    wsp.ast.literal_eval = strict; tight, r2 = wsp.apply_edits(text)
    wsp.ast.literal_eval = real
    try: stored = wsp.load_npz(n); dstored = max(float(np.abs(loose[k]-stored[k]).max()) for k in loose)
    except Exception as e: dstored = f"n/a ({type(e).__name__})"
    d = max(float(np.abs(loose[k]-tight[k]).max()) for k in loose)
    print(a.split("/runs/")[1], f"loose_applied={r1.applied} strict_applied={r2.applied} max|loose-strict|={d} max|loose-stored|={dstored}")
