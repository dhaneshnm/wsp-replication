import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp

# Build probe edits using ONLY the prompt's helper formulas:
#  column c in channel ch: rows c*6+ch : 600 : 60 ; row r in channel ch: rows r*60+ch : r*60+60 : 6
lines = []
for c in range(10):
    lines.append(f"W1[{c*6+3}:600:60, {c}] = 1   # ball (ch3) in column {c} -> unit {c}")
for r in range(10):
    lines.append(f"W1[{r*60+3}:{r*60+60}:6, {10+r}] = 1   # ball (ch3) in row {r} -> unit {10+r}")
for c in range(10):
    lines.append(f"W1[{c*6+0}:600:60, {20+c}] = 1   # paddle (ch0) in column {c} -> unit {20+c}")
text = "```edits\n" + "\n".join(lines) + "\n```\n"
res = wsp.apply_edits(text)
net, rep = res if isinstance(res, tuple) else (res, None)
print("parse report:", rep)

bad = 0; n = 0
for seed in range(100):
    env = wsp._make_env("breakout", seed)
    obs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed)
    for t in range(300):
        x = obs()
        pre = x @ net["W1"] + net["b1"]
        e = env.env
        col_units = np.flatnonzero(pre[0:10]); row_units = np.flatnonzero(pre[10:20]); pad_units = np.flatnonzero(pre[20:30])
        ok = (list(col_units) == [e.ball_x] and list(row_units) == [e.ball_y] and list(pad_units) == [e.pos])
        if not ok:
            bad += 1
            if bad <= 3:
                print("MISMATCH", seed, t, col_units, row_units, pad_units, (e.ball_y, e.ball_x, e.pos))
        n += 1
        _, d = env.act(int(rng.integers(6)))
        if d:
            break
print(f"probe steps: {n}, mismatches: {bad}")
