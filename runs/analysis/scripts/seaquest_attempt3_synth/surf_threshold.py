import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
nets = {"claude_a3": (wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz"), 8),
        "astra": (wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz"), 5)}
env = wsp._make_env("seaquest", 0); obsf = wsp.make_obs_fn(env, "seaquest"); E = env.env
def mk(x, y, oxy, d):
    E.reset(); E.sub_x, E.sub_y, E.sub_or, E.oxygen, E.diver_count = x, y, False, oxy, d
    E.e_fish = []; E.e_subs = []; E.e_bullets = []; E.divers = []
    return obsf()
for name, (net, col) in nets.items():
    for d in (1, 3, 6):
        row = []
        for oxy in (35, 39, 41, 55, 59, 61, 80):
            z = wsp.logits(net, mk(col, 4, oxy, d)); p = np.exp(z - z.max()); p /= p.sum()
            row.append(f"oxy{oxy}:up {p[2]:.2f}")
        print(f"{name} sub row4 col{col} facing L, empty board, divers={d}: " + "  ".join(row))
