import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import pickle, collections, numpy as np, wsp
from common import *
from hazard import row_status
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/"
net = load("claude")
eps = pickle.load(open(D + "eps_claude_200.pkl", "rb"))
rows = []
for e in eps:
    c = e["cls"]
    if not (c["sticky"] and not c["chosen_fatal"]): continue
    T = e["steps"] - 1
    env = wsp._make_env("asterix", e["seed"]); inner = env.env
    obsf = wsp.make_obs_fn(env, "asterix"); rng = np.random.default_rng(e["seed"] + 1_000_003)
    for t in range(T + 1):
        x = obsf(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        if t == T - 1:
            y = inner.player_y; own = row_status(inner, y)
            up_s = row_status(inner, y-1) if y > 1 else "edge"; dn_s = row_status(inner, y+1) if y < 8 else "edge"
            pp = p.copy(); chosen = a
        r, d = env.act(a)
        if t == T - 1: eff = env.last_action
        if d: break
    assert d and t == T
    tgt = up_s if eff == 2 else dn_s if eff == 4 else own
    rows.append(dict(seed=e["seed"], own=own, eff=ACT[eff], chosen=ACT[chosen], voluntary=(chosen == eff), p=pp[eff], tgt=tgt))
print("n sticky deaths", len(rows))
vert = [r for r in rows if r["eff"] in "ud"]
print("t-1 effective vertical:", len(vert), " voluntary (chosen==effective at t-1):", sum(r["voluntary"] for r in vert))
safe = [r for r in vert if r["own"] in ("empty", "enemy-passed")]
print("from empty/passed rows:", len(safe), " of which voluntary:", sum(r["voluntary"] for r in safe))
print(" target-row status of those moves:", collections.Counter(r["tgt"] for r in safe))
print(" p(move) for those: median %.3f; count p<=0.2: %d, p>0.5: %d" % (np.median([r["p"] for r in safe]), sum(r["p"] <= 0.2 for r in safe), sum(r["p"] > 0.5 for r in safe)))
print(" own x target crosstab:", collections.Counter((r["own"], r["tgt"]) for r in safe))
print(" gold-target moves p median:", np.median([r["p"] for r in safe if r["tgt"]=="gold-approach"]) if any(r["tgt"]=="gold-approach" for r in safe) else None)
dith = [r for r in safe if r["voluntary"] and r["tgt"] != "gold-approach"]
print("voluntary, safe-origin, non-gold-target moves:", len(dith), "of", len(rows), "sticky deaths; p median %.3f" % np.median([r["p"] for r in dith]))
print("all 175 vertical: p median %.3f" % np.median([r["p"] for r in vert]))
