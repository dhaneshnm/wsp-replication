"""Independent rollout recorder. Mirrors wsp.play_episode (same env seed, same sampling rng) and records
per-step diagnostics plus a one-step counterfactual at the terminal step (deep-copied env, every action tried)."""
import sys, os, copy, pickle
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np
import wsp
from concurrent.futures import ProcessPoolExecutor

D = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt1/"
NETS = {"claude": D + "net.npz",
        "astra": "/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz"}
OUT = os.path.dirname(os.path.abspath(__file__))


def hidden(net, x):
    h1 = np.tanh(x @ net["W1"] + net["b1"])
    return h1, np.tanh(h1 @ net["W2"] + net["b2"])


def sub_cells(x, right):
    return (x - 1, x) if right else (x, x + 1)


def try_action(env, a):
    """Return (terminal, reward) of executing action a (forced, sticky draw consumed) from a copy of env."""
    c = copy.deepcopy(env)
    c.random.rand()
    c.last_action = a
    r, d = c.env.act(a)
    return d, r


def episode(args):
    name, seed, mode = args
    net = wsp.load_npz(NETS[name])
    env = wsp._make_env("seaquest", seed)
    g = env.env
    ob = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    score, steps = 0.0, []
    death = None
    surf_onsets, surf_prev = [], False
    for t in range(wsp.MAX_STEPS):
        x = ob()
        z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        pre_env = copy.deepcopy(env)
        pre = dict(t=t, x=g.sub_x, y=g.sub_y, right=g.sub_or, oxy=g.oxygen, dc=g.diver_count, a=a,
                   pa=p.astype(float).round(4).tolist())
        surf = g.oxygen < 60 and g.diver_count >= 1
        if surf and not surf_prev:
            surf_onsets.append(t)
        surf_prev = surf
        if name == "claude" and mode == "full":
            h1, h2 = hidden(net, x)
            pre["h2"] = h2[:6].astype(float).round(3).tolist()
            pre["fish"] = [list(f[:3]) for f in g.e_fish]
            pre["subs"] = [list(s[:3]) for s in g.e_subs]
            pre["divers"] = [list(d[:3]) for d in g.divers]
            pre["bul"] = [list(b[:3]) for b in g.e_bullets]
            if g.sub_y >= 2:
                row = g.sub_y
                cells = sub_cells(g.sub_x, g.sub_or)
                grid = x.reshape(10, 10, 6)
                pre["foreign_trail_cols"] = [c for c in range(10) if grid[row, c, 4] and c not in cells]
                # counterfactual T without foreign trails in own row
                x2 = x.copy().reshape(10, 10, 6)
                for c in pre["foreign_trail_cols"]:
                    x2[row, c, 4] = 0
                _, h2b = hidden(net, x2.reshape(600))
                pre["h2_notrail"] = h2b[:6].astype(float).round(3).tolist()
                # counterfactual without divers in own row (ch2 at diver cells not shared with an enemy)
                x3 = x.copy().reshape(10, 10, 6)
                enemy_cells = {(e[1], e[0]) for e in g.e_fish + g.e_subs}
                for d in g.divers:
                    if d[1] == row and (d[1], d[0]) not in enemy_cells:
                        x3[row, d[0], 2] = 0
                _, h2c = hidden(net, x3.reshape(600))
                pre["h2_nodiver"] = h2c[:6].astype(float).round(3).tolist()
        r, done = env.act(a)
        score += r
        pre["ea"] = env.last_action
        pre["r"] = r
        pre["nx"], pre["ny"], pre["nright"], pre["ndc"] = g.sub_x, g.sub_y, g.sub_or, g.diver_count
        pre["done"] = done
        steps.append(pre)
        if done:
            alt = {b: try_action(pre_env, b)[0] for b in range(6)}
            # check replay of executed action reproduces the death
            alt_exec = try_action(pre_env, pre["ea"])[0]
            pe = pre_env.env
            death = dict(t=t, ea=pre["ea"], a=a, alt_terminal=alt, exec_reproduced=alt_exec,
                         pre_y=pe.sub_y, pre_x=pe.sub_x, pre_right=pe.sub_or, pre_dc=pe.diver_count, pre_oxy=pe.oxygen,
                         post_y=g.sub_y, post_x=g.sub_x,
                         spawn_timer=pe.e_spawn_timer,
                         fish=[list(f[:4]) for f in pe.e_fish], subs=[list(s[:4]) for s in pe.e_subs],
                         bul=[list(b[:3]) for b in pe.e_bullets],
                         post_fish=[list(f[:3]) for f in g.e_fish], post_subs=[list(s[:3]) for s in g.e_subs])
            break
    return dict(name=name, seed=seed, score=score, length=len(steps), death=death, surf_onsets=surf_onsets,
                steps=steps if mode == "full" else [
                    {k: s[k] for k in ("t", "x", "y", "right", "oxy", "dc", "a", "ea", "r", "nx", "ny", "nright", "ndc", "done")}
                    for s in steps])


if __name__ == "__main__":
    name, n = sys.argv[1], int(sys.argv[2])
    mode = "full" if name == "claude" else "lite"
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(episode, [(name, s, mode) for s in range(n)], chunksize=5))
    pickle.dump(res, open(os.path.join(OUT, f"roll_{name}_{n}.pkl"), "wb"))
    sc = np.array([r["score"] for r in res]); L = np.array([r["length"] for r in res])
    print(name, "episodes", n, "mean score", round(sc.mean(), 3), "se", round(sc.std(ddof=1) / np.sqrt(n), 3),
          "mean len", round(L.mean(), 1))
    # cross-check against wsp.play_episode on a few seeds
    net = wsp.load_npz(NETS[name])
    for s in range(0, n, max(1, n // 8)):
        ws, wl, _ = wsp.play_episode(net, "seaquest", s)
        print(f"  seed {s}: mine ({res[s]['score']}, {res[s]['length']})  wsp.play_episode ({ws}, {wl})")
