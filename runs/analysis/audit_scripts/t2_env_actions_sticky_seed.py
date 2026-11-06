import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import hashlib
import numpy as np
import wsp

GAMES = ["breakout", "seaquest", "asterix"]

# Instrument: record (requested action passed to Environment.act, executed action passed to Env.act)
log = {}
orig_make = wsp._make_env
def instrumented_make(game, seed):
    env = orig_make(game, seed)
    log["env"] = env; log["req"] = []; log["exe"] = []
    w_act, g_act = env.act, env.env.act
    def g(a):
        log["exe"].append(a); return g_act(a)
    env.env.act = g
    def w(a):
        log["req"].append(a); return w_act(a)
    env.act = w
    return env
wsp._make_env = instrumented_make

# ---------- A. action index -> game action mapping (b3 forces one action)
print("A. action mapping (b3[a] = 50 forces action a; 30 steps; position deltas from game internals)")
for game in GAMES:
    for a in range(6):
        n = wsp.zero_net(); n["b3"][a] = 50.0
        env = orig_make(game, 7)
        e = env.env
        before = (getattr(e, "pos", None), getattr(e, "player_x", None), getattr(e, "player_y", None), getattr(e, "sub_x", None), getattr(e, "sub_y", None))
        # one step only (no sticky effect possible to change sign: sticky repeats a or initial 0)
        env.act(a)
        after = (getattr(e, "pos", None), getattr(e, "player_x", None), getattr(e, "player_y", None), getattr(e, "sub_x", None), getattr(e, "sub_y", None))
        print(f"   {game:9s} a={a} map={e.action_map[a]!r} before={before} after={after}")
    print("   action_map:", orig_make(game, 0).env.action_map)

# ---------- B. requested action equals the sampled argmax when p ~ 1; sticky rate on uniform policy
print("B. sticky actions")
for game in GAMES:
    req, exe, prev_exe = [], [], []
    for s in range(60):
        wsp.play_episode(wsp.zero_net(), game, seed=s)
        r, x = log["req"], log["exe"]
        req += r; exe += x; prev_exe += [0] + x[:-1]
    req, exe, prev_exe = map(np.array, (req, exe, prev_exe))
    differ = req != prev_exe
    stuck = (exe == prev_exe) & differ
    changed = exe != req
    print(f"   {game:9s} steps={len(req)}  P(executed != requested)={changed.mean():.4f} (expect 0.1*5/6=0.0833)  "
          f"P(stuck | requested != previous)={stuck.sum()/differ.sum():.4f} (expect 0.1)  "
          f"executed always in {{requested, previous}}: {bool(np.all((exe == req) | (exe == prev_exe)))}  "
          f"uniform requested freq={np.round(np.bincount(req, minlength=6)/len(req),3)}")

# ---------- C. seeding: same seed -> identical; different seeds -> distinct; env RNG shared with game; action RNG separate
print("C. seeding")
def traj(game, seed, net):
    sc, st, fr = wsp.play_episode(net, game, seed, record=True)
    h = hashlib.sha1(np.stack(fr).tobytes() + np.array(log["req"]).tobytes()).hexdigest()
    return sc, st, h
for game in GAMES:
    net = wsp.zero_net()
    a1, a2 = traj(game, 5, net), traj(game, 5, net)
    hs = [traj(game, s, net)[2] for s in range(200)]
    env = orig_make(game, 3)
    print(f"   {game:9s} seed 5 twice identical: {a1 == a2} {a1[:2]}; distinct trajectories among seeds 0..199: {len(set(hs))}; "
          f"wrapper.random is game.random: {env.random is env.env.random}; last_action at start: {env.last_action}")

# initial-state dependence on seed (breakout ball side) and seed 0 is honoured
starts = [orig_make("breakout", s).env.ball_x for s in range(1000)]
print("   breakout initial ball_x over seeds 0..999:", dict(zip(*np.unique(starts, return_counts=True))))
e0a, e0b = orig_make("seaquest", 0), orig_make("seaquest", 0)
print("   seed 0 honoured (two envs seeded 0 draw same next rand):", e0a.random.rand() == e0b.random.rand())

# action RNG vs env RNG: different generator types and seeds
print("   action rng: default_rng(seed + 1_000_003) ->", type(np.random.default_rng(1).bit_generator).__name__,
      "; env rng:", type(orig_make('breakout', 1).random).__name__, "(MT19937) seeded with seed")
