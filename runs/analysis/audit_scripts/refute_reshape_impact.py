import sys, glob, re, ast
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

files = sorted(glob.glob("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/*/attempt*/answer.md")) + \
        sorted(glob.glob("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/*/reply/answer.md"))
for f in files:
    text = open(f).read()
    block = wsp.last_edits_block(text)
    net = wsp.zero_net()
    nres = 0; kinds = {}
    list_stmts = 0; twod = 0
    for stmt in wsp._logical_statements(block):
        m = wsp._STMT.match(stmt)
        if not m: continue
        name, idx, op, val = m.groups()
        arr = net[name]
        key = wsp._parse_index(idx, arr.ndim)
        value = np.asarray(ast.literal_eval(val.strip()), dtype=np.float32)
        target = arr[key]
        if value.ndim: list_stmts += 1
        if value.ndim == 2: twod += 1
        if np.ndim(target) and value.ndim and value.shape != np.shape(target):
            nres += 1
            k = f"{value.shape}->{np.shape(target)}"
            kinds[k] = kinds.get(k, 0) + 1
    print(f.split("/runs/")[-1], "list_stmts", list_stmts, "2d_lists", twod, "reshaped", nres, kinds)
