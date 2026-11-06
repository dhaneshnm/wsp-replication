# Claude's net with sticky_action_prob=0 (diagnostic; the scored setting is 0.1). Same seeding and sampling as wsp.play_episode.
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
from minatar import Environment
from concurrent.futures import ProcessPoolExecutor
CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"

def run(seeds):
    net = wsp.load_npz(CLAUDE); out = []
    for s in seeds:
        env = Environment("breakout", sticky_action_prob=0.0); env.seed(s); env.reset()
        obs = wsp.make_obs_fn(env, "breakout"); rng = np.random.default_rng(s + 1_000_003)
        sc = 0.0; offmodal = 0; done = False
        for t in range(wsp.MAX_STEPS):
            z = wsp.logits(net, obs()); p = np.exp(z - z.max()); p /= p.sum()
            a = int(rng.choice(6, p=p))
            if p[a] < 0.5: offmodal += 1
            r, done = env.act(a); sc += r
            if done: break
        out.append((s, sc, t+1, done, offmodal, env.env.ball_x if False else None))
    return out

if __name__ == "__main__":
    seeds = list(range(200))
    with ProcessPoolExecutor(4) as ex:
        res = sorted([e for part in ex.map(run, [seeds[i::4] for i in range(4)]) for e in part])
    sc = np.array([r[1] for r in res]); ln = np.array([r[2] for r in res]); dn = np.array([r[3] for r in res])
    print(f"sticky 0: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f} min {sc.min()} max {sc.max()} distinct scores {sorted(set(sc.tolist()))}")
    print(f"episodes reaching 10,000-step cap: {(ln >= 10000).sum()}/200; terminal (missed) episodes: {int(dn.sum())}; off-modal samples total: {sum(r[4] for r in res)}")
