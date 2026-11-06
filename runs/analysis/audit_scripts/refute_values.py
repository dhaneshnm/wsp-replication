import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
cases = ["1e-3", "-1e3", "2.5E2", "0x10", "1_000", "True", "'1.5'", "05", "007", "-07.5", "0.5", "-3", ".5", "5.", "+2", "1+2", "1/2", "[05, 1]", "[1e-3, 2]", "0b11", "0o7", "1j"]
for v in cases:
    txt = "```edits\nb1[0] = " + v + "\n```"
    net, rep = wsp.apply_edits(txt)
    print(f"{v!r:12} applied={rep.applied} b1[0]={float(net['b1'][0])!r} b1[1]={float(net['b1'][1])!r} errs={rep.errors}")
