import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

RUN = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1"
net = wsp.load_npz(f"{RUN}/net.npz")
text = open(f"{RUN}/answer.md").read()
re_net, rep = wsp.apply_edits(text)
print("parse:", rep.statements, rep.applied, rep.errors)
print("net.npz == re-parsed answer:", all(np.array_equal(net[k], re_net[k]) for k in net))
print("nonzero:", sum(int((net[k] != 0).sum()) for k in net))

np.set_printoptions(precision=3, suppress=True, linewidth=160)
ACT = ["noop", "left", "up", "right", "down", "fire"]

def obs(player=(5, 5), ents=()):
    """ents: list of (row, col, kind 'e'|'g', dir +1 right / -1 left)"""
    o = np.zeros((10, 10, 6), np.float32)
    o[player[0], player[1], 0] = 1
    for (r, c, k, d) in ents:
        o[r, c, 1 if k == "e" else 2] = 1
        b = c - 1 if d > 0 else c + 1
        if 0 <= b <= 9:
            o[r, b, 4] = 1
    return o.reshape(600)

def hidden(x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    return h1, h2, z, p

# --- D_r values per situation (row 3, player elsewhere) ---
print("\n== D unit (row 3 -> unit 2) and G unit (unit 18) for single entity in row 3 ==")
for kind in ["e", "g"]:
    for c in range(10):
        for d in [+1, -1]:
            h1, *_ = hidden(obs((5, 5), [(3, c, kind, d)]))
            print(f"{kind} c{c} {'R' if d>0 else 'L'}: D={h1[2]:+.3f} G={h1[18]:+.3f}", end=" | ")
        print()
h1, *_ = hidden(obs((5, 5), []))
print("empty row: D=%+.3f G=%+.3f" % (h1[2], h1[18]))
print("P units with player at row 5:", h1[8:16])

# --- action probabilities in canonical scenarios, player at (5,5) ---
print("\n== Logits / probs, player at row 5 col 5 ==")
scen = {
    "empty board": [],
    "own row enemy c4 R (fatal stay)": [(5, 4, "e", +1)],
    "own row enemy c4 R, row4 enemy c5": [(5, 4, "e", +1), (4, 5, "e", +1)],
    "own row enemy c4 R, rows 4&6 enemy c5": [(5, 4, "e", +1), (4, 5, "e", +1), (6, 5, "e", -1)],
    "own row enemy c3 R (medium)": [(5, 3, "e", +1)],
    "own row enemy c3 R, row4 c3 R (medium), row6 empty": [(5, 3, "e", +1), (4, 3, "e", +1)],
    "own row enemy c4 L (receding)": [(5, 4, "e", -1)],
    "row4 gold c5": [(4, 5, "g", +1)],
    "row4 gold c4 R (approaching)": [(4, 4, "g", +1)],
    "row4 gold c3 R": [(4, 3, "g", +1)],
    "row3 gold c5 (2 rows away)": [(3, 5, "g", +1)],
    "own row gold c4 R": [(5, 4, "g", +1)],
    "row4 gold c4 R + own row enemy c2 R": [(4, 4, "g", +1), (5, 2, "e", +1)],
    "row4 enemy c6 L (fatal up) ": [(4, 6, "e", -1)],
    "row6 enemy c5 (fatal down)": [(6, 5, "e", +1)],
}
for name, ents in scen.items():
    h1, h2, z, p = hidden(obs((5, 5), ents))
    print(f"{name:52s} logits={z} p(n,u,d)={p[[0,2,4]]} p(l,r,f)={p[[1,3,5]].sum():.1e}")

print("\n== Active layer-2 units for player row 5 (k12 stay, k13 up, k14 down), empty board ==")
h1, h2, z, p = hidden(obs((5, 5), []))
print("h2[12:15]=", h2[12:15], " inactive mean=", np.delete(h2[:24], [12, 13, 14]).mean())

print("\n== Edge rows: player at row 1 and row 8, empty board ==")
for r in [1, 8]:
    h1, h2, z, p = hidden(obs((r, 5), []))
    print(f"row {r}: logits={z} p(n,u,d)={p[[0,2,4]]}")
print("player row 2, empty board:", hidden(obs((2, 5), []))[3][[0, 2, 4]])
