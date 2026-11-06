"""Real states (seeds 0..9, policy rollouts as in wsp.play_episode): compare D_r with the reply's TABLE rows read literally,
and G_r with the reply's prose ("treasure at c5, at c4 or c6 approaching, more weakly at c3 or c7 approaching; trail cancels moving away")."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import collections, numpy as np, wsp
net = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
def S_table(x, right, gold):
    if gold: return None                     # table: "<= 0"
    appr = (x < 5 and right) or (x > 5 and not right)
    if x == 5: return 4
    if x in (4, 6) and appr: return 4
    if x in (3, 7) and appr: return 2
    if x in (2, 8): return 1                  # table row "c2 or c8 -> 1" (conflicts with "moving away -> 0" when receding)
    return 0
cnt = collections.Counter(); maxD = 0; maxD_gold = -9; g_bad = 0; n = 0
for seed in range(10):
    env = wsp._make_env("asterix", seed); obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003); inner = env.env
    for t in range(wsp.MAX_STEPS):
        x = obs(); h1 = np.tanh(x @ net["W1"] + net["b1"]); n += 1
        Dpre = np.arctanh(np.clip(h1[0:8], -0.999999, 0.999999)); Gpre = np.arctanh(np.clip(h1[16:24], -0.999999, 0.999999))
        S_from_D = (Dpre + 1.2) / 0.6; G_from = Gpre + 1.0
        for e in inner.entities:
            if e is None: continue
            ex, y, right, gold = e; i = y - 1
            st = S_table(ex, right, gold)
            if st is None:
                maxD_gold = max(maxD_gold, S_from_D[i])
                appr = (ex < 5 and right) or (ex > 5 and not right)
                want = 2 if (ex == 5 or (ex in (4, 6) and appr)) else 1 if (ex in (3, 7) and appr) else 0
                if (want > 0 and abs(G_from[i] - want) > 1e-3) or (want == 0 and G_from[i] > 1e-3): g_bad += 1
                cnt["gold"] += 1
            else:
                maxD = max(maxD, abs(S_from_D[i] - st)); cnt["enemy"] += 1
                if ex in (2, 8) and not ((ex < 5 and right) or (ex > 5 and not right)): cnt["enemy_c2c8_receding"] += 1
                if G_from[i] > 1e-3: g_bad += 1
        z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        r, done = env.act(int(rng.choice(6, p=p)))
        if done: break
print("states", n, dict(cnt))
print("max |S(from D) - table S| over enemy rows:", round(maxD, 4))
print("max S(from D) over gold rows (table says <= 0):", round(float(maxD_gold), 4))
print("gold/enemy rows where G deviates from reply prose:", g_bad)
