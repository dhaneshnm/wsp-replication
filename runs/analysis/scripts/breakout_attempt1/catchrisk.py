import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from instr import sim_landing
from collections import Counter
MOVE = {0: 0, 1: -1, 2: 0, 3: 1, 4: 0, 5: 0}
def run(args):
    net, seed = args
    env = wsp._make_env("breakout", seed)
    obs = wsp.make_obs_fn(env, "breakout")
    rng = np.random.default_rng(seed + 1_000_003)
    e = env.env
    st = Counter(); prev_exec = 0
    for t in range(wsp.MAX_STEPS):
        h1, h2, z, p = forward(net, obs())
        a = int(rng.choice(6, p=p))
        bx8, nx, k = sim_landing(e)
        pos = e.pos
        if k == 1:
            C = {bx8, nx}
            st["k1_events"] += 1
            rep = min(9, max(0, pos + MOVE[prev_exec]))
            if MOVE[prev_exec] != 0: st["prev_was_move"] += 1
            if pos in C and rep not in C: st["in_C_but_repeat_of_prev_move_exits_C"] += 1
            # probability mass of fatal actions under the policy at this step
            fatal = [aa for aa in range(6) if min(9, max(0, pos + MOVE[aa])) not in C]
            st["fatal_prob_sum_x1e6"] += int(1e6 * sum(p[aa] for aa in fatal))
            if pos not in C: st["pos_not_in_C_at_k1"] += 1
        r, done = env.act(a)
        prev_exec = env.last_action
        if done: st["miss"] += 1; break
    return st
if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    for which in ["claude", "astra"]:
        net = nets()[which]
        with ProcessPoolExecutor(4) as ex:
            res = list(ex.map(run, [(net, s) for s in range(200)], chunksize=5))
        tot = Counter()
        for r in res: tot.update(r)
        n = tot["k1_events"]
        print(f"{which}: k=1 (last-decision) events {n}, misses {tot['miss']}")
        print(f"   previous executed action was a move: {tot['prev_was_move']/n:.3f}")
        print(f"   paddle in catch set but a sticky repeat of previous move would leave it: {tot['in_C_but_repeat_of_prev_move_exits_C']/n:.3f}")
        print(f"   paddle NOT in catch set before last decision (must move): {tot['pos_not_in_C_at_k1']/n:.3f}")
        print(f"   mean policy probability of a fatal action at last decision: {tot['fatal_prob_sum_x1e6']/1e6/n:.5f}")
