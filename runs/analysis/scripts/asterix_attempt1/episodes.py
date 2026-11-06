"""Instrumented replay of wsp.play_episode (same seeds, same action RNG) with death classification.
usage: episodes.py <net.npz> <tag> <n_episodes>
"""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy, json, pickle
from multiprocessing import Pool
import numpy as np
import wsp

NET_PATH, TAG, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
NET = wsp.load_npz(NET_PATH)
V = [0, 2, 4]          # vertical action set (noop, up, down)
ALL5 = [0, 1, 2, 3, 4]


def step_dies(inner, a):
    e = copy.deepcopy(inner)
    e.act(a)
    return e.terminal, e


def survivable(inner, depth, acts):
    if depth == 0:
        return True
    for a in acts:
        dead, e = step_dies(inner, a)
        if not dead and survivable(e, depth - 1, acts):
            return True
    return False


def run(seed):
    env = wsp._make_env("asterix", seed)
    obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003)
    inner = env.env
    score = 0.0
    hist = []              # snapshots of inner env before each step
    gold_steps = []        # (step, ramp_index) for each reward
    moves = 0
    col_set = set()
    row_steps = np.zeros(10, int)
    for t in range(wsp.MAX_STEPS):
        x = obs()
        z = wsp.logits(NET, x)
        p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        snap = copy.deepcopy(inner)
        hist.append(snap)
        if len(hist) > 6:
            hist.pop(0)
        peek = copy.deepcopy(env.random)
        sticky = peek.rand() < wsp.STICKY
        prev = env.last_action
        executed = prev if sticky else a
        row_steps[inner.player_y] += 1
        col_set.add(inner.player_x)
        y0 = inner.player_y
        r, done = env.act(a)
        assert env.last_action == executed
        if inner.player_y != y0:
            moves += 1
        if r:
            score += r
            gold_steps.append((t, snap.ramp_index, r))
        if done:
            # classify death using the pre-step snapshot
            fatal = {b: step_dies(snap, b)[0] for b in ALL5}
            safe_vert = [b for b in V if not fatal[b]]
            safe_horiz = [b for b in (1, 3) if not fatal[b]]
            sampled_fatal = fatal[a if a != 5 else 0]
            if not safe_vert:
                cause = "trapped"
            elif sticky and fatal[executed] and not sampled_fatal:
                cause = "sticky"
            else:
                cause = "sampled_fatal"
            # how many steps earlier was the death still avoidable (vertical-only / all moves)?
            look_v, look_all = None, None
            for k in range(1, len(hist)):
                s = hist[-1 - k]
                if look_v is None and survivable(s, k + 1, V):
                    look_v = k
                if look_all is None and survivable(s, k + 1, ALL5):
                    look_all = k
                if look_v is not None and look_all is not None:
                    break
            # enemy configuration in player row and neighbours (pre-step)
            ents = [None if en is None else list(en) for en in snap.entities]
            info = dict(seed=seed, score=score, steps=t + 1, cause=cause, sticky=bool(sticky),
                        sampled=a, executed=executed, p=p.tolist(), fatal=fatal,
                        safe_vert=safe_vert, safe_horiz=safe_horiz,
                        ramp=snap.ramp_index, move_speed=snap.move_speed, spawn_speed=snap.spawn_speed,
                        move_timer=snap.move_timer, player=(snap.player_y, snap.player_x),
                        entities=ents, look_v=look_v, look_all=look_all,
                        n_alive=sum(en is not None for en in snap.entities))
            return dict(score=score, steps=t + 1, death=info, gold=gold_steps, moves=moves,
                        cols=sorted(col_set), row_steps=row_steps.tolist())
    return dict(score=score, steps=wsp.MAX_STEPS, death=None, gold=gold_steps, moves=moves,
                cols=sorted(col_set), row_steps=row_steps.tolist())


if __name__ == "__main__":
    with Pool(4) as pool:
        res = pool.map(run, range(N), chunksize=5)
    out = f"/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1/episodes_{TAG}.pkl"
    pickle.dump(res, open(out, "wb"))
    sc = np.array([r["score"] for r in res]); st = np.array([r["steps"] for r in res])
    print(f"{TAG}: episodes={N} mean score={sc.mean():.2f} (se {sc.std(ddof=1)/np.sqrt(N):.2f}) mean len={st.mean():.1f} max={sc.max()}")
