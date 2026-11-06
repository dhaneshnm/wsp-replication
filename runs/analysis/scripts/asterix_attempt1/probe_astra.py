import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

np.set_printoptions(precision=3, suppress=True, linewidth=170)
A = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz")
C = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
text = open("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs/asterix/reply/answer.md").read()
re_net, rep = wsp.apply_edits(text)
print("astra parse:", rep.statements, rep.applied, rep.errors[:3])
print("hand.npz == re-parsed astra answer:", all(np.allclose(A[k], re_net[k]) for k in A))


def obs(player=(5, 5), ents=()):
    o = np.zeros((10, 10, 6), np.float32)
    o[player[0], player[1], 0] = 1
    for (r, c, k, d) in ents:
        o[r, c, 1 if k == "e" else 2] = 1
        b = c - 1 if d > 0 else c + 1
        if 0 <= b <= 9:
            o[r, b, 4] = 1
    return o.reshape(600)


def pol(net, x):
    z = wsp.logits(net, x)
    p = np.exp(z - z.max()); p /= p.sum()
    return p[[0, 2, 4]]

scen = {
    "empty board": [],
    "own row enemy c4 R (stay fatal)": [(5, 4, "e", +1)],
    "own row enemy c3 R (medium)": [(5, 3, "e", +1)],
    "row4 enemy c5 (up fatal)": [(4, 5, "e", +1)],
    "row4 enemy c4 R (up fatal)": [(4, 4, "e", +1)],
    "row3 enemy c5 (sticky-up row)": [(3, 5, "e", +1)],
    "row3 enemy c4 R (sticky-up row)": [(3, 4, "e", +1)],
    "own c4 R + row3 enemy c5": [(5, 4, "e", +1), (3, 5, "e", +1)],
    "own c4 R + row7 enemy c5": [(5, 4, "e", +1), (7, 5, "e", +1)],
    "own c4 R, rows 4&6 c5 (trapped)": [(5, 4, "e", +1), (4, 5, "e", +1), (6, 5, "e", -1)],
    "row4 gold c5": [(4, 5, "g", +1)],
    "row4 gold c3 R": [(4, 3, "g", +1)],
    "row3 gold c3 R (2 rows up)": [(3, 3, "g", +1)],
    "row2 gold c1 R (3 rows up)": [(2, 1, "g", +1)],
    "row8 gold c1 R (3 rows down)": [(8, 1, "g", +1)],
    "row1 gold c0 R (4 rows up)": [(1, 0, "g", +1)],
    "own row gold c2 R": [(5, 2, "g", +1)],
    "own row gold c6 R (passed)": [(5, 6, "g", +1)],
    "row3 gold c3 R + row4 enemy c5": [(3, 3, "g", +1), (4, 5, "e", +1)],
    "row3 gold c3R + row4 enemy c3 R": [(3, 3, "g", +1), (4, 3, "e", +1)],
}
print(f"{'scenario (player row 5, col 5)':40s} {'Claude p(n,u,d)':>24s}   {'Astra p(n,u,d)':>24s}")
for name, ents in scen.items():
    x = obs((5, 5), ents)
    print(f"{name:40s} {str(pol(C, x)):>24s}   {str(pol(A, x)):>24s}")

print("\nAstra horizontal logits (empty board):", wsp.logits(A, obs())[[1, 3, 5]])
# Astra layer-1 unit activity for a few states
def h1(net, x):
    return np.tanh(x @ net["W1"] + net["b1"])
for name in ["empty board", "row4 enemy c5 (up fatal)", "row3 enemy c5 (sticky-up row)", "row3 gold c3 R (2 rows up)"]:
    x = obs((5, 5), scen[name])
    h = h1(A, x); g = np.tanh(h @ A["W2"] + A["b2"])
    print(f"\nAstra {name}: h1 up-haz[0:8]={h[0:8]}\n   down-haz[8:16]={h[8:16]}\n   wait-haz[16:24]={h[16:24]}\n   treas[24:32]={h[24:32]}\n   h2[0:3]={g[0:3]} h2[3:32]={g[3:32]}")
