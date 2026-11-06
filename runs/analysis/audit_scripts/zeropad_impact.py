import sys, re, glob
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
files = sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/**/answer.md", recursive=True)) + \
        sorted(glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/**/answer.md", recursive=True))
pat = re.compile(r'(?<![\w.])-?0\d+(?![\w.])')  # integer token with leading zero, not part of a float
for f in files:
    txt = open(f).read()
    blk = wsp.last_edits_block(txt) or ""
    # values side only
    hits = []
    nvals = 0
    for line in blk.splitlines():
        line = line.split("#",1)[0]
        if "=" not in line: 
            # continuation lines
            rhs = line
        else:
            rhs = line.split("=",1)[1]
        nvals += len(re.findall(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', rhs))
        hits += pat.findall(rhs)
    net, rep = wsp.apply_edits(txt)
    lz_err = [e for e in rep.errors if "leading zeros" in e]
    print(f"{f.split('/runs/')[-1]:45} stmts={rep.statements} applied={rep.applied} errs={len(rep.errors)} numeric_tokens~{nvals} zero_padded_int_tokens={len(hits)} leading_zero_errs={len(lz_err)}")
