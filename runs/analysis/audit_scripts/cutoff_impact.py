import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, pathlib
F = "```"
# 1. finder's two cases
only = f"design\n{F}edits\nb1[0] = 2\nb1[1] = 3\n"
draft = f"draft\n{F}edits\nb1[0] = 1\nb1[5] = 9\n{F}\nfinal\n{F}edits\nb1[0] = 2\nb1[1] = 3\n"
for name, t in [("only-unclosed", only), ("draft+unclosed", draft)]:
    net, rep = wsp.apply_edits(t)
    print(name, rep.applied, rep.statements, rep.errors, net["b1"][:6].tolist())
# 2. Real Claude replies: where in the text does the edits block start, as fraction of reply chars
root = pathlib.Path("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5")
for f in sorted(root.glob("*/attempt*/answer.md")):
    t = f.read_text()
    i = t.find(F + "edits")
    print(f.parent.parent.name, "reply chars", len(t), "block starts at char", i, "block chars", len(t) - i,
          "n edits blocks", t.count(F + "edits"))
