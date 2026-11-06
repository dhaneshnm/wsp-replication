import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

def run(stmt):
    net, rep = wsp.apply_edits("```edits\n" + stmt + "\n```\n")
    return net, rep

def numpy_plain(name, key, val):
    a = wsp.zero_net()[name]
    try:
        a[key] = np.asarray(val, dtype=np.float32)
        return "numpy OK"
    except Exception as e:
        return f"numpy {type(e).__name__}: {e}"

cases = [
  # (label, stmt, tensor, numpy key, value, slice to show)
  ("A transposed 4x2 list into 2x4 block W3[0:2,0:4]",
   "W3[0:2, 0:4] = [[11, 15], [12, 16], [13, 17], [14, 18]]", "W3", (slice(0,2), slice(0,4)),
   [[11,15],[12,16],[13,17],[14,18]]),
  ("B flat 8-list into 2x4 block W3[0:2,0:4]",
   "W3[0:2, 0:4] = [11, 12, 13, 14, 15, 16, 17, 18]", "W3", (slice(0,2), slice(0,4)),
   [11,12,13,14,15,16,17,18]),
  ("C 2x2 list into 1-D range b2[4:8]",
   "b2[4:8] = [[7, 8], [9, 10]]", "b2", (slice(4,8),), [[7,8],[9,10]]),
  ("D 1x3 nested list into 1-D column range W1[6:9, 2]",
   "W1[6:9, 2] = [[3, 4, 5]]", "W1", (slice(6,9), 2), [[3,4,5]]),
  ("E strided column block W1[1:600:60, 0:3] given as 3 lists of 10 (one per unit)",
   "W1[1:600:60, 0:3] = [[0,1,2,3,4,5,6,7,8,9],[10,11,12,13,14,15,16,17,18,19],[20,21,22,23,24,25,26,27,28,29]]",
   "W1", (slice(1,600,60), slice(0,3)),
   [list(range(0,10)), list(range(10,20)), list(range(20,30))]),
  ("F control: wrong total size (5 values into 2x3) must be rejected",
   "W2[0:2, 0:3] = [1, 2, 3, 4, 5]", "W2", (slice(0,2), slice(0,3)), [1,2,3,4,5]),
  ("G control: correct 2x3 shape",
   "W2[0:2, 0:3] = [[1, -1, 0.5], [0, 2, 0]]", "W2", (slice(0,2), slice(0,3)), [[1,-1,0.5],[0,2,0]]),
]
for label, stmt, name, key, val in cases:
    net, rep = run(stmt)
    print(f"== {label}")
    print(f"   stmt: {stmt}")
    print(f"   harness: applied={rep.applied}/{rep.statements} errors={rep.errors}")
    print(f"   harness result {name}{key}: {net[name][key].tolist()}")
    print(f"   {numpy_plain(name, key, val)}")
