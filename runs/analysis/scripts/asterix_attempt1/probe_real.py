"""Real-state check: compare Claude's D_r / G_r units with values computed from the env's entity list
using the reply's table, and check the policy's choices against simulated one-step fatality."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy, collections
import numpy as np
import wsp

net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
EW = {2: 1, 3: 2, 4: 4, 5: 6, 6: 4, 7: 2, 8: 1}   # reply: enemy weights c2..c8
TW = {4: -2, 5: -4, 6: -2}                        # reply: trail weights
GW = {3: 1, 4: 2, 5: 3, 6: 2, 7: 1}; GT = {4: -1, 5: -2, 6: -1}


def table_S(e):
    x, y, right, gold = e
    back = x - 1 if right else x + 1
    t = TW.get(back, 0) if 0 <= back <= 9 else 0
    return (0 if gold else EW.get(x, 0)) + t


def table_G(e):
    x, y, right, gold = e
    back = x - 1 if right else x + 1
    t = GT.get(back, 0) if 0 <= back <= 9 else 0
    return (GW.get(x, 0) if gold else 0) + t


maxdiff_D = maxdiff_G = 0.0
n_states = 0
stats = collections.Counter()
for seed in range(20):
    env = wsp._make_env("asterix", seed); obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003); inner = env.env
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1 = np.tanh(x @ net["W1"] + net["b1"])
        S = np.zeros(8); G = np.zeros(8)
        for e in inner.entities:
            if e is not None:
                S[e[1] - 1] = table_S(e); G[e[1] - 1] = table_G(e)
        maxdiff_D = max(maxdiff_D, np.abs(h1[0:8] - np.tanh(0.6 * S - 1.2)).max())
        maxdiff_G = max(maxdiff_G, np.abs(h1[16:24] - np.tanh(G - 1.0)).max())
        n_states += 1
        z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        fat = {}
        for b in (0, 2, 4):
            ec = copy.deepcopy(inner); ec.act(b); fat[b] = ec.terminal
        best = max((0, 2, 4), key=lambda b: z[b])
        safe_exists = not all(fat.values())
        stats["states"] += 1
        stats["move_frame" if inner.move_timer == 0 else "non_move_frame"] += 1
        if safe_exists:
            stats["safe_exists"] += 1
            stats["p_mass_on_fatal_when_safe_exists"] += sum(p[b] for b in fat if fat[b])
            if fat[best]:
                stats["argmax_fatal_when_safe_exists"] += 1
                stats["argmax_fatal_when_safe_exists_movetimer=%d" % inner.move_timer] += 1
        else:
            stats["all_vertical_fatal"] += 1
        a = int(rng.choice(6, p=p))
        r, done = env.act(a)
        if done:
            break
print(f"real states checked: {n_states} (seeds 0..19)")
print(f"max |D_r(net) - tanh(0.6*S_table - 1.2)| = {maxdiff_D:.2e}")
print(f"max |G_r(net) - tanh(G_table - 1)|      = {maxdiff_G:.2e}")
for k, v in sorted(stats.items()):
    print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
