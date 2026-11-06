"""Independent instrumented runner (my code). Calls the real minatar Environment.act wrapper and detects sticky
overrides from env.last_action afterwards, instead of re-implementing the sticky draw. Keeps a deepcopy of the
environment before each step so the fatal step can be replayed counterfactually."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy
import numpy as np
import wsp
from minatar import Environment

CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz"


def obs_vec(inner):
    s = inner.state()
    c = inner.channels
    o = np.zeros((10, 10, 6), np.float32)
    o[..., 0] = s[..., c["sub_front"]] | s[..., c["sub_back"]]
    o[..., 1] = s[..., c["enemy_fish"]] | s[..., c["enemy_sub"]] | s[..., c["enemy_bullet"]]
    o[..., 2] = s[..., c["enemy_fish"]] | s[..., c["enemy_sub"]] | s[..., c["diver"]]
    o[..., 3] = s[..., c["friendly_bullet"]]
    o[..., 4] = s[..., c["trail"]] | s[..., c["sub_back"]]
    o[..., 5] = s[..., c["oxygen_guage"]] | s[..., c["diver_guage"]]
    return o.reshape(600)


def forward(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    h2 = np.tanh(h1 @ net["W2"] + net["b2"])
    return h1, h2, h2 @ net["W3"] + net["b3"]


def replay(snap, action, oxygen=None):
    """Replay one step from a pre-step snapshot with a forced action (sticky draw consumed, not applied)."""
    e = copy.deepcopy(snap)
    e.random.rand()               # the sticky draw Environment.act would make
    if oxygen is not None:
        e.env.oxygen = oxygen
    r, done = e.env.act(action)
    return done


def objects_in_row(inner, row):
    """Ground-truth danger objects in a row: (kind, col, moving_right)."""
    out = []
    for f in inner.e_fish:
        if f[1] == row: out.append(("fish", f[0], bool(f[2])))
    for s in inner.e_subs:
        if s[1] == row: out.append(("esub", s[0], bool(s[2])))
    for b in inner.e_bullets:
        if b[1] == row: out.append(("bullet", b[0], bool(b[2])))
    return out


def episode(net, seed, sticky=0.1, detail=False):
    env = Environment("seaquest", sticky_action_prob=sticky)
    env.seed(seed); env.reset()
    inner = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0; kills = 0.0; bonus = 0.0
    sticky_vert = []          # (policy a, executed, moved, dest_danger_cols6_9, dest_danger_rel, fatal)
    n_override = 0
    steps_log = []
    out = dict(seed=seed)
    for t in range(wsp.MAX_STEPS):
        x = obs_vec(inner)
        h1, h2, z = forward(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        snap = copy.deepcopy(env)
        y0, x0, d0, o0, surf0 = inner.sub_y, inner.sub_x, inner.diver_count, inner.oxygen, inner.surface
        if detail:
            g = x.reshape(10, 10, 6)
            above = objects_in_row(inner, y0 - 1) if y0 >= 1 else []
            steps_log.append(dict(t=t, row=y0, col=x0, d=d0, oxy=o0, a=a, h1=h1.copy(), h2=h2.copy(),
                                  above=above, danger=g[:, :, 1].copy()))
        r, done = env.act(a)
        ex = env.last_action
        # surfacing bonus: _surface with 6 divers sets count to 0 then decrements -> -1
        b = (o0 * 10 // 200) if (d0 == 6 and inner.diver_count == -1) else 0
        score += r; bonus += b; kills += r - b
        if ex != a:
            n_override += 1
            if ex in (2, 4):
                g = x.reshape(10, 10, 6)
                moved = inner.sub_y != y0
                yd = inner.sub_y
                dz = bool(g[yd, 6:10, 1].any()) if moved else False
                drel = bool(g[yd, max(0, x0 - 2):min(10, x0 + 2), 1].any()) if moved else False
                sticky_vert.append((a, ex, moved, dz, drel, bool(done)))
        if done:
            # cause of death
            if inner.sub_y == 0 and not surf0 and d0 == 0:
                cause = "surface_no_diver"
            elif not replay(snap, ex, oxygen=200):
                cause = "oxygen"
            else:
                cause = "collision"
            cf_policy_survives = (not replay(snap, a)) if ex != a else None
            out.update(cause=cause, last_a=a, last_ex=ex, last_row_pre=y0, last_row_post=inner.sub_y,
                       last_col=x0, d_at_death=inner.diver_count, cf_policy_survives=cf_policy_survives)
            break
    else:
        out.update(cause="cap")
    out.update(score=score, steps=t + 1, kills=kills, bonus=bonus, sticky_vert=sticky_vert, n_override=n_override)
    if detail:
        out["log"] = steps_log
    return out


def work(args):
    path, seeds, sticky, detail_fn = args
    net = wsp.load_npz(path)
    res = []
    for s in seeds:
        r = episode(net, s, sticky=sticky, detail=detail_fn is not None)
        if detail_fn is not None:
            r = detail_fn(net, r)
        res.append(r)
    return res


def run_many(path, seeds, sticky=0.1, detail_fn=None, workers=4):
    from concurrent.futures import ProcessPoolExecutor
    chunks = [(path, seeds[i::workers], sticky, detail_fn) for i in range(workers)]
    with ProcessPoolExecutor(workers) as ex:
        res = [r for part in ex.map(work, chunks) for r in part]
    res.sort(key=lambda r: r["seed"])
    return res
