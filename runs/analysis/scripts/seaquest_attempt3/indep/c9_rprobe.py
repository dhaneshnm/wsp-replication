"""Claim 9: R_r pre-activations for single objects, measured on rows 3 and 6 (units 11 and 14), sub parked at row 8 col 8."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep")
import numpy as np, wsp, myrun
net = wsp.load_npz(myrun.CLAUDE)
env = wsp._make_env("seaquest", 5); E = env.env


def pre(row, kind, col, right):
    E.reset(); E.sub_x, E.sub_y, E.sub_or = 8, 8, False
    if kind == "diver": E.divers = [[col, row, right, 5]]
    if kind == "fish": E.e_fish = [[col, row, right, 5]]
    if kind == "esub": E.e_subs = [[col, row, right, 5, 10]]
    if kind == "bullet": E.e_bullets = [[col, row, right]]
    x = myrun.obs_vec(E); u = 8 + row
    return float(x @ net["W1"][:, u] + net["b1"][u])


for row in (3, 6):
    print(f"row {row} (unit {8+row}); empty row: {pre(row, 'none', 0, True):.1f}")
    for kind in ("diver", "fish", "esub", "bullet"):
        for right, lab in ((True, "moving right = approaching"), (False, "moving left = receding")):
            vals = [pre(row, kind, c, right) for c in range(10)]
            print(f"  {kind:6s} {lab:27s} cols0-9:", " ".join(f"{v:6.1f}" for v in vals))
