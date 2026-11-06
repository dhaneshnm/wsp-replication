"""Independent instrumented runner (claims 2,3,4,8,10).
Replays wsp.play_episode's exact sampling but judges fatality ANALYTICALLY from the entity list
(no deepcopy / env.act on copies), and self-checks that analytic fatality of the executed action == env's `done` on every step.
Usage: r2_runner.py <claude|astra> <n_episodes> <log_steps_for_first_k_seeds>
"""
import sys
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import pickle
import numpy as np
import wsp

NETS = {"claude": "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt2/net.npz",
        "astra": "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/asterix/hand.npz"}
OUT = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt2/refute_indep/"


def fatal(inner, b):
    """Would executing action b (no sticky) end the episode this step? Analytic, from MinAtar asterix.act."""
    px, py = inner.player_x, inner.player_y
    if b == 1: px = max(0, px - 1)
    elif b == 3: px = min(9, px + 1)
    elif b == 2: py = max(1, py - 1)
    elif b == 4: py = min(8, py + 1)
    for e in inner.entities:
        if e is None or e[3]:
            continue
        x, row, lr = e[0], e[1], e[2]
        if row != py:
            continue
        if x == px:
            return True
        if inner.move_timer == 0 and (x + (1 if lr else -1)) == px:
            return True
    return False


def own_row_status(inner, row):
    e = inner.entities[row - 1]
    if e is None:
        return "empty"
    x, _, lr, g = e
    toward = (5 - x) if lr else (x - 5)  # >0: still approaching col 5; 0: at col 5; <0: passed
    if g:
        return "gold_approach" if toward >= 0 else "gold_passed"
    if toward < 0:
        return "enemy_passed"
    if toward == 0:
        return "enemy_at5"
    if toward == 1:
        return "enemy_d1"
    if toward <= 3:
        return "enemy_d2_3"
    return "enemy_d4plus"


def run(net, seed, log_steps, has_units):
    env = wsp._make_env("asterix", seed); inner = env.env
    obsf = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    score, steps_log, hist = 0.0, [], []
    exp_sticky = exp_policy = 0.0
    for t in range(wsp.MAX_STEPS):
        assert inner.player_x == 5 or not has_units, "player left column 5"
        x = obsf()
        z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        last = env.last_action
        F = [fatal(inner, b if b != 5 else 0) for b in range(6)]
        y = inner.player_y
        st = own_row_status(inner, y)
        exp_sticky += 0.1 * F[last]
        exp_policy += 0.9 * float(sum(p[b] for b in range(6) if F[b]))
        rec = dict(t=t, y=y, last=last, a=a, p=p.astype(np.float64), F=F, st=st, mt=inner.move_timer, ms=inner.move_speed)
        if has_units and log_steps:
            h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
            rec["u"] = (float(h2[y - 1]), float(h2[7 + y]), float(h2[15 + y]))
            rec["h1"] = h1.copy()
        r, done = env.act(a)
        eff = env.last_action
        rec["eff"] = eff
        if F[eff] != done:
            raise RuntimeError(f"analytic fatality mismatch seed {seed} t {t}: F[eff]={F[eff]} done={done}")
        score += r
        if log_steps:
            steps_log.append(rec)
        hist.append(rec); hist = hist[-3:]
        if done:
            return dict(seed=seed, score=score, steps=t + 1, died=True, last3=hist, log=steps_log, es=exp_sticky, ep=exp_policy)
    return dict(seed=seed, score=score, steps=wsp.MAX_STEPS, died=False, last3=hist, log=steps_log, es=exp_sticky, ep=exp_policy)


def worker(args):
    which, seeds, k = args
    net = wsp.load_npz(NETS[which])
    return [run(net, s, s < k, which == "claude") for s in seeds]


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    which, n, k = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    seeds = list(range(n)); chunks = [seeds[i::4] for i in range(4)]
    with ProcessPoolExecutor(4) as ex:
        res = [r for part in ex.map(worker, [(which, c, k) for c in chunks]) for r in part]
    res.sort(key=lambda r: r["seed"])
    pickle.dump(res, open(OUT + f"run_{which}_{n}.pkl", "wb"))
    sc = np.array([r["score"] for r in res]); ln = np.array([r["steps"] for r in res])
    print(which, "n", n, "mean score %.3f se %.3f mean len %.2f" % (sc.mean(), sc.std(ddof=1) / np.sqrt(n), ln.mean()))
    print("analytic fatality matched env 'done' on every step of every episode (else RuntimeError)")
