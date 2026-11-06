"""Systematic wiring check: for every player row y and every target row r, put ONE immediate enemy (col 5) in row r
and see which of the policy's n/u/d logits drop. Expected: n drops iff r==y; u drops iff r==max(1,y-1); d drops iff r==min(8,y+1).
Also: gold-direction sign check (one approaching gold far above vs far below)."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/net.npz")
env = wsp._make_env("asterix", 0); inner = env.env; obsf = wsp.make_obs_fn(env, "asterix")


def z_of(py, ents):
    inner.player_x, inner.player_y = 5, py
    inner.entities = [None] * 8
    for (r, c, lr, g) in ents:
        inner.entities[r - 1] = [c, r, lr, g]
    return wsp.logits(net, obsf())

bad = 0
for y in range(1, 9):
    base = z_of(y, [])
    for r in range(1, 9):
        z = z_of(y, [(r, 5, True, False)])
        drop = base - z
        exp = {0: r == y, 2: r == max(1, y - 1), 4: r == min(8, y + 1)}
        got = {a: drop[a] > 3 for a in (0, 2, 4)}
        if exp != got:
            bad += 1
            print("MISMATCH y", y, "r", r, "drop n/u/d", drop[[0, 2, 4]].round(2))
print("wiring mismatches over 64 (player row, enemy row) pairs:", bad)
print("example drop (y=4, enemy at col5 in row 3): n/u/d", (z_of(4, []) - z_of(4, [(3, 5, True, False)]))[[0, 2, 4]].round(3))

# gold direction: gold far above (row 1, approaching from col 2 moving right) vs far below (row 8), player row 4
for name, ents in (("gold above r1", [(1, 2, True, True)]), ("gold below r8", [(8, 2, True, True)]), ("none", [])):
    z = z_of(4, ents)
    print(f"player row 4, {name:14s}: u-d logit = {z[2]-z[4]:+.3f}")
