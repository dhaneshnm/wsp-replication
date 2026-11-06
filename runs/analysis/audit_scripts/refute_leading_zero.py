import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
cases = [
    ("b3[0] = 05", "b3", 0, 5.0),
    ("b3[0] = -05", "b3", 0, -5.0),
    ("b3[0] = 007", "b3", 0, 7.0),
    ("b3[0] = 00.5", "b3", 0, 0.5),
    ("b3[0] = 0", "b3", 0, 0.0),
    ("b3[0] = 00", "b3", 0, 0.0),
    ("b1[0:3] = [05, 10, 15]", "b1", slice(0,3), [5.0,10.0,15.0]),
    ("W1[0:2, 3] = [02.0, 01]", "W1", (slice(0,2),3), [2.0,1.0]),
]
for stmt, name, key, want in cases:
    text = "```edits\nb3[5] = 9\n" + stmt + "\n```"
    net, rep = wsp.apply_edits(text)
    got = net[name][key]
    print(f"{stmt!r:32} applied={rep.applied}/{rep.statements} got={got.tolist() if hasattr(got,'tolist') else got} want={want} errs={[e[-70:] for e in rep.errors]}")
