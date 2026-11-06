"""My own episode runner (independent of wsp.play_episode / analyst code).
Uses wsp only for env construction/obs and loading; replicates Environment.act by hand so that
the sticky draw is observable, and evaluates each action's immediate outcome with a hand-written
collision check (validated against the real `done` flag of the executed action every step)."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

GAME = "asterix"
CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz"


def fwd(net, x):
    a1 = np.tanh(x @ net["W1"] + net["b1"])
    a2 = np.tanh(a1 @ net["W2"] + net["b2"])
    return a2 @ net["W3"] + net["b3"], a1, a2


def would_die(E, a):
    """Does executing action a now end the episode (ignoring the spawn, which lands at x=0/9)?"""
    px, py = E.player_x, E.player_y
    if a == 1:
        px = max(0, px - 1)
    elif a == 3:
        px = min(9, px + 1)
    elif a == 2:
        py = max(1, py - 1)
    elif a == 4:
        py = min(8, py + 1)
    for ent in E.entities:
        if ent is None:
            continue
        x, y, right, gold = ent
        if x == px and y == py:
            if gold:
                continue  # collected, removed before move
            return True
        if E.move_timer == 0:
            nx = x + (1 if right else -1)
            if nx == px and y == py and not gold:
                return True
    return False


def run(net, seed, sticky=0.1, record=False, check=None):
    env = wsp._make_env(GAME, seed)
    env.sticky_action_prob = sticky
    E = env.env
    obs = wsp.make_obs_fn(env, GAME)
    rng = np.random.default_rng(seed + 1_000_003)
    gold_spawned = [0]
    orig = E._spawn_entity

    def spawn_wrap():
        before = [e is None for e in E.entities]
        orig()
        for i, e in enumerate(E.entities):
            if before[i] and e is not None and e[3]:
                gold_spawned[0] += 1
    E._spawn_entity = spawn_wrap

    score = 0.0
    agg = dict(states=0, rep_fatal=0, prev_move=0, prev_move_rep_fatal=0,
               pmax_lrf=0.0, pmin_lrf=1.0, pmax_lr=0.0)
    chk = []
    steps = []
    mismatch = 0
    cols = set()
    done = False
    t = 0
    for t in range(wsp.MAX_STEPS):
        x = obs()
        z, a1, a2 = fwd(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        # replicate Environment.act
        u = env.random.rand()
        fired = u < env.sticky_action_prob
        prev = env.last_action
        a_exec = prev if fired else a
        fatal = [would_die(E, b) for b in range(6)]
        row, col = E.player_y, E.player_x
        agg["states"] += 1
        agg["rep_fatal"] += fatal[prev]
        if prev in (2, 4):
            agg["prev_move"] += 1
            agg["prev_move_rep_fatal"] += fatal[prev]
        plrf = max(p[1], p[3], p[5])
        agg["pmax_lrf"] = max(agg["pmax_lrf"], float(plrf))
        agg["pmin_lrf"] = min(agg["pmin_lrf"], float(min(p[1], p[3], p[5])))
        agg["pmax_lr"] = max(agg["pmax_lr"], float(max(p[1], p[3])))
        if check is not None:
            chk.append(check(x, a1, E))
        cols.add(col)
        rec = dict(t=t, row=row, col=col, prev=prev, a=a, fired=fired, a_exec=a_exec,
                   fatal=fatal, p=p, move_timer=E.move_timer)
        env.last_action = a_exec
        r, done = E.act(a_exec)
        if bool(done) != fatal[a_exec]:
            mismatch += 1
        score += r
        if record or done:
            steps.append(rec)
        if done:
            break
    if not record:
        steps = steps[-1:] if done else []
    return dict(seed=seed, score=score, length=t + 1, done=bool(done), steps=steps, agg=agg, chk=chk,
                mismatch=mismatch, cols=sorted(cols), gold_spawned=gold_spawned[0])
