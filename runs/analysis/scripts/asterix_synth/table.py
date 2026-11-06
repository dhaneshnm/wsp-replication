"""Uniform per-net table on seeds 0..N-1 (same RNG as wsp.play_episode).
Records score, length, executed row changes, gold spawned, and at the death step
whether sticky changed the action and whether the sampled action would have survived."""
import sys, copy
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from concurrent.futures import ProcessPoolExecutor

R = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix"
NETS = {
    "claude_a1": f"{R}/attempt1/net.npz",
    "claude_a2": f"{R}/attempt2/net.npz",
    "claude_a3": f"{R}/attempt3/net.npz",
    "astra": "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz",
}


def episode(args):
    path, seed = args
    net = wsp.load_npz(path)
    env = wsp._make_env("asterix", seed)
    obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    g = env.env
    spawned = [0]
    orig = g._spawn_entity

    def wrapped():
        before = list(g.entities)
        orig()
        for i in range(8):
            e = g.entities[i]
            if e is not None and e is not before[i] and e[3]:
                spawned[0] += 1

    g._spawn_entity = wrapped
    score, rowchg, cols = 0.0, 0, set()
    death = None
    for t in range(wsp.MAX_STEPS):
        x = obs()
        z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        y0 = g.player_y
        snap = copy.deepcopy(g)
        snap._spawn_entity = None  # not used: counterfactual only needs act
        r, done = env.act(a)
        cols.add(g.player_x)
        if g.player_y != y0:
            rowchg += 1
        score += r
        if done:
            executed = env.last_action
            sticky_changed = executed != a
            # counterfactual: would the sampled action have survived this step?
            cf = copy.deepcopy(snap)
            cf._spawn_entity = type(cf)._spawn_entity.__get__(cf)
            _, d2 = cf.act(a)
            death = dict(sticky_changed=bool(sticky_changed), sampled=a, executed=int(executed),
                         sampled_safe=not d2, row=int(y0))
            return dict(score=score, length=t + 1, rowchg=rowchg, spawned=spawned[0], death=death, cols=cols)
    return dict(score=score, length=wsp.MAX_STEPS, rowchg=rowchg, spawned=spawned[0], death=None, cols=cols)


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    for name, path in NETS.items():
        with ProcessPoolExecutor(4) as ex:
            res = list(ex.map(episode, [(path, s) for s in range(N)], chunksize=10))
        sc = np.array([r["score"] for r in res]); ln = np.array([r["length"] for r in res])
        sp = sum(r["spawned"] for r in res); rc = sum(r["rowchg"] for r in res)
        deaths = [r["death"] for r in res if r["death"]]
        st_safe = sum(d["sticky_changed"] and d["sampled_safe"] for d in deaths)
        st_vert = sum(d["sticky_changed"] and d["sampled_safe"] and d["executed"] in (2, 4) for d in deaths)
        own_fatal_with = sum((not d["sticky_changed"]) for d in deaths)
        cols = set().union(*[r["cols"] for r in res])
        print(f"{name}: seeds 0..{N-1} mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(N):.2f} "
              f"mean_len {ln.mean():.1f} score/step {sc.sum()/ln.sum():.4f} "
              f"gold spawned {sp} collected {int(sc.sum())} capture {sc.sum()/sp:.3f} "
              f"row changes/100 steps {100*rc/ln.sum():.2f} cols {sorted(cols)}")
        print(f"   deaths {len(deaths)}: sticky-changed & sampled action safe {st_safe} "
              f"(of which executed up/down {st_vert}); executed == sampled {own_fatal_with}")
        sys.stdout.flush()
