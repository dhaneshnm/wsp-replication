import sys, pathlib; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
d = pathlib.Path("/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/audit")
t = "x\n```edits\nb1[0] = 1\n```\n"
_, r = wsp.apply_edits(t.replace("\n", "\r\n")); print("in-memory CRLF:", r.applied, r.errors)
p = d / "crlf.md"; p.write_bytes(t.replace("\n", "\r\n").encode())
_, r = wsp.apply_edits(p.read_text()); print("CRLF file via read_text:", r.applied, r.errors)
for f in sorted(pathlib.Path("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5").glob("*/attempt*/answer.md")):
    b = f.read_bytes(); _, r = wsp.apply_edits(f.read_text())
    print(f.parent.parent.name, f.parent.name, "CR bytes:", b.count(b"\r"), "'``` edits':", b.count(b"``` edits"), "applied", r.applied, "/", r.statements)
