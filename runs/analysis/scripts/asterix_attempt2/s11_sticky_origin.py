import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import pickle, collections
import numpy as np, wsp
from common import *
from hazard import row_status
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/"
which = sys.argv[1]
net = load(which)
eps = pickle.load(open(D + f"eps_{which}_200.pkl", "rb"))
origin = collections.Counter(); beyond = collections.Counter(); pm = []
for e in eps:
    c = e["cls"]
    if not (c["sticky"] and not c["chosen_fatal"]): continue
    T = e["steps"] - 1  # death step index
    env = wsp._make_env("asterix", e["seed"]); inner = env.env
    obsf = wsp.make_obs_fn(env, "asterix"); rng = np.random.default_rng(e["seed"] + 1_000_003)
    for t in range(T + 1):
        x = obsf(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        if t == T - 1:
            y = inner.player_y
            s_own = row_status(inner, y)
            prev_info = (s_own, p.copy())
        r, d = env.act(a)
        if t == T - 1:
            eff_prev = env.last_action
            if eff_prev in (2, 4):
                beyond_row = y - 2 if eff_prev == 2 else y + 2
                beyond[row_status(inner, beyond_row) if 1 <= beyond_row <= 8 else "off-board"] += 0  # placeholder
        if d: break
    s_own, pp = prev_info
    kind = "move" if eff_prev in (2, 4) else ACT[eff_prev]
    origin[(kind, s_own)] += 1
    if eff_prev in (2, 4): pm.append(pp[eff_prev])
print(which, "sticky deaths:", sum(origin.values()))
print("action taken at t-1 and own-row status at t-1:", sorted(origin.items(), key=lambda kv: -kv[1]))
print("policy prob of the t-1 move that was later repeated: median %.3f, quartiles %s" % (np.median(pm), np.percentile(pm, [25, 75]).round(3)))
