import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
# Count statements whose value shape != target shape (the reshape path), without editing wsp.py
files = ["/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/%s/reply/answer.md" % g for g in ("breakout","seaquest","asterix")]
files += ["/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/answer.md",
          "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/answer.md"]
import ast
for f in files:
    text = open(f).read()
    block = wsp.last_edits_block(text)
    hits = []
    if block:
        net = wsp.zero_net()
        for s in wsp._logical_statements(block):
            m = wsp._STMT.match(s)
            if not m: continue
            name, idx, op, val = m.groups()
            try:
                key = wsp._parse_index(idx, net[name].ndim)
                v = np.asarray(ast.literal_eval(val.strip()), dtype=np.float32)
                t = net[name][key]
                if np.ndim(t) and v.ndim and v.shape != np.shape(t):
                    hits.append((s[:70], v.shape, np.shape(t)))
            except Exception as e:
                pass
    print(f.split("/")[-4:], "block" if block else "NO BLOCK", "reshape-path statements:", len(hits), hits[:3])
