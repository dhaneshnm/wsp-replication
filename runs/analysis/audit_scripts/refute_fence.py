import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np, pathlib, tempfile, os
body = "W1[12, 0] = 2.5\nb1[0:4] = -1\nW3[:, 2] = 3\n"
ref, rref = wsp.apply_edits("design\n```edits\n" + body + "```\n")
print("reference LF:", rref.applied, rref.statements, rref.errors)
def run(label, text):
    net, rep = wsp.apply_edits(text)
    d = max(float(np.abs(net[k]-ref[k]).max()) for k in ref)
    print(f"{label:40s} applied={rep.applied}/{rep.statements} errors={rep.errors} maxdiff={d}")
run("CRLF everywhere", ("design\n```edits\n" + body + "```\n").replace("\n", "\r\n"))
run("CRLF only on fence line", "design\n```edits\r\n" + body + "```\n")
run("'``` edits' spaced", "design\n``` edits\n" + body + "```\n")
run("'```edits  ' trailing spaces", "design\n```edits  \n" + body + "```\n")
run("'```Edits' capital", "design\n```Edits\n" + body + "```\n")
# CRLF block with an LF block earlier: earlier block wins silently?
run("LF block then CRLF last block", "```edits\nW1[0,0]=9\n```\n" + ("```edits\n" + body + "```\n").replace("\n","\r\n"))
# realistic path: answer.md saved and re-read via Path.read_text (universal newlines)
p = pathlib.Path(tempfile.mkdtemp())/"a.md"
p.write_bytes(("design\n```edits\n" + body + "```\n").replace("\n","\r\n").encode())
run("CRLF file re-read via read_text()", p.read_text())
