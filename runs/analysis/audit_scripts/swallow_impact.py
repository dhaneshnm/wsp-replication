import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
text = open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/answer.md").read()
net0, rep0 = wsp.apply_edits(text)
# drop the closing bracket of the 3rd list statement in the block (a single typo)
target = "W1[540:600:6, 2] = [0, -0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16, -0.18]"
assert text.count(target) == 1
bad = text.replace(target, target[:-1])
net1, rep1 = wsp.apply_edits(bad)
nz = lambda n: int(sum((v != 0).sum() for v in n.values()))
print("original : applied", rep0.applied, "/", rep0.statements, "errors", len(rep0.errors), "nonzero", nz(net0))
print("1 typo   : applied", rep1.applied, "/", rep1.statements, "errors", len(rep1.errors), "nonzero", nz(net1))
print("error msg:", rep1.errors[0][:100])
if __name__ == "__main__":
    s0 = wsp.evaluate(net0, "breakout", episodes=20, workers=8)
    s1 = wsp.evaluate(net1, "breakout", episodes=20, workers=8)
    print("20-episode mean: original", s0["mean"], " with 1 typo", s1["mean"])
