"""Own instrumented replica of wsp.play_episode for breakout (same env seed, same
action RNG, same sticky draw order), logging true game state, sticky draws and
paddle moves, then per-rally measurements computed from the env's TRUE ball_dir."""
import sys, copy, json
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

CL = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"
AS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
DX = {0: -1, 1: 1, 2: 1, 3: -1}
DOWN = {0: False, 1: False, 2: True, 3: True}
TUP = {0: 9, 1: 10, 2: 9, 3: 8, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11}


def fold(u):
    m = u % 20
    return 19 - m if m >= 10 else m


def greedy_from(g, net, obs_of):
    """Drive a copied game Env with argmax actions, no sticky, until the ball
    leaves row 8 downward. Returns True if caught."""
    for _ in range(40):
        a = int(np.argmax(wsp.logits(net, obs_of(g))))
        by, d = g.ball_y, g.ball_dir
        r, done = g.act(a)
        if by == 8 and DOWN[d]:
            return not done
    return None


def restore(sn):
    from minatar.environments.breakout import Env
    g = Env()
    g.ball_x, g.ball_y, g.ball_dir, g.pos, bm, g.strike, g.last_x, g.last_y = sn
    g.brick_map = bm.copy()
    g.terminal = False
    return g


def obs_of_game(g):
    s = g.state()
    o = np.zeros((10, 10, 6), np.float32)
    o[..., 0] = s[..., 0]; o[..., 2] = s[..., 3]; o[..., 3] = s[..., 1]; o[..., 4] = s[..., 2]
    return o.reshape(600)


def run(args):
    which, seed, sticky_p = args
    if which == "tfix":
        sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/breakout_attempt3/refute")
        import counterfactual
        net = counterfactual.T_fix(wsp.load_npz(CL))
    else:
        net = wsp.load_npz(CL if which == "claude" else AS)
    env = wsp._make_env("breakout", seed)
    env.sticky_action_prob = sticky_p
    obs = wsp.make_obs_fn(env, "breakout")
    g = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    log = []  # per step: bx,by,lx,ly,d,p_before,a,sticky,a_eff,p_after,Hpre,Vpre
    snaps = {}
    score = 0.0
    done = False
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1pre = x @ net["W1"] + net["b1"]
        z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        bx, by, lx, ly, d, pb = g.ball_x, g.ball_y, g.last_x, g.last_y, g.ball_dir, g.pos
        if which in ("claude", "tfix"):
            Hp, Vp = float(h1pre[8]), float(h1pre[9])
        else:
            Hp, Vp = float(h1pre[4]), float(h1pre[5])
        # replicate Environment.act exactly
        u = env.random.rand()
        st = u < env.sticky_action_prob
        ae = env.last_action if st else a
        env.last_action = ae
        # snapshot game at each frame (cheap enough: only keep last 60)
        snaps[t] = (g.ball_x, g.ball_y, g.ball_dir, g.pos, g.brick_map.copy(), g.strike, g.last_x, g.last_y)
        snaps.pop(t - 60, None)
        r, done = g.act(ae)
        score += r
        log.append((bx, by, lx, ly, d, pb, a, st, ae, g.pos, Hp, Vp, r, done))
        if by == 8 and DOWN[d] and done:
            # missed rally: greedy no-sticky replay from rally start and from turn
            pass
        if done:
            break
    steps = len(log)
    # ------------- per-rally analysis
    rallies = []
    catch_idx = [t for t, e in enumerate(log) if e[1] == 8 and DOWN[e[4]]]
    prev_end = -1
    for c in catch_idx:
        bx, by, lx, ly, d, pb, a, st, ae, pa, Hp, Vp, r, dn = log[c]
        x8 = bx
        nx = bx + DX[d]
        c2 = nx if 0 <= nx <= 9 else None
        cset = {x8} | ({c2} if c2 is not None else set())
        t0 = c
        while t0 - 1 > prev_end and DOWN[log[t0 - 1][4]]:
            t0 -= 1
        start_ep = (t0 == 0)
        turn_row = log[t0][1]
        p0 = log[t0][5]
        acts = c - t0 + 1
        slack = acts - abs(p0 - x8)
        slack_set = acts - min(abs(p0 - q) for q in cset)
        # last rising frame
        up_diff = up_diff_read = None
        if t0 - 1 > prev_end:
            e = log[t0 - 1]
            assert not DOWN[e[4]]
            up_diff = fold(e[0] + DX[e[4]] * TUP[e[1]]) - x8
            dxr = 1 if e[10] > 0 else -1
            up_diff_read = fold(e[0] + dxr * TUP[e[1]]) - x8
        walk = walk_pol = 0
        sticky_exit = policy_exit = 0
        events = []
        for t in range(t0, c + 1):
            e = log[t]
            pbt, pat, stt = e[5], e[9], e[7]
            if c2 is not None and pbt == c2 and pat == x8:
                walk += 1
                walk_pol += (not stt)
                events.append(("walk", t - t0, bool(stt)))
            if pbt in cset and pat not in cset:
                if stt:
                    sticky_exit += 1
                else:
                    policy_exit += 1
                events.append(("exit", t - t0, bool(stt)))
        caught = not dn
        rec = dict(seed=seed, c=c, t0=t0, start_ep=start_ep, turn_row=turn_row, x8=x8, c2=c2,
                   p0=p0, acts=acts, slack=slack, slack_set=slack_set, up_diff=up_diff,
                   up_diff_read=up_diff_read, walk=walk, walk_pol=walk_pol,
                   sticky_exit=sticky_exit, policy_exit=policy_exit, caught=caught, events=events)
        rallies.append(rec)
        prev_end = c
    # misreads (true dir vs sign of the network's own direction units)
    mis = {}
    for e in log:
        bx, by, lx, ly, d, pb, a, st, ae, pa, Hp, Vp, r, dn = e
        if (Hp > 0) != (DX[d] > 0):
            k = ("H", "flat" if by == ly else "diag" if bx != lx else "vert", by)
            mis[str(k)] = mis.get(str(k), 0) + 1
        if (Vp > 0) != DOWN[d]:
            k = ("V", "flat" if by == ly else "diag" if bx != lx else "vert", by)
            mis[str(k)] = mis.get(str(k), 0) + 1
        if Hp == 0 or Vp == 0:
            mis["zero"] = mis.get("zero", 0) + 1
    # greedy no-sticky replay for the missed rally
    replay = None
    if done and rallies and not rallies[-1]["caught"]:
        R = rallies[-1]
        rs = rallies[-2]["c"] + 1 if len(rallies) > 1 else 0  # frame after previous catch (or episode start)
        res = {}
        for name, t in (("rally_start", rs), ("turn", R["t0"])):
            if t in snaps:
                res[name] = greedy_from(restore(snaps[t]), net, obs_of_game)
            else:
                res[name] = "nosnap"
        replay = res
    return dict(which=which, seed=seed, sticky=sticky_p, score=score, steps=steps, done=done,
                rallies=rallies, mis=mis, replay=replay)


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    which = sys.argv[1]
    sticky_p = float(sys.argv[2])
    n = int(sys.argv[3])
    out = sys.argv[4]
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(which, s, sticky_p) for s in range(n)], chunksize=5))
    json.dump(res, open(out, "w"))
    print("done", which, sticky_p, n, "mean score", np.mean([r["score"] for r in res]))
