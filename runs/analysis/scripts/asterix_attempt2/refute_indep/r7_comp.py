"""Claim 6: bias-COMPENSATED lookahead for Claude (adds w*(H1_{y+-2}+1) so neutral boards are unchanged). seeds 0..199"""
import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep")
import numpy as np
import r5_variants as R
import wsp

def comp_look(n, w):
    n = R.cp(n)
    for y in range(1, 9):
        if y - 2 >= 1:
            n["W2"][7 + (y - 2), 7 + y] += w; n["b2"][7 + y] += w
        if y + 2 <= 8:
            n["W2"][7 + (y + 2), 15 + y] += w; n["b2"][15 + y] += w
    return n

def build(name):
    c = wsp.load_npz(R.CL)
    w = float(name.split("_")[-1])
    return comp_look(c, w), 0.1

def work(args):
    name, seeds = args
    net, st = build(name)
    return [R.play(net, s, st) for s in seeds]

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    name = sys.argv[1]
    net, _ = build(name)
    env = wsp._make_env("asterix", 0); inner = env.env; f = wsp.make_obs_fn(env, "asterix")
    inner.player_y = 5; inner.entities = [None] * 8
    z0 = wsp.logits(net, f())
    inner.entities[3 - 1] = [5, 3, True, False]
    z1 = wsp.logits(net, f())
    print(f"{name}: empty-board n,u,d {z0[[0,2,4]].round(2)}; immediate enemy 2 rows above: n,u,d {z1[[0,2,4]].round(2)}")
    seeds = list(range(200)); ch = [seeds[i::4] for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        res = [x for part in ex.map(work, [(name, c) for c in ch]) for x in part]
    sc = np.array([x[0] for x in res]); ln = np.array([x[1] for x in res])
    print(f"{name} seeds 0..199: mean {sc.mean():.2f} se {sc.std(ddof=1)/np.sqrt(200):.2f} mean_len {ln.mean():.1f}", flush=True)
