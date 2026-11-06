import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np, re
for game in ["breakout", "seaquest", "asterix"]:
    txt = open(f"/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/{game}/reply/answer.md").read()
    block = wsp.last_edits_block(txt)
    lines = block.splitlines()
    # find the 2nd single-line statement whose last code char is ']' and that holds a list value
    cands = [i for i,l in enumerate(lines) if re.match(r"\s*(W1|b1|W2|b2|W3|b3)\s*\[", l) and "= [" in wsp._strip_comment(l) and wsp._strip_comment(l).rstrip().endswith("]") and wsp._strip_comment(l).count("[")==wsp._strip_comment(l).count("]")]
    i = cands[1]
    code = wsp._strip_comment(lines[i]).rstrip()
    lines2 = list(lines); lines2[i] = code[:-1]
    txt2 = txt.replace(block, "\n".join(lines2) + "\n")
    n0, r0 = wsp.apply_edits(txt)
    n1, r1 = wsp.apply_edits(txt2)
    nz = lambda n: int(sum(np.count_nonzero(v) for v in n.values()))
    print(f"{game}: typo on block line {i}: {code[:70]!r}...")
    print(f"   original : statements {r0.statements} applied {r0.applied} errors {len(r0.errors)} nonzero {nz(n0)}")
    print(f"   one typo : statements {r1.statements} applied {r1.applied} errors {len(r1.errors)} nonzero {nz(n1)}")
