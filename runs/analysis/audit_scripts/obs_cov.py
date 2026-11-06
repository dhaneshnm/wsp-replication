import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

# per-source coverage: for every game channel, in how many steps was it nonempty, and did the
# harness obs light the mapped channel(s) at exactly those cells?
for g in ["seaquest", "asterix"]:
    env0 = wsp._make_env(g, 0)
    names = env0.env.channels
    hits = {n: 0 for n in names}
    bad = 0
    for ep in range(200):
        env = wsp._make_env(g, 10_000 + ep)
        obs = wsp.make_obs_fn(env, g)
        rng = np.random.default_rng(ep)
        for t in range(3000):
            s = env.state()
            o = obs().reshape(10, 10, 6)
            for n, k in names.items():
                if s[..., k].any():
                    hits[n] += 1
                for c, srcs in enumerate(wsp.CHANNEL_MAP[g]):
                    if n in srcs and not o[..., c][s[..., k]].all():
                        bad += 1
            # also: every lit harness cell must be backed by a mapped source cell
            for c, srcs in enumerate(wsp.CHANNEL_MAP[g]):
                src = np.zeros((10, 10), bool)
                for n in srcs:
                    src |= s[..., names[n]]
                if not np.array_equal(o[..., c].astype(bool), src):
                    bad += 1
            r, done = env.act(int(rng.integers(6)))
            if done:
                break
    print(f"{g}: steps-with-source-nonempty {hits}; violations={bad}")

# gauge sweep for seaquest: direct oxygen / diver_count settings
env = wsp._make_env("seaquest", 0)
e = env.env
e.e_fish = []; e.e_subs = []; e.divers = []; e.e_bullets = []; e.f_bullets = []
obs = wsp.make_obs_fn(env, "seaquest")
for oxy, dc in [(200, 0), (199, 0), (20, 0), (19, 0), (0, 0), (200, 1), (200, 6), (0, 6), (200, -1)]:
    e.oxygen, e.diver_count = oxy, dc
    row = obs().reshape(10, 10, 6)[9, :, 5].astype(int)
    print(f"oxygen={oxy:3d} divers={dc:2d} gauge row9 = {row.tolist()}")
