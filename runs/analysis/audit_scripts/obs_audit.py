import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import re
import numpy as np
import wsp
from minatar import Environment

RUNS = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/runs"

# ---------- A: parse the prompt's mapping line, compare with CHANNEL_MAP
def prompt_map(game):
    txt = open(f"{RUNS}/{game}/reply/prompt.txt").read()
    line = [l for l in txt.splitlines() if l.startswith("How the 6 channels are built")][0]
    m = {}
    for ch, srcs in re.findall(r"channel (\d) \([a-z]+\) <- ([^;.]+)", line):
        srcs = srcs.strip()
        m[int(ch)] = [] if srcs == "nothing" else [s.strip() for s in srcs.split(",")]
    return [m[i] for i in range(6)]

for g in ["seaquest", "asterix"]:
    pm = prompt_map(g)
    env = Environment(g)
    names = set(env.env.channels)
    used = {s for c in wsp.CHANNEL_MAP[g] for s in c}
    print(f"[A] {g}: prompt map == CHANNEL_MAP: {pm == wsp.CHANNEL_MAP[g]}")
    print(f"    prompt map: {pm}")
    print(f"    unknown names in CHANNEL_MAP: {sorted(used - names)}; game channels unused: {sorted(names - used)}")
    print(f"    env.channels: {env.env.channels}")

# ---------- B: independent expected obs from internal game objects (prompt's English description)
def expected_seaquest(e):
    o = np.zeros((10, 10, 6), np.float32)
    o[e.sub_y, e.sub_x, 0] = 1
    bx = e.sub_x - 1 if e.sub_or else e.sub_x + 1
    o[e.sub_y, bx, 0] = 1           # player: front and back
    o[e.sub_y, bx, 4] = 1           # trail: submarine's back cell
    for x, y, *_ in e.e_fish + e.e_subs + e.e_bullets:
        o[y, x, 1] = 1              # danger
    for x, y, *_ in e.e_fish + e.e_subs + e.divers:
        o[y, x, 2] = 1              # reward
    for x, y, *_ in e.f_bullets:
        o[y, x, 3] = 1              # projectile
    for x, y, lr, *_ in e.e_fish + e.e_subs + e.divers:
        b = x - 1 if lr else x + 1
        if 0 <= b <= 9:
            o[y, b, 4] = 1          # trail behind enemy/diver
    ox = max(0, e.oxygen) * 10 // 200
    o[9, 0:ox, 5] = 1
    if e.diver_count > 0:
        o[9, 9 - e.diver_count:9, 5] = 1
    return o.reshape(600)

def expected_asterix(e):
    o = np.zeros((10, 10, 6), np.float32)
    o[e.player_y, e.player_x, 0] = 1
    for ent in e.entities:
        if ent is None:
            continue
        x, y, lr, gold = ent
        o[y, x, 2 if gold else 1] = 1
        b = x - 1 if lr else x + 1
        if 0 <= b <= 9:
            o[y, b, 4] = 1
    return o.reshape(600)

EXP = {"seaquest": expected_seaquest, "asterix": expected_asterix}

def seaquest_policy(e, rng):
    # heuristic to collect divers and surface, so gauges/diver bar/surfacing are exercised
    if e.diver_count >= 6 or (e.diver_count > 0 and e.oxygen < 60):
        return 2  # up
    if e.divers:
        d = min(e.divers, key=lambda d: abs(d[0] - e.sub_x) + abs(d[1] - e.sub_y))
        if d[1] < e.sub_y: return 2
        if d[1] > e.sub_y: return 4
        if d[0] < e.sub_x: return 1
        if d[0] > e.sub_x: return 3
    if e.sub_y == 0:
        return 4
    return int(rng.integers(6))

for g in ["seaquest", "asterix"]:
    steps = mism = 0
    cov = np.zeros(6, int)
    extra = {"max_divers": -99, "min_divers": 99, "surf6": 0, "min_oxy_bar": 10}
    first_bad = None
    for ep in range(300):
        env = wsp._make_env(g, ep)
        obs = wsp.make_obs_fn(env, g)
        rng = np.random.default_rng(ep)
        for t in range(3000):
            x = obs()
            exp = EXP[g](env.env)
            steps += 1
            if not np.array_equal(x, exp):
                mism += 1
                if first_bad is None:
                    d = np.argwhere(x.reshape(10, 10, 6) != exp.reshape(10, 10, 6))
                    first_bad = (ep, t, d[:5].tolist())
            cov += (x.reshape(10, 10, 6).sum(axis=(0, 1)) > 0)
            if g == "seaquest":
                e = env.env
                extra["max_divers"] = max(extra["max_divers"], e.diver_count)
                extra["min_divers"] = min(extra["min_divers"], e.diver_count)
                extra["min_oxy_bar"] = min(extra["min_oxy_bar"], int(x.reshape(10, 10, 6)[9, :, 5][:].sum()))
                a = seaquest_policy(e, rng) if ep % 2 == 0 else int(rng.integers(6))
                before = e.diver_count
            else:
                a = int(rng.integers(6))
            r, done = env.act(a)
            if g == "seaquest" and before == 6 and env.env.diver_count == -1:
                extra["surf6"] += 1
            if done:
                break
    print(f"[B] {g}: steps={steps} mismatches={mism} first_bad={first_bad}")
    print(f"    steps where harness channel c is nonempty: {cov.tolist()}")
    if g == "seaquest":
        print(f"    coverage: {extra}")

# ---------- C: index layout with a placed object
env = wsp._make_env("seaquest", 0)
e = env.env
e.sub_x, e.sub_y, e.sub_or = 3, 4, True
e.e_fish = [[7, 2, False, 5]]; e.e_subs = []; e.divers = [[1, 6, True, 5]]
e.e_bullets = [[8, 5, False]]; e.f_bullets = [[4, 4, True]]
e.oxygen = 100; e.diver_count = 2
x = wsp.make_obs_fn(env, "seaquest")()
on = sorted(int(i) for i in np.flatnonzero(x))
dec = [((i // 6) // 10, (i // 6) % 10, i % 6) for i in on]
print("[C] seaquest placed-object (row,col,ch) on:", dec)
print("    equals independent:", np.array_equal(x, expected_seaquest(e)))
