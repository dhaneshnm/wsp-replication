import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import glob, wsp
files = sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/**/answer.md", recursive=True)) + \
        sorted(glob.glob("/Users/dhaneshneelamana/lm_understand-logs/**/answer.md", recursive=True))
for f in files:
    text = open(f).read()
    blk = wsp.last_edits_block(text)
    if blk is None:
        print(f, "NO BLOCK"); continue
    lines = [wsp._strip_comment(l) for l in blk.splitlines()]
    unbal = [l for l in lines if l.count('[') != l.count(']')]
    multi = sum(1 for s in wsp._logical_statements(blk) if s)  # logical
    _, rep = wsp.apply_edits(text)
    print(f.replace("/Users/dhaneshneelamana/",""), "lines", len(lines), "physical-unbalanced-lines", len(unbal), "applied", rep.applied, "/", rep.statements, "errors", len(rep.errors))
