import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp, json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
BASE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt%d/net.npz"
def run(args):
    k, seeds = args
    net = wsp.load_npz(BASE % k)
    out = []
    for seed in seeds:
        env = wsp._make_env("seaquest", seed); obs = wsp.make_obs_fn(env, "seaquest"); E = env.env
        rng = np.random.default_rng(seed + 1_000_003)
        score = 0.0; samp = Counter(); exe = Counter(); col = Counter(); T = wsp.MAX_STEPS
        for t in range(wsp.MAX_STEPS):
            x = obs(); z = wsp.logits(net, x); p = np.exp(z - z.max()); p /= p.sum()
            a = int(rng.choice(6, p=p))
            if E.sub_y >= 1: col[E.sub_x] += 1
            r, done = env.act(a); score += r
            samp[a] += 1; exe[env.last_action] += 1
            if done: T = t + 1; break
        out.append(dict(seed=seed, score=score, steps=T, samp=dict(samp), exe=dict(exe), col=dict(col)))
    return out
if __name__ == "__main__":
    res = {}
    for k in (1, 2, 3):
        seeds = list(range(200))
        with ProcessPoolExecutor(4) as ex:
            eps = [e for part in ex.map(run, [(k, seeds[i::4]) for i in range(4)]) for e in part]
        eps.sort(key=lambda e: e["seed"])
        sc = np.array([e["score"] for e in eps]); ln = np.array([e["steps"] for e in eps])
        S = Counter(); X = Counter(); C = Counter()
        for e in eps:
            S.update({int(a): v for a, v in e["samp"].items()}); X.update({int(a): v for a, v in e["exe"].items()}); C.update({int(c): v for c, v in e["col"].items()})
        tot = sum(S.values()); ctot = sum(C.values())
        net = wsp.load_npz(BASE % k)
        chk = [wsp.play_episode(net, "seaquest", s)[:2] for s in (0, 1, 2)]
        mine = [(eps[s]["score"], eps[s]["steps"]) for s in (0, 1, 2)]
        print(f"attempt{k}: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(len(sc)):.2f} mean_len {ln.mean():.1f} median_len {np.median(ln):.0f}")
        print(f"   sampled action share {[round(S[a]/tot,4) for a in range(6)]} (noop,left,up,right,down,fire)")
        print(f"   executed L/R per episode {(X[1]+X[3])/len(eps):.2f}; executed L/R share {(X[1]+X[3])/tot:.4f}")
        print(f"   sub column share (rows>=1) {[round(C[c]/ctot,3) for c in range(10)]}")
        print(f"   replica check vs wsp.play_episode seeds 0-2: mine {mine} official {chk}")
