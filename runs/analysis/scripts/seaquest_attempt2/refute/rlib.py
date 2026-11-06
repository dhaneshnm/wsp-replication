# My own instrumentation (independent of the analyst's common.py/instr.py).
import sys, copy
sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import numpy as np, wsp
A = "/Users/dhaneshneelamana/projects/wsp-replication/runs/cap128k/claude-opus-5-5/seaquest/attempt2/"
CL = wsp.load_npz(A + "net.npz")
AS = wsp.load_npz("/Users/dhaneshneelamana/lm_understand-logs/exp5_write_from_scratch/networks/seaquest/hand.npz")
NAMES = ['noop', 'left', 'up', 'right', 'down', 'fire']

def layers(net, x, h1_hook=None):
    a1 = x @ net["W1"] + net["b1"]
    h1 = np.tanh(a1)
    if h1_hook is not None:
        h1 = h1_hook(h1)
    a2 = h1 @ net["W2"] + net["b2"]
    h2 = np.tanh(a2)
    z = h2 @ net["W3"] + net["b3"]
    q = np.exp(z - z.max()); q = q / q.sum()
    return dict(a1=a1, h1=h1, h2=h2, z=z, p=q)

def snapshot(g):
    return dict(sx=g.sub_x, sy=g.sub_y, sor=bool(g.sub_or), dc=g.diver_count, oxy=g.oxygen,
                fish=[tuple(f[:3]) for f in g.e_fish], esub=[tuple(s[:3]) for s in g.e_subs],
                eb=[tuple(b[:3]) for b in g.e_bullets], div=[tuple(d[:3]) for d in g.divers],
                shot=g.shot_timer)

def episode(net, seed, step_cb=None, h1_hook_fn=None, max_steps=wsp.MAX_STEPS):
    """Replays wsp.play_episode exactly, but applies the sticky rule by hand so the sampled and executed
    actions are both known. step_cb(t, pre_snapshot, out, a_sampled, a_exec, r, done, g) is called per step.
    h1_hook_fn(g) -> hook or None, for intervention experiments."""
    env = wsp._make_env("seaquest", seed)
    g = env.env
    obs = wsp.make_obs_fn(env, "seaquest")
    rng = np.random.default_rng(seed + 1_000_003)
    score = 0.0
    for t in range(max_steps):
        x = obs()
        hook = h1_hook_fn(g, x) if h1_hook_fn else None
        out = layers(net, x, hook)
        out['x'] = x
        a = int(rng.choice(6, p=out['p']))
        pre = snapshot(g) if step_cb else None
        # same as minatar Environment.act, unrolled
        if env.random.rand() < env.sticky_action_prob:
            ae = env.last_action
        else:
            ae = a
        env.last_action = ae
        r, done = g.act(ae)
        score += r
        if step_cb:
            step_cb(t, pre, out, a, ae, r, done, g)
        if done:
            return score, t + 1
    return score, max_steps

def end_cause(pre, g):
    if g.sub_y == 0 and pre['sy'] > 0 and pre['dc'] == 0:
        return 'surface_no_diver'
    if pre['oxy'] <= 0:
        return 'oxygen'
    return 'collision'
