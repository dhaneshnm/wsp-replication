import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication"); sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2")
import collections
import numpy as np, wsp
from common import *

def worker(seeds):
    net = load("claude")
    C = collections.Counter(); pf = []
    for seed in seeds:
        env = wsp._make_env("asterix", seed); inner = env.env
        obsf = wsp.make_obs_fn(env, "asterix"); rng = np.random.default_rng(seed + 1_000_003)
        for t in range(wsp.MAX_STEPS):
            x = obsf(); h1, h2, z, p = forward(net, x)
            y = inner.player_y
            units = {0: h2[y - 1], 2: h2[7 + y], 4: h2[15 + y]}
            for a in (0, 2, 4):
                fat = try_action(inner, a)[1]
                flag = units[a] > 0.9
                C[(fat, flag)] += 1
                if fat: pf.append(p[a] + (p[5] if a == 0 else 0))
            a = int(rng.choice(6, p=p))
            r, d = env.act(a)
            if d: break
    return C, pf

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    n = int(sys.argv[1]); seeds = list(range(n)); chunks = [seeds[i::4] for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(worker, chunks))
    C = sum((r[0] for r in res), collections.Counter()); pf = np.concatenate([r[1] for r in res])
    print("(fatal, unit>0.9) counts over (state, vertical action) pairs:", dict(C))
    print("recall of fatal actions:", C[(True, True)] / (C[(True, True)] + C[(True, False)]))
    print("false-alarm rate on safe actions:", C[(False, True)] / (C[(False, True)] + C[(False, False)]))
    print("policy prob on fatal actions: median %.5f, 90th pct %.4f, 99th pct %.4f, max %.3f, share >0.01: %.4f" %
          (np.median(pf), np.percentile(pf, 90), np.percentile(pf, 99), pf.max(), (pf > 0.01).mean()))
