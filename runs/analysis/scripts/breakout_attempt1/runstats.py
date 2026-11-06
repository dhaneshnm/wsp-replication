import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from instr import sim_landing, DIRV
import pickle
from collections import Counter

def target_cols(net, by, bx, ly, lx):
    xs = np.stack([make_obs((by, bx), (ly, lx), p) for p in range(10)])
    h1 = np.tanh(xs @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"]); z = h2 @ net["W3"] + net["b3"]
    return [p for p in range(10) if np.argmax(z[p]) == 0]

def run(args):
    net, seed, mode, sticky = args
    env = wsp._make_env("breakout", seed)
    env.sticky_action_prob = sticky
    obs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed + 1_000_003)
    e = env.env
    score = 0.0; last_r = 0
    st = Counter()
    tcache = {}
    drought_steps = 0
    first_drought = None
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1, h2, z, p = forward(net, x)
        a = int(np.argmax(p)) if mode == "argmax" else int(rng.choice(6, p=p))
        bx8, nx, k = sim_landing(e)
        vx, vy = DIRV[e.ball_dir]
        # gate checks
        gH, gV = np.sign(h1[4]), np.sign(h1[5])
        dy = e.ball_y - e.last_y; dx = e.ball_x - e.last_x
        st["steps"] += 1
        if gH != vx: st["gH_err"] += 1; st[f"gH_err dx={dx} dy={dy} r={e.ball_y} c={e.ball_x}"] += 1
        if gV != vy: st["gV_err"] += 1; st[f"gV_err dx={dx} dy={dy} r={e.ball_y} dir={e.ball_dir}"] += 1
        key = (e.ball_y, e.ball_x, e.last_y, e.last_x)
        if key not in tcache: tcache[key] = target_cols(net, *key)
        T = tcache[key]
        C = {bx8, nx}
        if vy == 1:
            st["desc_steps"] += 1
            if not (set(T) & C): st["desc_target_wrong"] += 1
        else:
            st["asc_steps"] += 1
            if set(T) & C: st["asc_target_right"] += 1
            st["asc_target_err_sum"] += min(abs(tt - c) for tt in T for c in C) if T else 0
        nb = int(e.brick_map.sum()); pos0 = e.pos
        r, done = env.act(a)
        if env.last_action != a: st["sticky_changed"] += 1
        if k == 1 and not done:
            st["catches"] += 1
            if e.pos == bx8: st["catch_same_dir"] += 1
            else: st["catch_reverse"] += 1
        score += r
        if r: last_r = t
        if t - last_r > 100:
            drought_steps += 1
            if first_drought is None: first_drought = (t - 100, score)
        if done:
            break
    st["score"] = score; st["len"] = t + 1; st["done"] = int(done); st["drought_steps"] = drought_steps
    st["first_drought_t"] = first_drought[0] if first_drought else -1
    st["first_drought_score"] = first_drought[1] if first_drought else -1
    return st

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    which, mode, sticky, n = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
    net = nets()[which] if which in ("claude","astra") else wsp.load_npz(which + ".npz")
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(run, [(net, s, mode, sticky) for s in range(n)], chunksize=5))
    pickle.dump(res, open(f"stats_{which}_{mode}_{sticky}_{n}.pkl", "wb"))
    tot = Counter()
    for r in res: tot.update(r)
    sc = np.array([r["score"] for r in res])
    print(f"{which} mode={mode} sticky={sticky} n={n}: mean score {sc.mean():.2f} (se {sc.std(ddof=1)/np.sqrt(n):.2f}), median {np.median(sc)}, misses {tot['done']}, mean len {tot['len']/n:.0f}")
    print(f"  catches {tot['catches']}, misses/catch {tot['done']/max(1,tot['catches']):.5f}, bricks/catch {tot['score']/max(1,tot['catches']):.4f}")
    print(f"  catch type: same-horizontal-dir {tot['catch_same_dir']}, reverse {tot['catch_reverse']}")
    print(f"  steps >100 after last reward: {tot['drought_steps']} of {tot['steps']} ({tot['drought_steps']/tot['steps']:.3f})")
    print(f"  gate errors: gH {tot['gH_err']}/{tot['steps']}, gV {tot['gV_err']}/{tot['steps']}")
    for k_, v in sorted(((k_, v) for k_, v in tot.items() if k_.startswith('g') and '=' in k_), key=lambda kv: -kv[1])[:8]: print(f"     {v:7d} {k_}")
    print(f"  descending steps {tot['desc_steps']}, net target not a catch column {tot['desc_target_wrong']}")
    print(f"  ascending steps {tot['asc_steps']}, net target already a catch column {tot['asc_target_right']} ({tot['asc_target_right']/max(1,tot['asc_steps']):.3f}), mean |target err| {tot['asc_target_err_sum']/max(1,tot['asc_steps']):.2f}")
    print(f"  executed action changed by sticky: {tot['sticky_changed']}")
    fd = np.array([r['first_drought_t'] for r in res]); fs = np.array([r['first_drought_score'] for r in res])
    print(f"  episodes with a >100-step reward drought: {(fd>=0).sum()}; median start step {np.median(fd[fd>=0]) if (fd>=0).any() else None}; median score at its start {np.median(fs[fd>=0]) if (fd>=0).any() else None}")
