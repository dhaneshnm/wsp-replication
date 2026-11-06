"""Claim 4: hand-built observations. Player at (row r, col 5); one enemy in row r-2 (or r+2) at every
column/direction. Report p(up)/p(down) for Claude and Astra vs the empty board. Also a structural
read of Claude's W2: which D_r units feed each (row, up/down) layer-2 unit."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz"
nets = {"claude": wsp.load_npz(CLAUDE), "astra": wsp.load_npz(ASTRA)}


def obs(player_row, ents):
    o = np.zeros((10, 10, 6), np.float32)
    o[player_row, 5, 0] = 1
    for (row, col, right, gold) in ents:
        o[row, col, 2 if gold else 1] = 1
        tc = col - 1 if right else col + 1
        if 0 <= tc <= 9:
            o[row, tc, 4] = 1
    return o.reshape(600)


def probs(net, x):
    z = (np.tanh(np.tanh(x @ net["W1"] + net["b1"]) @ net["W2"] + net["b2"]) @ net["W3"] + net["b3"]).astype(np.float64)
    p = np.exp(z - z.max())
    return p / p.sum()


for name, net in nets.items():
    pe = probs(net, obs(5, []))
    pa = probs(net, obs(5, [(3, 5, True, False)]))
    pb = probs(net, obs(5, [(3, 4, True, False)]))
    pd = probs(net, obs(5, [(7, 5, True, False)]))
    print(f"{name}: empty board, player r5: p(noop,up,down)=({pe[0]:.4f},{pe[2]:.4f},{pe[4]:.4f})")
    print(f"{name}: enemy at r3 c5 (2 rows up):      p(up)={pa[2]:.3e}  p(noop)={pa[0]:.4f} p(down)={pa[4]:.4f}")
    print(f"{name}: enemy at r3 c4 moving right:     p(up)={pb[2]:.3e}")
    print(f"{name}: enemy at r7 c5 (2 rows down):    p(down)={pd[4]:.3e}")
    # sweep: every enemy position/direction two rows away, player rows 3..6
    for pr in (3, 4, 5, 6):
        base = probs(net, obs(pr, []))
        mx_up = mx_dn = 0.0
        for col in range(10):
            for right in (True, False):
                mx_up = max(mx_up, abs(probs(net, obs(pr, [(pr - 2, col, right, False)]))[2] - base[2]))
                mx_dn = max(mx_dn, abs(probs(net, obs(pr, [(pr + 2, col, right, False)]))[4] - base[4]))
        print(f"   {name} player r{pr}: max |dp(up)| over any single enemy in r-2 = {mx_up:.3e}; "
              f"max |dp(down)| over any enemy in r+2 = {mx_dn:.3e}  (empty p(up)={base[2]:.4f}, p(down)={base[4]:.4f})")

W2 = nets["claude"]["W2"]
print("Claude structural: D-unit (row) inputs to each (player row r, action) layer-2 unit:")
for r in range(1, 9):
    for k, nm in ((1, "up"), (2, "down")):
        u = 3 * (r - 1) + k
        drows = [i + 1 for i in range(8) if W2[i, u] != 0]
        grows = [i - 15 for i in range(16, 24) if W2[i, u] != 0]
        print(f"   r={r} {nm:4s}: D rows {drows}, G rows {grows}")
