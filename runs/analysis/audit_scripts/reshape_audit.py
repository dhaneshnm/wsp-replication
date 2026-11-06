import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import ast, glob, numpy as np, wsp
paths = sys.argv[1:]
for p in paths:
    text = open(p).read()
    block = wsp.last_edits_block(text)
    net = wsp.zero_net(); n_reshaped = 0; n_closed = text.count("```edits")
    for stmt in wsp._logical_statements(block or ""):
        m = wsp._STMT.match(stmt)
        if not m: continue
        name, idx, op, val = m.groups()
        try:
            key = wsp._parse_index(idx, net[name].ndim)
            v = np.asarray(ast.literal_eval(val.strip()), dtype=np.float32)
        except Exception: continue
        t = net[name][key]
        if np.ndim(t) and v.ndim and v.shape != np.shape(t):
            n_reshaped += 1
            print(f"  RESHAPED {p.split('/')[-4:]}: value {v.shape} -> target {np.shape(t)}: {stmt[:90]}")
    print(f"{p}: ```edits openings={n_closed}, reshaped statements={n_reshaped}")
