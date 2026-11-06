import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
cases = ["b1[0:3] = [05, 10, 15]", "b1[0] = 05", "b1[0] = -05", "b1[0] = 05.0", "b1[0] = 00", "b1[0] = 007.5", "b1[0] = 0.5", "b1[0] = 1e3", "b1[0] = 1_000", "b1[0] = 0x10", "b1[0] = +5"]
for c in cases:
    net, rep = wsp.apply_edits("```edits\n" + c + "\n```")
    print(f"{c!r:28} applied={rep.applied} b1[0:3]={net['b1'][0:3].tolist()} err={[e[-70:] for e in rep.errors]}")
