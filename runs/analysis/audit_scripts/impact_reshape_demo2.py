import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
for s in ["W2[0:2, 0:3] = [[1, 4], [2, 5], [3, 6]]", "W2[0:2, 0:3] = [1, -1, 0.5, 0, 2, 0]"]:
    net, rep = wsp.apply_edits("```edits\n" + s + "\n```")
    print(s, "-> applied", rep.applied, "errors", rep.errors, "W2[0:2,0:3] =", net["W2"][0:2, 0:3].tolist())
