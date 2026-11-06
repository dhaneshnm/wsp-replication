"""Detailed look at every missed rally (Claude, sticky 0.1, seeds 0-199) and at the
slack<3 rallies of the no-sticky run."""
import sys, json
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from collections import Counter

CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"
DX = {0: -1, 1: 1, 2: 1, 3: -1}
DOWN = {0: False, 1: False, 2: True, 3: True}
TUP = {0: 9, 1: 10, 2: 9, 3: 8, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11}


def fold(u):
    m = u % 20
    return 19 - m if m >= 10 else m


def raw(net, seed, sticky_p):
    env = wsp._make_env("breakout", seed); env.sticky_action_prob = sticky_p
    obs = wsp.make_obs_fn(env, "breakout"); g = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    log = []
    for t in range(wsp.MAX_STEPS):
        x = obs(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        rec = dict(bx=g.ball_x, by=g.ball_y, d=g.ball_dir, pb=g.pos, a=a)
        u = env.random.rand(); st = u < env.sticky_action_prob
        ae = env.last_action if st else a; env.last_action = ae
        r, done = g.act(ae)
        rec.update(st=bool(st), ae=ae, pa=g.pos, r=r, done=done)
        log.append(rec)
        if done:
            break
    return log


def mv(a):
    return {1: -1, 3: 1}.get(a, 0)


if __name__ == "__main__":
    net = wsp.load_npz(CL)
    R = json.load(open(sys.argv[1]))
    out = Counter()
    rs_slack = Counter()
    detail = []
    for ep in R:
        if not ep["done"]:
            continue
        log = raw(net, ep["seed"], 0.1)
        c = len(log) - 1
        e = log[c]; assert e["by"] == 8 and DOWN[e["d"]] and e["done"]
        x8 = e["bx"]; dx = DX[e["d"]]; c2 = x8 + dx if 0 <= x8 + dx <= 9 else None
        cset = {x8} | ({c2} if c2 is not None else set())
        # rally start = frame after previous catch
        prev = max([t for t in range(c) if log[t]["by"] == 8 and DOWN[log[t]["d"]]], default=-1)
        rs = prev + 1
        slack_rs = (c - rs + 1) - abs(log[rs]["pb"] - x8)
        t0 = c
        while t0 - 1 > prev and DOWN[log[t0 - 1]["d"]]:
            t0 -= 1
        slack_t0 = (c - t0 + 1) - abs(log[t0]["pb"] - x8)
        walks = [t for t in range(t0, c + 1) if c2 is not None and log[t]["pb"] == c2 and log[t]["pa"] == x8]
        exits = [t for t in range(t0, c + 1) if log[t]["pb"] in cset and log[t]["pa"] not in cset]
        kind = "other"
        if walks and exits and walks[0] < exits[-1]:
            w, x = walks[0], exits[-1]
            same_dir = mv(log[x]["ae"]) == mv(log[w]["ae"]) == -dx
            repeat_of_prev = log[x]["st"] and log[x]["ae"] == log[x - 1]["ae"]
            kind = ("walk+exit", "exit_sticky=%s" % log[x]["st"], "exit_same_dir_as_walk(-dx)=%s" % same_dir,
                    "exit_is_repeat_of_prev_eff_action=%s" % repeat_of_prev, "exit_at_catch_step=%s" % (x == c),
                    "walk_by_policy=%s" % (not log[w]["st"]))
        else:
            kind = ("no-walk", "slack_turn=%d" % slack_t0, "slack_rally_start=%d" % slack_rs)
        out[kind] += 1
        rs_slack[slack_rs] += 1
    for k, v in sorted(out.items(), key=lambda kv: -kv[1]):
        print(v, k)
    print("slack at rally start (all misses):", sorted(rs_slack.items()))
