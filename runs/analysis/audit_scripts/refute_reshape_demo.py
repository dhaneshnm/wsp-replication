import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
txt = "```edits\nW2[0:2, 0:3] = [[1, 0], [-1, 2], [0.5, 0]]\nW2[4:6, 4:6] = [[1, 2], [3, 4]]\n```"
net, rep = wsp.apply_edits(txt)
print("applied", rep.applied, "errors", rep.errors)
print("W2[0:2,0:3]", net["W2"][0:2, 0:3].tolist())
print("square 2x2 block (transposition undetectable by any shape check):", net["W2"][4:6, 4:6].tolist())
