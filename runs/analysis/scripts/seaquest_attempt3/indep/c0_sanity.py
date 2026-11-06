import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
sys.path.insert(0, "/private/tmp/claude-501/-Users-dhaneshneelamana-projects-wsp-replication/1de9272e-bb08-4c08-9f63-28011de783b7/scratchpad/analysis/seaquest_attempt3/indep")
import time, numpy as np, wsp, myrun
net = wsp.load_npz(myrun.CLAUDE)
# obs builder equality on random states along an episode
env = wsp._make_env("seaquest", 3); f = wsp.make_obs_fn(env, "seaquest")
for i in range(300):
    assert np.array_equal(f(), myrun.obs_vec(env.env)); env.act(i % 6)
print("obs_vec == make_obs_fn on 300 states")
t0 = time.time()
for s in [11, 12, 13]:
    a = wsp.play_episode(net, "seaquest", s)[:2]
    b = myrun.episode(net, s)
    print(s, a, (b["score"], b["steps"]), b["cause"], "kills", b["kills"], "bonus", b["bonus"])
print("time", round(time.time() - t0, 1))
