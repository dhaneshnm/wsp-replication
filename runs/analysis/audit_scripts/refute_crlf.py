import sys, pathlib, tempfile; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
lf = "design\n```edits\nb3[0] = 1\n```\n"
crlf = lf.replace("\n", "\r\n")
sp = lf.replace("```edits", "``` edits")
for name, t in [("LF", lf), ("CRLF", crlf), ("spaced", sp)]:
    net, rep = wsp.apply_edits(t); print(name, rep.applied, rep.errors, float(net["b3"][0]))
# round trip through the harness's own file path (write_text/read_text, universal newlines)
p = pathlib.Path(tempfile.mkdtemp(dir="/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/audit")) / "answer.md"
p.write_bytes(crlf.encode()); t = p.read_text()
net, rep = wsp.apply_edits(t); print("CRLF via read_text", rep.applied, rep.errors, float(net["b3"][0]))
