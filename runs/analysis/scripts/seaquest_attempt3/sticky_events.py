"""For each step where sticky actions replaced the policy's choice with a vertical move, record whether the
destination row had danger in the sub's neighbourhood at decision time, and whether the step was fatal."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, sys.argv[1])
import numpy as np, wsp
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
NETS = {"claude": ("/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz", 8),
        "astra": ("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz", 5)}
def episode(net, seed):
    env = wsp._make_env("seaquest", seed); obs = wsp.make_obs_fn(env, "seaquest"); e = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    ev = []; vert_policy = 0; steps = 0
    for t in range(wsp.MAX_STEPS):
        x = obs(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum(); a = int(rng.choice(6, p=p))
        aa = a
        if env.random.rand() < env.sticky_action_prob: aa = env.last_action
        env.last_action = aa
        y0, x0 = e.sub_y, e.sub_x
        vert_policy += a in (2, 4)
        r, done = e.act(aa); steps += 1
        if aa != a and aa in (2, 4):
            g = x.reshape(10, 10, 6)
            ydest = max(0, y0 - 1) if aa == 2 else min(8, y0 + 1)
            moved = ydest != y0
            danger_near = bool(g[ydest, max(0, x0 - 2):min(10, x0 + 2), 1].any()) if moved else False
            danger_any_right = bool(g[ydest, x0 - 2:, 1].any()) if moved else False
            ev.append((a, aa, moved, danger_near, done))
        if done: break
    return ev, vert_policy, steps, done
def work(args):
    name, seeds = args
    net = wsp.load_npz(NETS[name][0]); return [episode(net, s) for s in seeds]
if __name__ == "__main__":
    N = int(sys.argv[2])
    for name in NETS:
        with ProcessPoolExecutor(4) as ex:
            res = [r for part in ex.map(work, [(name, list(range(N))[i::4]) for i in range(4)]) for r in part]
        ev = [e for r in res for e in r[0]]
        steps = sum(r[2] for r in res)
        moved = [e for e in ev if e[2]]
        print(f"== {name}: {N} eps, {steps} steps; policy chose up/down on {sum(r[1] for r in res)/steps:.1%} of steps")
        print(f"  sticky-forced vertical moves (policy chose something else): {len(ev)} ({len(ev)/steps*1000:.1f} per 1000 steps), of which actually changed row: {len(moved)}")
        print(f"  fatal: {sum(e[4] for e in moved)} ({sum(e[4] for e in moved)/max(1,len(moved)):.1%} of row-changing ones)")
        dn = [e for e in moved if e[3]]
        print(f"  destination row had danger within 2 cols of sub at decision time: {len(dn)}; fatal among those {sum(e[4] for e in dn)} ({sum(e[4] for e in dn)/max(1,len(dn)):.1%}); fatal among the rest {sum(e[4] for e in moved if not e[3])}")
        print("  policy choice -> executed (counts):", dict(Counter(("nlurdf"[e[0]] + '->' + "nlurdf"[e[1]]) for e in moved)))
        print("  total deaths:", sum(r[3] for r in res))
