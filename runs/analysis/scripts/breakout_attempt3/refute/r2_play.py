# Independent instrumented replica of wsp.play_episode (same env seeding, same sampling RNG).
# Logs every frame; splits episodes into rallies; returns per-rally features and full paths of missed rallies.
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp, pickle, collections
from concurrent.futures import ProcessPoolExecutor

CLAUDE = "/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/breakout/attempt3/net.npz"
ASTRA = "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"
DXY = {0: (-1, -1), 1: (1, -1), 2: (1, 1), 3: (-1, 1)}
T_UP = [9, 10, 9, 8, 7, 8, 9, 10, 11]

def fold(u):
    m = u % 20; return 19 - m if m >= 10 else m

def episode(net, seed, hv):
    env = wsp._make_env("breakout", seed); g = env.env
    obs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0; F = []
    for t in range(wsp.MAX_STEPS):
        x = obs()
        h1 = np.tanh(x @ net["W1"] + net["b1"]); h2 = np.tanh(h1 @ net["W2"] + net["b2"])
        z = h2 @ net["W3"] + net["b3"]
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        fr = [g.ball_y, g.ball_x, g.last_y, g.last_x, g.ball_dir, g.pos, a,
              int(np.sign(h1[hv[0]])), int(np.sign(h1[hv[1]]))]
        r, done = env.act(a)
        fr += [env.last_action, g.pos, int(done), r]
        F.append(fr); score += r
        if done: break
    return score, len(F), F
# frame fields
BY, BX, LY, LX, D, POS, A, HS, VS, EFF, POSA, DONE, R = range(13)

def rallies_of(F):
    starts = [0] + [i+1 for i, f in enumerate(F) if f[BY] == 8 and f[D] in (2, 3) and not f[DONE]]
    out = []
    for j, st in enumerate(starts):
        if st >= len(F): continue
        en = starts[j+1]-1 if j+1 < len(starts) else len(F)-1
        seg = F[st:en+1]; last = seg[-1]
        if not (last[BY] == 8 and last[D] in (2, 3)): continue  # truncated at cap
        out.append(seg)
    return out

def analyse(args):
    path, seeds, hv = args
    net = wsp.load_npz(path)
    eps = []
    for s in seeds:
        score, steps, F = episode(net, s, hv)
        dirwrong = collections.Counter()
        for f in F:
            tdx, tdy = DXY[f[D]]
            kinds = []
            if f[HS] != tdx: kinds.append("H")
            if f[VS] != tdy: kinds.append("V")
            if kinds:
                flat = f[BY] == f[LY]
                ctx = ("row8-flat" if f[BY] == 8 and flat else (f"flat-row{f[BY]}" if flat else ("same-col" if f[BX] == f[LX] else f"diag-row{f[BY]}")))
                dirwrong["+".join(kinds) + ":" + ctx] += 1
        R = []
        for seg in rallies_of(F):
            last = seg[-1]; N = len(seg)
            x8 = last[BX]; dx8 = DXY[last[D]][0]; nx8 = min(9, max(0, x8 + dx8))
            cs = {x8, nx8}
            dist = lambda p: min(abs(p - x8), abs(p - nx8))
            missed = bool(last[DONE])
            fd = next(i for i in range(N) if all(seg[k][D] in (2, 3) for k in range(i, N)))
            ev = []  # ordered events in final descent
            for i in range(fd, N):
                f = seg[i]
                if x8 != nx8 and f[POS] == nx8 and f[POSA] == x8: ev.append(("walk", i, f[POSA]-f[POS], f[EFF] != f[A]))
                if f[POS] in cs and f[POSA] not in cs:
                    ev.append(("exit_sticky" if f[EFF] != f[A] else "exit_policy", i, f[POSA]-f[POS], f[EFF] != f[A]))
            rec = dict(seed=s, N=N, missed=missed, x8=x8, nx8=nx8, fd=fd, turn_row=seg[fd][BY],
                       slack0=N - dist(seg[0][POS]), desc_len=N - fd,
                       desc_pos=seg[fd][POS], ev=ev)
            if fd > 0:
                u = seg[fd-1]
                rec["up_net_dir"] = (u[HS], u[VS]); rec["up_true_dir"] = DXY[u[D]]
                rec["up_target"] = fold(u[BX] + u[HS]*T_UP[u[BY]]) if u[VS] < 0 else None
                rec["up_row"] = u[BY]
                rec["up_pos_before"] = u[POS]
            if missed:
                rec["path"] = [tuple(f) for f in seg]
            R.append(rec)
        eps.append(dict(seed=s, score=score, steps=steps, dirwrong=dict(dirwrong), frames=len(F), rallies=R,
                        sticky_changed=sum(1 for f in F if f[EFF] != f[A])))
    return eps

if __name__ == "__main__":
    which = sys.argv[1]; n = int(sys.argv[2])
    path, hv = (CLAUDE, (8, 9)) if which == "claude" else (ASTRA, (4, 5))
    seeds = list(range(n)); W = 4
    with ProcessPoolExecutor(W) as ex:
        res = [e for part in ex.map(analyse, [(path, seeds[i::W], hv) for i in range(W)]) for e in part]
    res.sort(key=lambda e: e["seed"])
    pickle.dump(res, open(f"play_{which}_{n}.pkl", "wb"))
    sc = np.array([e["score"] for e in res]); ln = np.array([e["steps"] for e in res])
    print(which, "episodes", len(res), "mean", sc.mean(), "se", sc.std(ddof=1)/np.sqrt(len(sc)), "mean_len", ln.mean(), "capped", int((ln >= 10000).sum()))
