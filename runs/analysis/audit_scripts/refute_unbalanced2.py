import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np, glob, re
# prose line with stray '[' inside the block (not a comment)
text = "```edits\nb2[0] = 1\nNote: hidden units [0..3] detect the ball\nb2[1] = 2\nW2[0, 0] = 7\n```\n"
net, rep = wsp.apply_edits(text)
print("prose:", rep.statements, rep.applied, rep.errors, net["b2"][:3], net["W2"][0,0])
# paper breakout answer: corrupt one closing ']' of an index in the first statement of the block
p = glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md")[0]
ans = open(p).read()
blk = wsp.last_edits_block(ans)
lines = blk.splitlines()
i = next(k for k,l in enumerate(lines) if re.match(r"^\s*(W1|b1|W2|b2|W3|b3)\s*\[[^\]]*\]\s*=", l))
bad = lines[i].replace("]", "", 1)
print("corrupted line:", repr(lines[i]), "->", repr(bad))
_, rep0 = wsp.apply_edits(ans)
_, rep1 = wsp.apply_edits(ans.replace(lines[i], bad, 1))
print("orig: statements", rep0.statements, "applied", rep0.applied, "errors", len(rep0.errors))
print("typo: statements", rep1.statements, "applied", rep1.applied, "errors", len(rep1.errors))
