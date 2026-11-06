"""Extra edge forms, and realistic demonstrations built from the paper's own replies."""
import re
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

F = "```"
RUNS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs"
NETS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks"


def nz(net):
    return int(sum((v != 0).sum() for v in net.values()))


def maxdiff(a, b):
    return max(float(np.abs(a[k] - b[k]).max()) for k in wsp.SHAPES)


print("== edge forms")
net, rep = wsp.apply_edits(f"{F}edits\nb1[0] = 1\n# same as the {F}python{F} snippet above\nb1[1] = 2\nb1[2] = 3\n{F}\n")
print("closing fence inside a '#' comment:", net["b1"][:3], f"statements={rep.statements}")

net, rep = wsp.apply_edits(f"{F} edits\nb1[0] = 1\n{F}\n")
print("'``` edits' opening (space):", net["b1"][:1], rep.errors)

net, rep = wsp.apply_edits(f"{F}edits\nW2[0:2, 0:3] =\n    [[1, -1, 0.5],\n     [0, 2, 0]]\nb1[0] = 1\n{F}\n")
print("list starting on line after '=':", net["W2"][0:2, 0:3].tolist(), rep.errors)

net, rep = wsp.apply_edits(f"{F}edits\nb3 = [0, 1, 2, 3, 4, 5]\n{F}\n")
print("whole-tensor without index:", net["b3"].tolist(), rep.errors)

print()
print("== demo 1: one missing ']' in the paper's Breakout reply (statement 4 of 92)")
ans = open(f"{RUNS}/breakout/reply/answer.md").read()
hand = wsp.load_npz(f"{NETS}/breakout/hand.npz")
line = "W1[540:600:6, 3] = [0, -0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14, -0.16, -0.18]"
assert ans.count(line) == 1
typo = ans.replace(line, line[:-1])  # drop the closing ']'
net_h, rep_h = wsp.apply_edits(typo)
spec = ans.replace(line + "\n", "")  # spec: that one statement is skipped, the other 91 apply
net_s, rep_s = wsp.apply_edits(spec)
print(f"harness: {rep_h.applied}/{rep_h.statements} applied, errors={len(rep_h.errors)}, nonzero={nz(net_h)}")
print(f"spec (only the bad statement skipped): {rep_s.applied} applied, nonzero={nz(net_s)}")
print("first error:", rep_h.errors[0][:100])
sc_h = [wsp.play_episode(net_h, "breakout", s)[0] for s in range(20)]
sc_s = [wsp.play_episode(net_s, "breakout", s)[0] for s in range(20)]
print(f"20-episode mean: harness {np.mean(sc_h):.1f}   spec {np.mean(sc_s):.1f}")

print()
print("== demo 2: a 10x3 block written unit-major (3 lists of 10) in the paper's Asterix reply")
ans = open(f"{RUNS}/asterix/reply/answer.md").read()
hand = wsp.load_npz(f"{NETS}/asterix/hand.npz")
old = "W1[61:120:6, 0:24:8] = [[0,0,0],[0,0,0],[0,0,3],[5,5,4],[6,6,9],[11,11,10],[6,6,9],[5,5,4],[0,0,3],[0,0,0]]"
assert ans.count(old) == 1
rows = [[0,0,0],[0,0,0],[0,0,3],[5,5,4],[6,6,9],[11,11,10],[6,6,9],[5,5,4],[0,0,3],[0,0,0]]
cols = [list(c) for c in zip(*rows)]  # same numbers, written one list per unit (3 x 10)
new = "W1[61:120:6, 0:24:8] = " + str(cols).replace(" ", "")
print("rewritten:", new)
net_t, rep_t = wsp.apply_edits(ans.replace(old, new))
print(f"harness: {rep_t.applied}/{rep_t.statements} applied, errors={rep_t.errors}")
print("intended unit 0 column:", [r[0] for r in rows])
print("harness  unit 0 column:", net_t["W1"][61:120:6, 0].tolist())
print(f"max |harness - hand.npz| = {maxdiff(net_t, hand)}")
try:
    a = np.zeros((600, 32), np.float32); a[61:120:6, 0:24:8] = np.asarray(cols, np.float32)
except Exception as e:
    print("plain numpy assignment of the same list:", type(e).__name__, e)

print()
print("== demo 3: the paper's Breakout reply cut off inside its edits block (e.g. stop_reason max_tokens)")
ans = open(f"{RUNS}/breakout/reply/answer.md").read()
cut = ans[: ans.index("# Unit 4: horizontal direction")]
net_c, rep_c = wsp.apply_edits(cut)
print(f"harness: statements={rep_c.statements} applied={rep_c.applied} errors={rep_c.errors} nonzero={nz(net_c)}")
blk = cut[cut.rindex(F + "edits"):].split("\n", 1)[1]
net_r, rep_r = wsp.apply_edits(f"{F}edits\n{blk}\n{F}\n")
print(f"reading that last (unterminated) block: statements={rep_r.statements} applied={rep_r.applied} nonzero={nz(net_r)}")
