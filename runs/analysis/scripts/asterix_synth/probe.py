"""Demo probes. Observations are built by setting a real MinAtar asterix state and calling the harness obs()."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_synth")
from table import NETS

env = wsp._make_env("asterix", 0)
g = env.env
obs = wsp.make_obs_fn(env, "asterix")
np.set_printoptions(precision=3, suppress=True)


def scene(player_row, ents):
    """ents: list of (row, col, moving_right, is_gold)."""
    g.entities = [None] * 8
    g.player_x, g.player_y = 5, player_row
    for (r, c, rt, gold) in ents:
        g.entities[r - 1] = [c, r, rt, gold]
    return obs()


def fwd(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    z = h2 @ net["W3"] + net["b3"]
    p = np.exp(z - z.max()); p /= p.sum()
    return h1, h2, z, p


A = wsp.load_npz(NETS["claude_a3"])
SC = {
    "A empty, player r5": (5, []),
    "B gold r4 c3->, player r5": (5, [(4, 3, True, True)]),
    "C enemy r5 c3-> (own-row threat), player r5": (5, [(5, 3, True, False)]),
    "D own threat + enemies at c5 in r4 and r6": (5, [(5, 3, True, False), (4, 5, False, False), (6, 5, True, False)]),
    "E gold r4 c3-> + enemy r3 c5 (two rows up), player r5": (5, [(4, 3, True, True), (3, 5, True, False)]),
    "F same board, player now in r4": (4, [(3, 5, True, False)]),
    "G gold own row r5 c3->": (5, [(5, 3, True, True)]),
    "H gold r4 c0-> (just spawned, no trail)": (5, [(4, 0, True, True)]),
    "I gold r4 c1->": (5, [(4, 1, True, True)]),
    "J empty, player r1": (1, []),
    "K enemy r3 c5 only, player r5": (5, [(3, 5, True, False)]),
}
print("=== Claude attempt 3: unit readout (rows 1..8) ===")
for name, (pr, ents) in SC.items():
    x = scene(pr, ents)
    h1, h2, z, p = fwd(A, x)
    y = pr - 1
    print(f"\n{name}")
    print("  P  ", h1[0:8]); print("  T  ", h1[8:16]); print("  Bk ", h1[16:24]); print("  G  ", h1[24:32])
    print(f"  active L2 (row {pr}): S={h2[y]:+.3f} U={h2[8+y]:+.3f} D={h2[16+y]:+.3f} V={h2[24+y]:+.3f}; "
          f"max inactive L2 = {np.delete(h2, [y, 8+y, 16+y, 24+y]).max():+.6f}")
    print(f"  logits n/u/d = {z[0]:+.2f}/{z[2]:+.2f}/{z[4]:+.2f}  l/r/f = {z[1]:.1f}/{z[3]:.1f}/{z[5]:.1f}")
    print(f"  p(noop,up,down) = {p[0]:.3f} {p[2]:.3f} {p[4]:.3f}")

print("\n=== cross-net probes, player r5 ===")
for k, path in NETS.items():
    net = wsp.load_npz(path)
    out = []
    for name in ["A empty, player r5", "K enemy r3 c5 only, player r5", "B gold r4 c3->, player r5",
                 "E gold r4 c3-> + enemy r3 c5 (two rows up), player r5"]:
        pr, ents = SC[name]
        p = fwd(net, scene(pr, ents))[3]
        out.append(f"{name[:1]}: n{p[0]:.3f} u{p[2]:.3g} d{p[4]:.3f}")
    print(f"{k:10s} | " + " | ".join(out))
