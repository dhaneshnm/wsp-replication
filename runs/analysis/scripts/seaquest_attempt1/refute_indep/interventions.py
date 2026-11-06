"""Policy interventions on the Claude net (independent implementation).
variants:
  base          : unmodified (sanity, should equal wsp.play_episode)
  surf_rule     : when env surfacing condition holds and the sampled action is up, replace with fire if an enemy/bullet
                  is in the row above within 2 columns of the front (re-implementation of the stated oracle)
  surf_look     : when the surfacing condition holds and sampled action is up, simulate the up step on a copy of the
                  env; if it kills, replace with fire (one-step lookahead oracle)
  mask_lr       : actions left/right removed from the softmax (renormalized)
  lr_to_fire    : sampled left/right replaced by fire
"""
import sys, os, copy
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from concurrent.futures import ProcessPoolExecutor

D = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt1/"


def kills(env, a):
    c = copy.deepcopy(env); c.random.rand(); c.last_action = a
    return c.env.act(a)[1]


def ep(args):
    variant, seed = args
    net = wsp.load_npz(D + "net.npz")
    env = wsp._make_env("seaquest", seed); g = env.env
    ob = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0; n_override = 0
    for t in range(wsp.MAX_STEPS):
        z = wsp.logits(net, ob())
        if variant == "mask_lr":
            z = z.copy(); z[[1, 3]] = -np.inf
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        surf = g.oxygen < 60 and g.diver_count >= 1
        if variant == "surf_rule" and a == 2 and surf and g.sub_y >= 1:
            above = g.sub_y - 1
            if any(o[1] == above and abs(o[0] - g.sub_x) <= 2 for o in g.e_fish + g.e_subs + g.e_bullets):
                a = 5; n_override += 1
        elif variant == "surf_look" and a == 2 and surf:
            if kills(env, 2):
                a = 5; n_override += 1
        elif variant == "lr_to_fire" and a in (1, 3):
            a = 5; n_override += 1
        r, done = env.act(a); score += r
        if done: break
    return score, t + 1, n_override


if __name__ == "__main__":
    variant, n = sys.argv[1], int(sys.argv[2])
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(ep, [(variant, s) for s in range(n)], chunksize=5))
    s = np.array([r[0] for r in res]); L = np.array([r[1] for r in res]); o = np.array([r[2] for r in res])
    print(f"{variant:12s} n={n} mean {s.mean():.3f} se {s.std(ddof=1)/np.sqrt(n):.3f} mean_len {L.mean():.1f} overrides/ep {o.mean():.2f}")
