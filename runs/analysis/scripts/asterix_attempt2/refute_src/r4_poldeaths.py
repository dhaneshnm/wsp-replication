import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import pickle, numpy as np, wsp
from common import *
from hazard import row_status
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/"
net = load("claude")
eps = pickle.load(open(D + "eps_claude_200.pkl", "rb"))
for e in eps:
    c = e["cls"]
    if (c["sticky"] and not c["chosen_fatal"]) or not c["safe_vert"]: continue
    T = e["steps"] - 1
    env = wsp._make_env("asterix", e["seed"]); inner = env.env
    obsf = wsp.make_obs_fn(env, "asterix"); rng = np.random.default_rng(e["seed"] + 1_000_003)
    for t in range(T + 1):
        x = obsf(); h1, h2, z, p = forward(net, x)
        a = int(rng.choice(6, p=p))
        if t == T:
            y = inner.player_y
            print(f"seed {e['seed']} row {y} own={row_status(inner,y)} H2own={h1[15+y]:+.2f} stay/up/down={h2[y-1]:+.2f}/{h2[7+y]:+.2f}/{h2[15+y]:+.2f} P(n,u,d)=({p[0]:.3f},{p[2]:.3f},{p[4]:.3f}) chosen {ACT[a]} p_fatal={c['p_fatal']:.4f}")
        r, d = env.act(a)
        if d: break
