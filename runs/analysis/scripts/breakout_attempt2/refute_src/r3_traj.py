import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp, numpy as np, json
from minatar import Environment
from concurrent.futures import ProcessPoolExecutor
DX = {0: -1, 1: 1, 2: 1, 3: -1}; DY = {0: -1, 1: -1, 2: 1, 3: 1}
MOVE = {1: -1, 3: 1}

def episode(args):
    path, seed, sticky = args
    net = wsp.load_npz(path)
    # identical RNG usage to wsp.play_episode
    env = Environment("breakout", sticky_action_prob=sticky); env.seed(seed); env.reset(); e = env.env
    obs = wsp.make_obs_fn(env, "breakout"); rng = np.random.default_rng(seed + 1_000_003)
    start_side = e.ball_x
    L = []; score = 0.0; nonargmax = 0; done = False
    for t in range(wsp.MAX_STEPS):
        x = obs(); z = wsp.logits(net, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        am = int(np.argmax(z)); cls = lambda q: q if q in (1, 3) else 0
        if cls(a) != cls(am): nonargmax += 1
        rec = dict(by=e.ball_y, bx=e.ball_x, dir=e.ball_dir, pos=e.pos, a=a)
        r, done = env.act(a)
        rec.update(ex=env.last_action, pos2=e.pos, done=done, r=r)
        L.append(rec); score += r
        if done: break
    steps = len(L)
    flights = []; start = 0
    for i, s in enumerate(L):
        if s["by"] == 8 and DY[s["dir"]] > 0:
            x8 = s["bx"]; dx = DX[s["dir"]]; p0 = L[start]["pos"]; n = i - start + 1
            seg = L[start:i + 1]
            delays = sum(1 for m in seg if m["ex"] != m["a"] and MOVE.get(m["a"], 0) != 0 and MOVE.get(m["ex"], 0) == 0)
            nsticky = sum(1 for m in seg if m["ex"] != m["a"])
            prev = L[i - 1] if i >= 1 else None
            catA = (not (not s["done"])) and s["pos"] == x8 and MOVE.get(s["a"], 0) == 0 and MOVE.get(s["ex"], 0) == -dx and s["ex"] != s["a"]
            info = dict(caught=not s["done"], n=n, d=abs(p0 - x8), p0=p0, x8=x8, dx=dx, start_bx=L[start]["bx"], start_by=L[start]["by"],
                        delays=delays, nsticky=nsticky, top=min(m["by"] for m in seg), catA=bool(catA), first=(start == 0),
                        pre_pos=s["pos"], a=s["a"], ex=s["ex"])
            if catA and prev is not None:
                info["prev"] = dict(pos=prev["pos"], rel=(prev["pos"] - x8) * dx, a=prev["a"], ex=prev["ex"], sticky=prev["ex"] != prev["a"],
                                    exmove=MOVE.get(prev["ex"], 0) * dx, amove=MOVE.get(prev["a"], 0) * dx, by=prev["by"])
                info["push4"] = any(m["ex"] != m["a"] and MOVE.get(m["ex"], 0) * dx > 0 for m in L[max(0, i - 4):i])
                info["by_minus2"] = L[i - 2]["by"]
            flights.append(info); start = i + 1
    return dict(seed=seed, score=score, steps=steps, done=done, start_side=start_side, nonargmax=nonargmax, flights=flights)

if __name__ == "__main__":
    path, tag, sticky, base, n = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    assert n <= 200
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(episode, [(path, s, sticky) for s in range(base, base + n)], chunksize=5))
    json.dump(res, open(f"tr_{tag}.json", "w"))
    sc = np.array([r["score"] for r in res]); st = np.array([r["steps"] for r in res])
    print(tag, "sticky", sticky, "seeds", base, "-", base + n - 1, "mean", sc.mean(), "se", sc.std(ddof=1) / np.sqrt(n),
          "min", sc.min(), "max", sc.max(), "mean_len", st.mean(), "capped(not done)", sum(1 for r in res if not r["done"]),
          "start sides", sorted(set(r["start_side"] for r in res)), "non-argmax samples", sum(r["nonargmax"] for r in res))
