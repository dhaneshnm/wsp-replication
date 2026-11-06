import sys, re, glob
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
DEC = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)$")
paths = sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/*/attempt*/answer.md")) + \
        sorted(glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/*/reply/answer.md"))
for p in paths:
    text = open(p).read()
    block = wsp.last_edits_block(text)
    if block is None:
        print(p, "NO BLOCK"); continue
    stmts = wsp._logical_statements(block)
    nondec = []; leadzero = []; ntok = 0
    for s in stmts:
        m = wsp._STMT.match(s)
        if not m: continue
        val = m.group(4)
        toks = [t.strip() for t in re.split(r"[\[\],]", val) if t.strip()]
        for t in toks:
            ntok += 1
            if not DEC.match(t): nondec.append(t)
            elif re.match(r"^[+-]?0\d", t): leadzero.append(t)
    net, rep = wsp.apply_edits(text)
    print(p.split("/runs/")[1], f"stmts={rep.statements} applied={rep.applied} errs={len(rep.errors)} value_tokens={ntok} non_decimal={nondec[:10]} (n={len(nondec)}) leading_zero={leadzero[:10]} (n={len(leadzero)})")
    for e in rep.errors[:5]: print("   ERR", e)
