import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

GAME = "breakout"
SPEC = {0: "paddle", 1: None, 2: "brick", 3: "ball", 4: "trail", 5: None}  # from prompt THE INPUT
NAMES = ["player", "danger", "reward", "projectile", "trail", "gauge"]

print("CHANNEL_MAP['breakout'] =", wsp.CHANNEL_MAP[GAME])

def spec_obs(env):
    """Independent re-implementation straight from the prompt text."""
    s = env.state()
    ch = env.env.channels
    x = np.zeros(600, dtype=np.float32)
    for row in range(10):
        for col in range(10):
            for c in range(6):
                src = SPEC[c]
                if src is not None and s[row, col, ch[src]]:
                    x[(row * 10 + col) * 6 + c] = 1.0
    return x

def grid(x, c):
    g = x.reshape(10, 10, 6)[:, :, c]
    return ["".join("#" if v else "." for v in r) for r in g]

env = wsp._make_env(GAME, seed=3)
obs = wsp.make_obs_fn(env, GAME)
print("raw channels:", env.env.channels, "state shape:", env.state().shape, "dtype:", env.state().dtype)

rng = np.random.default_rng(0)
mismatch = 0
for t in range(6):
    e = env.env
    x = obs()
    y = spec_obs(env)
    mismatch += int(not np.array_equal(x, y))
    print(f"\n--- step {t}: ball (y={e.ball_y},x={e.ball_x}) last (y={e.last_y},x={e.last_x}) paddle pos={e.pos} dir={e.ball_dir}")
    # direct index probes using the prompt formula
    bi = (e.ball_y * 10 + e.ball_x) * 6 + 3
    pi = (9 * 10 + e.pos) * 6 + 0
    ti = (e.last_y * 10 + e.last_x) * 6 + 4
    print(f"  x[ball idx {bi}]={x[bi]}  x[paddle idx {pi}]={x[pi]}  x[trail idx {ti}]={x[ti]}")
    print(f"  per-channel sums: {[int(x.reshape(10,10,6)[:,:,c].sum()) for c in range(6)]}  brick_map sum={int(e.brick_map.sum())}")
    if t in (0, 3):
        for c in range(6):
            print(f"  ch{c} {NAMES[c]:<10}", " ".join(grid(x, c)))
        print("  raw brick_map rows:", " ".join("".join("#" if v else "." for v in r) for r in e.brick_map))
    a = int(rng.choice([0, 1, 3]))
    r, done = env.act(a)
    if done:
        break

# brute check over many random steps / seeds
tot = 0
for seed in range(200):
    env = wsp._make_env(GAME, seed)
    obs = wsp.make_obs_fn(env, GAME)
    r_ = np.random.default_rng(seed)
    for t in range(400):
        x = obs(); y = spec_obs(env)
        tot += 1
        if not np.array_equal(x, y):
            mismatch += 1
        # value set & dims
        assert x.shape == (600,) and set(np.unique(x)).issubset({0.0, 1.0})
        _, d = env.act(int(r_.integers(6)))
        if d:
            break
print(f"\nchecked {tot} observations; mismatches vs spec re-implementation: {mismatch}")
# spec examples
print("index examples: input 0 ->", np.unravel_index(0, (10,10,6)), " input 6 ->", np.unravel_index(6, (10,10,6)), " input 599 ->", np.unravel_index(599, (10,10,6)))
