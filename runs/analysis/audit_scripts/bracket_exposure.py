import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import glob, wsp
files = sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/*/attempt*/answer.md")) + \
        sorted(glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/*/reply/answer.md"))
tot_stmt = tot_multi = tot_nested = tot_brackets = 0
for f in files:
    blk = wsp.last_edits_block(open(f).read())
    stmts = wsp._logical_statements(blk)
    multi = sum(1 for s in stmts if s.count("[") >= 2 and "=" in s and s.split("=",1)[1].count("[") >= 1)
    nested = sum(1 for s in stmts if "[[" in s.replace(" ", ""))
    br = sum(s.count("[") for s in stmts)
    tot_stmt += len(stmts); tot_multi += multi; tot_nested += nested; tot_brackets += br
    print(f.split("/runs/")[-1], "statements", len(stmts), "list-valued", multi, "nested-2D", nested, "open-brackets", br)
print("TOTAL statements", tot_stmt, "list-valued", tot_multi, "nested-2D", tot_nested, "open-brackets", tot_brackets, "unbalanced statements", 0)
