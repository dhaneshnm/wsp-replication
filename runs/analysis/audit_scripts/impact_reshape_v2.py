import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import glob, ast
import numpy as np
import wsp
files = sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/*/attempt*/answer.md")) + \
        sorted(glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/*/reply/answer.md"))
for f in files:
    text = open(f).read()
    block = wsp.last_edits_block(text)
    tag = f.split("/runs/")[-1]
    if block is None:
        print(tag, "NO EDITS BLOCK"); continue
    net = wsp.zero_net()
    n = list1d_on_1d = list_on_2d = list2d = mism = 0
    for stmt in wsp._logical_statements(block):
        m = wsp._STMT.match(stmt)
        if not m: continue
        n += 1
        name, idx, op, val = m.groups()
        key = wsp._parse_index(idx, net[name].ndim)
        v = np.asarray(ast.literal_eval(val.strip()), dtype=np.float32)
        t = net[name][key]
        if v.ndim == 0: continue
        if v.ndim == 2: list2d += 1
        if np.ndim(t) == 2: list_on_2d += 1
        if np.shape(t) != v.shape:
            mism += 1; print("   MISMATCH", stmt[:90], v.shape, np.shape(t))
    print(tag, "stmts", n, "list-valued stmts on 2-D blocks", list_on_2d, "2-D lists", list2d, "shape mismatches", mism)
