"""Per-step exposure stats + gold capture rate + optional sticky-prob override.
usage: episodes2.py <net.npz> <tag> <n_episodes> <sticky_prob>
Same seeds and action RNG as wsp.play_episode. With sticky_prob=0.1 this reproduces wsp exactly.
(The sticky draw env.random.rand() is still consumed when sticky_prob=0, so the spawn stream is unchanged.)
"""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy, pickle
from multiprocessing import Pool
import numpy as np
import wsp
from minatar import Environment

NET_PATH, TAG, N, STICKY = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
NET = wsp.load_npz(NET_PATH)


def fatal(inner, a):
    e = copy.deepcopy(inner)
    e.act(a)
    return e.terminal


def run(seed):
    env = Environment("asterix", sticky_action_prob=STICKY)
    env.seed(seed); env.reset()
    inner = env.env
    spawned = {"gold": 0, "enemy": 0}
    obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0
    st = dict(steps=0, prev_fatal=0, prev_move_steps=0, prev_move_fatal=0, prev_noop_fatal=0,
              gold_stay=0, gold_move=0, sticky_exec=0)
    for t in range(wsp.MAX_STEPS):
        x = obs()
        z = wsp.logits(NET, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        prev = env.last_action
        pf = fatal(inner, prev)
        st["steps"] += 1
        st["prev_fatal"] += pf
        if prev in (2, 4):
            st["prev_move_steps"] += 1
            st["prev_move_fatal"] += pf
        else:
            st["prev_noop_fatal"] += pf
        y0 = inner.player_y
        prev_objs = list(inner.entities)   # keep references so ids are not reused
        r, done = env.act(a)
        for e in inner.entities:
            if e is not None and all(e is not q for q in prev_objs):
                spawned["gold" if e[3] else "enemy"] += 1
        if r:
            score += r
            st["gold_move" if inner.player_y != y0 else "gold_stay"] += r
        if done:
            break
    return dict(score=score, steps=t + 1, spawned=spawned, **{k: v for k, v in st.items() if k != "steps"})


if __name__ == "__main__":
    with Pool(4) as pool:
        res = pool.map(run, range(N), chunksize=5)
    pickle.dump(res, open(f"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1/ep2_{TAG}.pkl", "wb"))
    sc = np.array([r["score"] for r in res]); L = np.array([r["steps"] for r in res])
    S = lambda k: sum(r[k] for r in res)
    gs = sum(r["spawned"]["gold"] for r in res)
    print(f"{TAG} sticky={STICKY}: mean score {sc.mean():.2f} (se {sc.std(ddof=1)/np.sqrt(N):.2f}) mean len {L.mean():.1f}")
    print(f"  gold spawned {gs}, collected {sc.sum():.0f}, capture rate {sc.sum()/gs:.3f}; collected while staying {S('gold_stay')}, while moving {S('gold_move')}")
    print(f"  steps where previous action would be fatal if repeated: {S('prev_fatal')/L.sum():.4f} of all steps")
    print(f"  ... given previous action was up/down: {S('prev_move_fatal')}/{S('prev_move_steps')} = {S('prev_move_fatal')/max(1,S('prev_move_steps')):.4f}")
    print(f"  ... given previous action was noop/other: {S('prev_noop_fatal')}/{L.sum()-S('prev_move_steps')} = {S('prev_noop_fatal')/(L.sum()-S('prev_move_steps')):.4f}")
    print(f"  expected sticky deaths per episode at p=0.1: {0.1*S('prev_fatal')/N:.3f}")
