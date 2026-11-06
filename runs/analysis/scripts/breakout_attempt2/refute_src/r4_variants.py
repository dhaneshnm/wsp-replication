import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt2/net.npz"
AN = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt2/"
net = wsp.load_npz(A)
for rows, name in [((6, 7, 8), "v_rows678"), ((8,), "v_row8")]:
    n2 = {k: v.copy() for k, v in net.items()}
    changed = 0
    for r in rows:
        for c in range(10):
            i = (r * 10 + c) * 6 + 3
            n2["W1"][i, 1] -= 10; n2["W1"][i, 2] -= 10; changed += 2
    wsp.save_npz(n2, name + ".npz")
    an = wsp.load_npz(AN + ("cf2_rows678.npz" if name == "v_rows678" else "cf2_row8.npz"))
    diff = sum(int((n2[k] != net[k]).sum()) for k in net)
    print(name, "weights changed vs Claude:", diff, "(loop count", changed, ") identical to analyst file:", all(np.array_equal(n2[k], an[k]) for k in net))

# Astra vs Claude tables
ast = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz")
print("Astra W1 nonzero cols:", np.nonzero(np.abs(ast["W1"]).sum(0))[0].tolist(), " Claude:", np.nonzero(np.abs(net["W1"]).sum(0))[0].tolist())
print("Astra W2 nonzero rows:", np.nonzero(np.abs(ast["W2"]).sum(1))[0].tolist(), "cols:", np.nonzero(np.abs(ast["W2"]).sum(0))[0].tolist())
print("Astra b3:", ast["b3"].tolist(), " Claude b3:", net["b3"].tolist())
for t, nm in enumerate(["D+", "D-", "U+", "U-"]):
    Ta = ast["W1"][3::6, t].reshape(10, 10) / 0.02
    Tc = net["W1"][3::6, 2 * t].reshape(10, 10) / 10
    pa = ast["W1"][540:600:6, t] / 0.02
    rows_diff = [r for r in range(10) if not np.allclose(Ta[r], Tc[r], atol=1e-4)]
    print(nm, "astra paddle/0.02:", np.round(pa, 3).tolist(), "rows differing from Claude:", rows_diff)
    for r in rows_diff:
        print("    row", r, "astra", np.round(Ta[r], 2).tolist(), " claude", Tc[r].tolist(), " astra-claude", np.round(Ta[r] - Tc[r], 2).tolist())
