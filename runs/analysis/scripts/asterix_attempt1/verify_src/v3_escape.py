"""For each Claude trapped death (from episodes_claude.pkl), replay the same episode (same seeds/RNG as wsp.play_episode),
take the pre-step snapshot at the death step, and test whether a sideways step leads to survival for D further steps
(any of 5 actions per step, spawn RNG kept aligned by consuming the sticky draw before each simulated step, no sticky repeats)."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import copy, pickle, collections
from multiprocessing import Pool
import numpy as np
import wsp
D = "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/asterix_attempt1"
NET = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
ALL5 = [0, 1, 2, 3, 4]

def step(inner, a):
    e = copy.deepcopy(inner); e.random.rand(); e.act(a); return e

def surv(inner, depth):
    if depth == 0: return True
    for a in ALL5:
        e = step(inner, a)
        if not e.terminal and surv(e, depth - 1): return True
    return False

def run(args):
    seed, death_step = args
    env = wsp._make_env("asterix", seed); obs = wsp.make_obs_fn(env, "asterix")
    rng = np.random.default_rng(seed + 1_000_003); inner = env.env
    for t in range(wsp.MAX_STEPS):
        x = obs(); z = wsp.logits(NET, x); p = np.exp(z - z.max()); p /= p.sum()
        a = int(rng.choice(6, p=p))
        snap = copy.deepcopy(inner)
        r, done = env.act(a)
        if done:
            assert t + 1 == death_step, (seed, t + 1, death_step)
            out = {"seed": seed, "row": snap.player_y}
            fat = {b: step(snap, b).terminal for b in ALL5}
            out["fatal"] = fat
            for b in (1, 3):
                if fat[b]: continue
                e = step(snap, b)
                out[b] = {d: surv(e, d) for d in (1, 2, 3, 4, 5, 6)}
            return out
    return None

if __name__ == "__main__":
    res = pickle.load(open(f"{D}/episodes_claude.pkl", "rb"))
    tr = [(r["death"]["seed"], r["death"]["steps"]) for r in res if r["death"] and r["death"]["cause"] == "trapped"]
    with Pool(4) as pool:
        outs = pool.map(run, tr)
    print("trapped deaths replayed:", len(outs))
    print("vertical all fatal (with RNG-aligned sim):", sum(all(o["fatal"][b] for b in (0, 2, 4)) for o in outs))
    for d in (1, 2, 3, 4, 5, 6):
        ok = sum(any(o[b][d] for b in (1, 3) if b in o) for o in outs)
        print(f"sideways step then survive {d} more steps (best follow-up, 5 actions): {ok}/{len(outs)}")
    bad = [o for o in outs if not any(o[b][6] for b in (1, 3) if b in o)]
    print("not survivable 6 more steps after sideways:", [(o["seed"], o["row"]) for o in bad])
