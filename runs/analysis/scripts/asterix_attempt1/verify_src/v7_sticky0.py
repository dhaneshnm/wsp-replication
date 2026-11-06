"""Independent re-run: Claude's net, 200 episodes (seeds 0..199), same loop as wsp.play_episode but MinAtar sticky_action_prob=0.0."""
import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
from multiprocessing import Pool
import numpy as np, wsp
from minatar import Environment
NET = wsp.load_npz("/Users/dhaneshneelamana/projects/wsp-replication/runs/claude-opus-5-5/asterix/attempt1/net.npz")
def run(seed):
    env = Environment("asterix", sticky_action_prob=0.0); env.seed(seed); env.reset()
    obs = wsp.make_obs_fn(env, "asterix"); rng = np.random.default_rng(seed + 1_000_003); score = 0.0
    for t in range(wsp.MAX_STEPS):
        z = wsp.logits(NET, obs()); p = np.exp(z - z.max()); p /= p.sum()
        r, done = env.act(int(rng.choice(6, p=p))); score += r
        if done: return score, t + 1
    return score, wsp.MAX_STEPS
if __name__ == "__main__":
    with Pool(4) as pool: res = pool.map(run, range(200), chunksize=5)
    s = np.array([r[0] for r in res]); L = np.array([r[1] for r in res])
    print(f"sticky=0.0 seeds 0..199: mean {s.mean():.2f} se {s.std(ddof=1)/np.sqrt(len(s)):.2f} len {L.mean():.1f}")
