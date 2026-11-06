"""Claims 5 and 11: build a 2-row lookahead veto myself (indices found from the weights, not hard-coded), check which
rows each move unit vetoes, and score it with wsp.evaluate on seeds 0..199 (in memory only)."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz"
U = lambda row: 16 + row          # layer-1 U_r unit for rows 1..8 (W1 cols 6..9 of row r on channel 1)


def structure(net):
    W1, W2 = net["W1"], net["W2"]
    # confirm U units: which input cells feed units 17..24
    for j in range(17, 25):
        nz = np.nonzero(W1[:, j])[0]
        cells = sorted({(i // 6 // 10, i // 6 % 10, i % 6) for i in nz})
        assert all(c[2] == 1 for c in cells) and len({c[0] for c in cells}) == 1
        assert [c[1] for c in cells] == [6, 7, 8, 9] and U(cells[0][0]) == j, (j, cells)
    moves = []
    for j in range(16):
        gate = [r for r in range(9) if W2[r, j] == 100]
        vetoes = [j1 - 16 for j1 in range(17, 25) if W2[j1, j] < 0]
        moves.append((j, gate[0], vetoes))
    return moves


def guard2(net):
    n = {k: v.copy() for k, v in net.items()}
    for j, r, vetoes in structure(net):
        for v in vetoes:
            beyond = v + (v - r)          # same direction, one row further
            if 1 <= beyond <= 8:
                n["W2"][U(beyond), j] += -75
                n["b2"][j] -= 75          # U unit off (~-1) contributes +75; keep the 'off' total unchanged
    return n


if __name__ == "__main__":
    net = wsp.load_npz(CL)
    for j, r, v in structure(net):
        print(f"L2 unit {j:2d}: gated on sub row {r}, vetoed by danger rows {v}")
    g = guard2(net)
    print("changed W2 entries:", [(int(a), int(b), float(g['W2'][a, b])) for a, b in zip(*np.nonzero(g["W2"] != net["W2"]))])
    if len(sys.argv) > 1:
        sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3")
        import variants
        a = variants.variant("guard2")
        print("identical to analyst's guard2 weights:", all(np.array_equal(a[k], g[k]) for k in g))
        base = wsp.evaluate(net, "seaquest", episodes=200, workers=4)
        print("base  ", base)
        res = wsp.evaluate(g, "seaquest", episodes=200, workers=4)
        print("guard2", res)
