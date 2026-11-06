import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt1/"
CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt1/net.npz"
cl = wsp.load_npz(CL); va = wsp.load_npz(D + "variant_samedir.npz")
for k in cl:
    d = cl[k] != va[k]
    print("variant vs claude", k, "entries changed:", int(d.sum()))
Wd = (cl["W1"] != va["W1"]).reshape(10, 10, 6, 32)
print("changed entries by (channel, unit):", {(ch, u): int(Wd[:, :, ch, u].sum()) for ch in range(6) for u in range(32) if Wd[:, :, ch, u].any()})

def run_det(net, seed, maxT=10000, trace_loop=False):
    env = wsp._make_env("breakout", seed); env.sticky_action_prob = 0.0
    obs = wsp.make_obs_fn(env, "breakout"); e = env.env
    seen = {}; score = 0; hist = []
    for t in range(maxT):
        key = (e.ball_x, e.ball_y, e.ball_dir, e.pos, e.last_x, e.last_y, e.strike, e.brick_map.tobytes())
        if key in seen:
            return dict(start=seed, loop=(seen[key], t), score=score, bricks=int(e.brick_map.sum()), hist=hist)
        seen[key] = t
        a = int(np.argmax(wsp.logits(net, obs())))
        bdir, bx, by, pos = e.ball_dir, e.ball_x, e.ball_y, e.pos
        r, done = env.act(a); score += r
        ev = ""
        if by == 8 and not done and e.ball_y == 8 and bdir in (2, 3):
            ev = "catch-" + ("same" if (bdir == 2) == (e.ball_dir == 1) else "reverse")
        if r: ev += " brick"
        hist.append((t, (by, bx), bdir, pos, a, ev))
        if done:
            return dict(start=seed, loop=None, done=True, t=t + 1, score=score, bricks=int(e.brick_map.sum()), hist=hist)
    return dict(start=seed, loop=None, done=False, t=maxT, score=score, bricks=int(e.brick_map.sum()), hist=hist)

for name, net in [("claude", cl), ("variant", va)]:
    for seed in (0, 1):
        out = run_det(net, seed)
        print(name, "seed", seed, {k: v for k, v in out.items() if k != "hist"})
        if name == "claude" and out["loop"]:
            a, b = out["loop"]
            for h in out["hist"][a:b]:
                if h[5]: print("    ", h)
