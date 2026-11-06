"""Misc: (a) reply's '85% escape from a near enemy' check; (b) claim 4 stricter count of dithering moves."""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep")
import pickle, collections
import numpy as np, wsp
from r2_runner import own_row_status, NETS
net = wsp.load_npz(NETS["claude"])
env = wsp._make_env("asterix", 0); inner = env.env; f = wsp.make_obs_fn(env, "asterix")
inner.player_y = 4; inner.entities = [None] * 8; inner.entities[3] = [3, 4, True, False]
z = wsp.logits(net, f()); p = np.exp(z - z.max()); p /= p.sum()
print("near enemy (col3, moving right) in own row 4, other rows empty: P(n,u,d) = %.3f %.3f %.3f ; P(move away) = %.3f" % (p[0], p[2], p[4], p[2] + p[4]))

C = pickle.load(open("/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep/run_claude_200.pkl", "rb"))
cnt = collections.Counter()
for r in C:
    s = r["last3"][-1]
    if not (s["eff"] != s["a"] and s["eff"] in (2, 4) and not s["F"][s["a"]]):
        continue
    T = s["t"]; prev = r["last3"][-2]
    e = wsp._make_env("asterix", r["seed"]); inn = e.env; ff = wsp.make_obs_fn(e, "asterix")
    rng = np.random.default_rng(r["seed"] + 1_000_003)
    for t in range(T):
        zz = wsp.logits(net, ff()); pp = np.exp(zz - zz.max()); pp /= pp.sum()
        a = int(rng.choice(6, p=pp))
        if t == T - 1:
            y = inn.player_y; mv = prev["eff"]
            ty = y - 1 if mv == 2 else y + 1
            entered = own_row_status(inn, ty)
            vol = prev["a"] == prev["eff"]
            safe_own = prev["st"] in ("empty", "enemy_passed", "gold_passed")
            cnt["total"] += 1
            if vol and safe_own: cnt["voluntary & own row empty/passed"] += 1
            if vol and safe_own and entered != "gold_approach": cnt["... & entered row not approaching gold"] += 1
        e.act(a)
print(dict(cnt))
