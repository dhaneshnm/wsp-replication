import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import ast, numpy as np
import wsp
base = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch"
for g in ["breakout", "seaquest", "asterix"]:
    text = open(f"{base}/runs/{g}/reply/answer.md").read()
    block = wsp.last_edits_block(text)
    net = wsp.zero_net(); n = 0; mism = []
    for stmt in wsp._logical_statements(block):
        m = wsp._STMT.match(stmt)
        name, idx, op, val = m.groups()
        tgt = net[name][wsp._parse_index(idx, net[name].ndim)]
        v = np.asarray(ast.literal_eval(val.strip()), dtype=np.float32)
        n += 1
        if np.ndim(tgt) and v.ndim and v.shape != np.shape(tgt):
            mism.append((stmt[:60], v.shape, np.shape(tgt)))
    print(g, "statements", n, "reshape-path statements", len(mism), mism[:3])
