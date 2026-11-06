"""Independent instrumented replica of wsp.play_episode (same RNG call order). Written for refutation checks."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp

CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt3/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz"

def guard2(n):
    # same edit as analyst's variants.py guard2, re-typed: add U_{r-2} veto to Up_r, U_{r+2} veto to Down_r
    n = {k: v.copy() for k, v in n.items()}
    for r in range(3, 9):          # Up_r is L2 unit r-1; U_{r-2} is L1 unit 17+(r-2)-1
        n["W2"][17 + (r - 2) - 1, r - 1] = -75; n["b2"][r - 1] -= 75
    n["W2"][17 + 2 - 1, 8] = -75; n["b2"][8] -= 75     # Down_0 (unit 8) also checks U_2
    for r in range(1, 7):          # Down_r is L2 unit 8+r; U_{r+2} is L1 unit 17+(r+2)-1
        n["W2"][17 + (r + 2) - 1, 8 + r] = -75; n["b2"][8 + r] -= 75
    return n

def run(net, seed, sticky=None, detail=False):
    env = wsp._make_env("seaquest", seed)
    if sticky is not None: env.sticky_action_prob = sticky
    obs = wsp.make_obs_fn(env, "seaquest"); e = env.env
    rng = np.random.default_rng(seed + 1_000_003)
    W1, b1, W2, b2, W3, b3 = (net[k] for k in ("W1", "b1", "W2", "b2", "W3", "b3"))
    score = 0.0; bonus = 0; ev = []; win = []
    out = dict(seed=seed)
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1 = np.tanh(x @ W1 + b1); h2 = np.tanh(h1 @ W2 + b2); z = h2 @ W3 + b3
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        y0, x0, d0, o0, surf0 = e.sub_y, e.sub_x, e.diver_count, e.oxygen, e.surface
        if detail:
            g = x.reshape(10, 10, 6)
            objs = [(o[0], o[1], bool(o[2]), k) for k, L in (("fish", e.e_fish), ("sub", e.e_subs), ("bullet", e.e_bullets)) for o in L]
            win.append(dict(t=t, y=y0, x=x0, d=d0, o=o0, h1=h1, h2=h2, z=z, a=a, g_danger=g[:, :, 1].copy(), objs=objs))
            pass
        aa = a
        if env.random.rand() < env.sticky_action_prob:
            aa = env.last_action
        env.last_action = aa
        r, done = e.act(aa)
        if e.sub_y == 0 and y0 > 0 and d0 == 6:
            bonus += o0 * 10 // 200
        score += r
        if aa != a and aa in (2, 4):
            g = x.reshape(10, 10, 6)
            moved = e.sub_y != y0
            ydest = e.sub_y
            ev.append(dict(t=t, a=a, aa=aa, y0=y0, x0=x0, ydest=ydest, moved=moved,
                           d69=bool(g[ydest, 6:10, 1].any()) if moved else False,
                           dnear=bool(g[ydest, max(0, x0 - 2):min(10, x0 + 2), 1].any()) if moved else False,
                           done=bool(done)))
        if done:
            if e.oxygen < 0: cause = "oxygen"
            elif e.sub_y == 0 and e.diver_count == 0 and y0 > 0: cause = "surface_no_diver"
            else: cause = "collision"
            out.update(cause=cause, d_end=e.diver_count, y_end=e.sub_y, last_a=a, last_aa=aa, last_y0=y0)
            break
    else:
        out.update(cause="cap", d_end=e.diver_count)
    out.update(score=score, steps=t + 1, kills=score - bonus, bonus=bonus, ev=ev)
    if detail: out["win"] = win
    return out
