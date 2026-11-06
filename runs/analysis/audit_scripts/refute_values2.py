import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
for v in ["[05, 1, 0]", "[5, 1, 0]", "[1e-3, 2, 0]", "[0.50, 1.00, 0.25]", "[00.5, 1, 0]"]:
    net, rep = wsp.apply_edits("```edits\nb1[0:3] = " + v + "\n```")
    print(f"{v!r:22} applied={rep.applied} b1[0:3]={net['b1'][0:3].tolist()} errs={[e[-60:] for e in rep.errors]}")
