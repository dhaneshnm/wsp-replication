"""Claim 5: for each Claude 'trapped' death (noop/up/down all fatal), replay to the death step, then on a
deep copy of the game try left and right, and check whether some continuation of 1 and 3 further
steps (any of noop/left/up/right/down, no sticky) also survives."""
import sys
HERE = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1/indep_verify"
sys.path.insert(0, HERE)
import copy, itertools, pickle
from collections import Counter
import numpy as np
import common, wsp


def replay_to(net, seed, T):
    env = wsp._make_env("asterix", seed)
    E = env.env
    obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    for t in range(T + 1):
        x = obs()
        z, _, _ = common.fwd(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        u = env.random.rand()
        a_exec = env.last_action if u < 0.1 else a
        if t == T:
            return E, a_exec
        env.last_action = a_exec
        r, done = E.act(a_exec)
        assert not done


def survives(E, seq):
    E2 = copy.deepcopy(E)
    for a in seq:
        r, d = E2.act(a)
        if d:
            return False
    return True


net = wsp.load_npz(common.CLAUDE)
res = pickle.load(open(f"{HERE}/main_claude01.pkl", "rb"))
cnt = Counter()
rows = Counter()
for r in res:
    d = r["steps"][-1]
    f = d["fatal"]
    if not all(f[b] for b in (0, 2, 4)):
        continue
    E, a_exec = replay_to(net, r["seed"], d["t"])
    # sanity: executing the real action on a copy dies
    assert not survives(E, [a_exec])
    side1 = any(survives(E, [s]) for s in (1, 3))
    side2 = any(survives(E, [s, b]) for s in (1, 3) for b in (0, 1, 2, 3, 4))
    side4 = any(survives(E, [s, *seq]) for s in (1, 3) for seq in itertools.product((0, 1, 2, 3, 4), repeat=3))
    own_any = any(survives(E, [b]) for b in (0, 2, 4))
    cnt["trapped"] += 1
    cnt["own action survives (should be 0)"] += own_any
    cnt["sideways survives 1 step"] += side1
    cnt["sideways + 1 more step survives"] += side2
    cnt["sideways + 3 more steps survives"] += side4
    rows[d["row"]] += 1
print(dict(cnt))
print("trapped deaths by row:", dict(sorted(rows.items())), " edge rows (1,8):", rows[1] + rows[8])
