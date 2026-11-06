import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import warnings; warnings.simplefilter("ignore")
import numpy as np, wsp
cases = {
  "break after '=' then list": "W1[0:6, 3] =\n  [1, 0, -1, 0, 2, 0]\nb1[0] = 1",
  "trailing semicolon": "b1[0] = 1;\nb1[1] = 2",
  "partial index W1[12] (row)": "W1[12] = 1",
  "unicode minus": "b1[0] = −1",
  "underscore 1_000": "b1[0] = 1_000",
  "transposed list with *=": "W2[0:2, 0:3] = 1\nW2[0:2, 0:3] *= [[1, 0], [-1, 2], [0.5, 0]]",
  "multi-line list closed on same line as next stmt": "b1[0:2] = [1,\n 2]  # ok\nb1[2] = 3",
}
for k, body in cases.items():
    net, rep = wsp.apply_edits("x\n```edits\n" + body + "\n```\n")
    print(f"{k:50s} applied {rep.applied}/{rep.statements}  b1[:3]={net['b1'][:3].tolist()}  W1[0:6,3]={net['W1'][0:6,3].tolist()}  W2[0:2,0:3]={net['W2'][0:2,0:3].tolist()}")
    for e in rep.errors: print("     err:", e[:110])
