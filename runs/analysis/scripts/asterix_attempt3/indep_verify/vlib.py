"""Independent verification library (not derived from the analyst's common.py / instrument.py).

Drives MinAtar's inner game object directly and draws the sticky-action coin from the
same RandomState that minatar.Environment.act uses, so a run must reproduce
wsp.play_episode exactly (checked in check_repro.py).
"""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy
import numpy as np
import wsp

RUN = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt3/"
ASTRA_NPZ = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz"


def nets():
    return {"claude": wsp.load_npz(RUN + "net.npz"), "astra": wsp.load_npz(ASTRA_NPZ)}


def layers(net, x):
    a1 = np.tanh(x @ net["W1"] + net["b1"])
    a2 = np.tanh(a1 @ net["W2"] + net["b2"])
    z = a2 @ net["W3"] + net["b3"]
    q = np.exp(z - z.max())
    return a1, a2, z, q / q.sum()


def board(prow, items, pcol=5):
    """items: dicts with r, c, kind ('E'|'G'), dir (+1 right, -1 left), trail (bool, default: in-bounds)."""
    g = np.zeros((10, 10, 6), np.float32)
    g[prow, pcol, 0] = 1.0
    for it in items:
        g[it["r"], it["c"], 1 if it["kind"] == "E" else 2] = 1.0
        tc = it["c"] - it["dir"]
        if it.get("trail", True) and 0 <= tc <= 9:
            g[it["r"], tc, 4] = 1.0
    return g.reshape(600)


def obs_from_game(game):
    """Build the 600-vector straight from the game's entity list (independent of wsp.make_obs_fn)."""
    g = np.zeros((10, 10, 6), np.float32)
    g[game.player_y, game.player_x, 0] = 1.0
    for e in game.entities:
        if e is None:
            continue
        x, y, right, gold = e
        g[y, x, 2 if gold else 1] = 1.0
        tc = x - 1 if right else x + 1
        if 0 <= tc <= 9:
            g[y, tc, 4] = 1.0
    return g.reshape(600)


def episode(net, seed, sticky=0.1, instrument=False, max_steps=wsp.MAX_STEPS):
    from minatar import Environment
    env = Environment("asterix", sticky_action_prob=sticky)
    env.seed(seed)
    env.reset()
    game = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    last = 0
    score = 0.0
    log = []
    tracked = [None] * 8     # identity tracking of entity objects to count spawns
    gold_spawned = 0
    enemy_spawned = 0
    pre_snap = None
    for t in range(max_steps):
        x = obs_from_game(game)
        _, _, z, p = layers(net, x)
        a = int(rng.choice(6, p=p))
        u = env.random.rand()             # same draw Environment.act makes
        is_sticky = u < sticky
        ex = last if is_sticky else a
        last = ex
        if instrument:
            pre_snap = copy.deepcopy(game)   # includes RandomState at this point (after the sticky draw)
            rec = dict(t=t, py=game.player_y, px=game.player_x, ents=copy.deepcopy(game.entities),
                       mt=game.move_timer, ms=game.move_speed, a=a, ex=ex, sticky=bool(is_sticky),
                       p=p.astype(float))
        r, done = game.act(ex)
        score += r
        if instrument:
            rec["r"] = r
            rec["py1"] = game.player_y
            log.append(rec)
            for i, e in enumerate(game.entities):
                if e is not None and e is not tracked[i]:
                    if e[3]:
                        gold_spawned += 1
                    else:
                        enemy_spawned += 1
                tracked[i] = e
        if done:
            out = dict(seed=seed, score=score, steps=t + 1, done=True)
            if instrument:
                out.update(log=log, death_snap=pre_snap, gold_spawned=gold_spawned, enemy_spawned=enemy_spawned,
                           gold_in_flight=sum(1 for e in game.entities if e is not None and e[3]))
            return out
    out = dict(seed=seed, score=score, steps=max_steps, done=False)
    if instrument:
        out.update(log=log, death_snap=None, gold_spawned=gold_spawned, enemy_spawned=enemy_spawned,
                   gold_in_flight=sum(1 for e in game.entities if e is not None and e[3]))
    return out


def counterfactual_dies(snap, action):
    g = copy.deepcopy(snap)
    _, done = g.act(action)
    return bool(done)
