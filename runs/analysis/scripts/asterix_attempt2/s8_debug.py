import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import numpy as np, wsp
from common import *
net = load("claude")
def show(inner):
    for r in range(10):
        line = ""
        for c in range(10):
            ch = "."
            if inner.player_y == r and inner.player_x == c: ch = "P"
            for e in inner.entities:
                if e is not None and e[1] == r and e[0] == c:
                    ch = ("g" if e[3] else "E") + (">" if e[2] else "<")
                    ch = ch[0] if ch[0] != "." else ch
                    ch = ("G" if e[3] else "E") if True else ch
                    ch += ">" if e[2] else "<"
            line += f"{ch:3s}"
        print("   ", r, line)
def replay(seed, upto):
    env = wsp._make_env("asterix", seed); inner = env.env
    obsf = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    for t in range(upto + 1):
        x = obsf(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        if t >= upto - 2:
            h1, h2, _, _ = forward(net, x)
            y = inner.player_y
            print(f"t={t} player row {y} move_timer {inner.move_timer} P(n,u,d)=({p[0]:.3f},{p[2]:.3f},{p[4]:.3f}) chosen {ACT[a]}")
            print("    H1 rows1-8", h1[8:16].round(2), "H2", h1[16:24].round(2), "G", h1[24:32].round(2))
            print(f"    stay/up/down units: {h2[y-1]:+.2f} {h2[7+y]:+.2f} {h2[15+y]:+.2f}")
            show(inner)
        r, d = env.act(a)
        if t >= upto - 2: print("    effective", ACT[env.last_action], "done", d)
        if d: break
for seed, steps in [(int(s.split(":")[0]), int(s.split(":")[1])) for s in sys.argv[1:]]:
    print("##### seed", seed); replay(seed, steps - 1)
