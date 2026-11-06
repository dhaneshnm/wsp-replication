import sys, glob, re
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

files = sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/*/*/answer.md")
              + glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/*/*/thinking.md")
              + glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/*/reply/answer.md"))

def line_fence_block(text):
    # markdown-style: closing fence must be a line consisting only of ```
    blocks = re.findall(r"^```edits[ \t]*\n(.*?)^[ \t]*```[ \t]*$", text, re.S | re.M)
    return blocks[-1] if blocks else None

for f in files:
    t = open(f).read()
    # count backtick triples that are not on a fence-only line or an opening ```lang line
    inline = [ln for ln in t.splitlines() if "```" in ln and not re.fullmatch(r"[ \t]*```[A-Za-z0-9_-]*[ \t]*", ln)]
    b_wsp = wsp.last_edits_block(t)
    b_md = line_fence_block(t)
    same = (b_wsp == b_md)
    n_wsp = len(wsp._logical_statements(b_wsp)) if b_wsp else 0
    n_md = len(wsp._logical_statements(b_md)) if b_md else 0
    print(f.replace("/Users/dhaneshneelamana/",""), "| inline-``` lines:", len(inline), "| blocks identical:", same, "| stmts wsp/md:", n_wsp, n_md)
    for ln in inline[:3]:
        print("    inline:", ln[:120])
